@echo off
::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto uninstall
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:uninstall

@echo installation paths
SET PYTHON_HOME=C:\Python39\
SET PYTHON_EXE=%PYTHON_HOME%\python.exe
IF NOT EXIST %PYTHON_EXE% (
    SET /p PYTHON_HOME="Enter python.exe path (%PYTHON_HOME%):" %=%
    SET PYTHON_EXE=%PYTHON_HOME%\python.exe
)

set talos_wps=c:\talos_wps
set wheels=%~dp0\wheels\
%PYTHON_EXE% -m pip uninstall -y -r %talos_wps%\requirements.txt

echo Would you like to delete %talos_wps%?
echo You might want to backup %talos_wps%\config before...
rmdir /s %talos_wps%

@echo done!

:finish
pause