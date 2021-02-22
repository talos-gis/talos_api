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
set APP_REPO=https://github.com/talos-gis/pywps-flask.git

SET APP_BASE_PATH=c:\%APP_NAME%
SET /p APP_BASE_PATH="Enter app base path (%APP_BASE_PATH%):" %=%

SET APP_ROOT_PATH=%APP_BASE_PATH%\%APP_NAME%
set APP_NAME_ZIP=%~dp0\app_install\%APP_NAME%.7z

call python_env.bat

if exist %APP_NAME_ZIP% (
    @echo extract %APP_NAME%...
	7za x %APP_NAME_ZIP% -aoa -o%APP_ROOT_PATH%
) else (
    @echo git clone %APP_NAME%...
	git clone %APP_REPO% %APP_ROOT_PATH%
	pushd "%~dp0"
	cd /d %APP_ROOT_PATH%
	git pull
	popd 
)
popd

@echo done!

:finish
pause