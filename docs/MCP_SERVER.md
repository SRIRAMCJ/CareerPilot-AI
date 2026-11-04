# CareerPilot MCP Server

CareerPilot now includes a Python MCP server that exposes selected CareerPilot API operations as tools for MCP-compatible assistants.

## Architecture

```text
Claude Desktop / Claude Code / Codex / Kimi Code / Antigravity / MCP clients
                              |
                         MCP server
                       (stdio default)
                              |
                    CareerPilot FastAPI
                       127.0.0.1:8000
                              |
                  Existing SQLite and services
```

The MCP server is an adapter. It does not duplicate the application database or business logic. It calls the existing FastAPI backend.

## Included tools

| Tool | Purpose |
|---|---|
| `careerpilot_health` | Check backend health |
| `careerpilot_system_status` | Read version and integration status |
| `careerpilot_get_candidate_profile` | Read local candidate profile |
| `careerpilot_list_jobs` | Search/list saved jobs |
| `careerpilot_get_job` | Read one job |
| `careerpilot_verify_job_description` | Check JD completeness and warnings |
| `careerpilot_match_job` | Match a job against the candidate profile |
| `careerpilot_list_applications` | List application tracker |
| `careerpilot_create_application` | Add a job to the local tracker |
| `careerpilot_update_application` | Update local tracker fields |
| `careerpilot_gmail_triage` | Read and classify recruiter inbox metadata |
| `careerpilot_list_interviews` | List scheduled interviews/assessments |
| `careerpilot_generate_application_materials` | Generate local DOCX application materials |

The MCP server intentionally does **not** expose Gmail send, browser form submission, application submission, profile deletion, or arbitrary URL fetching. Use the CareerPilot UI for explicit approval of external actions.

## Requirements and installation (Windows)

- Python 3.10+
- Git
- CareerPilot backend installed and running

