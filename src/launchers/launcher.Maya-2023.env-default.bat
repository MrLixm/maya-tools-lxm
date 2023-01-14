:: Launcher for Maya on Windows
:: Barebone variant for fast startup time.
echo "started %0"
echo "cwd=%~dp0"

set U_MAYA_VERSION=2023
set "U_MAYA_HOME=C:\Program Files\Autodesk\Maya%U_MAYA_VERSION%"

set "PYTHONPATH=%~dp0startup"
set "MAYA_APP_DIR=%~dp0prefs"

set "LXM_MAYA_ENV_DIR=%~dp0env-default"
set LXM_MAYA_PYTHON_LOGGING_DEBUG=1
set LXM_MAYA_ALWAYS_OVERRIDE_PREFS=1

:: =============================================================================
:: region PERFORMANCES IMPROVEMENTS

set MAYA_DISABLE_LOOKDEV_MATERIAL_VIEWER=1

:: https://www.regnareb.com/pro/2015/06/viewport-2-0-and-performances/
:: disable cloud login utility on maya start
set MAYA_DISABLE_CLIC_IPM=1
:: disable cloud connections on maya start
set MAYA_DISABLE_CIP=1
:: disable Customer Error Reporting on maya shutdown
set MAYA_DISABLE_CER=1
:: disable analytic
set MAYA_DISABLE_ADP=1

:: export MAYA_ENABLE_LEGACY_VIEWPORT=1  # enabling increases vp2.0 memory usage for scenes with smoothed openSubdiv meshes
:: export MAYA_DISABLE_VP2_WHEN_POSSIBLE=1
:: endregion

start "" "%U_MAYA_HOME%\bin\maya.exe"

echo Launcher finished, press any to escape.
pause >nul