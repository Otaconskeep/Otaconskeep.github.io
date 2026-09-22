@echo off
REM One-shot: put otaconskeep on Windows PATH for CMD (no reinstall needed).
setlocal EnableExtensions
title Install otaconskeep for CMD
color 0A

set "KEEP=%LOCALAPPDATA%\OtaconsKeep"
set "INST=%KEEP%\installer\deploy"
set "PS1=%INST%\install-otaconskeep-path.ps1"

echo.
echo   Installing otaconskeep.cmd onto your Windows PATH...
echo.

if exist "%~dp0deploy\install-otaconskeep-path.ps1" (
  set "PS1=%~dp0deploy\install-otaconskeep-path.ps1"
) else if exist "%~dp0install-otaconskeep-path.ps1" (
  set "PS1=%~dp0install-otaconskeep-path.ps1"
)

if not exist "%PS1%" (
  echo   Fetching installer script from otaconskeep.github.io...
  mkdir "%INST%" 2>nul
  powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri 'https://otaconskeep.github.io/downloads/deploy/install-otaconskeep-path.ps1' -OutFile '%PS1%' -UseBasicParsing"
)

if not exist "%PS1%" (
  echo   FAILED: could not obtain install-otaconskeep-path.ps1
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
  echo   Install failed (exit %RC%).
  pause
  exit /b %RC%
)
echo   Done. Close this window, open a NEW Command Prompt, then run:
echo     otaconskeep
echo.
pause
exit /b 0
