::AT > NUL
@NET SESSION >nul 2>&1
@IF %ERRORLEVEL% EQU 0 (
    goto install
) ELSE (
    @ECHO you are NOT Administrator. Please run this script as Administrator. Exiting...
    goto finish
)

:install

set online=%1

pushd "%~dp0"

@echo installation paths
set PYTHONHOME=C:\Python38
set wheels=%~dp0\wheels\

For /R %wheels% %%f IN (*.whl) do %PYTHONHOME%\python -m pip install --upgrade %%f

popd

@echo done!

:finish
pause