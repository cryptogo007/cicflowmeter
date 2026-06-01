# Build the Windows GUI executable (requires uv + dev dependencies).
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Syncing dependencies..."
uv sync --group dev

Write-Host "Building CICFlowMeter.exe with PyInstaller..."
uv run pyinstaller packaging/cicflowmeter-gui.spec --noconfirm

$exe = Join-Path $Root "dist" "CICFlowMeter.exe"
if (Test-Path $exe) {
    Write-Host "Build complete: $exe"
} else {
    Write-Error "Expected executable not found at $exe"
}
