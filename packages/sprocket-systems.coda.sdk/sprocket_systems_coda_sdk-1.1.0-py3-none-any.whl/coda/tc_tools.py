###########################################################
# Application Name  : tc_tools.py
# Author            : Skywalker Dev Labs
# Date              : December 13th, 2024
# Description       : tools for calculations with timecode
# Location          : Original is kept in 1031-tc_tools
#
# Frame rate tools:
#   string      float_to_v_fr_string(double v_fr)                              <- does not yet exist (29.97df can not be distinguished from 29.97)
#   double      v_fr_string_to_float(v_fr_string)
#   double      v_fr_string_to_non_pulldown_float(v_fr_string)
#   Conversion to/from:
#     double      vid_frames_to_audio_frames(v_fs, v_fr_string, a_fr)
#     double      audio_frames_to_vid_frames(a_fs, v_fr_string, a_fr)
#     double      vid_frames_to_time_seconds(v_fs, v_fr_string)
#     double      time_seconds_to_vid_frames(time_s, v_fr_string)
#     double      vid_frames_to_timecode_seconds(v_fs, v_fr_string)
#     double      timecode_seconds_to_vid_frames(timecode_s, v_fr_string)      <- does not yet exist
#   Specialty:
#     double      vid_frames_align_to_audio_frames(v_fs, v_fr_string, a_fr, pad_or_trim)
# Timecode/frame rate tools:
#   General:
#     bool        tc_is_whole_video_frames(tc, v_fr_string)
#     string      tc_round(tc, partial_v_fr_digits, v_fr_string)
#   Conversion to/from:
#     double      tc_to_vid_frames(tc, v_fr_string)
#     string      vid_frames_to_tc(v_fs, v_fr_string)
#     double      tc_to_time_seconds(tc, v_fr_string)
#     string      time_seconds_to_tc(time_s, v_fr_string)
#     double      tc_to_audio_frames(tc, v_fr_string, a_fr)
#     string      audio_frames_to_tc(a_fs, v_fr_string, a_fr)
#   double      tc_add(tc_addend_a, tc_addend_b, v_fr_string)
#   double      tc_sub(tc_minuend, tc_subtrahend, v_fr_string)
# 
# Utilites
#   string      tc_tools_version()
#   bool        compare_with_precision(float_a, float_b, precision)  (this should be removed!!!)
#
# Abbreviations used in this file:
#   v_fr          video frame rate as a double      "(v)ideo (f)rame (r)ate"
#   v_fs          video frame count as a double     "(v)ideo (f)rame(s)"
#   a_fr          audio frame rate as a double      "(a)udio (f)rame (r)ate"
#   a_fs          audio frame count as a double     "(a)udio (f)rame(s)"
#   tc            timecode as a string in the form "HR:MN:SC:FR.partial_frames"
#   time_s        time in real seconds (not timecode seconds)
#   timecode_s    time in timecode seconds
#   v_fr_string   video frame rate as a string, one of:
#       VID_FRAME_RATE_STRING_2397
#       VID_FRAME_RATE_STRING_2400
#       VID_FRAME_RATE_STRING_2500
#       VID_FRAME_RATE_STRING_2997
#       VID_FRAME_RATE_STRING_2997df
#       VID_FRAME_RATE_STRING_3000
#   pad_or_trim   add or trim to align video frames to audio frames.  one of:
#       'pad'
#       'trim'
# 
# Notes:
#   partial_frames:       is a fraction of the given frame rate.
#       For example: "00:00:00:03.141" @ 24.00 fps is equal to 3.141 video frames.
#
#   timecode_seconds:     the number of seconds at the timecode rate... not the clock on the wall.
#       timecode_seconds will differ from time_s for pull-down rates (23, 29, and 29DF)
#       29.97df is a special case where timecode_seconds is equal to the number of video frames at the timecode rate.
#       And so:
#           00:01:00;02 @29.97df  is equal to 60.0000000 timecode_seconds.
#           00:01:00:00 @29.97    is equal to 60.0000000 timecode_seconds.
#           00:01:00:02 @29.97    is equal to 60.0666667 timecode_seconds.
#           00:01:00:00 @30.00    is equal to 60.0000000 timecode_seconds.
#   partial_v_fr_digits:  an int, the number of decimal places to round to
#
#   As of 2023-05-09:
#       vid_frames_to_tc    will round to the nearest thousandth of a partial frame (using const PARTIAL_FRAME_NUMBER_OF_DIGITS for precision)
#       time_seconds_to_tc  will round to the nearest thousandth of a partial frame (using const PARTIAL_FRAME_NUMBER_OF_DIGITS for precision)
###########################################################

