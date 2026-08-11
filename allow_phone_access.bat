@echo off
echo ============================================
echo  Hospital App - Fix Phone Connection
echo ============================================
echo.
echo This will allow your phone to connect to the server.
echo Run this script as ADMINISTRATOR.
echo.

REM Add inbound firewall rule for port 8000
netsh advfirewall firewall add rule name="Hospital App Port 8000" dir=in action=allow protocol=TCP localport=8000
if %errorlevel% equ 0 (
    echo.
    echo [OK] Firewall rule added for port 8000
) else (
    echo.
    echo [ERROR] Failed - please right-click this file and "Run as Administrator"
    pause
    exit /b 1
)

REM Also add outbound just in case
netsh advfirewall firewall add rule name="Hospital App Port 8000 OUT" dir=out action=allow protocol=TCP localport=8000

echo.
echo [OK] Done! Your phone should now be able to connect.
echo.
echo Your PC IP address is:
ipconfig | findstr "IPv4"
echo.
echo Make sure the app is using the WiFi IP shown above (not 192.168.56.1)
echo The correct one is usually 192.168.X.X under "Wireless LAN adapter Wi-Fi"
echo.
pause
