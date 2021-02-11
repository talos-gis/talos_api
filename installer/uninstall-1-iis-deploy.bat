:: Authors: James <spyjamesbond0072003@gmail.com>; Idan Miara <idan@miara.com>
:: based on:
:: * https://stackoverflow.com/questions/19949788/python-fastcgi-on-iis-error-500
:: other resources:
:: * https://docs.microsoft.com/en-us/iis/get-started/getting-started-with-iis/getting-started-with-appcmdexe
:: * https://docs.microsoft.com/en-us/iis/configuration/system.webserver/handlers/
:: * https://docs.microsoft.com/en-us/iis/configuration/system.webserver/fastcgi/application/environmentvariables/


@ECHO OFF
ECHO IIS 7.5 Python app Setup
ECHO ==========================
ECHO.


::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto install
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:: Check for IIS setup
IF NOT EXIST %windir%\system32\inetsrv\appcmd.exe (
    ECHO Please have IIS 7.5 install first
    GOTO END
)

:install

:: Default settings
SET PYTHON_HOME=c:\Python39
SET PYTHON_EXE=%PYTHON_HOME%\python.exe
:: root app is in the parent folder
SET ROOT_RELATIVE_PATH=..
for %%I in (%ROOT_RELATIVE_PATH%) do set ROOT_DIR_NAME=%%~nxI
ECHO Root dir name: "%ROOT_DIR_NAME%"

SET PROJECT_NAME=%ROOT_DIR_NAME%
SET SITE_NAME=%PROJECT_NAME%

IF NOT EXIST %PYTHON_EXE% (
    SET /p PYTHON_HOME="Enter python.exe path (%PYTHON_HOME%):" %=%
    SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)

:: Gathering information
IF [%1] == [v] (
	SET /p SITE_NAME="Enter IIS site name (%PROJECT_NAME%):" %=%
)

ECHO This script will uninstall wfastcgi, clear fastCGI settings and delete %SITE_NAME% site.
ECHO press Ctrl+C to break or any key to start uninstallation...
pause

ECHO ... Uninstall %WFASTCGI_TGZ%
%PYTHON_HOME%\python -m pip uninstall wfastcgi

ECHO.
ECHO ... Delete IIS Site: %SITE_NAME%
%windir%\system32\inetsrv\appcmd delete site %SITE_NAME%

ECHO.
ECHO ... Clear Python FastCGI Handler
%windir%\system32\inetsrv\appcmd delete clear /section:system.webServer/fastCGI

pause