from decimal import Decimal

DEBUG_vid_frames_to_tc = False
DEBUG_tc_components_to_tc = False
DEBUG_audio_frames_to_vid_frames = False
DEBUG_tc_to_vid_frames = False


def tc_tools_version():
    return "1.2.4"

# @abstract     Video frame rates as strings use by tool
# @discussion   VID_FRAME_RATE_STRING_2997df is not fully supported
VID_FRAME_RATE_STRING_2397 = '23'
VID_FRAME_RATE_STRING_2400 = '24'
VID_FRAME_RATE_STRING_2500 = '25'
VID_FRAME_RATE_STRING_2997 = '29'
VID_FRAME_RATE_STRING_2997df = '29DF'
VID_FRAME_RATE_STRING_3000 = '30'

# delimeter to use when creating a 2997df tc string
# this has no effect on reading a tc string (when reading, it can be either : or ;);
TC_TOOLS_29DF_SEC_FRAME_DELIM = ':' # traditionally, this is a ;

PARTIAL_FRAME_NUMBER_OF_DIGITS = 7
ALIGN_VFS_ROUND_DIGITS = 9


def v_fr_string_to_non_pulldown_float(v_fr_string):
    """Convert from one of the enum frame rate strings to the non-pulldown float value."""
    if v_fr_string == VID_FRAME_RATE_STRING_2397:
        v_fr = 24.0
    elif v_fr_string == VID_FRAME_RATE_STRING_2400:
        v_fr = 24.0
    elif v_fr_string == VID_FRAME_RATE_STRING_2500:
        v_fr = 25.0
    elif v_fr_string == VID_FRAME_RATE_STRING_2997:
        v_fr = 30.0
    elif v_fr_string == VID_FRAME_RATE_STRING_2997df:
        v_fr = 30.0
    elif v_fr_string == VID_FRAME_RATE_STRING_3000:
        v_fr = 30.0
    else:
        print("tc_tools: frame rate not recognized = " , v_fr_string)
        raise;
    return v_fr


def v_fr_string_to_float(v_fr_string):
    """Convert from one of the enum frame rate strings to the actual float value."""
    if v_fr_string == VID_FRAME_RATE_STRING_2397:
        v_fr = 24.0/1.001
    elif v_fr_string == VID_FRAME_RATE_STRING_2400:
        v_fr = 24.0
    elif v_fr_string == VID_FRAME_RATE_STRING_2500:
        v_fr = 25.0
    elif v_fr_string == VID_FRAME_RATE_STRING_2997:
        v_fr = 30/1.001
    elif v_fr_string == VID_FRAME_RATE_STRING_2997df:
        v_fr = 30/1.001
    elif v_fr_string == VID_FRAME_RATE_STRING_3000:
        v_fr = 30.0
    else:
        print("tc_tools: frame rate not recognized = " , v_fr_string)
        raise;
    return v_fr


def vid_frames_to_audio_frames(v_fs, v_fr_string, a_fr):
    """Convert from number of video frames to audio frames."""
    v_fr = v_fr_string_to_float(v_fr_string)
    a_fs = v_fs * ( a_fr / v_fr )
    return a_fs


def vid_frames_to_time_seconds(v_fs, v_fr_string):
    """Convert from number of video frames to time in seconds."""
    v_fr = v_fr_string_to_float(v_fr_string)
    return v_fs / v_fr


def vid_frames_to_timecode_seconds(v_fs, v_fr_string):
    """Convert from number of video frames to time in timcode seconds."""
    #if v_fr_string == VID_FRAME_RATE_STRING_2997df:
    if False:
        # for every 1800 video frames, add two video frames
        minutes_fr_to_add = int(v_fs/1800) * 2
        #print('vid_frames_to_timecode_seconds(): minutes_fr_to_add =',minutes_fr_to_add)
        # for every 18000 video frames, take away two video frames
        minutes_fr_to_remove = int(v_fs/18000) * 2
        #print('vid_frames_to_timecode_seconds(): minutes_fr_to_remove =',minutes_fr_to_remove)
        v_fs += minutes_fr_to_add
        v_fs -= minutes_fr_to_remove
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_string)
    return v_fs / v_fr


def time_seconds_to_vid_frames(time_s, v_fr_string):
    """Convert from time in seconds to number of video frames."""
    v_fr = v_fr_string_to_float(v_fr_string)
    return v_fr * time_s


