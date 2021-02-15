@echo off
::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto doit
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:doit

::Installation paths
SET APP_BASE_RELATIVE_PATH=..\..
SET APP_ROOT_RELATIVE_PATH=..
for %%i in ("%~dp0%APP_BASE_RELATIVE_PATH%") do SET "APP_BASE_PATH=%%~fi"
ECHO app base path: "%APP_BASE_PATH%"
for %%i in ("%~dp0%APP_ROOT_RELATIVE_PATH%") do SET "APP_ROOT_PATH=%%~fi"
ECHO full path: "%APP_ROOT_PATH%"
for %%I in (%APP_BASE_RELATIVE_PATH%) do set APP_NAME=%%~nxI
ECHO App Name: "%APP_NAME%"

:PYTHON
SET PYTHON_HOME=%APP_BASE_PATH%\Python39
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

%PYTHON_EXE% -m pip uninstall -y -r %APP_ROOT_PATH%\requirements.txt

echo Would you like to delete %APP_BASE_PATH%?
echo You might want to backup %APP_ROOT_PATH%\config before...
rmdir /s %APP_BASE_PATH%

@echo done!

:finish
pause