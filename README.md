# CareerPilot AI

A local-first personal career workspace for discovering jobs, matching opportunities against a verified candidate profile, preparing application documents, tracking applications, and organizing interviews.

## Current capabilities

- Candidate profile CRUD and PDF/DOCX resume import with local storage.
- Public Greenhouse, Lever, Ashby and Workable company-board discovery.
- Company-board watchlist, multi-board scans and optional Windows daily scans.
- Explainable matching, application tracker and per-application DOCX material generation.
- Visible Playwright form assistance for safe basic profile fields, with separate submission gate and duplicate-attempt lock.
- Gmail OAuth inbox search, threaded reply drafts, explicit sending and recruiter-message triage.
- Interview/assessment scheduling with timezone-aware ICS export.
- JD quality check for completeness, HTTPS URL hygiene, source identifiers and listing freshness.
- Optional recurring Windows Gmail triage task (default every 30 minutes).

## JD verification and Gmail monitoring

See [docs/AGENT_MONITORING.md](docs/AGENT_MONITORING.md). The JD check evaluates metadata quality; it does not authenticate an employer or guarantee the vacancy remains open. Gmail triage is heuristic and requires reviewing the original email.

Register recurring Gmail monitoring after configuring Gmail OAuth and starting the local API:

```powershell
.\scripts\register-gmail-monitor.ps1 -IntervalMinutes 30
```

## Quick start (Windows)

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
```

Open `http://localhost:3000` and API docs at `http://127.0.0.1:8000/docs`. See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## AI assistant installation

Use [docs/AI_ASSISTANT_INSTALLATION.md](docs/AI_ASSISTANT_INSTALLATION.md) for Windows clone/setup instructions and per-client guidance for Codex, ChatGPT Desktop, Claude Desktop, Claude Code, Kimi Code, Google Antigravity, and other MCP-compatible assistants. The guide clearly distinguishes using an AI coding assistant to work on the repository from connecting CareerPilot as an MCP tool server; the dedicated CareerPilot MCP server is planned but is not yet included.

## Integrations and privacy

LinkedIn, Naukri, Indeed and Foundit are user-session search links, not claimed official API integrations. CareerPilot does not scrape private pages or bypass CAPTCHA, OTP, login restrictions or rate limits. Keep resumes, personal data, browser profiles, OAuth tokens and credentials outside Git. Make this repository private before adding real personal information.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for completed milestones and remaining work.