def audio_frames_to_vid_frames(a_fs, v_fr_string, a_fr):
    """Convert from number of audio frames to video frames."""
    if DEBUG_audio_frames_to_vid_frames:
        print('tc_tools: audio_frames_to_vid_frames: Top of Function.')
        print('tc_tools: audio_frames_to_vid_frames() a_fs        =', a_fs)
        print('tc_tools: audio_frames_to_vid_frames() v_fr_string =', v_fr_string)
        print('tc_tools: audio_frames_to_vid_frames() a_fr        =', a_fr)
    v_fr = v_fr_string_to_float(v_fr_string);
    v_fs = a_fs * (v_fr / a_fr);
    if DEBUG_audio_frames_to_vid_frames:
        print('tc_tools: audio_frames_to_vid_frames() v_fs        =', v_fs)
        print('tc_tools: audio_frames_to_vid_frames: Bottom of Function.')
    return v_fs;


def is_float_whole_number(f):
    if f == round(f): return True
    return False

    
#
# returns the number of video frames you must add or trim so that video and audio frames are aligned
#     v_fs          the current number of video frames
#     v_fr_string   the video frame rate
#     a_fr          the audio frame rate
#     pad_or_trim   either 'pad' or 'trim'
def vid_frames_align_to_audio_frames(v_fs, v_fr_string, a_fr, pad_or_trim):
    rounded_v_fs = round(v_fs, ALIGN_VFS_ROUND_DIGITS)
    if pad_or_trim == 'pad':
        v_fs_to_add = 0.0
        if not is_float_whole_number(rounded_v_fs):
            v_fs_to_add += int(v_fs + 1) - v_fs
            v_fs_to_add = round(v_fs_to_add, ALIGN_VFS_ROUND_DIGITS)
        if (v_fr_string == VID_FRAME_RATE_STRING_2997) or (v_fr_string == VID_FRAME_RATE_STRING_2997df):
            if a_fr != 48000.0:
                print('tc_tools: vid_frames_align_to_audio_frames() currently only audio frame rate of 48000.0 is supported.')
                raise        
            v_fs_whole_vid_frames = round(v_fs + v_fs_to_add, ALIGN_VFS_ROUND_DIGITS)
            v_fs_whole_vid_frames_mod_5 = v_fs_whole_vid_frames % 5.0
            if v_fs_whole_vid_frames_mod_5:
                v_fs_to_add += 5 - v_fs_whole_vid_frames_mod_5
        return v_fs_to_add
    if pad_or_trim == 'trim':
        v_fs_to_trim = 0.0
        if not is_float_whole_number(rounded_v_fs):
            v_fs_to_trim += v_fs - int(v_fs)
        if (v_fr_string == VID_FRAME_RATE_STRING_2997) or (v_fr_string == VID_FRAME_RATE_STRING_2997df):
            if a_fr != 48000.0:
                print('tc_tools: vid_frames_align_to_audio_frames() currently only audio frame rate of 48000.0 is supported.')
                raise        
            v_fs_whole_vid_frames = round(v_fs - v_fs_to_trim, ALIGN_VFS_ROUND_DIGITS)
            v_fs_whole_vid_frames_mod_5 = v_fs_whole_vid_frames % 5.0
            if v_fs_whole_vid_frames_mod_5:
                v_fs_to_trim += v_fs_whole_vid_frames_mod_5
        return v_fs_to_trim
    print('tc_tools: vid_frames_align_to_audio_frames() mode must be one of trim or pad.')
    raise        



def tc_is_whole_video_frames(tc, v_fr_string):
    """Return true if timecode string is a whole number of video frames."""
    tc_splits = tc.split(":")
    if 4 == len(tc_splits):
        tc_fr_and_partial = tc_splits[3]
    elif 3 == len(tc_splits):
        tc_splits_df = tc_splits[2].split(";")
        if 2 == len(tc_splits_df):
            tc_fr_and_partial = tc_splits_df[1]
        else:
            print("tc_tools: tc_is_whole_video_frames() failed to parse tc.")
            raise
    else:
        print("tc_tools: tc_is_whole_video_frames() tc is not valid form HR:MN:SC:FR.partial")
        raise;
    tc_frames = int(tc_fr_and_partial.split(".")[0])
    if len(tc_fr_and_partial) > 2:
        tc_partial_frames = float(''.join(['0.', tc_fr_and_partial.split(".")[1]]))
        #print('tc_tools: tc_is_whole_video_frames()  tc_partial_frames =',tc_partial_frames)
        if tc_partial_frames != 0.0:
            return False
    return True


