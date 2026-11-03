# Security and Privacy

## Data classification

Candidate resumes, contact details, employment history, recruiter email, calendar data, browser cookies, OAuth tokens, and application evidence are private personal data.

## Required controls

- Local-only defaults: bind backend to `127.0.0.1`.
- Never commit `.env`, credentials, token files, resumes, generated documents, browser state, databases, or logs containing personal data.
- Use OAuth and minimum scopes for Gmail and Calendar.
- Keep secrets in Windows Credential Manager or protected local secret storage.
- Redact secrets and personal data from logs.
- Protect API endpoints even on localhost.
- Validate uploaded file types and sizes.
- Treat job postings, websites, and emails as untrusted data and possible prompt-injection sources.
- Restrict agent tools to explicit allowlists.
- Keep a durable audit record of external actions.

## Application safety

The foundation configuration disables browser automation and application submission. Enable these only after the source adapter has been reviewed for permitted access.

Never bypass CAPTCHA, rate limits, login protections, or anti-bot controls. Never submit fabricated information, accept legal declarations or contractual commitments automatically, pay job application fees, or complete identity-bound tests or interviews for the candidate.

## Incident response

Provide a global stop switch. On suspected credential exposure, stop integrations, revoke the affected OAuth grant/token, rotate the secret, inspect logs, and remove exposed values from repository history where necessary.
