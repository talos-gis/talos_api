@echo off

call env_set_root.bat
call env_python.bat

SET CONFIG=%1
SET /p CONFIG="Enter path for config file (%config%):" %=%

%PYTHON_EXE% ..\generate_configs.py %CONFIG%
pause