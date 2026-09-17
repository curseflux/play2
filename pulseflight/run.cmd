@echo off
setlocal
where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%~dp0exam.py" %*
    exit /b
)
python --version >nul 2>&1
if not errorlevel 1 (
    python "%~dp0exam.py" %*
    exit /b
)
set "PULSE_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%PULSE_PYTHON%" (
    "%PULSE_PYTHON%" "%~dp0exam.py" %*
    exit /b
)
echo Python 3.10 or newer is required. Install it and run: python exam.py --help
exit /b 2