def tc_round(tc, partial_v_fr_digits, v_fr_string):
    v_fs = tc_to_vid_frames(tc, v_fr_string)
    v_fs = round(v_fs, partial_v_fr_digits)
    return vid_frames_to_tc(v_fs, v_fr_string)


def tc_to_vid_frames(tc, v_fr_string):
    """Get the number of video frames from timecode."""
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_string)
    tc_splits = tc.split(":")
    if 3 == len(tc_splits):
        tc_splits_df = tc_splits[2].split(";")
        if 2 == len(tc_splits_df):
            tc_sec = int(tc_splits_df[0])
            tc_fr_and_partial = tc_splits_df[1]
        else:
            print("tc_tools: tc_to_vid_frames() failed to parse tc. tc_splits_df =", str(tc_splits_df))
            raise
    elif 4 == len(tc_splits):
        tc_sec = int(tc.split(":")[2])
        tc_fr_and_partial = tc.split(":")[3]
    else:
        print("tc_tools: tc_to_vid_frames() failed to parse tc")
        raise
    tc_hr = int(tc.split(":")[0])
    tc_min = int(tc.split(":")[1])
    tc_frames = int(tc_fr_and_partial.split(".")[0])
    if len(tc_fr_and_partial) > 2:
        tc_partial_frames = float(''.join(['0.', tc_fr_and_partial.split(".")[1]]))
    else:
        tc_partial_frames = 0.0
    frame_count = tc_frames
    if DEBUG_tc_to_vid_frames:
        print('tc_to_vid_frames() tc_hr =',tc_hr)
        print('tc_to_vid_frames() tc_min =',tc_min)
        print('tc_to_vid_frames() tc_sec =',tc_sec)
        print('tc_to_vid_frames() tc_fr_and_partial =',tc_fr_and_partial)
        print('tc_to_vid_frames() tc_frames =',tc_frames)
        print('tc_to_vid_frames() tc_partial_frames =',tc_partial_frames)

    # 29.97 Drop-Frame Time Code eliminates 2 frames every minute except for minutes 00, 10, 20, 30, 40, and 50
    if v_fr_string == VID_FRAME_RATE_STRING_2997df:
        total_minutes = tc_min + (tc_hr * 60)
        frames_due_to_minutes = v_fr * total_minutes * 60
        frames_due_to_minutes -= (int(total_minutes) * 2)
        frames_due_to_minutes += (int(total_minutes / 10) * 2)
        frames_due_to_seconds = v_fr * tc_sec
        frame_count += frames_due_to_seconds
        frame_count += frames_due_to_minutes
    else:
        frame_count += v_fr * tc_sec
        frame_count += v_fr * tc_min * 60 
        frame_count += v_fr * tc_hr * 60 * 60
    if DEBUG_tc_to_vid_frames:
        print('tc_to_vid_frames() frame_count =',frame_count + tc_partial_frames)
    return frame_count + tc_partial_frames


