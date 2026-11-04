# Vercel + Render deployment

This is the recommended single-user production deployment for CareerPilot AI.

## Architecture

- **Vercel:** Next.js dashboard and authenticated server-side API proxy.
- **Render:** FastAPI backend and authenticated remote Streamable HTTP MCP service.
- **Render persistent disk:** SQLite database, uploaded resumes, generated DOCX files, and Gmail OAuth token.
- **Domain:** Not required initially. Use the generated `.vercel.app` and `.onrender.com` hostnames.

The initial deployment deliberately keeps SQLite and local file storage. The backend is one instance with one persistent disk. Do not scale it horizontally or remove the disk. This avoids an unnecessary PostgreSQL/object-storage migration for a single-user installation. Render persistent disks are available on paid services, preserve only data written under the mount path, and are attached to one instance: https://render.com/docs/disks.

## 1. Repository preparation

1. Merge the deployment pull request into `main` after reviewing it.
2. Confirm the repository contains `render.yaml`.
3. Keep this repository private before putting real candidate data or credentials into the deployed application. Never commit secrets, resumes, OAuth token files, or a production database.

## 2. Deploy the backend and MCP on Render

1. Create a Render account at https://render.com/ and connect GitHub.
2. In Render, choose **New → Blueprint** and select `SRIRAMCJ/CareerPilot-AI`.
3. Select the `main` branch and confirm the Blueprint from `render.yaml`.
4. Render creates two services: `careerpilot-api` and `careerpilot-mcp`, both in Singapore. The API receives a 10 GB persistent disk mounted at `/var/data`.
5. The Blueprint marks secrets as unsynced values. Generate two independent random values on Windows PowerShell:

   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

6. Set `CAREERPILOT_PROXY_TOKEN` to the **same first value** on both Render services.
7. Set `CAREERPILOT_MCP_AUTH_TOKEN` on the MCP service to the **second value**.
8. Deploy both services. Wait for the API health check to pass.

The API accepts application requests only when the proxy token is correct. The health endpoint is intentionally exempt so Render can monitor service health. MCP-to-API traffic uses Render's private network.

## 3. Deploy the dashboard on Vercel

1. Create/sign in to https://vercel.com/ and import `SRIRAMCJ/CareerPilot-AI`.
2. Set **Root Directory** to `apps/frontend`.
3. Framework preset: **Next.js**. Build command: `npm run build`. Install command: `npm install`.
4. Add these Production environment variables:

   | Key | Value |
   |---|---|
   | `CAREERPILOT_API_URL` | `https://careerpilot-api.onrender.com` (use the actual Render API URL) |
   | `CAREERPILOT_PROXY_TOKEN` | The same first value used on both Render services |
   | `DASHBOARD_USERNAME` | Your chosen dashboard username |
   | `DASHBOARD_PASSWORD` | A strong, unique dashboard password |

5. Do not set `NEXT_PUBLIC_API_BASE_URL`. API calls must remain same-origin and pass through the server-side proxy. Do not expose the proxy token as a `NEXT_PUBLIC_` variable.
6. Deploy. Open the generated Vercel URL and confirm the Basic Auth prompt appears.

The OAuth callback path `/api/v1/gmail/auth/callback` is exempt from dashboard Basic Auth so Google can return the user to the app. The backend proxy token and one-time OAuth state still protect the callback.

## 4. Verify the services

- Dashboard: `https://YOUR-PROJECT.vercel.app`
- Backend health: `https://careerpilot-api.onrender.com/api/v1/health` (health only; other API routes require the proxy token)
- MCP endpoint: `https://careerpilot-mcp.onrender.com/mcp`

Test dashboard login, profile save/load, job discovery, resume upload/list/delete (4 MB hosted upload limit), DOCX generation/download, application tracking, and interviews. Test MCP with a remote Streamable HTTP client using the MCP URL and `Authorization: Bearer <CAREERPILOT_MCP_AUTH_TOKEN>`.

## 5. Gmail OAuth (optional)

After Vercel gives you its production hostname:

1. In Render API environment variables, set `GMAIL_ENABLED=true`, `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, and `GMAIL_REDIRECT_URI=https://YOUR-PROJECT.vercel.app/api/v1/gmail/auth/callback`.
2. In Google Cloud Console, add that exact URL as an authorized redirect URI for the OAuth web client.
3. Redeploy the backend, then connect Gmail from the dashboard.

The Gmail OAuth token is written to `/var/data/gmail-token.json` on the persistent disk. The OAuth callback route is public at the frontend edge but is still forwarded with the private backend proxy token and validated OAuth state.

## 6. Operational constraints

- Keep the API at one instance while it uses the attached SQLite disk. Render disks cannot be shared across multiple instances.
- Back up the Render disk and test restore procedures. A disk snapshot is not a substitute for an independent backup.
- Keep browser automation and application submission disabled unless deliberately enabled after review. CAPTCHA, OTP, login restrictions, and legal declarations must never be bypassed.
- Gmail send and job application submission remain explicit user-approved actions.
- The MCP server has its own bearer token; do not reuse the dashboard password.
- Render service URLs and service plans may differ from the examples. Use the actual generated hostnames shown in the Render dashboard.
- Custom domains and DNS are optional and can be configured later.

## Why Neon and R2 are deferred

The current backend uses one SQLite database and writes resume/generated files to local directories. A Render persistent disk preserves those paths with minimal code changes. Neon PostgreSQL and Cloudflare R2 become useful when moving to multi-user operation, multiple backend instances, or larger file-storage requirements. That migration should include schema migration tooling, data export/import, storage lifecycle rules, and backup/restore tests rather than simply changing environment variables.
