if %1x==x (
	echo: make an installer?
	pause
)


pushd "%~dp0"

@echo installation paths
set PYTHONHOME=C:\Python38
set talos_wps=%~dp0\talos_wps
set wheels=%~dp0\wheels\

mkdir %wheels%

@echo step 3: install talos_wps python package requirements
%PYTHONHOME%\python -m pip download -r %talos_wps%\requirements.txt -d %wheels%
::%PYTHONHOME%\python -m pip download -r %talos_wps%\requirements-opt.txt -d %wheels%
%PYTHONHOME%\python -m pip download -r %talos_wps%\requirements-iis.txt -d %wheels%
%PYTHONHOME%\python -m pip download -r %talos_wps%\requirements-apache.txt -d %wheels%

popd

@echo done!

if %1x==x pause