def tc_components_to_tc(tc_hr, tc_min, tc_sec, tc_fr, tc_partial_frames, v_fr_string):
    """Assemble timecode components into a timecode string."""
    # 2023-11-30 DRJ: need to accomodate 2997df
    # if tc_partial_frames + tc_fr + tc_sec ends up adding to minutes, we need to make adjustments.
    #       v_fr_string = VID_FRAME_RATE_STRING_2997df
    #            tc_hr  = 0
    #            tc_min = 0
    #            tc_sec = 59
    #             tc_fr = 30
    # tc_partial_frames = 0
    # the resulting tc would be 00:01:00:02
    # 2024-05-10 DRJ: when tc_partial_frames was less than 0.0001, it was being written in exp notation.
    #   And so, I added the Decimal bits.
    # 2025-01-07 DRJ: Decimal does some mangled rounding!  0.6 is printed ad 0.599999999999999999999
    if DEBUG_tc_components_to_tc:
        print('tc_tools: tc_components_to_tc: Top of Function.')
        print('tc_tools: tc_components_to_tc()              tc_hr =', tc_hr)
        print('tc_tools: tc_components_to_tc()             tc_min =', tc_min)
        print('tc_tools: tc_components_to_tc()             tc_sec =', tc_sec)
        print('tc_tools: tc_components_to_tc()              tc_fr =', tc_fr)
        print('tc_tools: tc_components_to_tc()  tc_partial_frames =', tc_partial_frames)
        print('tc_tools: tc_components_to_tc()  PARTIAL_FRAME_NUMBER_OF_DIGITS =', PARTIAL_FRAME_NUMBER_OF_DIGITS)
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_string)
    sec_fr_delimiter = ':'
    if v_fr_string == VID_FRAME_RATE_STRING_2997df:
        sec_fr_delimiter = TC_TOOLS_29DF_SEC_FRAME_DELIM

    while tc_partial_frames >= 1.0:
        tc_fr += 1
        tc_partial_frames -= 1.0
    while tc_fr >= v_fr:
        tc_sec += 1
        tc_fr -= int(v_fr)
    while tc_sec >= 60:
        tc_min += 1
        tc_sec -= 60
    while tc_min >= 60:
        tc_hr += 1
        tc_min -= 60

    tc = ''.join([ str(tc_hr).zfill(2), ':', str(tc_min).zfill(2), ':',str(tc_sec).zfill(2), sec_fr_delimiter, str(tc_fr).zfill(2)])
    if tc_partial_frames > 0.0:
        tc_partial_frames_string = str(tc_partial_frames).lstrip('0')
        if tc_partial_frames < 0.0001:
            tc_partial_frames_string = str(Decimal(tc_partial_frames)).lstrip('0')
        if DEBUG_tc_components_to_tc:
            print('tc_tools: tc_components_to_tc()  tc_partial_frames         =', tc_partial_frames)
            print('tc_tools: tc_components_to_tc()  tc_partial_frames_string  =', tc_partial_frames_string)
        if (len(tc_partial_frames_string) + 1) > PARTIAL_FRAME_NUMBER_OF_DIGITS:
            tc_partial_frames_string = tc_partial_frames_string[0:PARTIAL_FRAME_NUMBER_OF_DIGITS + 1].rstrip('0')
        tc = ''.join([tc,tc_partial_frames_string ])
    if DEBUG_tc_components_to_tc:
        print('tc_tools: tc_components_to_tc() tc =',tc)
        print('tc_tools: tc_components_to_tc() Bottom of Function.')

    return tc


def vid_frames_to_tc(v_fs, v_fr_string):
    """Get timecode from the number of video frames ."""
    if DEBUG_vid_frames_to_tc:
        print('vid_frames_to_tc() Top of Funcion.')
        print('vid_frames_to_tc() v_fr_string      =',v_fr_string)
        print('vid_frames_to_tc() v_fs             =',v_fs)
    v_fr = v_fr_string_to_non_pulldown_float(v_fr_string)
    # if we are negative, wrap around
    v_fs_24hr = tc_to_vid_frames('24:00:00:00', v_fr_string)
    v_fs = round(v_fs,PARTIAL_FRAME_NUMBER_OF_DIGITS)
    if DEBUG_vid_frames_to_tc:
        print('vid_frames_to_tc() v_fs (rounded)   =',v_fs)
    if v_fs < 0:
        v_fs = v_fs + v_fs_24hr
    if v_fs > v_fs_24hr:
        v_fs = v_fs - v_fs_24hr

    _tc = str("00:00:00:00")
    _vid_frames = v_fs
    if v_fr_string == VID_FRAME_RATE_STRING_2997df:
        if True:
            # for every 1800 video frames, add two video frames
            minutes_fr_to_add = int(v_fs/1800) * 2
            #print('vid_frames_to_timecode_seconds(): minutes_fr_to_add =',minutes_fr_to_add)
            # for every 18000 video frames, take away two video frames
            minutes_fr_to_remove = int(v_fs/18000) * 2
            #print('vid_frames_to_timecode_seconds(): minutes_fr_to_remove =',minutes_fr_to_remove)
            v_fs += minutes_fr_to_add
            v_fs -= minutes_fr_to_remove
        total_seconds = v_fs / v_fr
        total_minutes = total_seconds / 60.0
        total_minutes_int = int(total_minutes)
        _vid_frames += (total_minutes_int * 2)
        _vid_frames -= (int(total_minutes_int / 10) * 2)
        if DEBUG_vid_frames_to_tc:
            print('vid_frames_to_tc() v_fs              =',v_fs)
            print('vid_frames_to_tc() total_seconds     =',total_seconds)
            print('vid_frames_to_tc() total_minutes     =',total_minutes)
            print('vid_frames_to_tc() total_minutes_int =',total_minutes_int)
            print('vid_frames_to_tc() _vid_frames       =',_vid_frames)
    if True:
        #tc_hr = 0
        #tc_min = 0
        #tc_sec = 0
        #tc_fr = 0
        _tc_hr = int(_vid_frames / (v_fr * 60 * 60))
        _vid_frames = _vid_frames - v_fr * _tc_hr * 60 * 60
        _tc_min = int(_vid_frames / (v_fr * 60))
        _vid_frames = _vid_frames - v_fr * _tc_min * 60
        _tc_sec = int(_vid_frames / (v_fr))
        _vid_frames = _vid_frames - v_fr * _tc_sec
        _tc_fr = int(_vid_frames)
        _vid_frames = _vid_frames - _tc_fr
        _tc_subfr = _vid_frames
        _subframes = round(_tc_subfr, PARTIAL_FRAME_NUMBER_OF_DIGITS)

        if DEBUG_vid_frames_to_tc:
            print('vid_frames_to_tc() _tc_hr      =',_tc_hr)
            print('vid_frames_to_tc() _tc_min     =',_tc_min)
            print('vid_frames_to_tc() _tc_sec     =',_tc_sec)
            print('vid_frames_to_tc() _tc_fr      =',_tc_fr)
            print('vid_frames_to_tc() _tc_subfr   =',_tc_subfr)
            print('vid_frames_to_tc() _subframes  =',_subframes)

        _tc  = tc_components_to_tc(_tc_hr, _tc_min, _tc_sec, _tc_fr, _subframes, v_fr_string)
    _tc_v_vs = tc_to_vid_frames(_tc,v_fr_string)
    if _tc_v_vs > v_fs_24hr:
        # should never happen
        print("tc_tools: vid_frames_to_tc() result exceeds 24hr.  This should never happen.")
        raise
    if DEBUG_vid_frames_to_tc:
        print('vid_frames_to_tc() _tc =',_tc)
        print('vid_frames_to_tc() Bottom of Funcion.')

    return _tc


