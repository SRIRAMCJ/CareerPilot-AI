$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000/api/v1/gmail/triage"
$root = Join-Path $HOME ".careerpilot"
$logDir = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir "gmail-triage.jsonl"
try {
    $result = Invoke-RestMethod -Method Get -Uri ($baseUrl + "?q=newer_than:2d&max_results=50") -TimeoutSec 60
    $record = [ordered]@{
        checked_at = (Get-Date).ToString("o")
        checked = $result.checked
        classified = $result.items.Count
        action_required = @($result.items | Where-Object { $_.action_required }).Count
        items = $result.items
    }
    ($record | ConvertTo-Json -Depth 8 -Compress) | Add-Content -Path $logFile -Encoding UTF8
    Write-Output "Gmail checked: $($record.classified) messages; $($record.action_required) need attention."
} catch {
    $record = [ordered]@{ checked_at = (Get-Date).ToString("o"); error = $_.Exception.Message }
    ($record | ConvertTo-Json -Compress) | Add-Content -Path $logFile -Encoding UTF8
    Write-Error "Gmail triage failed. Ensure CareerPilot is running and Gmail OAuth is connected."
    exit 1
}
