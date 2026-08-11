@echo off
cd /d "%~dp0"

echo ====================================================
echo   HOSPITAL APP - AUTORUN CONFIGURATION
echo ====================================================
echo.

REM 1. Clean up old scheduled background task if it exists (fails silently if not admin or doesn't exist)
schtasks /delete /tn "HospitalServer" /f >nul 2>&1

REM 2. Define Startup folder paths
set STARTUP_VBS="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\StartHospitalServer.vbs"
set STARTUP_BAT="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\StartHospitalServer.bat"

echo Configuring automatic startup...

REM Trim trailing backslash from %~dp0 to prevent escaping the closing double-quote in cd /d command
set "CURRENT_DIR=%~dp0"
if "%CURRENT_DIR:~-1%"=="\" set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

REM Delete existing startup files if they exist
if exist %STARTUP_VBS% del %STARTUP_VBS%
if exist %STARTUP_BAT% del %STARTUP_BAT%

REM 3. Create a hidden .bat launcher
(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo call run_on_startup.bat
) > %STARTUP_BAT%

REM 4. Create a VBScript wrapper that runs the .bat silently (no CMD window)
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run Chr^(34^) ^& "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\StartHospitalServer.bat" ^& Chr^(34^), 0, False
) > %STARTUP_VBS%

if exist %STARTUP_VBS% (
    echo.
    echo SUCCESS: Automatic startup has been successfully configured!
    echo The Hospital application will start silently in the background
    echo every time the computer is turned on/restarted and you log in.
    echo No CMD window will appear on startup.
    echo.
    echo Created startup script: %STARTUP_VBS%
) else (
    echo.
    echo ERROR: Failed to configure automatic startup.
    echo Please make sure you have appropriate folder permissions.
)
echo.
pause
