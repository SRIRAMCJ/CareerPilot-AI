param(
    [string]$Time = "09:00"
)

$ErrorActionPreference = "Stop"
$scanScript = Join-Path $PSScriptRoot "scan-watchlist.ps1"
if (-not (Test-Path $scanScript)) {
    throw "scan-watchlist.ps1 was not found."
}
try {
    [datetime]::ParseExact($Time, "HH:mm", [Globalization.CultureInfo]::InvariantCulture) | Out-Null
} catch {
    throw "Provide the run time in 24-hour HH:mm format, for example -Time '09:00'."
}

$actionArgs = '-NoProfile -ExecutionPolicy Bypass -File "' + $scanScript + '"'
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "CareerPilot-Daily-Job-Scan" -Action $action -Trigger $trigger -Principal $principal -Description "Scan CareerPilot's saved public company job boards once daily." -Force | Out-Null

Write-Host "Registered CareerPilot daily job scan at $Time. The task runs while you are logged in." -ForegroundColor Green
Write-Host "Logs: $HOME\.careerpilot\logs\watchlist-scan.log"
