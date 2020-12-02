if %1x==x (
	echo: make an installer?
	pause
)

set talos_gis=D:\dev\gis\TaLoS\1\p\talos
set gdalos=d:\dev\gis\gdalos
set wheels="%~dp0\wheels\"

set talos_wps_install_dir=%~dp0\talos_wps_install
set PYTHONHOME=C:\Python38
set talos_7z=%talos_wps_install_dir%\talos.7z

mkdir %wheels%
for %%m in (%talos_gis%, %gdalos%) do (
  pushd %%m
  rmdir /s/q dist
  rmdir /s/q build
  python setup.py sdist bdist_wheel
  copy dist\*.whl %wheels%
  popd
)


mkdir %talos_wps_install_dir%
7za a %talos_7z% %PYTHONHOME%\talos.dll

if %1x==x pause