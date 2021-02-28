::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto install
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:install

set online=%1

pushd "%~dp0"

@echo installation paths
call env_installer.bat
call env_python_ver.bat

SET PYTHON_INST_PATH=%INSTALLER_ROOT%\%PYTHON_INST%
IF NOT EXIST %PYTHON_INST_PATH% (
    SET /p PYTHON_INST_PATH="Enter full path for the installer file of (%PYTHON_NAME%):" %=%
)

SET PYTHON_HOME=%INSTALLER_ROOT%\%PYTHON_NAME%
SET /p PYTHON_HOME="Enter path to install %PYTHON_INST% (%PYTHON_HOME%):" %=%

@echo ready to install %PYTHON_INST_PATH% to %PYTHON_HOME%?
@echo press ctrl+c to cancel
pause
%PYTHON_INST_PATH% /passive InstallAllUsers=1 PrependPath=1 TargetDir=%PYTHON_HOME%

:finish
pause