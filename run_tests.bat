@echo off
chcp 65001 >nul
setlocal

pushd "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
set "PYTHONPATH=%~dp0src"

if not exist "%PYTHON_EXE%" (
    echo Python virtual environment was not found:
    echo %PYTHON_EXE%
    echo.
    echo Create it first:
    echo py -3.13 -m venv .venv
    popd
    exit /b 1
)

echo Running tests...
echo.

"%PYTHON_EXE%" -m pytest -q tests --basetemp=.pytest_tmp

set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Tests passed.
) else (
    echo Tests failed. Exit code: %EXIT_CODE%
)

popd
exit /b %EXIT_CODE%