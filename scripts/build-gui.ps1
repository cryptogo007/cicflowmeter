# Build the Windows GUI executable.
# See docs/BUILD_GUIDE.md for full instructions and troubleshooting.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"

if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "Syncing dependencies (uv)..."
    uv sync --group dev
    Write-Host "Building CICFlowMeter.exe with PyInstaller..."
    uv run pyinstaller packaging/cicflowmeter-gui.spec --noconfirm
} else {
    Write-Host "uv not found — using pip + .venv"
    if (-not (Test-Path $venvPython)) {
        python -m venv .venv
    }
    & $venvPython -m pip install -e . -q
    & $venvPython -m pip install pyinstaller -q
    Write-Host "Building CICFlowMeter.exe with PyInstaller..."
    & $venvPython -m PyInstaller packaging/cicflowmeter-gui.spec --noconfirm
}

$exe = Join-Path $Root "dist" "CICFlowMeter.exe"
if (Test-Path $exe) {
    Write-Host "Build complete: $exe"
} else {
    Write-Error "Expected executable not found at $exe"
}
