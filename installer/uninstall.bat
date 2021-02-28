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
call "%~dp0\env_set_root.bat"
call "%~dp0\env_python.bat"

%PYTHON_EXE% -m pip uninstall -y -r %APP_ROOT_PATH%\requirements.txt

echo Would you like to delete %APP_BASE_PATH%?
echo You might want to backup %APP_ROOT_PATH%\config before...
pause
rmdir /s %APP_BASE_PATH%

@echo done!

:finish
pause