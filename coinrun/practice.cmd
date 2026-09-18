@echo off
setlocal
where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0run.py" %*
    exit /b
)
python --version >nul 2>&1
if not errorlevel 1 (
    python "%~dp0run.py" %*
    exit /b
)
set "COINRUN_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%COINRUN_PYTHON%" (
    "%COINRUN_PYTHON%" "%~dp0run.py" %*
    exit /b
)
echo Python 3.10 or newer is required. Run: python run.py --help
exit /b 2

