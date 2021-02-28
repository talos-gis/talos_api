:: root app is in the parent folder
SET APP_BASE_RELATIVE_PATH=..\..
SET APP_ROOT_RELATIVE_PATH=..
for %%i in ("%~dp0%APP_BASE_RELATIVE_PATH%") do SET "APP_BASE_PATH=%%~fi"
ECHO app base path: "%APP_BASE_PATH%"
for %%i in ("%~dp0%APP_ROOT_RELATIVE_PATH%") do SET "APP_ROOT_PATH=%%~fi"
ECHO full path: "%APP_ROOT_PATH%"
for %%I in (%APP_ROOT_RELATIVE_PATH%) do set APP_NAME=%%~nxI
ECHO App Name: "%APP_NAME%"
::set APP_BASE_PATH=%~dp0