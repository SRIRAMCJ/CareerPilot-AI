# CareerPilot AI

A secure, cloud-ready personal career workspace for discovering jobs, matching opportunities against a verified candidate profile, preparing application documents, tracking applications, and organizing interviews.

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

## Cloud deployment

**Recommended:** deploy the Next.js dashboard to Vercel and the FastAPI backend plus authenticated remote MCP server to Render. The existing SQLite database and resume/generated-document files are preserved on a Render persistent disk for this single-user deployment.

See [docs/VERCEL_RENDER_DEPLOYMENT.md](docs/VERCEL_RENDER_DEPLOYMENT.md) for the deployment walkthrough and [render.yaml](render.yaml) for the Render Blueprint.

An alternative self-managed Docker Compose deployment on a Linux VM remains documented in [docs/CLOUD_DEPLOYMENT.md](docs/CLOUD_DEPLOYMENT.md).

## Optional local development

Local setup is intended for contributors who want to modify the code. It is not required to use the hosted dashboard or remote MCP deployment.

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
```

Open `http://localhost:3000`. See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## AI assistant integration (MCP)

CareerPilot includes both a local stdio MCP server and an authenticated remote Streamable HTTP MCP endpoint for compatible clients. It exposes scoped tools for jobs, JD checks, matching, the application tracker, Gmail triage, interviews, and local application-material generation.

For the hosted deployment, use the MCP URL and bearer token described in [docs/VERCEL_RENDER_DEPLOYMENT.md](docs/VERCEL_RENDER_DEPLOYMENT.md). For local development, install the MCP server on Windows:

```powershell
.\scripts\install-mcp.ps1
```

Keep the CareerPilot backend running at `http://127.0.0.1:8000`. Then configure your assistant using [docs/MCP_SERVER.md](docs/MCP_SERVER.md). ChatGPT custom MCP connections require an authenticated HTTPS deployment; the local stdio setup is not directly reachable by ChatGPT.

See [docs/AI_ASSISTANT_INSTALLATION.md](docs/AI_ASSISTANT_INSTALLATION.md) for client installation and repository workspace instructions.

## Integrations and privacy

LinkedIn, Naukri, Indeed and Foundit are user-session search links, not claimed official API integrations. CareerPilot does not scrape private pages or bypass CAPTCHA, OTP, login restrictions or rate limits. Keep resumes, personal data, browser profiles, OAuth tokens and credentials outside Git. Make this repository private before adding real personal information.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for completed milestones and remaining work.
