# External job boards, browser assistance and Gmail

## Job-board search

CareerPilot creates user-facing searches for LinkedIn, Naukri, Indeed India and Foundit at:

- `GET /api/v1/integrations/job-boards?query=AI%20Engineer&location=Chennai`

The links open each provider's own website and use the user's own browser session. CareerPilot does not claim a public partner API for these consumer sites and does not scrape private pages or defeat login, CAPTCHA, bot checks or rate limits. Greenhouse, Lever, Ashby and Workable public company boards remain available through the existing discovery watchlist.

## Browser-assisted application workflow

Optional dependencies:

```powershell
cd apps/backend
pip install -e ".[browser]"
playwright install chromium
```

Configure local `.env`:

```dotenv
BROWSER_AUTOMATION_ENABLED=true
APPLICATION_SUBMISSION_ENABLED=false
# BROWSER_PROFILE_DIR=C:/Users/YourName/AppData/Local/CareerPilot/browser-profile
```

The dashboard route is `/integrations`. Enter a tracked application ID and choose **Open page and fill safe fields**. CareerPilot opens a visible persistent Chromium profile and fills only basic verified fields (name, email, phone, location, headline and summary). Review every field, upload the correct resume, and complete all declarations manually.

Submission is a separate, disabled-by-default action. After reviewing the live page, enable `APPLICATION_SUBMISSION_ENABLED=true` and type `SUBMIT APPLICATION` into the confirmation prompt. CareerPilot clicks only an unambiguous enabled button named Submit, Submit application, or Send application. It does not solve CAPTCHA, enter passwords/OTPs, answer identity/legal declarations, complete assessments, or claim that a click means the website accepted the application. Verify the result on the employer's website and update the tracker yourself.

This browser feature is best-effort across changing websites. Some providers may prohibit automation or require an official partner integration; respect each site's terms and stop if the site blocks automation.

## Gmail recruiter communication

1. Create a Google Cloud project and enable the Gmail API.
2. Configure the OAuth consent screen for personal use/testing and create a **Web application** OAuth client.
3. Add this exact authorized redirect URI: `http://127.0.0.1:8000/api/v1/gmail/auth/callback`.
4. Copy the client ID and secret into your private local `.env`:

```dotenv
GMAIL_ENABLED=true
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REDIRECT_URI=http://127.0.0.1:8000/api/v1/gmail/auth/callback
```

5. Restart the backend, open `/integrations`, and choose **Connect Gmail**. Approve the requested Gmail read, compose and send scopes.
6. Search recruiter messages using Gmail query syntax, prepare a reply, save it as a Gmail draft, or explicitly confirm sending.

OAuth token JSON is stored outside the repository under `~/.careerpilot/gmail-token.json` by default. Do not commit it or share it. Revoke access from your Google Account security settings when no longer needed. Gmail OAuth may require consent-screen configuration and, for public distribution, Google verification for the requested scopes.

## API endpoints

- `GET /api/v1/gmail/status`
- `POST /api/v1/gmail/auth/start`
- `GET /api/v1/gmail/auth/callback` (Google redirect)
- `GET /api/v1/gmail/messages?q=...`
- `POST /api/v1/gmail/drafts`
- `POST /api/v1/gmail/send`
- `POST /api/v1/browser/applications/{id}/prepare`
- `POST /api/v1/browser/applications/{id}/submit`

Gmail sending and application submission are explicit external actions. Use the UI confirmation checkpoints and review the final content before proceeding.
