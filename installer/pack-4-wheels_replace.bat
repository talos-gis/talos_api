@echo Replacing some wheels...

call "%~dp0\env_installer.bat"

set WHEELS_SOURCE=d:\dev\pip\wheels1
set WHEELS_ARCH=win_amd64

for %%W in (GDAL,talosgis,gdal_mrr,gdal_utils) do (
    @echo Replacing %%W wheel
    del %WHEELS_TARGET%\%%W-*.*
    copy %WHEELS_SOURCE%\%%W-*-%WHEELS_ARCH%.whl %WHEELS_TARGET%
)
copy %WHEELS_SOURCE%\GDAL_*.whl %WHEELS_TARGET%

pause