def time_seconds_to_tc(time_s, v_fr_string):
    v_fs = time_s * v_fr_string_to_float(v_fr_string)
    return vid_frames_to_tc(v_fs,v_fr_string)


def tc_to_time_seconds(tc, v_fr_string):
    v_fs = tc_to_vid_frames(tc, v_fr_string)
    time_s = v_fs / v_fr_string_to_float(v_fr_string)
    return time_s


def tc_to_audio_frames(tc, v_fr_string, a_fr):
    v_fs = tc_to_vid_frames(tc, v_fr_string)
    return vid_frames_to_audio_frames(v_fs, v_fr_string, a_fr)


def audio_frames_to_tc(a_fs, v_fr_string, a_fr):
    v_fs = audio_frames_to_vid_frames(a_fs, v_fr_string, a_fr)
    return vid_frames_to_tc(v_fs, v_fr_string)


def tc_sub(tc_minuend, tc_subtrahend, v_fr_string):
    """Get the timecode difference in video frames."""
    dif_vid_frames = tc_to_vid_frames(tc_minuend, v_fr_string) - tc_to_vid_frames(tc_subtrahend, v_fr_string)
    return dif_vid_frames


def tc_add(tc_addend_a, tc_addend_b, v_fr_string):
    """Get the timecode sum in video frames."""
    sum_vid_frames = tc_to_vid_frames(tc_addend_a, v_fr_string) + tc_to_vid_frames(tc_addend_b, v_fr_string)
    return sum_vid_frames

############################################################################################
#
#   for direct testing
#
############################################################################################

def compare_with_precision(float_a, float_b, precision):
    """return true if the floats are close"""
    _diff = abs(float_a - float_b)
    if _diff > precision: return False
    return True


