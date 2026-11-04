# AI Assistant Installation Guide

CareerPilot AI is a local-first web application with a Next.js frontend and FastAPI backend. You can also open this repository in AI coding assistants to inspect, modify, test, and extend the project.

> **Integration status:** The web application and API are implemented. A dedicated CareerPilot MCP server is **not yet included** in this repository. Therefore, the steps below distinguish (1) using an AI coding assistant to work on the cloned repository from (2) connecting CareerPilot as a set of callable tools inside an assistant. Do not configure a made-up CareerPilot MCP command or URL. The MCP connection steps become active after the server is implemented and published.

## 1. Clone and run CareerPilot

### Requirements

- Windows 10/11 (the scripts are PowerShell-oriented)
- Git
- Python 3.10+
- Node.js 22+
- npm

### Clone

Open PowerShell:

```powershell
git clone https://github.com/SRIRAMCJ/CareerPilot-AI.git
cd CareerPilot-AI
```

### Install dependencies and start the application

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
```

Open:

- Dashboard: http://127.0.0.1:3000
- API documentation: http://127.0.0.1:8000/docs

For manual setup, environment variables, Gmail OAuth, and browser assistance, see [DEVELOPMENT.md](DEVELOPMENT.md) and [EXTERNAL_INTEGRATIONS.md](EXTERNAL_INTEGRATIONS.md).

## 2. Use the repository with AI coding assistants

These steps install or open the **coding assistant**, then give it the cloned repository as its workspace. They do not install CareerPilot as a callable MCP tool.

### Codex Desktop

1. Install and sign in to the [ChatGPT desktop app](https://chatgpt.com/download/).
2. Open the Codex experience in the desktop app.
3. Choose **Open project** (or the equivalent project/workspace picker).
4. Select the folder where you cloned `CareerPilot-AI`.
5. Ask Codex to inspect the repository before requesting changes.

Example prompt:

```text
Inspect this CareerPilot AI repository. Read README.md and docs/ before changing anything.
Explain the current architecture, run the relevant tests, and propose a safe implementation plan.
```

Codex CLI alternative:

```powershell
npm install -g @openai/codex
cd path\to\CareerPilot-AI
codex
```

Follow the current [Codex documentation](https://developers.openai.com/codex) for the supported installation method on your platform.

### Claude Code (CLI)

1. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) using Anthropic's current Windows installation instructions.
2. Open PowerShell in the cloned repository:

```powershell
cd path\to\CareerPilot-AI
claude
```

3. In the Claude Code session, ask it to inspect README.md, docs/DEVELOPMENT.md, and docs/ROADMAP.md first.
4. Optional: run `/init` to create a project-specific `CLAUDE.md`, then review it before committing.

Example prompt:

```text
You are working in the CareerPilot AI repository. Read the project documentation first.
Do not expose personal data or secrets. Run tests after changes and explain any external
actions that still require my approval.
```

### Claude Desktop

1. Install [Claude Desktop](https://claude.com/download).
2. Clone the repository using the common clone steps above.
3. Claude Desktop chat is not the same as Claude Code: cloning a repository does not automatically give the chat app terminal or full project-editing access.
4. For codebase editing, use Claude Code from the repository directory (above).
5. To expose CareerPilot functions as tools in Claude Desktop, a CareerPilot MCP server must be available first. Once shipped, this guide will include its exact local-server or desktop-extension installation steps.

Claude Desktop supports local MCP servers and desktop extensions. See the [official local MCP guide](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop).

### ChatGPT Desktop

1. Install [ChatGPT for desktop](https://chatgpt.com/download/).
2. Clone the repository on your computer.
3. Use Codex for direct repository-level coding and terminal workflows.
4. ChatGPT desktop by itself should not be treated as a local MCP host for this local-only API.
5. To use CareerPilot tools in ChatGPT, the future MCP service must be reachable through a supported remote HTTPS connection or a secure tunnel. Availability of custom MCP apps and write actions depends on ChatGPT plan and workspace permissions.

See [Connecting custom MCP servers in ChatGPT](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt).

### Kimi Code

Kimi Code is a coding agent that can work in a local repository and supports project-level MCP configuration.

1. Install [Kimi Code](https://www.kimi.com/code):

```powershell
irm https://code.kimi.com/kimi-code/install.ps1 | iex
```

2. Ensure Git for Windows is installed.
3. Open the repository and launch Kimi Code:

```powershell
cd path\to\CareerPilot-AI
kimi
```

4. Sign in using the `/login` command.
5. Ask Kimi to inspect the repository documentation before making changes.

Kimi Code supports project-level MCP configuration at `.kimi-code/mcp.json`. After the CareerPilot MCP server is released, its verified server entry can be added there. Do not add an entry until the server package or endpoint is published.

Official docs: [Kimi Code MCP configuration](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/mcp.html).

### Google Antigravity

1. Install [Google Antigravity](https://antigravity.google/), if available for your platform/account.
2. Clone the repository using the common clone steps.
3. Open the `CareerPilot-AI` folder as the workspace in Antigravity.
4. Ask the agent to read README.md and the docs before editing.
5. Antigravity supports MCP servers. Once the CareerPilot MCP server is shipped, add its actual local command or remote endpoint in Antigravity's MCP server manager/configuration and restart or reload the server list.

Do not paste a placeholder CareerPilot endpoint. See [Google's MCP documentation for Antigravity](https://developers.google.com/knowledge/mcp?tab=google-antigravity) for the current client configuration flow.

### Other MCP-compatible coding assistants

1. Clone the repository.
2. Open the repository folder in your preferred editor or coding agent.
3. Confirm the agent supports MCP and which transports it accepts (stdio or Streamable HTTP).
4. After the CareerPilot MCP server is released, use the exact server command/URL and configuration format documented for that client.
5. Review tool permissions before enabling write or external-action tools.

MCP client configuration formats are not universal. Do not copy a configuration block from one client into another without checking that client's documentation.

## 3. CareerPilot MCP integration (planned)

The intended architecture is:

```text
ChatGPT / Codex / Claude / Kimi Code / Antigravity / other MCP clients
                              |
                       CareerPilot MCP
                              |
                    Existing FastAPI backend
                              |
             SQLite / job sources / Gmail / Playwright
