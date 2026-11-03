$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "apps\backend"
$python = Join-Path $backend ".venv\Scripts\python.exe"
$logDir = Join-Path $HOME ".careerpilot\logs"
$logFile = Join-Path $logDir "watchlist-scan.log"

if (-not (Test-Path $python)) {
    throw "CareerPilot backend is not installed. Run .\scripts\setup-local.ps1 first."
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$apiProcess = $null
try {
    $apiProcess = Start-Process -FilePath $python -ArgumentList @(
        "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"
    ) -WorkingDirectory $backend -PassThru -WindowStyle Hidden

    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -TimeoutSec 2 | Out-Null
            $ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $ready) {
        throw "CareerPilot API did not become ready within 30 seconds."
    }

    $body = @{ limit_per_board = 50 } | ConvertTo-Json
    $result = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/discovery/run" -ContentType "application/json" -Body $body -TimeoutSec 180
    $line = "$(Get-Date -Format o) $($result | ConvertTo-Json -Compress -Depth 8)"
    Add-Content -Path $logFile -Value $line
    Write-Host ($result | ConvertTo-Json -Depth 8)
} catch {
    $line = "$(Get-Date -Format o) ERROR: $($_.Exception.Message)"
    Add-Content -Path $logFile -Value $line
    throw
} finally {
    if ($apiProcess -and -not $apiProcess.HasExited) {
        Stop-Process -Id $apiProcess.Id -Force
    }
}
