@echo off
REM ============================================================
REM  otaconskeep.cmd  — Keep cinema for Windows CMD
REM  After ACCESS GRANTED: KeepRoute Auto via WSL (picks the provider)
REM  OR open KeepRoute / Otacon web — same Keep, two doors.
REM  No hardcoded LAN IPs — uses localhost.
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
echo   You're in.  Keep Auto uses YOUR installed Ollama/Otacon model (qwen tier from setup). Full Claude/Codex/Cursor/Grok routing when Missions is up.
echo.
echo   WEB
echo   KeepRoute    -^> %KEEP_URL%
echo   Otacon Core  -^> %OTACON_URL%
echo   OmniRoute    -^> %OMNI_URL%
echo   Missions     -^> %MISS_URL%
echo.
echo   CMD  (KeepRoute Auto REPL — type missions at keep^>)
echo   wsl -e otaconskeep
echo   One-shot mission:
echo   wsl -e otaconskeep "check disk space on the keep"
echo.

if /I "%~1"=="web" goto OPEN_WEB
if /I "%~1"=="open" goto OPEN_WEB
if /I "%OTACONSKEEP_OPEN_WEB%"=="1" goto OPEN_WEB

REM If user passed a mission on the Windows side, forward into WSL Auto
if not "%~1"=="" goto WSL_ONESHOT

REM Default: drop into KeepRoute Auto in WSL (same as Linux otaconskeep)
where wsl >nul 2>&1
if errorlevel 1 goto NO_WSL
echo   Dropping into KeepRoute Auto via WSL...
echo.
wsl -e otaconskeep
goto END

:WSL_ONESHOT
where wsl >nul 2>&1
if errorlevel 1 goto NO_WSL
wsl -e otaconskeep %*
goto END

:NO_WSL
echo   WSL not found — open KeepRoute in the browser instead?
set /p "ANS=   [Y/N] > "
if /I "%ANS%"=="Y" goto OPEN_WEB
if /I "%ANS%"=="YES" goto OPEN_WEB
goto END

:OPEN_WEB
start "" "%KEEP_URL%"
echo   Opened %KEEP_URL%
goto END

:END
echo.
endlocal
exit /b 0