def test_vid_frames_to_tc():
    tc_1 = '01:00:11:16.6'
    vid_frame_rate = VID_FRAME_RATE_STRING_2397
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    #_v_fs = 86592.0 + 89.6 - 1

    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " = " , _v_fs, " frames = " , tc)
    if tc_1 != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

    exit(-1)
    vid_frame_rate = VID_FRAME_RATE_STRING_2400
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " = " , _v_fs, " frames = " , tc)
    if tc_1 != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " = " , _v_fs, " frames = " , tc)
    if tc_1 != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " = " , _v_fs, " frames = " , tc)
    if tc_1 != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

    #vid_frame_rate = VID_FRAME_RATE_STRING_2997df
    #_v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    #tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    #print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " = " , _v_fs, " frames = " , tc)


    # Test 1 frame less than 1 hour
    tc_1 = '01:00:00:00'
    vid_frame_rate = VID_FRAME_RATE_STRING_2397
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    _v_fs -= 1
    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " - 1 frame = " , _v_fs, " frames = " , tc)
    if '00:59:59:23' != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

    vid_frame_rate = VID_FRAME_RATE_STRING_2400
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    _v_fs -= 1
    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " - 1 frame  = " , _v_fs, " frames = " , tc)
    if '00:59:59:23' != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    _v_fs -= 1
    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " - 1 frame  = " , _v_fs, " frames = " , tc)
    if '00:59:59:24' != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    _v_fs = tc_to_vid_frames(tc_1, vid_frame_rate)
    _v_fs -= 1
    tc = vid_frames_to_tc(_v_fs,vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_1, " - 1 frame  = " , _v_fs, " frames = " , tc)
    if '00:59:59:29' != tc:
        print("FAIL: tc_to_vid_frames()")
        raise

def test_audio_frames_to_tc():
    a_fs = 1.0
    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    tc = audio_frames_to_tc(a_fs, vid_frame_rate, 48000.0)
    print("test_audio_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", a_fs, ": tc = " , tc)
    #if tc_1 != tc:
    #    print("FAIL: tc_to_vid_frames()")
    #    raise

    exit(-1)

def test_time_seconds_to_tc():
    print('test_time_seconds_to_tc()')
    a_fr = 48000.0
    a_fs = 1.0 
    time_seconds_1af = a_fs / a_fr    # .000020833333333333333
    time_seconds = time_seconds_1af
    print('test_time_seconds_to_tc() time_seconds =',time_seconds)
    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    vid_frame_rate = VID_FRAME_RATE_STRING_2997df

    tc = time_seconds_to_tc(time_seconds, vid_frame_rate)
    print("test_time_seconds_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", time_seconds, ": tc = " , tc)
    #if tc_1 != tc:
    #    print("FAIL: tc_to_vid_frames()")
    #    raise

    time_seconds = 86399.0
    time_seconds = 86399.0 + 0.000020833333333333333

    time_seconds = 86485.3990 #  23:59:59:00 @ 2997
    time_seconds = 86398.9126 #  23:59:59:00 @ 2997df  86398.9126
    time_seconds += time_seconds_1af 
    tc = time_seconds_to_tc(time_seconds, vid_frame_rate)
    print('test_time_seconds_to_tc() time_seconds =',time_seconds)
    print("test_time_seconds_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", time_seconds, ": tc = " , tc)