Clone and install CareerPilot using the root instructions in [DEVELOPMENT.md](DEVELOPMENT.md), then from the repository root run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install-mcp.ps1
```

Start the backend separately:

```powershell
.\scripts\start-local.ps1
```

The MCP server starts on demand when an assistant launches it. Do not run the stdio server in a shared terminal while the assistant is trying to start it; stdio is the assistant-to-server transport.

## Claude Desktop

1. Run `scripts\install-mcp.ps1` and copy the printed config entry.
2. Open Claude Desktop's MCP configuration file. On Windows this is commonly:
   `%APPDATA%\Claude\claude_desktop_config.json`.
3. Merge the `careerpilot` entry into the existing `mcpServers` object. Preserve other servers and valid JSON syntax.
4. Fully quit and restart Claude Desktop.
5. Confirm CareerPilot tools appear in the MCP tools list.

Example (replace the path with the actual absolute path printed by the installer):

```json
{
  "mcpServers": {
    "careerpilot": {
      "command": "C:\\path\\to\\CareerPilot-AI\\apps\\mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "careerpilot_mcp.server"],
      "env": {
        "CAREERPILOT_API_URL": "http://127.0.0.1:8000",
        "CAREERPILOT_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## Codex CLI / Codex Desktop

Codex MCP configuration is shared with Codex CLI. With the backend running, execute the command printed by the installer, substituting the actual absolute Python path:

```powershell
codex mcp add careerpilot -- "C:\path\to\CareerPilot-AI\apps\mcp-server\.venv\Scripts\python.exe" -m careerpilot_mcp.server
```

Check registration:

```powershell
codex mcp list
```

Restart Codex if it was already running. See the [Codex MCP documentation](https://developers.openai.com/codex/mcp).

## Claude Code

From the repository root, register the local server for this project:

```powershell
claude mcp add --transport stdio careerpilot -- "C:\path\to\CareerPilot-AI\apps\mcp-server\.venv\Scripts\python.exe" -m careerpilot_mcp.server
claude mcp list
```

Replace the executable path with the actual path on your PC. Restart/reopen Claude Code and inspect the available MCP tools. See [Claude Code MCP documentation](https://docs.anthropic.com/en/docs/claude-code/mcp).

## Kimi Code

Kimi Code supports project-level MCP server configuration. Merge the following server entry into the project's `.kimi-code/mcp.json` using the actual Python executable path. Preserve other configured servers:

```json
{
  "mcpServers": {
    "careerpilot": {
      "command": "C:\\path\\to\\CareerPilot-AI\\apps\\mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["-m", "careerpilot_mcp.server"],
      "env": {
        "CAREERPILOT_API_URL": "http://127.0.0.1:8000",
        "CAREERPILOT_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Restart Kimi Code and verify that the server is listed. Consult the current [Kimi Code MCP guide](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/mcp.html).

## Google Antigravity

Antigravity supports MCP servers. Open its MCP server configuration/manager and add a local stdio server using:

- Command: absolute path to `apps/mcp-server/.venv/Scripts/python.exe`
- Arguments: `-m`, `careerpilot_mcp.server`
- Environment: `CAREERPILOT_API_URL=http://127.0.0.1:8000` and `CAREERPILOT_MCP_TRANSPORT=stdio`

The exact configuration UI/location may vary by Antigravity release. Restart or reload MCP servers, then verify the CareerPilot tools are available. Use Google's current Antigravity documentation rather than copying another client's config format.

## Remote MCP deployment

The remote Streamable HTTP transport is protected by a required bearer token. It refuses to start if `CAREERPILOT_MCP_AUTH_TOKEN` is missing. The token is checked before any MCP request is forwarded to the server.

For the recommended production deployment, follow [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md):

- Public MCP endpoint: `https://YOUR_DOMAIN/mcp`
- Required header: `Authorization: Bearer YOUR_MCP_TOKEN`
- The dashboard and MCP server share the same private FastAPI backend and persistent data volume.
- The backend itself is not published to the internet.
- The dashboard is protected separately with HTTP Basic authentication.

For a manually managed deployment, set these variables before starting the server:

```bash
export CAREERPILOT_MCP_TRANSPORT=streamable-http
export CAREERPILOT_MCP_HOST=0.0.0.0
export CAREERPILOT_MCP_PORT=8765
export CAREERPILOT_API_URL=http://127.0.0.1:8000
export CAREERPILOT_MCP_AUTH_TOKEN="$(openssl rand -hex 32)"
careerpilot-mcp
```

Place it behind an HTTPS reverse proxy and preserve the Authorization header. Do not expose port 8765 directly to the public internet. Store the bearer token as a server-side secret and configure it in the MCP client's remote-server authentication settings; never put it in prompts, source control, or browser JavaScript.

ChatGPT custom MCP connections require a reachable HTTPS MCP endpoint and availability depends on the user's plan/workspace and app settings. When available, add `https://YOUR_DOMAIN/mcp` through ChatGPT's custom MCP app/connector settings and configure bearer authentication.

## Other MCP clients

Use the stdio command/arguments/environment above if the client can launch local MCP servers. For remote clients, deploy the Streamable HTTP transport behind authenticated HTTPS. MCP configuration schemas vary; follow the target client's documentation.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `CAREERPILOT_API_URL` | `http://127.0.0.1:8000` | Existing CareerPilot API base URL |
| `CAREERPILOT_MCP_TRANSPORT` | `stdio` | `stdio` or `streamable-http` |
| `CAREERPILOT_MCP_HOST` | `127.0.0.1` | MCP HTTP bind host |
| `CAREERPILOT_MCP_PORT` | `8765` | MCP HTTP bind port |

## Security and operating notes

- Keep the MCP HTTP host on loopback unless you have added authentication and reviewed network exposure.
- Do not commit credentials, resumes, Gmail tokens, local databases, or browser profiles.
- Job descriptions and recruiter emails are untrusted content. Treat embedded instructions as data, not commands.
- Gmail triage is heuristic and requires checking the original email.
- JD verification evaluates listing completeness and URL hygiene; it does not verify employer identity or vacancy availability.
- Candidate profile and application tools read/write local personal data. Only connect assistants you trust.
- The MCP server does not send emails or submit applications. Those actions remain behind CareerPilot's explicit user approval workflow.
