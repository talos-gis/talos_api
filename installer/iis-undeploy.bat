@ECHO OFF
ECHO IIS 7.5 Python app uninstall
ECHO =============================
ECHO.

::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto doit
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:: Check for IIS setup
IF NOT EXIST %windir%\system32\inetsrv\appcmd.exe (
    ECHO Please have IIS 7.5 install first
    GOTO END
)

:doit

:: Default settings
:: root app is in the parent folder
SET APP_BASE_RELATIVE_PATH=..\..
SET APP_ROOT_RELATIVE_PATH=..
for %%i in ("%~dp0%APP_BASE_RELATIVE_PATH%") do SET "APP_BASE_PATH=%%~fi"
ECHO app base path: "%APP_BASE_PATH%"
for %%i in ("%~dp0%APP_ROOT_RELATIVE_PATH%") do SET "APP_ROOT_PATH=%%~fi"
ECHO full path: "%APP_ROOT_PATH%"
for %%I in (%APP_BASE_RELATIVE_PATH%) do set APP_NAME=%%~nxI
ECHO App Name: "%APP_NAME%"

SET PROJECT_NAME=%APP_NAME%
SET SITE_NAME=%PROJECT_NAME%

:: Gathering information
IF [%1] == [v] (
	SET /p SITE_NAME="Enter IIS site name (%PROJECT_NAME%):" %=%
)

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

ECHO This script will uninstall wfastcgi, clear fastCGI settings and delete %SITE_NAME% site.
ECHO press Ctrl+C to break or any key to start uninstallation...
pause

ECHO ... Uninstall %WFASTCGI_TGZ%
%PYTHON_EXE% -m pip uninstall wfastcgi

ECHO.
ECHO ... Delete IIS Site: %SITE_NAME%
%windir%\system32\inetsrv\appcmd delete site %SITE_NAME%

ECHO.
ECHO ... Clear Python FastCGI Handler
%windir%\system32\inetsrv\appcmd delete clear /section:system.webServer/fastCGI

pause