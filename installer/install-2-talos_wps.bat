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

set talos_wps=c:\talos_wps
set wheels=%~dp0\wheels\

@echo talos_wps install files
set talos_wps_7z=%~dp0\talos_wps_install\talos_wps.7z

@echo step 2: git clone or extract talos_wps
if exist %talos_wps_7z% (
	7za x %talos_wps_7z% -aoa -o%talos_wps%
) else (
	git clone https://github.com/talos-gis/pywps-flask.git %talos_wps%
	pushd "%~dp0"
	cd /d %talos_wps%
	git checkout talos_wps
	git pull
	popd 
)

@echo step 3: install talos_wps python package requirements
::%PYTHONHOME%\python -m pip install -r %talos_wps%\requirements.txt
::%PYTHONHOME%\python -m pip install --no-index --find-links %wheels% -r %talos_wps%\requirements-iis.txt
%PYTHONHOME%\python -m pip install --upgrade --no-index --find-links %wheels% -r %talos_wps%\requirements.txt

popd

@echo done!

:finish
pause