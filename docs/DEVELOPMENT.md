# Local Development

## Prerequisites

- Windows 11
- Git
- Python 3.11+
- Node.js 22+
- npm

## Clone and configure

```powershell
git clone https://github.com/SRIRAMCJ/CareerPilot-AI.git
cd CareerPilot-AI
Copy-Item .env.example .env
```

Keep real candidate data, resumes, API keys, and browser profiles outside the repository. The local SQLite database is written under `apps/backend/data` when the backend is started from `apps/backend`; this directory is ignored by Git. You can override it with `CAREERPILOT_DATABASE_PATH`.

## One-command Windows setup

From the repository root, run:

```powershell
.\scripts\setup-local.ps1
.\scripts\start-local.ps1
```

The setup script creates the backend virtual environment, installs Python and npm dependencies, and copies `.env.example` to the root `.env` if it does not already exist. The launcher opens separate backend/frontend PowerShell windows and opens the dashboard. Stop each service by closing its terminal window or pressing Ctrl+C there.

## Start the backend

```powershell
cd apps/backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation is available at `http://127.0.0.1:8000/docs`.

## Start the frontend

Open a second PowerShell window:

```powershell
cd apps/frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend expects the API at `http://127.0.0.1:8000` by default. To override it, create `apps/frontend/.env.local` with:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The backend CORS origin defaults to `http://localhost:3000`.

## Current features

- Candidate profile CRUD in local SQLite.
- Manual job capture and job listing search.
- Public Greenhouse and Lever company-board discovery. See [JOB_SOURCES.md](JOB_SOURCES.md).
- Deterministic match scoring with skill overlap and preference reasons.
- Application tracking and status updates.
- External account automation and application submission remain disabled.

## Tests

```powershell
cd apps/backend
pytest -q
```

GitHub Actions runs backend tests and frontend checks on pushes and pull requests to the configured branches.

## Local data and security

- Do not put resumes, contact details, credentials, OAuth tokens, or browser profiles in Git.
- Keep the repository private before introducing personal candidate data into any tracked file.
- The API binds to loopback by default. Do not expose it to a public network without authentication and security review.
- Public job discovery uses fixed provider hosts and validated board slugs. Do not allow arbitrary fetch URLs.
- Review each original job listing before applying. Discovery does not submit applications.
