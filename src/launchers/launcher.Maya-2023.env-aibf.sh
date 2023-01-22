# Launcher for Maya
# With Arnold and Bifrost
echo "started $0"
echo "cwd=$PWD"

MAYA_VERSION=2023
MAYA_HOME="/c/Program Files/Autodesk/Maya$MAYA_VERSION"

export PYTHONPATH="$PWD/startup"
export MAYA_APP_DIR="$PWD/prefs"

export LXM_MAYA_ENV_DIR="$PWD/env-aibf"
export LXM_MAYA_PYTHON_LOGGING_DEBUG=1
export LXM_MAYA_ALWAYS_OVERRIDE_PREFS=1

# =============================================================================
# region PERFORMANCES IMPROVEMENTS

export MAYA_DISABLE_LOOKDEV_MATERIAL_VIEWER=1

# https://www.regnareb.com/pro/2015/06/viewport-2-0-and-performances/
export MAYA_DISABLE_CLIC_IPM=1  # disable cloud login utility on maya start
export MAYA_DISABLE_CIP=1  # disable cloud connections on maya start
export MAYA_DISABLE_CER=1  # disable Customer Error Reporting on maya shutdown
export MAYA_DISABLE_ADP=1  # disable analytic

# export MAYA_ENABLE_LEGACY_VIEWPORT=1  # enabling increases vp2.0 memory usage for scenes with smoothed openSubdiv meshes
# export MAYA_DISABLE_VP2_WHEN_POSSIBLE=1
# endregion

"$MAYA_HOME/bin/maya.exe"

# read -p "Press any key to continue... " -n1 -s