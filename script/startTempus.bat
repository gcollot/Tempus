@ECHO OFF
SET BIN_DIR="%~dp0"
SET PLUGIN_DIR="%~dp0."

SET TEMPUS_DATA_DIRECTORY=%~dp0\..\data
%BIN_DIR%\tempus_wps -c %PLUGIN_DIR% -p 9000 %*

pause
