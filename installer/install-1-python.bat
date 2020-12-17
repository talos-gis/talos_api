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
set PYTHONHOME=C:\Python38
set python_inst=python-3.8.6-amd64.exe

@echo step 1: installing python
if %1x==x (
	@echo to skip python installation run this installer with any argument for installing python as well, i.e.:
	@echo %~nx0 x
	%python_inst% /passive InstallAllUsers=1 PrependPath=1 TargetDir=%PYTHONHOME%
) else (
	@echo skipping python installtion
)


:finish
pause