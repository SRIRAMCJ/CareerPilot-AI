# Local Development

## Prerequisites

- Windows 11
- Git
- Python 3.10+
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
py -3.10 -m venv .venv
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

- Candidate profile CRUD in local SQLite, including skills, experience, education, projects, and preferences.
- PDF/DOCX resume import, text extraction, skill/contact hints, preview, and local deletion.
- Public Greenhouse, Lever, Ashby, and Workable company-board discovery.
- Persistent company-board watchlist and one-click multi-board scan.
- Manual job capture, local search, duplicate detection, and explainable match scoring with eligibility blockers.
- Application tracker with status, notes, next actions, and follow-up dates.
- Per-application DOCX resume and cover-letter draft generation from saved profile facts.
- Interview and assessment scheduling with timezone-aware ICS export and reminder alarms.
- Automated application submission, Gmail, and direct Google Calendar OAuth remain disabled/unimplemented.

## Optional daily job scan

After adding company boards in the Job Discovery watchlist, you can run a scan manually:

```powershell
.\scripts\scan-watchlist.ps1
```

To register a Windows Task Scheduler job (default 9:00 AM local time):

```powershell
.\scripts\register-daily-scan.ps1 -Time "09:00"
```

The scheduled task starts the local API, scans saved public boards, records results under `$HOME\.careerpilot\logs\watchlist-scan.log`, and stops the API it started. It runs while your Windows account is logged in. Remove it with:

```powershell
Unregister-ScheduledTask -TaskName "CareerPilot-Daily-Job-Scan" -Confirm:$false
```

This automation only discovers and saves job listings. It never submits applications or sends messages.

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
