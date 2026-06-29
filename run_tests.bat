@echo off
chcp 65001 >nul
setlocal

pushd "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
set "PYTHONPATH=%~dp0src"

if not exist "%PYTHON_EXE%" (
    echo Не найден Python виртуального окружения:
    echo %PYTHON_EXE%
    popd
    exit /b 1
)

echo Запуск тестов...
echo.

"%PYTHON_EXE%" -m pytest -q tests --basetemp=.pytest_tmp

set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Тесты успешно пройдены.
) else (
    echo Тесты завершились с ошибкой. Код: %EXIT_CODE%
)

popd
exit /b %EXIT_CODE%