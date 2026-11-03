# Local Development

## Prerequisites

- Windows 11
- Git
- Python 3.11+
- Node.js 22+
- npm
- Optional Docker Desktop for PostgreSQL in a later phase

## Clone the repository

```powershell
git clone https://github.com/SRIRAMCJ/CareerPilot-AI.git
cd CareerPilot-AI
Copy-Item .env.example .env
```

Review local values in `.env`. Never commit it.

## Engineering workflow

1. Create a feature branch from `main`.
2. Implement one milestone at a time.
3. Add tests with each feature.
4. Run formatters, linters, type checks, and tests.
5. Open a pull request with implementation notes and test results.
6. Do not merge failing CI.

## Local data

The runtime data directory is intentionally ignored by Git. Back up private data locally using an encrypted backup destination.

## Current implementation status

The initial commit establishes product principles, architecture, roadmap, and repository hygiene. Backend and frontend commands will be documented when their skeletons are added.
