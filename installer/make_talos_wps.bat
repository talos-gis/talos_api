if %1x==x (
	echo: make an installer?
	pause
)

pushd "%~dp0"

@echo installation paths
set talos_wps=%~dp0\talos_wps
set talos_wps_install_dir=%~dp0\talos_wps_install
set talos_wps_7z=%talos_wps_install_dir%\talos_wps.7z

@echo talos_wps install files

@echo step 2: git clone or extract talos_wps
git clone https://github.com/talos-gis/pywps-flask.git %talos_wps%
pushd "%~dp0"
cd /d %talos_wps%
git checkout talos_wps
git pull
popd 

mkdir %talos_wps_install_dir%
7za a %talos_wps_7z% %talos_wps%\*

popd

@echo done!

if %1x==x pause