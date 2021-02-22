pushd "%~dp0"

::Installation paths
call set_root_env.bat
call python_env.bat

set APP_REPO=https://github.com/talos-gis/pywps-flask.git

set APP_ROOT_PATH=%APP_BASE_PATH%\%APP_NAME%
set APP_NAME_ZIP=%~dp0\app_install\%APP_NAME%.7z
set WHEELS=%~dp0\wheels\

@echo git clone %APP_NAME%
rmdir /s/q %APP_ROOT_PATH%
git clone %APP_REPO% %APP_ROOT_PATH%
pushd "%~dp0"
cd /d %APP_ROOT_PATH%
git pull
popd 

@echo zipping %APP_ROOT_PATH% -> %APP_NAME_ZIP% ...
del %APP_NAME_ZIP%
7za a %APP_NAME_ZIP% %APP_ROOT_PATH%\*
pause

@echo step 3: install %APP_NAME% python package requirements
%PYTHON_EXE% -m pip download -r %APP_ROOT_PATH%\requirements.txt -d %WHEELS%
pause

call pack-2-replace_wheels.bat

::@echo Delete %APP_ROOT_PATH%...
::rmdir /s/q %APP_ROOT_PATH%
::pause

popd

@echo Done!

:finish
pause