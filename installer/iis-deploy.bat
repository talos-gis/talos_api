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
call "%~dp0\env_set_root.bat"
call "%~dp0\env_python.bat"

SET PROJECT_NAME=%APP_NAME%
SET SITE_NAME=%PROJECT_NAME%
SET APP_POOL_NAME=%SITE_NAME%
SET SITE_PHYSIC_PATH=%APP_ROOT_PATH%
SET SITE_URL=*
SET SITE_PORT=5000
SET SITE_HOST_NAME=
SET SITE_PROTOCOL=http
SET WSGI_HANDLER=app.app
SET IIS_PREMISSIONS=y

:: Gathering information
IF [%1] == [v] (
	SET /p PROJECT_NAME="Enter project name (%PROJECT_NAME%):" %=%
	SET SITE_NAME=%PROJECT_NAME%
	SET /p SITE_PHYSIC_PATH="Enter project directory, which contain manage.py (%SITE_PHYSIC_PATH%): " %=%
	SET /p SITE_NAME="Enter IIS site name (%PROJECT_NAME%):" %=%
	SET /p APP_POOL_NAME="Enter IIS App Pool name (%APP_POOL_NAME%):" %=%
	SET /p SITE_PROTOCOL="Enter http|https for protocol (%SITE_PROTOCOL%): " %=%
	SET /p SITE_URL="Enter site url (%SITE_URL%):" %=%
	SET /p WSGI_HANDLER="Enter WSGI Handler (%WSGI_HANDLER%):" %=%
)
SET /p IIS_PREMISSIONS="Enter Set IIS Permissions (%IIS_PREMISSIONS%):" %=%
SET /p SITE_PORT="Enter port (%SITE_PORT%):" %=%

IF %SITE_URL%==localhost (
    SET SITE_URL=*
)
SET PYHANDLE=PyFastCGI_%SITE_NAME%

ECHO press Ctrl+C to break or any key to start installation...
pause
::goto env

:wfastcgi
ECHO .
SET WFASTCGI_TGZ=wfastcgi-3.0.0.tar.gz
IF NOT EXIST %WFASTCGI_TGZ% SET WFASTCGI_TGZ=wfastcgi
ECHO ... Install %WFASTCGI_TGZ%
%PYTHON_EXE% -m pip install %WFASTCGI_TGZ%

::SET WFCGI_FILE=%SITE_PHYSIC_PATH%wfastcgi.py
SET WFCGI_FILE=%PYTHON_HOME%\Lib\site-packages\wfastcgi.py
IF NOT EXIST %WFCGI_FILE% (
    SET /p WFCGI_FILE="Please enter full path for wfastcgi.py: " %=%
)

ECHO ... Enable wfastcgi
%PYTHON_HOME%\Scripts\wfastcgi-enable

:fastcgi_iis
ECHO .
ECHO ... Install FASTCGI for IIS. Please wait.
:: https://stackoverflow.com/questions/8054282/how-can-you-programmatically-turn-off-or-on-windows-features#:~:text=Currently%2C%20users%20must%20go%20into,that%20they%20want%20to%20activate.
dism.exe /online /enable-feature /all /featurename:IIS-CGI
::start /wait %windir%\System32\PkgMgr.exe /iu:IIS-WebServerRole;IIS-WebServer;IIS-CommonHttpFeatures;IIS-StaticContent;IIS-DefaultDocument;IIS-DirectoryBrowsing;IIS-HttpErrors;IIS-HealthAndDiagnostics;IIS-HttpLogging;IIS-LoggingLibraries;IIS-RequestMonitor;IIS-Security;IIS-RequestFiltering;IIS-HttpCompressionStatic;IIS-WebServerManagementTools;IIS-ManagementConsole;WAS-WindowsActivationService;WAS-ProcessModel;WAS-NetFxEnvironment;WAS-ConfigurationAPI;IIS-CGI

