$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "apps\backend"
$frontend = Join-Path $root "apps\frontend"

Write-Host "Setting up CareerPilot AI..." -ForegroundColor Cyan
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python 3.10+ and retry."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js 22+ and retry."
}

Push-Location $backend
try {
    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        py -3.10 -m venv .venv
    }
    & ".venv\Scripts\python.exe" -m pip install --upgrade pip
    & ".venv\Scripts\python.exe" -m pip install -e ".[dev]"
} finally {
    Pop-Location
}

Push-Location $frontend
try {
    npm install
} finally {
    Pop-Location
}

$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $root ".env.example") $envFile
}

Write-Host "Setup complete. Run .\scripts\start-local.ps1 to launch CareerPilot." -ForegroundColor Green
