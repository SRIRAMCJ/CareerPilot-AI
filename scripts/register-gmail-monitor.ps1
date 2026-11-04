param(
    [ValidateRange(5, 1440)]
    [int]$IntervalMinutes = 30
)
$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot "check-gmail.ps1"
if (-not (Test-Path $scriptPath)) { throw "Missing Gmail monitor script: $scriptPath" }
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "CareerPilot-Gmail-Monitor" -Action $action -Trigger $trigger -Settings $settings -Description "Checks connected CareerPilot Gmail for recruiter, interview and assessment updates." -Force | Out-Null
Write-Output "Registered Gmail monitoring every $IntervalMinutes minutes."
Write-Output "Task runs as the current Windows user; CareerPilot API and Gmail OAuth must be available."
Write-Output "Logs: $HOME\.careerpilot\logs\gmail-triage.jsonl"
