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
call set_root_env.bat
call python_env.bat

SET PROJECT_NAME=%APP_NAME%
SET SITE_NAME=%PROJECT_NAME%

:: Gathering information
IF [%1] == [v] (
	SET /p SITE_NAME="Enter IIS site name (%PROJECT_NAME%):" %=%
)

ECHO This script will uninstall wfastcgi, clear fastCGI settings and delete %SITE_NAME% site.
ECHO press Ctrl+C to break or any key to start uninstallation...
pause

ECHO ... Uninstall %WFASTCGI_TGZ%
%PYTHON_EXE% -m pip uninstall -y wfastcgi

ECHO.
ECHO ... Delete IIS Site: %SITE_NAME%
%windir%\system32\inetsrv\appcmd delete site %SITE_NAME%

ECHO.
ECHO ... Clear Python FastCGI Handler
%windir%\system32\inetsrv\appcmd clear config /section:system.webServer/fastCGI

pause