::@echo off
::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto doit
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:doit

pushd "%~dp0"

::Installation paths
call "%~dp0\env_set_root.bat"
call "%~dp0\env_installer.bat"
call "%~dp0\env_python.bat"

SET online=
if "%1x" neq "x" SET online=y
if not exist %WHEELS_TARGET% SET online=y

SET pip_offline=
if %online%x==x SET pip_offline=--upgrade --no-index --find-links %WHEELS_TARGET%

@echo Install %APP_NAME% python package requirements
FOR %%R IN (requirements.txt, requirements-opt.txt, requirements-ext.txt) DO %PYTHON_EXE% -m pip install --force-reinstall %pip_offline% -r %APP_ROOT_PATH%\%%R

:: process one requirement at a time so that if one failes it would still process the rest.
::FOR %%R IN (requirements.txt, requirements-opt.txt, requirements-ext.txt) DO for /F "tokens=*" %%F in (%APP_ROOT_PATH%\%%R) do %PYTHON_EXE% -m pip install --force-reinstall %pip_offline% %%F

popd

@echo done!

:finish
pause