IF [%IIS_PREMISSIONS%] neq [y] goto site
:permissions
ECHO .
ECHO ... Give permmissions for iusr,iis_iusrs groups to the dirs "%SITE_PHYSIC_PATH%", "%PYTHON_HOME%"
FOR %%d IN ("%SITE_PHYSIC_PATH%", "%PYTHON_HOME%") DO FOR %%u IN (iusr,iis_iusrs) DO icacls %%d /grant:r %%u:(OI)(CI)M /T /C

:site
ECHO.
ECHO ... Create IIS Site: %SITE_NAME%
%windir%\system32\inetsrv\appcmd add site /name:%SITE_NAME% /physicalPath:%SITE_PHYSIC_PATH% /bindings:%SITE_PROTOCOL%/%SITE_URL%:%SITE_PORT%:%SITE_HOST_NAME%
%windir%\system32\inetsrv\appcmd start site /site.name:%SITE_NAME%

ECHO.
ECHO ... Create IIS App Pool: %APP_POOL_NAME%
%windir%\system32\inetsrv\appcmd add apppool /name:%APP_POOL_NAME%
%windir%\system32\inetsrv\appcmd set app "%SITE_NAME%/" /applicationPool:%APP_POOL_NAME%


ECHO.
ECHO ... Setup Python FastCGI Handler
%windir%\system32\inetsrv\appcmd set config /section:system.webServer/fastCGI "/+[fullPath='%PYTHON_EXE%', arguments='%WFCGI_FILE%']"

ECHO.
ECHO ... Register the handler for %SITE_NAME% site
%windir%\system32\inetsrv\appcmd set config "%SITE_NAME%" /section:system.webServer/handlers "/+[name='%PYHANDLE%',path='*',verb='*',modules='FastCgiModule',scriptProcessor='%PYTHON_EXE%|%WFCGI_FILE%',resourceType='Unspecified']" /commit:site

:env
ECHO.
ECHO ... Configure %PYTHONPATH% so your Python app can be found by the Python interpreter
%windir%\system32\inetsrv\appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='%PYTHON_EXE%', arguments='%WFCGI_FILE%'].environmentVariables.[name='PYTHONPATH',value='%SITE_PHYSIC_PATH%']" /commit:apphost

ECHO.
ECHO ...Tell the FastCGI to WSGI gateway which WSGI handler to use %WSGI_HANDLER%:
%windir%\system32\inetsrv\appcmd.exe set config -section:system.webServer/fastCgi /+"[fullPath='%PYTHON_EXE%', arguments='%WFCGI_FILE%'].environmentVariables.[name='WSGI_HANDLER',value='%WSGI_HANDLER%']" /commit:apphost

echo ...
echo You probably got an error at the stage "Register the handler for %SITE_NAME% site", so you need to do it manually via IIS UI:
echo follow the following instructions (also documented as step 7 in the attached document)
echo goto: https://docs.microsoft.com/en-us/iis/configuration/system.webserver/handlers/
echo look for: How create a handler mapping for an ASP.NET handler in an IIS 7 application running in Integrated mode
echo Or follow the following instructions:
echo ======================================
echo Open IIS (Start - IIS)
echo Select the site %SITE_NAME% from the left name and open the "Handler Mappings" feature from the middle pane.
echo Click on "Add Module Mapping" from the right pane
echo * Request Path: "*"
echo * Type: "FastCgiModule"
echo * Executable: "%PYTHON_EXE%|%WFCGI_FILE%"
echo * Name: %PYHANDLE%
echo Click Request Restrictions
echo * Uncheck "Invoke handler only if request is mapped to:"
echo OK, OK
echo Do you want to create FastCGI...: Yes
echo ...
echo When you are done press enter to restart IIS and finish setup...
pause

::%windir%\system32\inetsrv\appcmd list site /name:%SITE_NAME%
::%windir%\system32\inetsrv\appcmd list config %SITE_NAME%

ECHO.
ECHO ... Restart IIS
iisreset
ECHO ... Done...
:END
