import os
import sys
import json
import subprocess
import requests
import copy
import shutil

from .tc_tools import time_seconds_to_vid_frames,vid_frames_to_tc, tc_to_time_seconds

def make_request(func,port,route,payload=None):
    url = f'http://localhost:{port}'
    if port==38383 and os.getenv('CODA_API_BASE_URL'):
        url = os.getenv('CODA_API_BASE_URL')
    url += route
    #print('request',url,file=sys.stderr)
    auth = None
    if os.getenv('CODA_API_TOKEN'):
        auth= {'Authorization': f"Bearer {os.getenv('CODA_API_TOKEN')}"}
    ret = func(url,json=payload,headers=auth)
    return ret

def timingInfo(inputs,venue=None,fps=None,ffoa=None,lfoa=None,start_time=None):
    if not inputs:
        return None
    tinfo = {}
    if venue:
        tinfo['venue'] = venue
    else:
        tinfo['venue'] = inputs['venue']
    if not fps:
        tinfo['source_frame_rate'] = inputs['source_frame_rate']
        fps = tinfo['source_frame_rate']
    else:
        tinfo['source_frame_rate'] = fps
    if not ffoa:
        tinfo['ffoa_timecode'] = inputs['ffoa_timecode']
    else:
        tinfo['ffoa_timecode'] = ffoa
    if not lfoa:
        tinfo['lfoa_timecode'] = inputs['lfoa_timecode']
    else:
        tinfo['lfoa_timecode'] = lfoa
    startt=-1
    srate=-1
    filelen = -1
    sources = inputs['sources']
    for i in sources:
        if len(sources[i]):
            if 'programme_timing' in sources[i][0]:
                srate = sources[i][0]['sample_rate']
                filelen = sources[i][0]['frames'] / srate
                startt = sources[i][0]['programme_timing']['audio_programme_start_time_reference'] / srate
            elif 'resources' in sources[i][0]:
                startt = sources[i][0]['resources'][0]['bext_time_reference']/sources[i][0]['resources'][0]['sample_rate']
                srate = sources[i][0]['resources'][0]['sample_rate']
                filelen = sources[i][0]['resources'][0]['frames'] / srate
            break
    tinfo['start_time_sec'] = startt
    tinfo['file_duration_sec'] = filelen
    tinfo["file_duration"] =""
    if fps!="":
        tinfo['file_duration'] = vid_frames_to_tc(time_seconds_to_vid_frames(filelen,fps),fps)
        tinfo["start_timecode"] =""
    if fps!="":
        tinfo['start_timecode'] = vid_frames_to_tc(time_seconds_to_vid_frames(startt,fps),fps)
    tinfo["end_timecode"] =""
    if fps!="":
        tinfo['end_timecode'] = vid_frames_to_tc(time_seconds_to_vid_frames(startt+filelen,fps)-1,fps)
    tinfo["ffoa_seconds"] = -1
    tinfo["lfoa_seconds"] = -1
    if fps!="":
        tinfo["ffoa_seconds"] = tc_to_time_seconds(tinfo['ffoa_timecode'],fps)
        tinfo["lfoa_seconds"] = tc_to_time_seconds(tinfo['lfoa_timecode'],fps)
    tinfo['sample_rate'] = srate

    return tinfo

class CodaPreset(object):

    routes = {
            'groups': 'groups',
            'jobs': 'jobs',
            'workflows': 'workflows',
            'naming':'naming-conventions',
            'dolby': 'presets/encoding/dolby',
            'dts':'presets/encoding/dts' ,
            'loudness':'presets/loudness',
            'timecode':'presets/timecode',
            'super_session':'presets/super-session'
            }

    def __init__(self,preset_type,value):
        self.preset = preset_type
        self.value = value

    def register(self):
        # check if name exists and find preset id
        assert(self.preset in CodaPreset.routes)
        presets = CodaPreset.getPresets(self.preset)
        foundid =None
        if presets and len(presets)>0:
            pf = [ p for p in presets if p['name']==self.value['name'] ]
            if len(pf)>0:
                assert(len(pf)==1)
                if self.preset=='dolby' or self.preset=='dts':
                    foundid  = pf[0]['encoding_preset_id']
                elif self.preset == 'loudness':
                    foundid  = pf[0]['loudness_preset_id']
                elif self.preset == 'timecode':
                    foundid  = pf[0]['timecode_preset_id']
                elif self.preset == 'naming':
                    foundid  = pf[0]['naming_convention_id']
                elif self.preset == 'super_session':
                    foundid  = pf[0]['super_session_preset_id']
                elif self.preset == 'groups':
                    foundid  = pf[0]['group_id']
        if not foundid:
            # add preset with that name for the first time
            print(f"creating new preset {self.value['name']}",file=sys.stderr)
            #ret = requests.post(f'http://localhost:38383/interface/v1/{CodaPreset.routes[self.preset]}',json=self.value)
            ret = make_request(requests.post,38383,f'/interface/v1/{CodaPreset.routes[self.preset]}',self.value)
        else:
            # update found preset
            print(f"updating preset {self.value['name']}, id={foundid}",file=sys.stderr)
            #ret = requests.put(f'http://localhost:38383/interface/v1/{CodaPreset.routes[self.preset]}/{foundid}',json=self.value)
            ret = make_request(requests.put,38383,f'/interface/v1/{CodaPreset.routes[self.preset]}/{foundid}',self.value)
        J = ret.json()
        return J

    @staticmethod
    def getPresets(preset_type):
        assert(preset_type in CodaPreset.routes)
        #ret = requests.get(f'http://localhost:38383/interface/v1/{CodaPreset.routes[preset_type]}')
        ret = make_request(requests.get,38383,f'/interface/v1/{CodaPreset.routes[preset_type]}')
        J = ret.json()
        if 'error' in J:
            return None
        return J

class CodaEssence(object):
    def __init__(self,stemformat,stemtype="audio/pm",program="program-1",description=""):
        self.payload = {
                'type':stemtype,
                'format': stemformat,
                'resources':[],
                'program':program,
                'description':description
                }
        self.esstype = None
        self.stemtype = stemtype

    def addInterleavedResource(self,file,channel_selection,chans,samps,quant=24,srate=48000):
        self.esstype='interleaved'
        auth=None
        opts=None
        F = file
        if type(F)==str:
            f = F
        else:
            if 'auth' in F:
                auth = F['auth']
            if 'opts' in F:
                opts = F['opts']
            f = F['url']

        res ={
                'bit_depth' : quant,
                'sample_rate' : srate,
                'url':f,
                'channel_count':chans,
                'frames':samps,
                'channel_selection':channel_selection.copy()
         }

        if auth is not None:
            res['auth'] = auth
        if opts is not None:
            res['opts'] = opts
        for r in res:
            self.payload[r] = res[r]
        del self.payload['resources']

    def addMultiMonoResources(self,files,samps,quant=24,srate=48000):
        self.esstype='multi_mono'
        for F in files:
            auth=None
            opts=None
            if type(F)==str:
                f = F
            else:
                if 'auth' in F:
                    auth = F['auth']
                if 'opts' in F:
                    opts = F['opts']
                f = F['url']

            label =""
            chlabels = ['Lsr','Rsr','Lts','Rts','Lss','Rss','Lfe','Ls','Rs','L','C','R']
            for ch in chlabels:
                if '.'+ch.upper()+'.' in f.upper():
                    label = ch[0:1].upper()+ch[1:].lower()
                    if ch=='Lfe':
                        label = 'LFE'
                    break
            res ={
                    'bit_depth' : quant,
                    'sample_rate' : srate,
                    'url':f,
                    'channel_count':1,
                    'frames':samps,
                    'channel_label':label,
                    'bext_time_reference':0
             }
            if auth is not None:
                res['auth'] = auth
            if opts is not None:
                res['opts'] = opts
            self.payload['resources'] += [res]
        return

    def dict(self):
        if self.payload['format']!='atmos':
            if 'resources' in self.payload:
                assert len(self.payload['resources'])==sum([ int(e) for e in self.payload['format'].split('.')])
            else:
                assert len(self.payload['channel_selection'])==sum([ int(e) for e in self.payload['format'].split('.')])
        return self.payload


