pushd "%~dp0"

@echo installation paths
SET PYTHON_HOME=C:\Python39\
SET PYTHON_EXE=%PYTHON_HOME%\python.exe
IF NOT EXIST %PYTHON_EXE% (
    SET /p PYTHON_HOME="Enter python.exe path (%PYTHON_HOME%):" %=%
    SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)

set talos_wps=%~dp0\talos_wps
set wheels=%~dp0\wheels\
set talos_gis=D:\dev\gis\TaLoS\1\p\talos

@echo talos_wps install files
set talos_wps_7z=%~dp0\talos_wps_install\talos_wps.7z

@echo step 2: git clone or extract talos_wps
rmdir /s/q %talos_wps%
git clone https://github.com/talos-gis/pywps-flask.git %talos_wps%
pushd "%~dp0"
cd /d %talos_wps%
git checkout talos_wps
git pull
popd 

del talos_wps_7z
7za a %talos_wps_7z% %talos_wps%\*
pause

@echo step 3: install talos_wps python package requirements
%PYTHON_EXE% -m pip download -r %talos_wps%\requirements.txt -d %wheels%
pause

pushd %talos_gis%
rmdir /s/q dist
rmdir /s/q build
%PYTHON_EXE% setup.py bdist_wheel
copy dist\*.whl %wheels%
popd

popd

@echo done!

:finish
pause