def test_tc_to_time_seconds():
    print('test_tc_to_time_seconds() Top of Function.')
    a_fr = 48000.0
    a_fs = 1.0 
    tc = '23:59:59:00'
    tc = '23:59:59:02'
    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    vid_frame_rate = VID_FRAME_RATE_STRING_2997df
    time_seconds = tc_to_time_seconds(tc, vid_frame_rate)
    print("test_time_seconds_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate),"  tc = " , tc, ' time_seconds =',time_seconds)
    tc = '23:59:59;02.0006244'
    time_seconds = tc_to_time_seconds(tc, vid_frame_rate)
    print("test_time_seconds_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate),"  tc = " , tc, ' time_seconds =',time_seconds)
    #if tc_1 != tc:
    #    print("FAIL: tc_to_vid_frames()")
    #    raise


def test_tc_to_vid_frames():
    print('test_tc_to_vid_frames() Top of Function.')
    a_fr = 48000.0
    a_fs = 1.0 
    tc = '23:59:59:02'
    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    vid_frame_rate = VID_FRAME_RATE_STRING_2997df
    v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print("test_tc_to_vid_frames: video frame rate = ", '{0: <7}'.format(vid_frame_rate),"  tc = " , tc, ' v_fs =',v_fs)
    tc = '23:59:59;02.0006244'
    v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print("test_tc_to_vid_frames: video frame rate = ", '{0: <7}'.format(vid_frame_rate),"  tc = " , tc, ' v_fs =',v_fs)
    #if tc_1 != tc:
    #    print("FAIL: tc_to_vid_frames()")
    #    raise


def test_vid_frames_to_audio_frames():
    print('test_vid_frames_to_audio_frames() Top of Function.')
    a_fr = 48000.0
    a_fs = 1.0 
    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    vid_frame_rate = VID_FRAME_RATE_STRING_2997df
    v_fs = 2589380.0006244
    a_fs = vid_frames_to_audio_frames(v_fs, vid_frame_rate, a_fr)
    print("test_vid_frames_to_audio_frames: video frame rate = ", '{0: <7}'.format(vid_frame_rate),"  v_fs = " , v_fs, ' a_fs =',a_fs)
    #if tc_1 != tc:
    #    print("FAIL: tc_to_vid_frames()")
    #    raise


def test_rounding():
    vid_frame_rate = VID_FRAME_RATE_STRING_2397
    time_s = 3633.5882708333334
    tc     = time_seconds_to_tc(time_s, vid_frame_rate)
    print("test_rounding: time_seconds_to_tc:  ", time_s, " = " , tc, " @" ,vid_frame_rate, "fps")
    if '01:00:29:23' != tc:
        print("FAIL: time_seconds_to_tc()")
        raise

    time_s = 3633.5882608333334
    tc     = time_seconds_to_tc(time_s, vid_frame_rate)
    print("test_rounding: time_seconds_to_tc:  ", time_s, " = " , tc, " @" ,vid_frame_rate, "fps")
    if '01:00:29:22.999' != tc:
        print("FAIL: time_seconds_to_tc()")
        raise

    tc_24hrs = "24:00:00:00"
    vid_frame_rate = VID_FRAME_RATE_STRING_3000
    vid_frames = tc_to_vid_frames(tc_24hrs, vid_frame_rate)
    print("test_vid_frames_to_tc: video frame rate = ", '{0: <7}'.format(vid_frame_rate)," ", tc_24hrs, " = " , vid_frames, " frames")
    vid_frames_2 = vid_frames - 0.1
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.01
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.0001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.00001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.000001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.0000001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.00000001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    vid_frames_2 = vid_frames - 0.000000001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000000005
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames = 2
    vid_frames_2 = vid_frames - 0.000000001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000000005
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000000006
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames = 3
    vid_frames_2 = vid_frames - 0.000000005
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000000006
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')

    vid_frames = 4147200000
    vid_frames_2 = vid_frames - 0.0001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.00001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000001
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,8), " frames")
    print('.')
    print('.')
    print('.')
    vid_frames_2 = vid_frames - 0.000004
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000005
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000006
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")
    print('.')
    print('.')
    print('.')
    print('.')
    vid_frames = 3.14159265358979323846
    vid_frames_2 = vid_frames - 0.0
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")
    print('.')
    vid_frames = 1.14159265358979323846
    vid_frames_2 = vid_frames - 0.0
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")
    print('.')
    vid_frames = 2.14159265358979323846
    vid_frames_2 = vid_frames - 0.0
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000005
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")
    print('.')
    vid_frames_2 = vid_frames - 0.000006
    print("test_vid_frames_to_tc: vid_frames_2 =" , vid_frames_2, " frames")
    print("test_vid_frames_to_tc: vid_frames_2 =" , round(vid_frames_2,5), " frames")



    print('done.')






if __name__ == "__main__":
    print('tc_tools: top of __main__')
    #test_audio_frames_to_tc()
    test_time_seconds_to_tc()
    test_tc_to_time_seconds()
    test_tc_to_vid_frames()
    test_vid_frames_to_audio_frames()
    #test_vid_frames_to_tc()
    #test_rounding()
    exit(-1);
    vid_frame_rate = VID_FRAME_RATE_STRING_2397
    tc = "01:00:23:45.31415"
    tc_rounded = tc_round(tc, 3, vid_frame_rate )

    tc = '00:00:01:15'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))

    vid_frame_rate = VID_FRAME_RATE_STRING_2997
    tc_v_fs = 2589411
    tc = vid_frames_to_tc(tc_v_fs,vid_frame_rate)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: tc               = ',tc)
    tc_v_fs = 757473

    tc = vid_frames_to_tc(tc_v_fs,vid_frame_rate)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: tc               = ',tc)


    vid_frame_rate = VID_FRAME_RATE_STRING_2400
    tc = '00:00:01:15'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))

    tc = '00:00:01:20'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))
    
    vid_frame_rate = VID_FRAME_RATE_STRING_2500
    tc = '00:00:01:14'
    tc_v_fs = tc_to_vid_frames(tc, vid_frame_rate)
    print('__main__: tc               = ',tc)
    print('__main__: tc_v_fs          = ',tc_v_fs)
    print('__main__: timecode_seconds = ',vid_frames_to_timecode_seconds(tc_v_fs, vid_frame_rate))



    exit(0)
