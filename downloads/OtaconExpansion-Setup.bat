@echo off
REM ============================================================
REM  OtaconExpansion-Setup.bat  (Premium placeholder)
REM  One-click slot for the Expansion installer.
REM  Full surface pack is NOT shipping yet — this BAT tells the
REM  truth and points at the foundation install that is real.
REM ============================================================
setlocal EnableExtensions
title Otacon Expansion Setup (placeholder)
chcp 65001 >nul

echo.
echo ============================================================
echo   OTACON EXPANSION SETUP — PLACEHOLDER
echo   Otaconskeep Premium · Designed by Antonio G. Garcia
echo ============================================================
echo.
echo  Status
echo  ------
echo  The full one-click Expansion installer (Dashboard / Codec /
echo  War Room / Video Studio) is reserved for this download slot
echo  and is NOT ready yet.
echo.
echo  What IS real today
echo  ------------------
echo  1. Install Otaconskeep Lite first (OtaconsKeep-Setup.bat).
echo  2. Install the Expansion foundation layer (schema + roster):
echo.
echo     curl -fsSL https://raw.githubusercontent.com/Otaconskeep/otacons-ai-ecosystem/main/install_otacon_expansion.sh ^| bash
echo.
echo     (Git Bash / WSL / Linux / macOS)
echo.
echo  3. Unlock Member HQ on the Premium site for news + license card.
echo.
echo  License
echo  -------
echo  Your Premium seat is one license. Do not share password/PIN.
echo  Sharing can revoke the seat. Ask Antonio in Discord if unsure.
echo.
echo ============================================================
echo  Press any key to open the Premium Member page in your browser.
echo ============================================================
pause >nul

start "" "https://otaconskeep.github.io/premium/#install"
exit /b 0
