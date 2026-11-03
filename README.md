# CareerPilot AI

A local-first personal career workflow application for discovering opportunities, matching jobs to a verified candidate profile, preparing application materials, and tracking recruiter communication and interviews.

> **Current status:** Foundation initialization. Live job-source integrations, AI generation, application submission, Gmail, and Calendar are not enabled yet.

## Principles

- **Local-first:** candidate data, resumes, browser sessions, and databases remain on the user's machine.
- **Provider-independent:** start with deterministic Python logic; add optional cloud or local AI providers later.
- **Truthful applications:** generated claims must be supported by verified candidate-profile evidence.
- **Safe automation:** never bypass CAPTCHA, anti-bot protections, login restrictions, or rate limits.
- **Auditable:** persist important decisions, workflow transitions, and external actions.
- **Candidate-controlled:** the candidate personally completes interviews and identity-bound assessments.

## Planned stack

- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Alembic
- Frontend: Next.js, TypeScript
- Workflows: LangGraph when multi-step stateful workflows are introduced
- Browser: Playwright for permitted and authorized workflows only
- Database: PostgreSQL
- AI: optional provider abstraction; no model required for initial development

## Repository layout

```
apps/
  backend/
  frontend/
docs/
  ARCHITECTURE.md
  DEVELOPMENT.md
  ROADMAP.md
  SECURITY.md
.github/
  workflows/
```

## Development

Read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) and [docs/ROADMAP.md](docs/ROADMAP.md). The first milestone is a tested backend foundation and a minimal frontend shell. Use fixtures and mock data until integrations have been reviewed and authorized.

## Privacy

Never commit resumes, personal contact details, browser profiles, OAuth tokens, API keys, local database files, generated application documents, or real application evidence. Review `.gitignore` before adding files.

## Integration status

Every integration must be labeled **implemented**, **partial**, or **unavailable**. Do not represent mock integrations as live.


## Public job discovery

CareerPilot supports manual job capture plus public Greenhouse and Lever company-board discovery. See [docs/JOB_SOURCES.md](docs/JOB_SOURCES.md) for setup and limitations.

The discovery endpoint fetches public postings, normalizes the listing, saves it to local SQLite, and skips duplicate source IDs. It does not scrape authenticated job-board pages or submit applications.

### Local development

Install backend dependencies from `apps/backend` with `pip install -e ".[dev]"`. Start the API with `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`. Start the frontend from `apps/frontend` with `npm install` and `npm run dev`.
