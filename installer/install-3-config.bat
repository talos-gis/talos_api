@echo off

SET ROOT_RELATIVE_PATH=..
for %%i in ("%~dp0%ROOT_RELATIVE_PATH%") do SET "ROOT_DIR_PATH=%%~fi"
SET PYTHON_HOME=%ROOT_DIR_PATH%\Python39
SET PYTHON_EXE=%PYTHON_HOME%\python.exe
IF NOT EXIST %PYTHON_EXE% (
	SET PYTHON_HOME=c:\Python39
	SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)
IF NOT EXIST %PYTHON_EXE% (
    SET /p PYTHON_HOME="Enter python.exe path (%PYTHON_HOME%):" %=%
    SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)
ECHO Using Python: %PYTHON_EXE%

SET CONFIG=%1
SET /p CONFIG="Enter path for config file (%config%):" %=%

%PYTHON_EXE% ..\generate_configs.py %CONFIG%
pause