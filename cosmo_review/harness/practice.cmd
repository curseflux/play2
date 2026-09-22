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
set "COSMO_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%COSMO_PYTHON%" (
    "%COSMO_PYTHON%" "%~dp0assess.py" %*
    exit /b
)
echo Python 3.10 or newer is required.
exit /b 2
