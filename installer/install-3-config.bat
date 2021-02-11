@echo off
SET PYTHON_HOME=C:\Python39\
SET PYTHON_EXE=%PYTHON_HOME%\python.exe
IF NOT EXIST %PYTHON_EXE% (
    SET /p PYTHON_HOME="Enter python.exe path (%PYTHON_HOME%):" %=%
    SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)
%PYTHON_EXE% ..\generate_configs.py %1
pause