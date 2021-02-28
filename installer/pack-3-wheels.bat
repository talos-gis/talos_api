pushd "%~dp0"

::Installation paths
call "%~dp0\env_set_root.bat"
call "%~dp0\env_installer.bat"
call "%~dp0\env_python.bat"

set APP_ROOT_PATH=%APP_BASE_PATH%\%APP_NAME%

@echo step 3: install %APP_NAME% python package requirements

FOR %%R IN (requirements.txt, requirements-opt.txt) DO %PYTHON_EXE%  -m pip download -r %APP_ROOT_PATH%\%%R -d %WHEELS_TARGET%

popd

pause
