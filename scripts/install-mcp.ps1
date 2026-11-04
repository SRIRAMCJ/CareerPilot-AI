param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$McpRoot = Join-Path $RepoRoot "apps\mcp-server"
$VenvPython = Join-Path $McpRoot ".venv\Scripts\python.exe"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python 3.10+ and retry."
}

if (-not (Test-Path $VenvPython)) {
    py -3.10 -m venv (Join-Path $McpRoot ".venv")
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -e $McpRoot

$Config = [ordered]@{
    command = $VenvPython
    args = @("-m", "careerpilot_mcp.server")
    env = [ordered]@{
        CAREERPILOT_API_URL = "http://127.0.0.1:8000"
        CAREERPILOT_MCP_TRANSPORT = "stdio"
    }
}
$Json = $Config | ConvertTo-Json -Depth 5

Write-Host ""
Write-Host "CareerPilot MCP installed." -ForegroundColor Green
Write-Host "Ensure the CareerPilot backend is running at http://127.0.0.1:8000."
Write-Host ""
Write-Host "Claude Desktop config entry (merge into claude_desktop_config.json):"
Write-Host ('"mcpServers": { "careerpilot": ' + $Json + ' }')
Write-Host ""
Write-Host "Codex CLI command:"
Write-Host ('codex mcp add careerpilot -- "' + $VenvPython + '" -m careerpilot_mcp.server')
Write-Host ""
Write-Host "For clients with a JSON MCP config, use command, args, and env above."
Write-Host "Do not overwrite an existing client config; merge the careerpilot entry."
