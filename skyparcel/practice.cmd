@echo off
setlocal
where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0assess.py" %*
    exit /b
)
python --version >nul 2>&1
if not errorlevel 1 (
    python "%~dp0assess.py" %*
    exit /b
)
set "SKYPARCEL_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%SKYPARCEL_PYTHON%" (
    "%SKYPARCEL_PYTHON%" "%~dp0assess.py" %*
    exit /b
)
echo Python 3.10 or newer is required. Run: python assess.py --help
exit /b 2
