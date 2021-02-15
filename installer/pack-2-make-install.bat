pushd "%~dp0"

::Installation paths
SET APP_BASE_RELATIVE_PATH=.
SET APP_ROOT_RELATIVE_PATH=.
for %%i in ("%~dp0%APP_BASE_RELATIVE_PATH%") do SET "APP_BASE_PATH=%%~fi"
ECHO app base path: "%APP_BASE_PATH%"
for %%i in ("%~dp0%APP_ROOT_RELATIVE_PATH%") do SET "APP_ROOT_PATH=%%~fi"
ECHO full path: "%APP_ROOT_PATH%"
for %%I in (%APP_BASE_RELATIVE_PATH%) do set APP_NAME=%%~nxI
ECHO App Name: "%APP_NAME%"
::set APP_BASE_PATH=%~dp0

set APP_REPO=https://github.com/talos-gis/pywps-flask.git

set APP_ROOT_PATH=%APP_BASE_PATH%\app
set APP_NAME_ZIP=%~dp0\app_install\%APP_NAME%.7z
set WHEELS=%~dp0\wheels\

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