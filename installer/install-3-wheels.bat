@echo off
::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto doit
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:doit

pushd "%~dp0"

::Installation paths
SET APP_NAME=talos_wps
SET APP_BASE_PATH=c:\%APP_NAME%
SET /p APP_BASE_PATH="Enter app base path (%APP_BASE_PATH%):" %=%
SET APP_ROOT_PATH=%APP_BASE_PATH%\%APP_NAME%

:PYTHON
SET PYTHON_HOME=%APP_BASE_PATH%\Python39
SET PYTHON_EXE=%PYTHON_HOME%\python.exe
IF NOT EXIST %PYTHON_EXE% (
	SET PYTHON_HOME=c:\Python39
	SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)
IF NOT EXIST %PYTHON_EXE% (
    SET /p PYTHON_HOME="Enter python.exe path (%PYTHON_HOME%):" %=%
    SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)
ECHO Using Python: %PYTHON_EXE%

SET WHEELS=%~dp0\wheels\

SET online=
if "%1x" neq "x" SET online=y
if not exist %WHEELS% SET online=y

SET pip_offline=
if %online%x==x SET pip_offline=--upgrade --no-index --find-links %WHEELS%

@echo Install %APP_NAME% python package requirements
%PYTHON_EXE% -m pip install --force-reinstall %pip_offline% -r %APP_ROOT_PATH%\requirements.txt

popd

@echo done!

:finish
pause