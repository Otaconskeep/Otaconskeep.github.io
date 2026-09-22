# Put otaconskeep.cmd on the Windows user PATH so CMD can run: otaconskeep
# Idempotent. Safe to re-run. Does not need admin.
#
# Always writes CRLF (CMD breaks on Unix LF). Prefers a fresh Pages download
# over stale local copies that may still have LF line endings.
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

function Write-OtaconskeepCmdCrlf {
    param(
        [Parameter(Mandatory = $true)][string]$From,
        [Parameter(Mandatory = $true)][string]$To
    )
    $bytes = [System.IO.File]::ReadAllBytes($From)
    $offset = 0
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $offset = 3
    }
    $text = [System.Text.Encoding]::UTF8.GetString($bytes, $offset, $bytes.Length - $offset)
    $text = $text -replace "`r`n", "`n" -replace "`r", "`n"
    if (-not $text.EndsWith("`n")) { $text += "`n" }
    $text = $text -replace "`n", "`r`n"
    $enc = New-Object System.Text.UTF8Encoding $false
    $dir = Split-Path -Parent $To
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [System.IO.File]::WriteAllText($To, $text, $enc)
}

if (-not $KeepDir) {
    $KeepDir = Join-Path $env:LOCALAPPDATA "OtaconsKeep"
}
$shimDir = Join-Path $KeepDir "bin"
New-Item -ItemType Directory -Force -Path $shimDir | Out-Null

$dest = Join-Path $shimDir "otaconskeep.cmd"
$tmp = Join-Path $env:TEMP "otaconskeep.cmd.download"

$src = $null
$srcLabel = ""

# 1) Explicit source wins (still CRLF-normalized below)
if ($CmdSource -and (Test-Path -LiteralPath $CmdSource)) {
    $src = $CmdSource
    $srcLabel = "CmdSource"
}

# 2) Prefer fresh Pages download so LF/stale KeepDir copies cannot stick forever
if (-not $src) {
    $urls = @(
        "https://otaconskeep.github.io/downloads/otaconskeep.cmd",
        "https://www.otaconskeep.com/downloads/otaconskeep.cmd"
    )
    foreach ($u in $urls) {
        try {
            Invoke-WebRequest -Uri $u -OutFile $tmp -UseBasicParsing -TimeoutSec 30
            if ((Test-Path -LiteralPath $tmp) -and ((Get-Item -LiteralPath $tmp).Length -gt 200)) {
                $src = $tmp
                $srcLabel = $u
                Write-Host "  Downloaded otaconskeep.cmd from $u"
                break
            }
        } catch {
            Write-Host "  Download miss: $u"
        }
    }
}

# 3) Local fallbacks (installer cache / Keep tree)
if (-not $src) {
    $candidates = @(
        (Join-Path $PSScriptRoot "..\otaconskeep.cmd"),
        (Join-Path $KeepDir "installer\downloads\otaconskeep.cmd"),
        (Join-Path $KeepDir "installer\otaconskeep.cmd"),
        (Join-Path $KeepDir "otaconskeep.cmd")
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path -LiteralPath $c)) {
            $src = $c
            $srcLabel = $c
            break
        }
    }
}

if (-not $src) {
    Write-Host "FAILED: could not find or download otaconskeep.cmd"
    exit 1
}

Write-OtaconskeepCmdCrlf -From $src -To $dest
# Also refresh KeepDir copy so desktop shortcuts stay CRLF-safe
try {
    Write-OtaconskeepCmdCrlf -From $src -To (Join-Path $KeepDir "otaconskeep.cmd")
} catch {}

Write-Host "  Installed: $dest (CRLF, from $srcLabel)"

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

if ($env:Path -notlike "*$shimDir*") {
    $env:Path = "$shimDir;$env:Path"
}

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
