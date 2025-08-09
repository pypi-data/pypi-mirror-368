# The versions below will be replaced automatically in CI.
# You do not need to modify any of the versions below.
__version__ = "1.1.0"
CODA_APP_SUITE_VERSION = "+coda-1.68.0"
FINAL_VERSION = __version__ + CODA_APP_SUITE_VERSION

import sys
import shutil
import subprocess

# Find the full path to 'coda'
coda_path = shutil.which("coda")

if coda_path:
    # Run '<path to coda> -v'
    result = subprocess.run(
        [coda_path, "-v"], capture_output=True, text=True, shell=False
    )
    ver = result.stdout.replace("\n", "").replace("coda version ", "")
    # Print output
    if f"+coda-{ver}" not in FINAL_VERSION:
        print(
            "WARNING !!!  Mismatched core tools version",
            ver,
            f"for coda python sdk {__version__}",
            file=sys.stderr,
        )
else:
    split = FINAL_VERSION.split("-")
    ver = split[-1]
    print(
        f"WARNING !!! coda CLI not found in system PATH. Make sure you install coda [v{ver}] if you intend to use the agent.",
        file=sys.stderr,
    )
