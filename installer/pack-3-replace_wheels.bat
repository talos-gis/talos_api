@echo Replacing some wheels...

set WHEELS=%~dp0\wheels\

set WHL=gdal
@echo Replacing %WHL% wheel
del %WHEELS%\%WHL%-*.*
copy d:\dev-install\GDAL\MRR\GDAL-3.2.1-cp39-cp39-win_amd64.whl %WHEELS%

set WHL=talosgis
set SRC_WHL=D:\dev\gis\TaLoS\1\p\talos
@echo Replacing %WHL% wheel
del %WHEELS%\%WHL%-*.*
copy %SRC_WHL%\dist\*.whl %WHEELS%

pause