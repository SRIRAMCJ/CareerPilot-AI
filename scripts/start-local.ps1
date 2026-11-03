$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "apps\backend"
$frontend = Join-Path $root "apps\frontend"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path $python) -or -not (Test-Path (Join-Path $frontend "node_modules"))) {
    throw "Dependencies are missing. Run .\scripts\setup-local.ps1 first."
}

$backendPath = $backend.Replace("'", "''")
$frontendPath = $frontend.Replace("'", "''")
$pythonPath = $python.Replace("'", "''")

$backendCommand = "Set-Location -LiteralPath '$backendPath'; & '$pythonPath' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
$frontendCommand = "Set-Location -LiteralPath '$frontendPath'; npm run dev"

Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $backendCommand)
Start-Sleep -Seconds 2
Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $frontendCommand)
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host "CareerPilot API: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "CareerPilot UI:  http://localhost:3000" -ForegroundColor Green
