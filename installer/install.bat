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

@echo python installation files
set python_inst=python-3.8.5-amd64.exe
set gdal_whl=GDAL-3.1.2-cp38-cp38-win_amd64.whl
set wheels=%~dp0\wheels\

@echo talos_wps install files
set talos_wps_7z=%~dp0\talos_wps_install\talos_wps.7z
set talos2_7z=%~dp0\talos_wps_install\talos2.7z

@echo step 1: installing python
if %1x==x (
	@echo to skip python installation run this installer with any argument for installing python as well, i.e.:
	@echo %~nx0 x
	%python_inst% /passive InstallAllUsers=1 PrependPath=1 TargetDir=%PYTHONHOME%
) else (
	@echo skipping python installtion
)


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
::%PYTHONHOME%\python -m pip install wheels\%gdal_whl%
::%PYTHONHOME%\python -m pip install -r %talos_wps%\requirements.txt
::%PYTHONHOME%\python -m pip download -r %talos_wps%\requirements.txt
python -m pip install --no-index --find-links %wheels% -r %talos_wps%\requirements.txt
python -m pip install --no-index --find-links %wheels% -r %talos_wps%\requirements-opt.txt

@echo step 4: extract talos_wps additional files
7za x %talos2_7z% -aoa -o%PYTHONHOME%

popd

@echo done!

:finish
pause