@echo off
setlocal

pushd "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
set "SPEC_FILE=%~dp0timer_2.spec"

if not exist "%PYTHON_EXE%" (
    echo Python virtual environment was not found:
    echo %PYTHON_EXE%
    echo.
    echo Create it first:
    echo py -3.13 -m venv .venv
    popd
    exit /b 1
)

if not exist "%SPEC_FILE%" (
    echo Spec file was not found:
    echo %SPEC_FILE%
    popd
    exit /b 1
)

echo Removing old build directories...

if exist build (
    rmdir /s /q build
)

if exist dist (
    rmdir /s /q dist
)

echo.
echo Building executable...
echo.

"%PYTHON_EXE%" -m PyInstaller --clean timer_2.spec

set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Build completed successfully.
    echo Executable:
    echo dist\timer_2\timer_2.exe
) else (
    echo Build failed. Exit code: %EXIT_CODE%
)

popd
exit /b %EXIT_CODE%