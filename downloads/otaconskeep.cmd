@echo off
REM ============================================================
REM  otaconskeep.cmd  — Keep cinema for Windows CMD
REM  Dual entry: WEB (browser) or CMD (WSL otaconskeep / otacon)
REM  No hardcoded LAN IPs — uses localhost + optional detection.
REM ============================================================
setlocal EnableExtensions EnableDelayedExpansion
title Otaconskeep
color 0A

set "CHAT_PORT=5757"
if defined OTACON_CHAT_PORT set "CHAT_PORT=%OTACON_CHAT_PORT%"
set "OTACON_URL=http://127.0.0.1:%CHAT_PORT%"
set "OMNI_URL=http://127.0.0.1:20128"
set "KEEP_URL=http://127.0.0.1:20129"
set "MISS_URL=http://127.0.0.1:20130"

cls
echo.
echo      ████████╗██╗  ██╗███████╗    ██╗  ██╗███████╗███████╗██████╗
echo      ╚══██╔══╝██║  ██║██╔════╝    ██║ ██╔╝██╔════╝██╔════╝██╔══██╗
echo         ██║   ███████║█████╗      █████╔╝ █████╗  █████╗  ██████╔╝
echo         ██║   ██╔══██║██╔══╝      ██╔═██╗ ██╔══╝  ██╔══╝  ██╔═══╝
echo         ██║   ██║  ██║███████╗    ██║  ██╗███████╗███████╗██║
echo         ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝
echo.
echo               ========================================
echo               =  O T A C O N S K E E P  ·  ONLINE  =
echo               ========================================
echo.
echo   ^> dialing secure satellite uplink...
ping -n 1 127.0.0.1 >nul
echo   ^> cracking perimeter ICE...
ping -n 1 127.0.0.1 >nul
echo   ^> injecting rootkit into mainframe...
ping -n 1 127.0.0.1 >nul
echo.
echo   [+] hacking into the mainframe...
ping -n 1 127.0.0.1 >nul
echo   [+] overriding security protocols...
ping -n 1 127.0.0.1 >nul
echo   [+] syncing keep neural lattice...
ping -n 1 127.0.0.1 >nul
echo   [+] ACCESS GRANTED
echo.
echo      ==================================================
echo           ***  ACCESS GRANTED  ***
echo              welcome to the mainframe
echo      ==================================================
echo.
echo   You're in.  Use the WEB or the CMD — same Keep.
echo.
echo   WEB
echo   Otacon Core  -^> %OTACON_URL%
echo   OmniRoute    -^> %OMNI_URL%   (if installed)
echo   KeepRoute    -^> %KEEP_URL%   (if installed)
echo   Missions     -^> %MISS_URL%   (if installed)
echo.
echo   CMD
echo   Full cinema in Linux/WSL :  wsl -e otaconskeep
echo   Health check             :  wsl -e otacon doctor
echo   Re-run this window       :  otaconskeep
echo.
echo   Tip: Otacon Core and KeepRoute share one Keep — pick web UI or terminal.
echo.

if /I "%~1"=="web" goto OPEN_WEB
if /I "%~1"=="open" goto OPEN_WEB
if /I "%OTACONSKEEP_OPEN_WEB%"=="1" goto OPEN_WEB
goto ASK

:ASK
echo   Open Otacon Core in your browser now? [Y/N]
set /p "ANS=   > "
if /I "%ANS%"=="Y" goto OPEN_WEB
if /I "%ANS%"=="YES" goto OPEN_WEB
goto END

:OPEN_WEB
start "" "%OTACON_URL%"
echo   Opened %OTACON_URL%
goto END

:END
echo.
endlocal
exit /b 0
