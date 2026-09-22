# Put otaconskeep.cmd on the Windows user PATH so CMD can run: otaconskeep
# Idempotent. Safe to re-run. Does not need admin.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File deploy\install-otaconskeep-path.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File deploy\install-otaconskeep-path.ps1 -CmdSource C:\path\otaconskeep.cmd

[CmdletBinding()]
param(
    [string]$KeepDir = "",
    [string]$CmdSource = ""
)

$ErrorActionPreference = "Continue"

if (-not $KeepDir) {
    $KeepDir = Join-Path $env:LOCALAPPDATA "OtaconsKeep"
}
$shimDir = Join-Path $KeepDir "bin"
New-Item -ItemType Directory -Force -Path $shimDir | Out-Null

$dest = Join-Path $shimDir "otaconskeep.cmd"

$candidates = @()
if ($CmdSource) { $candidates += $CmdSource }
$candidates += @(
    (Join-Path $PSScriptRoot "..\otaconskeep.cmd"),
    (Join-Path $KeepDir "otaconskeep.cmd"),
    (Join-Path $KeepDir "installer\otaconskeep.cmd"),
    (Join-Path $KeepDir "installer\downloads\otaconskeep.cmd")
)

$src = $null
foreach ($c in $candidates) {
    if ($c -and (Test-Path -LiteralPath $c)) {
        $src = $c
        break
    }
}

if (-not $src) {
    $tmp = Join-Path $env:TEMP "otaconskeep.cmd"
    $urls = @(
        "https://otaconskeep.github.io/downloads/otaconskeep.cmd",
        "https://www.otaconskeep.com/downloads/otaconskeep.cmd"
    )
    foreach ($u in $urls) {
        try {
            Invoke-WebRequest -Uri $u -OutFile $tmp -UseBasicParsing -TimeoutSec 30
            if ((Test-Path -LiteralPath $tmp) -and ((Get-Item -LiteralPath $tmp).Length -gt 200)) {
                $src = $tmp
                Write-Host "  Downloaded otaconskeep.cmd from $u"
                break
            }
        } catch {
            Write-Host "  Download miss: $u"
        }
    }
}

if (-not $src) {
    Write-Host "FAILED: could not find or download otaconskeep.cmd"
    exit 1
}

Copy-Item -LiteralPath $src -Destination $dest -Force
Write-Host "  Installed: $dest"

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
$needle = $shimDir.TrimEnd('\')
$parts = @($userPath -split ';' | Where-Object { $_ -and $_.Trim() })
$already = $false
foreach ($p in $parts) {
    if ($p.TrimEnd('\').Equals($needle, [StringComparison]::OrdinalIgnoreCase)) {
        $already = $true
        break
    }
}
if (-not $already) {
    $newPath = if ($userPath.Trim()) { ($userPath.TrimEnd(';') + ";" + $shimDir) } else { $shimDir }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "  User PATH += $shimDir"
} else {
    Write-Host "  User PATH already includes $shimDir"
}

# Current process (this PowerShell only)
if ($env:Path -notlike "*$shimDir*") {
    $env:Path = "$shimDir;$env:Path"
}

# Tell Explorer / new shells about the PATH change (best-effort)
try {
    Add-Type -Namespace Otaconskeep -Name Native -MemberDefinition @"
[DllImport("user32.dll", SetLastError=true, CharSet=CharSet.Auto)]
public static extern IntPtr SendMessageTimeout(
    IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam,
    uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
"@ -ErrorAction SilentlyContinue
    $HWND_BROADCAST = [IntPtr]0xffff
    $WM_SETTINGCHANGE = 0x1A
    $SMTO_ABORTIFHUNG = 0x0002
    [UIntPtr]$result = [UIntPtr]::Zero
    [void][Otaconskeep.Native]::SendMessageTimeout(
        $HWND_BROADCAST, $WM_SETTINGCHANGE, [UIntPtr]::Zero, "Environment",
        $SMTO_ABORTIFHUNG, 5000, [ref]$result)
} catch {}

Write-Host "OTACONSKEEP_PATH_OK shim=$dest"
Write-Host "Open a NEW Command Prompt, then type: otaconskeep"
exit 0
