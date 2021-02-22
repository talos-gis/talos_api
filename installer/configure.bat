@echo off

call set_root_env.bat
call python_env.bat

SET CONFIG=%1
SET /p CONFIG="Enter path for config file (%config%):" %=%

%PYTHON_EXE% ..\generate_configs.py %CONFIG%
pause