@echo off

call "%~dp0\env_set_root.bat"
call "%~dp0\env_python.bat"

SET CONFIG=%1
SET /p CONFIG="Enter path for config file (%config%):" %=%

%PYTHON_EXE% ..\generate_configs.py %CONFIG%
pause