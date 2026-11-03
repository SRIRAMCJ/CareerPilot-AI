# CareerPilot AI

A local-first personal career workspace for discovering jobs, matching opportunities against a verified candidate profile, preparing application documents, tracking applications, and organizing interviews.

## Implemented in the current local-first release

- Candidate profile CRUD in SQLite, including roles, preferences, experience, education, projects, and certifications.
- PDF/DOCX resume import, local storage, text extraction, and skill/contact hints for candidate review.
- Public job discovery from Greenhouse, Lever, Ashby, and Workable company boards.
- Persistent company-board watchlist, one-click multi-board scans, and optional Windows Task Scheduler daily scans.
- Manual job capture, local search, duplicate detection, and explainable matching with location, work-mode, and salary eligibility blockers.
- Application tracker with statuses, notes, next actions, follow-up dates, and original job-page links.
- Per-application DOCX resume and cover-letter draft generation from saved profile facts.
- Optional local Ollama cover-letter drafting; all other core workflows work without a model.
- Interview and assessment scheduling with timezone-aware ICS export and calendar reminder alarms.
- Windows setup and local launch scripts.

## Technology

- Backend: Python 3.10+, FastAPI, Pydantic, SQLite, HTTPX.
- Resume and document handling: pypdf and python-docx.
- Frontend: Next.js 15, React 19, TypeScript.
- Runtime: Windows 11 local-first workflow; backend binds to loopback by default.

## Quick start (Windows)

From the repository root:

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
```

Open the dashboard at `http://localhost:3000` and API documentation at `http://127.0.0.1:8000/docs`.

For manual setup, troubleshooting, daily scanning, and tests, read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Use [docs/ACCEPTANCE_TESTS.md](docs/ACCEPTANCE_TESTS.md) to verify the end-to-end local workflow.

## Integration status

| Capability | Status | Notes |
|---|---|---|
| Greenhouse, Lever, Ashby, Workable | Implemented | Public company-board discovery; user supplies board slugs |
| PDF/DOCX resume parsing | Partial | Selectable text only; scanned PDF OCR not included |
| Matching and eligibility | Implemented | Deterministic and explainable; skill extraction is heuristic |
| Application preparation | Partial | DOCX drafts from saved profile facts; candidate review required |
| Application form assistance | Partial | Visible Playwright browser fills safe profile fields; explicit submit gate is disabled by default |
| LinkedIn, Naukri, Indeed, Foundit | Search links | User-session search links; no private-page scraping or unrestricted API assumption |
| Gmail and recruiter email | Implemented, requires setup | OAuth inbox search, drafts and explicitly confirmed sending |
| Google Calendar | Partial | ICS export supported; direct Calendar OAuth/sync not implemented |
| Local LLM | Partial | Optional loopback-only Ollama cover-letter drafts; deterministic workflows work without a model |

## Privacy and safety

Candidate profiles, resumes, extracted resume text, generated documents, and databases are stored locally and excluded from Git. Never commit real candidate data, credentials, OAuth tokens, browser profiles, or application evidence. Make the repository private before adding any private project configuration or personal data.

CareerPilot does not bypass CAPTCHA, anti-bot protections, login restrictions, or rate limits. It does not invent candidate qualifications, submit legal declarations, pay application fees, or complete identity-bound assessments/interviews. Generated documents must be reviewed before use.

## External integrations\n\nSee [docs/EXTERNAL_INTEGRATIONS.md](docs/EXTERNAL_INTEGRATIONS.md) for Gmail OAuth setup, job-board search links, browser-assisted form preparation, and submission safety controls. The dashboard is available at `/integrations`.\n\n## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for completed milestones and remaining work. In particular, authenticated job-board integrations, actual application submission, Gmail, direct Google Calendar sync, audit logging, encrypted backup, and full end-to-end runtime verification remain release work.
