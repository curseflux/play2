@echo off
setlocal
where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0grade.py" %*
    exit /b
)
python --version >nul 2>&1
if not errorlevel 1 (
    python "%~dp0grade.py" %*
    exit /b
)
set "ECHOFLIGHT_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%ECHOFLIGHT_PYTHON%" (
    "%ECHOFLIGHT_PYTHON%" "%~dp0grade.py" %*
    exit /b
)
echo Python 3.10 or newer is required. Run: python grade.py --help
exit /b 2