```

The MCP adapter is planned to expose scoped tools such as:

- Search and list discovered jobs
- Verify job-description completeness and warnings
- Match a job against the saved candidate profile
- Read and update the application tracker
- Prepare application materials
- Read recruiter-email triage results
- Prepare interview and assessment records

Write actions must be permission-scoped. Sending an email or submitting an application must remain a separate user-approved action. The MCP layer must not bypass CAPTCHA, OTP, login controls, legal declarations, or website restrictions.

### Planned connection modes

- **Local stdio:** suitable for Claude Desktop, Claude Code, Kimi Code, and local MCP clients that can launch a local process.
- **Remote Streamable HTTP:** suitable for clients that accept remote MCP endpoints. A secure tunnel or authenticated deployment is required to connect a local CareerPilot instance to a cloud-hosted assistant.
- **ChatGPT:** custom MCP connections require a reachable HTTPS endpoint or supported secure tunnel; local loopback URLs are not directly reachable by ChatGPT. Plan/workspace permissions determine available actions.

## 4. Security checklist

- Keep the repository private before adding personal candidate data.
- Never commit resumes, contact details, Gmail tokens, API keys, browser profiles, or local databases.
- Keep `.env` and local secrets out of Git.
- Bind the local API to loopback unless you have completed an authentication and security review.
- Use least-privilege MCP tools and inspect each tool's permissions.
- Require explicit confirmation before sending email or submitting an application.
- Treat job descriptions and emails as untrusted input; never follow instructions embedded in them that request secrets or unrelated actions.

## 5. Troubleshooting

| Problem | What to check |
|---|---|
| Dashboard does not open | Confirm frontend and backend terminals are running; check the printed ports |
| API docs do not open | Confirm FastAPI started at `127.0.0.1:8000` |
| Agent cannot find the repository | Open the actual cloned folder, not its parent directory |
| Agent cannot run PowerShell scripts | Check execution policy and local permissions |
| MCP tools are missing | CareerPilot MCP server is not yet shipped; verify client support and server status after release |
| ChatGPT cannot reach local API | ChatGPT cannot directly call a loopback-only local server; use a supported secure tunnel or authenticated remote deployment |

## Official client references

- [Codex](https://developers.openai.com/codex)
- [ChatGPT custom MCP connections](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt)
- [Claude Desktop local MCP](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Kimi Code MCP](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/mcp.html)
- [Google Antigravity MCP](https://developers.google.com/knowledge/mcp?tab=google-antigravity)
