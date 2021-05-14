pushd "%~dp0"

::Installation paths
call "%~dp0\env_set_root.bat"
call "%~dp0\env_installer.bat"

set APP_REPO=https://github.com/talos-gis/talos_api.git

set APP_ROOT_PATH=%INSTALLER_ROOT%\%APP_NAME%
set APP_NAME_ZIP=%INSTALLER_ROOT%\%APP_NAME%.7z

if EXIST %APP_ROOT_PATH% rmdir /s %APP_ROOT_PATH%

git clone %APP_REPO% %APP_ROOT_PATH%
::pushd "%~dp0"
::cd /d %APP_ROOT_PATH%
::git pull
::popd 

@echo zipping %APP_ROOT_PATH% -> %APP_NAME_ZIP% ...
del %APP_NAME_ZIP%
7za a %APP_NAME_ZIP% %APP_ROOT_PATH%\*

popd

@echo Done!

:finish
pause