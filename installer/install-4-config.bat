pushd "%~dp0"

::Installation paths
call "%~dp0\env_set_root.bat"
call "%~dp0\env_installer.bat"
call "%~dp0\env_python.bat"

%PYTHON_EXE% %INSTALLER_APP%\generate_configs.py %*

popd

@echo done!

:finish
pause