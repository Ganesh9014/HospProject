@echo off
cd /d "%~dp0"

REM 1. Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in system PATH!
    echo Please install Python and check the 'Add Python to PATH' box.
    pause
    exit /b 1
)

REM 2. Check if .env file exists
if not exist ".env" (
    if exist ".env.template" (
        copy .env.template .env >nul
    ) else (
        echo ERROR: .env configuration file is missing!
        pause
        exit /b 1
    )
)

REM 3. Start server silently using pythonw (no console window)
if exist "%~dp0venv\Scripts\pythonw.exe" (
    start "" "%~dp0venv\Scripts\pythonw.exe" serve.py
) else (
    start "" pythonw serve.py
)
exit