class CodaWorkflow(object):
    def __init__(self,name):
        self.name = name
        self.packages = {}
        self.agents = {}
        self.processBlocks = {}
        self.destinations= {}
        self.wfparams= {}

    @staticmethod
    def getChannels(fmt):
        if fmt=='7.1.4':
            return ['L','R','C','LFE','Lss','Rss','Lsr','Rsr','Ltf','Rtf','Ltr','Rtr']
        elif fmt=='7.1.2':
            return ['L','R','C','LFE','Lss','Rss','Lsr','Rsr','Ltm','Rtm']
        elif fmt=='7.1':
            return ['L','R','C','LFE','Lss','Rss','Lsr','Rsr']
        elif fmt=='5.1':
            return ['L','R','C','LFE','Ls','Rs']
        elif fmt=='2.0':
            return ['L','R']

    def setParameters(self,params):
        self.wfparams = params.copy()

    def importFromPreset(self,preset):
       if preset and type(preset) is dict:
            self.processBlocks = copy.deepcopy(preset['definition']['process_blocks'])
            self.packages = copy.deepcopy(preset['definition']['packages'])
            self.agents = copy.deepcopy(preset['definition']['agents'])
            self.destinations = copy.deepcopy(preset['definition']['destinations'])
            if 'name' in preset:
                self.name = preset['name']
            return 0
       else:
            wfpresets = CodaPreset.getPresets("workflows")
            for J in wfpresets:
                if preset and type(preset) is str and J['name']==preset:
                    self.processBlocks = copy.deepcopy(J['definition']['process_blocks'])
                    self.packages = copy.deepcopy(J['definition']['packages'])
                    self.agents = copy.deepcopy(J['definition']['agents'])
                    self.destinations = copy.deepcopy(J['definition']['destinations'])
                    self.name = J['name']
                    print('imported workflow',self.name,'id',J['workflow_id'],file=sys.stderr)
                    return J['workflow_id']
                elif preset and type(preset) is int and J['workflow_id']==preset:
                    self.processBlocks = copy.deepcopy(J['definition']['process_blocks'])
                    self.packages = copy.deepcopy(J['definition']['packages'])
                    self.agents = copy.deepcopy(J['definition']['agents'])
                    self.destinations = copy.deepcopy(J['definition']['destinations'])
                    self.name = J['name']
                    print('imported workflow',self.name,'id',J['workflow_id'],file=sys.stderr)
                    return J['workflow_id']
       return -1


    def importFromJob(self,jobid,use_mne_definition=False):
        print(f'importing workflow from job {jobid}',file=sys.stderr)
        #ret = requests.get(f'http://localhost:38383/interface/v1/jobs/{jobid}')
        ret = make_request(requests.get,38383,f'/interface/v1/jobs/{jobid}')
        J = ret.json()
        assert(J['status']=='COMPLETED')
        if use_mne_definition and 'mne_workflow_definition' in J:
            self.processBlocks = copy.deepcopy(J['mne_workflow_definition']['process_blocks'])
            self.packages = copy.deepcopy(J['mne_workflow_definition']['packages'])
            self.agents = copy.deepcopy(J['mne_workflow_definition']['agents'])
            self.destinations = copy.deepcopy(J['mne_workflow_definition']['destinations'])
        else:
            if use_mne_definition:
                print('** WARNING ** Mne workflow definition was not found. using normal workflow',file=sys.stderr)
            self.processBlocks = copy.deepcopy(J['workflow_definition']['process_blocks'])
            self.packages = copy.deepcopy(J['workflow_definition']['packages'])
            self.agents = copy.deepcopy(J['workflow_definition']['agents'])
            self.destinations = copy.deepcopy(J['workflow_definition']['destinations'])
        return


    def addProcessBlock(self,name, output_venue="nearfield",loudness=None,timecode=None,input_filter="all_stems"):

        if not loudness:
            loudness= {}
        if not timecode:
            timecode= {}

        if timecode and type(timecode) is str:
            presets = CodaPreset.getPresets('timecode')
            pf = [ p for p in presets if p['name']==timecode ]
            assert(len(pf)==1)
            print('found timecode id',pf[0]['timecode_preset_id'],'for',timecode,file=sys.stderr)
            timecode  = pf[0]['definition']

        if loudness and type(loudness) is str:
            presets = CodaPreset.getPresets('loudness')
            pf = [ p for p in presets if p['name']==loudness ]
            assert(len(pf)==1)
            print('found loudness id',pf[0]['loudness_preset_id'],'for',loudness,file=sys.stderr)
            loudness  = pf[0]['definition']

        if 'tolerances' not in loudness:
            loudness['tolerances']= {
                            "target_program_loudness": [
                                -0.5,
                                0.4
                            ],
                            "target_dialog_loudness": [
                                -0.5,
                                0.4
                            ],
                            "target_true_peak": [
                                -0.2,
                                0.0
                            ]
             }
        pblock = {
                "name":name,
                "input_filter": input_filter,
                "output_settings": {
                    "loudness": loudness,
                    "venue":output_venue,
                    },
                "output_essences": {}
        }
        if timecode:
               pblock["output_settings"][ "timecode"]=timecode

        pid = f"my-process-block-{len(self.processBlocks)+1}"
        self.processBlocks[pid] = pblock
        return

    def addDCPPackage(self,name,process_blocks,reels=False,naming_convention=None,naming_options=None,package_wide_uuid=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        blist = []
        for b in process_blocks:
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            assert(block['output_settings']['venue']=='theatrical')
            fps = "24"
            fmt = ["atmos"]
            typ = ["printmaster"]
            for F in fmt:
                for t in typ:
                    block['output_essences'][t+'_'+fps+'_'+F]= {
                                'audio_format': F,
                                'frame_rate': fps,
                                'type':t
                            }
        if 'dcp_mxf' not in self.packages:
            self.packages['dcp_mxf'] = {}
        pid = f"my-dcp-mxf-package-{len(self.packages['dcp_mxf'])+1}"

        self.packages['dcp_mxf'][pid] = {
                    "name": name,
                    "process_block_ids":blist,
                    "include_reel_splitting" : reels,
                    "include_package_wide_uuid" :package_wide_uuid,
                }
        if naming_convention_id:
            self.packages['dcp_mxf'][pid]['naming_convention_id'] =  naming_convention_id
        if naming_convention:
            self.packages['dcp_mxf'][pid]['naming_convention'] =  naming_convention.copy()
        if naming_options:
            self.packages['dcp_mxf'][pid]["naming_convention_options"] = naming_options

    def addSuperSessionPackage(self,name,process_blocks,essences,super_session_profile=None,naming_convention=None,naming_options=None,package_wide_uuid=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        super_session_profile_id=None
        if super_session_profile and type(super_session_profile) is str:
            presets = CodaPreset.getPresets('super_session')
            pf = [ p for p in presets if p['name']==super_session_profile ]
            assert(len(pf)==1)
            print('found super_session_profile id',pf[0]['super_session_preset_id'],'for',super_session_profile,file=sys.stderr)
            super_session_profile_id  = int(pf[0]['super_session_profile_id'])
            super_session_profile=None
        elif super_session_profile and type(super_session_profile) is dict:
            super_session_profile_id=None
        elif super_session_profile:
            super_session_profile_id  = int(super_session_profile)
            super_session_profile=None
        else:
            assert(super_session_profile is None)
            print('populating default session profile')
            # populate default profile with all essences from all blocks
            super_session_profile_id = None
            super_session_profile= {'session_name_template': "{{TITLE}}_{{FRAME_RATE}}", 'tracks':[] }


        tracks = []
        blist = []
        venues = []
        for idx,b in enumerate(process_blocks):
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            venues += [ block['output_settings']['venue']]
            fps = [essences[0]]
            fmt = essences[1][idx][0]
            typ = essences[1][idx][1]
            ven = block['output_settings']['venue']
            for fr in fps:
                for F in fmt:
                    for t in typ:
                        block['output_essences'][t+'_'+fr+'_'+F]= {
                                    'audio_format': F,
                                    'frame_rate': fr,
                                    'type':t
                                }
                        if ven != 'same_as_input':
                            tracks += [ { 'element': t, 'format':F, 'venue': ven } ]
                        else:
                            tracks += [ { 'element': t, 'format':F, 'venue': 'theatrical' } ]
                            tracks += [ { 'element': t, 'format':F, 'venue': 'nearfield' } ]

        if super_session_profile and len(super_session_profile['tracks'])==0:
            T = []
            for t in tracks:
                if t['element']=='wides' or t['element']=='same_as_input':
                    stemlist = ['audio/dx','audio/fx','audio/mx','audio/vox','audio/fol','audio/fix']
                    for k in stemlist:
                        T += [ { 'element':k , 'format':t['format'], 'venue':t['venue']} ]
                elif t['element']=='dme':
                    stemlist = ['audio/dx','audio/fx','audio/mx']
                    for k in stemlist:
                        T += [ { 'element':k , 'format':t['format'], 'venue':t['venue']} ]
                elif t['element']=='printmaster':
                        T += [ { 'element':'audio/pm' , 'format':t['format'], 'venue':t['venue']} ]
                else:
                    T += [t]
            super_session_profile['tracks'] = T

        if 'super_session' not in self.packages:
            self.packages['super_session'] = {}
        pid = f"my-super-session-package-{len(self.packages['super_session'])+1}"

        self.packages['super_session'][pid] = {
                    "name": name,
                    "process_block_ids":blist,
                    "frame_rate" : essences[0],
                    "include_package_wide_uuid" :package_wide_uuid,
                }
        if super_session_profile_id:
            self.packages['super_session'][pid]['super_session_profile_id'] =  super_session_profile_id
        if super_session_profile:
            self.packages['super_session'][pid]['super_session_profile'] =  super_session_profile.copy()
        if naming_convention_id:
            self.packages['super_session'][pid]['naming_convention_id'] =  naming_convention_id
        if naming_convention:
            self.packages['super_session'][pid]['naming_convention'] =  naming_convention.copy()
        if naming_options:
            self.packages['super_session'][pid]["naming_convention_options"] = naming_options


    def addMultiMonoReelsPackage(self,name,process_blocks,essences=['same_as_input'],naming_convention=None,naming_options=None,package_wide_uuid=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        blist = []
        for b in process_blocks:
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            assert(block['output_settings']['venue']=='theatrical')
            fps = "24"
            fmt = essences
            typ = ["printmaster"]
            for F in fmt:
                for t in typ:
                    block['output_essences'][t+'_'+fps+'_'+F]= {
                                'audio_format': F,
                                'frame_rate': fps,
                                'type':t
                            }
        if 'multi_mono_reels' not in self.packages:
            self.packages['multi_mono_reels'] = {}
        pid = f"my-multi-mono-reels-package-{len(self.packages['multi_mono_reels'])+1}"

        #if 'same_as_input' in fmt:
            #fmt = ['all_from_essence']

        self.packages['multi_mono_reels'][pid] = {
                    "name": name,
                    "process_block_ids":blist,
                    "formats" : fmt,
                    #"include_package_wide_uuid" :package_wide_uuid,
                }
        if naming_convention_id:
            self.packages['multi_mono_reels'][pid]['naming_convention_id'] =  naming_convention_id
        if naming_convention:
            self.packages['multi_mono_reels'][pid]['naming_convention'] =  naming_convention.copy()
        if naming_options:
            self.packages['multi_mono_reels'][pid]["naming_convention_options"] = naming_options

    def addDolbyEncodePackage(self,name,process_blocks,encode_profile,essences=('same_as_input','same_as_input'),naming_convention=None,naming_options=None,package_wide_uuid=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        if type(encode_profile) is str:
            presets = CodaPreset.getPresets('dolby')
            pf = [ p for p in presets if p['name']==encode_profile and essences[1] in p['formats'] ]
            assert(len(pf)==1)
            print('found encode profile id',pf[0]['encoding_preset_id'],'for',encode_profile,file=sys.stderr)
            encode_profile  = pf[0]['encoding_preset_id']
        elif type(encode_profile) is dict:
            assert(essences[1] in encode_profile['formats'])

        blist = []
        for b in process_blocks:
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            assert(block['output_settings']['venue']=='nearfield')
            fps = essences[0]
            fmt = essences[1]
            typ = "printmaster"
            block['output_essences'][typ+'_'+fps+'_'+fmt]= {
                                'audio_format': fmt,
                                'frame_rate': fps,
                                'type':typ
                            }
            
        if 'dolby' not in self.packages:
            self.packages['dolby'] = {}
        if fmt=='atmos':
            pid = f"my-dolby-atmos-package-{len(self.packages['dolby'])+1}"
        else:
            pid = f"my-dolby-package-{len(self.packages['dolby'])+1}"

        #if fmt=='same_as_input':
            #fmt = 'all_from_essence'
        #if fps=='same_as_input':
            #fps = 'all_from_essence'

        self.packages['dolby'][pid] = {
                    "name": name,
                    "process_block_ids":blist,
                    "format" : fmt,
                    "frame_rate": fps,
                    "include_package_wide_uuid" :package_wide_uuid,
                }

        if type(encode_profile) is dict:
            self.packages['dolby'][pid]["encoding_profile"]=encode_profile
        else:
            self.packages['dolby'][pid]["encoding_profile_id"]=encode_profile

        if naming_convention_id:
            self.packages['dolby'][pid]['naming_convention_id'] =  naming_convention_id
        if naming_convention:
            self.packages['dolby'][pid]['naming_convention'] =  naming_convention.copy()
        if naming_options:
            self.packages['dolby'][pid]["naming_convention_options"] = naming_options

    def addImaxEnhancedEncodePackage(self,name,process_blocks,encode_profile,essences=('same_as_input','same_as_input'),naming_convention=None,naming_options=None,package_wide_uuid=False):

        assert(essences[1] in ['5.1','5.1.4','7.1.4','7.1.5','5.1.1','imax5','imax6','imax12'])
        if type(encode_profile) is str:
            presets = CodaPreset.getPresets('dts')
            pf = [ p for p in presets if p['name']==encode_profile and essences[1] in p['formats'] and 't1cc' in p['definition'] and p['definition']['t1cc']]
            assert(len(pf)==1)
            print('found encode profile id',pf[0]['encoding_preset_id'],'for',encode_profile,file=sys.stderr)
            encode_profile  = pf[0]['encoding_preset_id']
        else:
            assert('t1cc' in encode_profile and encode_profile['t1cc'])

        self.addDtsEncodePackage(name,process_blocks,encode_profile,essences,naming_convention,naming_options)

    def addDtsEncodePackage(self,name,process_blocks,encode_profile,essences=('same_as_input','same_as_input'),naming_convention=None,naming_options=None,package_wide_uuid=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        t1cc= False
        if type(encode_profile) is str:
            presets = CodaPreset.getPresets('dts')
            pf = [ p for p in presets if p['name']==encode_profile and essences[1] in p['formats'] ]
            assert(len(pf)==1)
            t1cc =('t1cc' in pf[0]['definition'] and pf[0]['definition']['t1cc'])
            print('found encode profile id',pf[0]['encoding_preset_id'],'for',encode_profile,file=sys.stderr)
            encode_profile  = pf[0]['encoding_preset_id']
        elif type(encode_profile) is dict:
            t1cc =('t1cc' in encode_profile and encode_profile['t1cc'])

        #print('t1cc is',t1cc)

        blist = []
        for b in process_blocks:
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            #if not t1cc:
            assert(block['output_settings']['venue']=='nearfield')
            #else:
                #assert(block['output_settings']['venue']=='theatrical')
            fps = essences[0]
            fmt = essences[1]
            if t1cc and fmt!='same_as_input' and 'imax' not in fmt:
                fmt += ';mode=imax_enhanced'
            typ = "printmaster"
            block['output_essences'][typ+'_'+fps+'_'+fmt.replace(';','_').replace('=','_')]= {
                                'audio_format': fmt,
                                'frame_rate': fps,
                                'type':typ
                            }
            
        packtype = 'dts'
        if t1cc:
            packtype = 'imax_enhanced'

        if packtype not in self.packages:
            self.packages[packtype] = {}
        pid = f"my-{packtype.replace('_','-')}-package-{len(self.packages[packtype])+1}"

        #if fmt=='same_as_input':
            #fmt = 'all_from_essence'
        #if fps=='same_as_input':
            #fps = 'all_from_essence'

        pfmt = fmt
        if fmt=='imax12':
            pfmt = '5.1.4;mode=imax_enhanced'
        elif fmt=='imax6':
            pfmt = '5.1.1;mode=imax_enhanced'
        elif fmt=='imax5':
            pfmt = '5.1;mode=imax_enhanced'

        self.packages[packtype][pid] = {
                    "name": name,
                    "process_block_ids":blist,
                    "format" : pfmt,
                    "frame_rate": fps,
                    "include_package_wide_uuid" :package_wide_uuid,
                }
        if type(encode_profile) is dict:
            self.packages[packtype][pid]["encoding_profile"]=encode_profile
        else:
            self.packages[packtype][pid]["encoding_profile_id"]=encode_profile

        if naming_convention_id:
            self.packages[packtype][pid]['naming_convention_id'] =  naming_convention_id
        if naming_convention:
            self.packages[packtype][pid]['naming_convention'] =  naming_convention.copy()
        if naming_options:
            self.packages[packtype][pid]["naming_convention_options"] = naming_options


    def addInterleavedPackage(self,name,process_blocks,essences=('same_as_input',['same_as_input'],['same_as_input']),container='wav',streams=None,naming_convention=None,naming_options=None,package_wide_uuid=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        blist = []
        for b in process_blocks:
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            fps = essences[0]
            fmt = essences[1]
            typ = essences[2]
            for F in fmt:
                for t in typ:
                    block['output_essences'][t+'_'+fps+'_'+F]= {
                                    'audio_format': F,
                                    'frame_rate': fps,
                                    'type':t
                                }

        tag = 'interleaved'
        if container=='mov':
            tag = 'mov'

        if tag not in self.packages:
            self.packages[tag] = {}
        pid = f"my-{tag}-package-{len(self.packages[tag])+1}"

        if not streams:
            streams = []
            for t in sorted(typ):
                for f in fmt:
                    if t == "printmaster":
                        E = ['audio/pm']
                    elif t== "dme":
                        E = ['audio/dx','audio/fx','audio/mx']
                    else:
                        continue
                    for e in E:
                        for ch in CodaWorkflow.getChannels(f):
                            streams += [ {'format':f, 'element':e, 'channel':ch } ]

        #if fps=='same_as_input':
            #fps = 'all_from_essence'

        self.packages[tag][pid] = {
                    "name": name,
                    "frame_rate": fps,
                    "process_block_ids":blist,
                    "streams": streams,
                    "include_package_wide_uuid" :package_wide_uuid,
                }
        if naming_convention:
            self.packages[tag][pid]['naming_convention'] =  naming_convention.copy()
        if naming_convention_id:
            self.packages[tag][pid]['naming_convention_id'] =  naming_convention_id
        if naming_options:
            self.packages[tag][pid]["naming_convention_options"] = naming_options

        return 

    def addMultiMonoPackage(self,name,process_blocks,essences=(['same_as_input'],['same_as_input'],['same_as_input']),naming_convention=None,naming_options=None,package_wide_uuid=False,include_pt_session=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        blist = []
        venues = []
        for b in process_blocks:
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            venues += [ block['output_settings']['venue']]
            fps = essences[0]
            fmt = essences[1]
            typ = essences[2]
            for fr in fps:
                for F in fmt:
                    for t in typ:
                        block['output_essences'][t+'_'+fr+'_'+F]= {
                                    'audio_format': F,
                                    'frame_rate': fr,
                                    'type':t
                                }

        if 'multi_mono' not in self.packages:
            self.packages['multi_mono'] = {}
        pid = f"my-multi-mono-package-{len(self.packages['multi_mono'])+1}"

        #if 'same_as_input' in fps:
            #fps = ['all_from_essence']
        #if 'same_as_input' in fmt:
            #fmt = ['all_from_essence']
        #if 'same_as_input' in typ:
            #typ = ['all_from_essence']
        #if 'same_as_input' in venues:
            #venues = ['all_from_essence']

        self.packages['multi_mono'][pid] = {
                    "name": name,
                    "frame_rates": fps,
                    "formats":fmt,
                    "elements":typ,
                    "venues": list(set(venues)),
                    "process_block_ids":blist,
                    "include_package_wide_uuid" :package_wide_uuid,
                    "include_pro_tools_session" :include_pt_session,
                }
        if naming_convention:
            self.packages['multi_mono'][pid]['naming_convention'] =  naming_convention.copy()
        if naming_convention_id:
            self.packages['multi_mono'][pid]['naming_convention_id'] =  naming_convention_id
        if naming_options:
            self.packages['multi_mono'][pid]["naming_convention_options"] = naming_options

        return 

    def addAdmPackage(self,name,process_blocks,essences=("same_as_input","same_as_input"),naming_convention=None,naming_options=None,package_wide_uuid=False):

        naming_convention_id=None
        if naming_convention and type(naming_convention) is str:
            presets = CodaPreset.getPresets('naming')
            pf = [ p for p in presets if p['name']==naming_convention ]
            assert(len(pf)==1)
            print('found naming convention id',pf[0]['naming_convention_id'],'for',naming_convention,file=sys.stderr)
            naming_convention_id  = int(pf[0]['naming_convention_id'])
            naming_convention=None
        elif naming_convention and type(naming_convention) is dict:
            naming_convention_id=None
        #else:
        elif naming_convention is not None:
            naming_convention_id  = int(naming_convention)
            naming_convention=None

        blist = []
        venues = []
        assert(len(process_blocks)==1)
        for b in process_blocks:
            block = [ B for B in self.processBlocks if self.processBlocks[B]['name']==b]
            if len(block)==0:
                print('process block not found',b,file=sys.stderr)
                return -1
            blist += block
            block = self.processBlocks[block[0]]
            venues += [ block['output_settings']['venue']]
            fps = essences[0]
            fmt = "atmos"
            typ = essences[1]
            block['output_essences'][typ+'_'+fps+'_'+fmt]= {
                                    'audio_format': fmt,
                                    'frame_rate': fps,
                                    'type':typ
                                }

        if 'adm' not in self.packages:
            self.packages['adm'] = {}
        pid = f"my-adm-package-{len(self.packages['adm'])+1}"

        #if fps=='same_as_input':
            #fps = 'all_from_essence'
        #if typ=='same_as_input':
            #typ = 'all_from_essence'

        self.packages['adm'][pid] = {
                    "name": name,
                    "frame_rate": fps,
                    "format":fmt,
                    "element":typ,
                    "venue": list(set(venues))[0],
                    "process_block_ids":blist,
                    "include_package_wide_uuid" :package_wide_uuid,
                }
        if naming_convention:
            self.packages['adm'][pid]['naming_convention'] =  naming_convention.copy()
        if naming_convention_id:
            self.packages['adm'][pid]['naming_convention_id'] =  naming_convention_id
        if naming_options:
            self.packages['adm'][pid]["naming_convention_options"] = naming_options

        return

    def addDestination(self,name,url,auth=None, options=None):
        self.destinations[name] = {
                'url':url,
                'auth':auth,
                'opts':options
                }
        return

    def sendPackagesToDestination(self,dest,packageList):
        assert dest in self.destinations
        plist = []
        for pname in packageList:
            found = False
            for t in self.packages:
                for p in self.packages[t]:
                    if self.packages[t][p]['name']==pname:
                        plist +=  [p]
                        found=True
            if not found:
                print(f'warning !!! package {pname} not found',file=sys.stderr)

        assert(len(plist)>0)

        for p in plist:
            if 'package_ids' not in self.destinations[dest]:
                self.destinations[dest]['package_ids'] =[]
            self.destinations[dest]['package_ids'] += [p]
        return
    
    def sendPackagesToAgent(self,client,packageList):

        #aid=0
        #if (os.getenv('DATAIO_AGENT_ID')):
            #aid = int(os.getenv('DATAIO_AGENT_ID'))
        #else:
            #try:
                #ret = requests.get("http://localhost:38384/info")
                #J = ret.json()
                #if 'id' in J:
                    #print('got src agent from data-io client',J['id'],file=sys.stderr)
                    #aid= J['id']
            #except:
                #pass

        if type(client)== str:
            if client!='Origin':
                #ret = requests.get('http://localhost:38383/interface/v1/agents')
                ret = make_request(requests.get,38383,'/interface/v1/agents')
                allclients = ret.json()
                C = [ k for k in allclients if k['hostname']==client]
                #for c in C:
                    #print(c['hostname'],c['id'],file=sys.stderr)
                assert(len(C)==1)
                aid = C[0]['id']
                print('fetched agent id',client,'->',aid,file=sys.stderr)
            else:
                aid=0
        else:
            aid = int(client)
            #print('sending to agent',aid,file=sys.stderr)

        # check if agent already exists or use new
        pid = f"my-agent-{len(self.agents)+1}"
        for a in self.agents:
            if self.agents[a]['agent_id']==aid:
                pid = a

        plist = []
        for pname in packageList:
            found = False
            for t in self.packages:
                for p in self.packages[t]:
                    if self.packages[t][p]['name']==pname:
                        plist +=  [p]
                        found = True
            if not found:
                print(f'warning !!! package {pname} not found',file=sys.stderr)

        assert(len(plist)>0)

        if pid not in self.agents:
            self.agents[pid] = {
                "agent_id":aid,
                "package_ids": plist
               }
        else:
            self.agents[pid]['package_ids'] += plist
            self.agents[pid]['package_ids'] = list(set(self.agents[pid]['package_ids'])) # enforce unique packages
        return

    def getPackageList(self):
        packlist= []
        for t in self.packages:
            for n in self.packages[t]:
                p = copy.deepcopy(self.packages[t][n])
                p['type'] =t
                packlist += [p]
        return packlist

    def dict(self):

        dests = {}
        for d in self.destinations:
            if len(self.destinations[d]['package_ids'])>0:
                if 's3://' in self.destinations[d]['url']:
                    if 's3' not in dests:
                        dests['s3']= {}
                        dests['s3'][d] = self.destinations[d]
                    else:
                        dests['s3'][d] = self.destinations[d]

        _wfDef = {
                "name":self.name,
                "process_blocks" : copy.deepcopy(self.processBlocks),
                "packages" : copy.deepcopy(self.packages),
                "workflow_parameters": {
                    "dme_stem_mapping": {
                        #"audio/fx1": "audio/fx;contents=comp",
                        "audio/nar": "audio/dx;contents=comp",
                        "audio/vox": "audio/mx;contents=comp",
                        "audio/fx": "audio/fx;contents=comp",
                        #"audio/fx2": "audio/fx;contents=comp",
                        #"audio/dx1": "audio/dx;contents=comp",
                        "audio/arch": "audio/dx;contents=comp",
                        #"audio/dx2": "audio/dx;contents=comp",
                        "audio/fffx": "audio/fx;contents=comp",
                        #"audio/fol2": "audio/fx;contents=comp",
                        "audio/dx": "audio/dx;contents=comp",
                        #"audio/mx2": "audio/mx;contents=comp",
                        #"audio/fol1": "audio/fx;contents=comp",
                        #"audio/mx1": "audio/mx;contents=comp",
                        #"audio/fx3": "audio/fx;contents=comp",
                        #"audio/fx4": "audio/fx;contents=comp",
                        "audio/scr": "audio/mx;contents=comp",
                        "audio/adr": "audio/dx;contents=comp",
                        #"audio/dxcomp": "audio/dx;contents=comp",
                        "audio/sng": "audio/mx;contents=comp",
                        #"audio/wla": "audio/fx;contents=comp",
                        #"audio/mxcomp": "audio/mx;contents=comp",
                        "audio/mnemx": "audio/mx;contents=comp",
                        "audio/fol": "audio/fx;contents=comp",
                        #"audio/fxcomp": "audio/fx;contents=comp",
                        "audio/mx": "audio/mx;contents=comp",
                        "audio/pfx": "audio/fx;contents=comp",
                        "audio/bg": "audio/fx;contents=comp",
                        #"audio/fix4": "audio/fx;contents=comp",
                        "audio/audiodescription": "audio/dx;contents=comp",
                        #"audio/fix2": "audio/fx;contents=comp",
                        "audio/vo": "audio/dx;contents=comp",
                        #"audio/fix3": "audio/fx;contents=comp",
                        "audio/crd": "audio/fx;contents=comp",
                        "audio/fix": "audio/fx;contents=comp",
                        #"audio/fix1": "audio/fx;contents=comp",
                        "audio/lg": "audio/dx;contents=comp"
                    },
                    "enable_atmos_renders": [
                                    "7.1.4",
                                    "7.1"
                    ]
            }
        }

        for k in self.wfparams:
            _wfDef['workflow_parameters'][k] = self.wfparams[k]

        if self.agents and len(self.agents):
                _wfDef["agents"]= copy.deepcopy(self.agents)
        if dests and len(dests):
                _wfDef["destinations"]= copy.deepcopy(dests)

        return _wfDef


class CodaJob(object):

    def __init__(self,name,input_venue=None,input_time_options=None,sequence=None,output_language=None):

        self.programFPS = None
        self.programLFOA = None
        self.programFFOA = None
        self.programStart = None

        if input_time_options:
            inputFramerate,ffoa,lfoa,start_time = input_time_options
            if inputFramerate is not None:
                inputFramerate = inputFramerate.upper()
            if start_time is not None:
                if type(start_time) is str:
                    """
                    start_time = [float(s) for s in start_time.split(':')]
                    dt = {
                    "23":  24000./1001.,
                    "24" : 1./24.,
                    "25" : 1./25,
                    "29" : 24000./1001. * 1.25,
                    "30" :1./30.
                    }
                    hmsf = [ 3600., 60.,1.0, dt[inputFramerate] ]
                    start_time = sum ( [ a[0]*a[1] for a in zip(start_time,hmsf) ])
                    """
                    start_time =tc_to_time_seconds(start_time,inputFramerate)
            self.programFPS = inputFramerate
            self.programLFOA = lfoa
            self.programFFOA = ffoa
            self.programStart = start_time

        self.reference_run = None
        self.programName = name
        self.programVenue = input_venue
        self.sequence = sequence
        self.language = output_language
        self.inputs = { "sources" : {"interleaved" : [], "multi_mono_groups": [] ,"adms":[] ,"iab_mxfs": [] }}
        self.wfDef = None
        self.edits = None
        if not self.sequence:
            self.sequence = ""
        if not self.language:
            self.language=  "UND"

        self.src_agent=None
        if (os.getenv('DATAIO_AGENT_ID')):
            self.src_agent = int(os.getenv('DATAIO_AGENT_ID'))
        else:
            try:
                #ret = requests.get("http://localhost:38384/api/agent")
                ret = make_request(requests.get,38384,'/api/agent')
                J = ret.json()
                if 'id' in J:
                    print('got src agent from data-io client',J['id'],file=sys.stderr)
                    self.src_agent= J['id']
            except:
                pass

        if (os.getenv('CODA_GROUP_ID')):
            self.groupId = int(os.getenv('CODA_GROUP_ID'))
        else:
            self.groupId = 1
        return

    def forceImax5(self):
        fmts = []
        for t in self.inputs['sources']:
            for k in self.inputs['sources'][t]:
                fmts += [ not (k['format']=='5.0' or k['format']=='imax5') ]
        if any(fmts):
            return False
        for t in self.inputs['sources']:
            for k in self.inputs['sources'][t]:
                k['format'] = 'imax5'
        return True

    def setInputLanguage(self,lang):
        for t in self.inputs['sources']:
            for k in self.inputs['sources'][t]:
                k['language'] = lang

    def setProgramForType(self,typ,prog="program-1"):
        for t in self.inputs['sources']:
            for k in self.inputs['sources'][t]:
                if typ in k['type']:
                    k['program'] = prog
        return

    def setProgramForFormat(self,fmt,prog="program-1"):
        for t in self.inputs['sources']:
            for k in self.inputs['sources'][t]:
                if fmt == k['format']:
                    k['program'] = prog
        return

    def setUniqueProgram(self,prog="program-1"):
        for t in self.inputs['sources']:
            for k in self.inputs['sources'][t]:
                k['program'] = prog
        return

    def addInputEssences(self,essences):
        if len(essences)==0:
            return
        for e in essences:
            assert(e.esstype)
        self.inputs['sources']['multi_mono_groups'] += [e.dict() for e in essences if isinstance(e,CodaEssence) and e.esstype=='multi_mono']
        self.inputs['sources']['interleaved'] += [e.dict() for e in essences if isinstance(e,CodaEssence) and e.esstype=='interleaved']
        return

    def addInputFiles(self,files,file_info=None,program=None,force_fps=None):
        alls3ins = all(['s3://' in f for f in files])
        if not alls3ins and not self.src_agent:
            print('** ERROR !!!! : you need a data-io agent ID to transfer local files. install data-io or export DATAIO_AGENT_ID=<id>',file=sys.stderr)
            return -1 #assert(self.src_agent)

        absfiles = [os.path.abspath(f) for f in files if 's3://' not in f] ### make sure to use absolute paths for coda inspect...

        if len(absfiles)>0:
            print('coda inspect scanning',len(absfiles),'files',file=sys.stderr)
            codaexe = shutil.which('coda') #'/usr/local/bin/coda'
            if os.getenv('CODA_CLI_EXE'):
                codaexe = os.getenv('CODA_CLI_EXE')
            if not codaexe:
                if not file_info:
                    print('ERRROR ! you need coda cli installed to autoscan local files',file=sys.stderr)
                    return -1 #assert(codaexe)
                else:
                    # manual essence creation from local files
                    essences = [ CodaEssence(file_info['format'],stemtype=file_info['type']) ]
                    for e in essences:
                        res = []
                        for r in absfiles:
                            res += [
                                {
                                'url' : r
                                }
                            ]
                        e.addMultiMonoResources(res,samps=file_info['samps'])
                    self.addInputEssences(essences)
            else:
                try:
                    print('using coda cli', codaexe,file=sys.stderr)
                    try:
                        ret = subprocess.run([codaexe] +['checkin'],shell=False,check=True,stdout = subprocess.PIPE)
                    except:
                        print('ERRROR ! you need coda agent to be running to autoscan local files',file=sys.stderr)
                        return -1

                    fpsflag = []
                    if force_fps is not None:
                        fpsflag  = [ '--frame-rate']  + [ force_fps ]

                    ret = subprocess.run([codaexe] +['inspect']+ ['-i'] + fpsflag + absfiles,shell=False,check=True,stdout = subprocess.PIPE)
                    j = json.loads(ret.stdout)
                    for t in j['sources']:
                        for g in j['sources'][t]:
                            if 'resources' in g:
                                g['resources'] = sorted(g['resources'], key=lambda d: d['channel_label']) ## sort file list by channel label for repeatability
                    if program is not None:
                        for t in j['sources']:
                            for g in j['sources'][t]:
                                g['program']= program
                    if 'multi_mono_groups' in j['sources']:
                        for mmgroup in j['sources']['multi_mono_groups']:
                            if mmgroup['format']=='7.1.5' or mmgroup['format']=='5.1.1':
                                mmgroup['format']+= ';mode=imax_enhanced'
                    for t in j['sources']:
                        self.inputs['sources'][t] +=  j['sources'][t]
                    self.inputs['ffoa_timecode'] = j['ffoa_timecode']
                    self.inputs['lfoa_timecode'] = j['lfoa_timecode']
                    self.inputs['source_frame_rate'] = j['source_frame_rate']
                except Exception as e:
                    print(str(e),file=sys.stderr)
                    return -1

        s3files = [f for f in files if 's3://' in f]

        if len(s3files)>0:
            print('adding',len(s3files),'s3 files',file=sys.stderr)
            assert(file_info is not None)

            # manual essence creation from s3 bucket
            essences = [ CodaEssence(file_info['format'],stemtype=file_info['type']) ]
            for e in essences:
                res = []
                for r in s3files:
                    res += [
                        {
                        'url' : r,
                        'auth':file_info['s3_auth'],
                        'opts':file_info['s3_options'],
                        }
                    ]
                e.addMultiMonoResources(res,samps=file_info['samps'])

            self.addInputEssences(essences)

        return 0

    def addEdits(self,edit_payload):
        self.edits = edit_payload
        return

    def validate(self, skip_cloud_validation=True):
        # we could check for errors here, like adding a reel package but having no edits, etc...
        if self.wfDef:
            for f in self.wfDef.packages:
                if f=='dcp_mxf':
                    for p in self.wfDef.packages[f]:
                        if self.wfDef.packages[f][p]['include_reel_splitting']:
                            assert(self.edits)
                elif f=='multi_mono_reels' and len(self.wfDef.packages[f])>0:
                    assert(self.edits)

        J = json.loads(self.json())

        assert( 'agents' in J['workflow_definition'] or 'destinations' in J['workflow_definition'] )
        if 'agents' in J['workflow_definition']:
            for a in J['workflow_definition']['agents']:
                assert(len(J['workflow_definition']['agents'][a]['package_ids']) >0)

        # check that all multi monos have same bext
        if 'multi_mono_groups' in J['workflow_input']['sources']:
            bext =None
            for t in J['workflow_input']['sources']['multi_mono_groups']:
                for f in t['resources']:
                    if bext is None:
                        bext = f['bext_time_reference']
                    else:
                        assert(bext==f['bext_time_reference'])

        #ret = requests.post("http://localhost:38383/interface/v1/jobs?validate_only=true&skip_cloud_validation=true",json =J)
        ret = make_request(requests.post,38383,f"/interface/v1/jobs?validate_only=true&skip_cloud_validation={skip_cloud_validation}",J)
        print('validate :: ',ret.json(),file=sys.stderr)
        return ret.json()

    def setWorkflow(self,wf):
        self.wfDef = copy.deepcopy(wf)
        return

    def useReferenceJob(self,jobid):
        #ret = requests.get(f'http://localhost:38383/interface/v1/jobs/{jobid}')
        ret = make_request(requests.get,38383,f'/interface/v1/jobs/{jobid}')
        J = ret.json()
        assert(J['status']=='COMPLETED')
        wid = J['conductor_workflow_instance_id']
        print(f'referencing cache from job {jobid} --> {wid}',file=sys.stderr)
        self.reference_run = jobid
        return

    def setGroup(self,gid):
        if type(gid) is str:
            #ret = requests.get(f'http://localhost:38383/interface/v1/groups')
            ret = make_request(requests.get,38383,'/interface/v1/groups')
            J = ret.json()
            if 'error' in J:
                return None
            pf = [ p for p in J if p['name']==gid ]
            assert(len(pf)==1)
            print('found group id',pf[0]['group_id'],'for',gid,file=sys.stderr)
            self.groupId = int(pf[0]['group_id'])
        else:
            self.groupId = int(gid)
        return

    @staticmethod
    def run_raw_payload(J):
        CodaJob.validate_raw_payload(J)
        if 'errors' in ret or ('success' in ret and not ret['success']):
            return None
        if 'source_agent_id' in J['workflow_input']:
            assert(J['workflow_input']['source_agent_id']>0)
        print("run raw :: launching job.",file=sys.stderr)
        #ret = requests.post("http://localhost:38383/interface/v1/jobs",json =J)
        ret = make_request(requests.post,38383,'/interface/v1/jobs',J)
        print(ret.json(),file=sys.stderr)
        J = ret.json()
        if 'errors' in J:
            return None
        if 'job_id' not in J:
            return None
        return int(J['job_id'])

    @staticmethod
    def validate_raw_payload(J):
        #ret = requests.post("http://localhost:38383/interface/v1/jobs?validate_only=true",json =J)
        ret = make_request(requests.post,38383,"/interface/v1/jobs?validate_only=true",J)
        print('validate raw :: ',ret.json(),file=sys.stderr)
        return ret.json()

    def get_edge_payload(self):
        ret = self.validate()
        if 'errors' in ret or ('success' in ret and not ret['success']):
            return None
        J = json.loads(self.json())
        ret = make_request(requests.post,38383,"/interface/v1/jobs/edge",J)
        try:
            J = ret.json()
        except:
            print('get_edge_payload::',ret,file=sys.stderr)
            return None
        if 'errors' in J:
            return None
        return J

    def run(self):
        ret = self.validate()
        if 'errors' in ret or ('success' in ret and not ret['success']):
            return None
        J = json.loads(self.json())
        if 'source_agent_id' in J['workflow_input']:
            assert(J['workflow_input']['source_agent_id']>0)
        print("run :: launching job.",file=sys.stderr)
        #ret = requests.post("http://localhost:38383/interface/v1/jobs",json =J)
        ret = make_request(requests.post,38383,"/interface/v1/jobs",J)
        print(ret.json(),file=sys.stderr)
        J = ret.json()
        if 'errors' in J:
            return None
        if 'job_id' not in J:
            return None
        return int(J['job_id'])

    @staticmethod
    def getStatus(jobid):
        #print(f'getting status for job {jobid}',file=sys.stderr)
        #ret = requests.get(f"http://localhost:38383/interface/v1/jobs/{jobid}")
        ret = make_request(requests.get,38383,f'/interface/v1/jobs/{jobid}')
        J = ret.json()
        #print(J['status'],file=sys.stderr)
        errorcnt=0
        while 'error' in J and errorcnt<3:
            print('error in getstatus::',ret.status_code,J['error'],file=sys.stderr)
            time.sleep(1)
            #ret = requests.get(f"http://localhost:38383/interface/v1/jobs/{jobid}")
            ret = make_request(requests.get,38383,f'/interface/v1/jobs/{jobid}')
            J = ret.json()
            errorcnt+=1
        if 'error' in J:
            return None
        return {'status':J['status'],'progress':J['progress']}

    @staticmethod
    def getReport(jobid):
        #print(f'getting report for job {jobid}',file=sys.stderr)
        #ret = requests.get(f"http://localhost:38383/interface/v1/report/raw/{jobid}")
        ret = make_request(requests.get,38383,f'/interface/v1/report/raw/{jobid}')
        J = ret.json()
        #if 'error' in J:
            #print(J,file=sys.stderr)
            #return None
        return J


    def checkInputCompatibility(self,jobid):
        print(f'checking input compatibility against job {jobid}',file=sys.stderr)
        #ret = requests.get(f'http://localhost:38383/interface/v1/jobs/{jobid}')
        ret = make_request(requests.get,38383,f'/interface/v1/jobs/{jobid}')
        J = ret.json()
        current = self.getInputTimingInfo()
        remote = timingInfo(J['workflow_input'])
        print('local',current,file=sys.stderr)
        print(f'job {jobid}',remote,file=sys.stderr)
        return current==remote

    def getInputTimingInfo(self):
        return timingInfo(self.inputs,self.programVenue,self.programFPS,self.programFFOA,self.programLFOA,self.programStart)

    def json(self):

        sources = copy.deepcopy(self.inputs['sources'])
        for s in self.inputs['sources']:
            if len(self.inputs['sources'][s])==0:
                del sources[s]

        if self.programFPS is None:
            self.programFPS = self.inputs['source_frame_rate']
        else:
            self.inputs['source_frame_rate'] = self.programFPS
        if self.programFFOA is None:
            self.programFFOA = self.inputs['ffoa_timecode']
        else:
            self.inputs['ffoa_timecode'] = self.programFFOA
        if self.programLFOA is None:
            self.programLFOA = self.inputs['lfoa_timecode']
        else:
            self.inputs['lfoa_timecode'] = self.programLFOA

        if self.programStart is None:
            for i in sources:
                if len(sources[i]):
                    if 'resources' in sources[i][0]:
                        self.programStart = sources[i][0]['resources'][0]['bext_time_reference']/sources[i][0]['resources'][0]['sample_rate']
                    break
            print('setting prog start from sources',self.programStart,file=sys.stderr)
        else:
            print('punching prog start into sources',self.programStart,file=sys.stderr)
            for i in sources:
                for k in sources[i]:
                    if 'resources' in k:
                        for r in k['resources']:
                            #print(r['url'],r['sample_rate'],int(self.programStart*r['sample_rate']),file=sys.stderr)
                            r['bext_time_reference']= int(self.programStart*r['sample_rate'])

        if self.programLFOA=="":
            print('invalid LFOA !!!!!',file=sys.stderr)
        if self.programFFOA=="":
            print('invalid FFOA !!!!!',file=sys.stderr)
        if self.programFPS=="":
            print('invalid FPS !!!!!',file=sys.stderr)

        #print('prg start',self.programStart,file=sys.stderr)

        wfIn = {
                "project": {"title":self.programName, "sequence":self.sequence,"language":self.language,"version":""},
                "source_frame_rate":self.programFPS,
                "venue":self.programVenue,
                "sources": sources,
                #"source_agent_id" : self.src_agent,
                "ffoa_timecode": self.inputs['ffoa_timecode'],
                "lfoa_timecode": self.inputs['lfoa_timecode']
        }
        if self.src_agent:
            wfIn['source_agent_id'] = self.src_agent
        if self.edits:
            wfIn["edits"] = self.edits

        wdef = copy.deepcopy(self.wfDef.dict())
        for t in wdef['packages']:
            for p in wdef['packages'][t]:

                for k in wdef['packages'][t][p]:
                    #print(t,k,'::',wdef['packages'][t][p][k])
                    if not ('venue' in k or 'element' in k or 'format' in k or 'frame' in k):
                        continue
                    if 'same_as_input' in wdef['packages'][t][p][k]:
                        if 'venue' in k:
                            if type(wdef['packages'][t][p][k]) is list:
                                wdef['packages'][t][p][k] += [self.programVenue]
                                wdef['packages'][t][p][k].remove('same_as_input')
                            else:
                                wdef['packages'][t][p][k] = self.programVenue
                        if 'element' in k:
                            if type(wdef['packages'][t][p][k]) is list:
                                wdef['packages'][t][p][k] = ['all_from_essence']
                            else:
                                wdef['packages'][t][p][k] = self.programVenue
                        if 'format' in k:
                            if type(wdef['packages'][t][p][k]) is list:
                                wdef['packages'][t][p][k] =  ['all_from_essence'] #sources[0][0]['specifications']['audio_format']
                            else:
                                wdef['packages'][t][p][k] =  'all_from_essence' #sources[0][0]['specifications']['audio_format']
                        if 'frame' in k:
                            if type(wdef['packages'][t][p][k]) is list:
                                wdef['packages'][t][p][k] += [self.programFPS]
                                wdef['packages'][t][p][k].remove('same_as_input')
                            else:
                                wdef['packages'][t][p][k] = self.programFPS

                #print(wdef['packages'][t][p])

                if 'naming_convention' in wdef['packages'][t][p]:
                    if 'package_data' not in wfIn:
                        wfIn['package_data'] ={}
                    wfIn['package_data'][p] = {'naming_convention':wdef['packages'][t][p]['naming_convention']}
                    del wdef['packages'][t][p]['naming_convention']


        J = {
                "group_id":self.groupId,
                "workflow_input": wfIn,
                "workflow_definition": wdef
        }

        if self.reference_run:
            J['parent_job_id'] = self.reference_run

        return json.dumps(J,indent=2)


