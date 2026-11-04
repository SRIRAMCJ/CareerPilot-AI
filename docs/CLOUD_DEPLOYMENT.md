# Cloud deployment: Docker Compose VM alternative

This is the self-managed alternative to the recommended Vercel + Render deployment in [VERCEL_RENDER_DEPLOYMENT.md](VERCEL_RENDER_DEPLOYMENT.md). It runs the dashboard, backend, and remote MCP endpoint on one Docker-capable Linux VM. It does not require Python, Node.js, or Git on your Windows workstation.

## Production topology

```text
Browser
  | HTTPS + dashboard Basic Auth
  v
Caddy (automatic TLS, ports 80/443)
  |------------------------------|
  v                              v
Next.js dashboard                MCP Streamable HTTP
  | /api/* server proxy          | Bearer token required
  | shared proxy token           | shared API proxy token
  v                              v
Private FastAPI backend <--------|
  |
  +-- persistent SQLite database
  +-- resume and generated-document storage
```

The backend has no published host port. Only Caddy is exposed publicly. The dashboard requires a username/password, the backend personal-data API requires a separate shared proxy token, and the MCP endpoint independently requires a bearer token.

## VM and DNS requirements

- A Linux VM with Docker Engine and the Docker Compose plugin.
- Suggested starting size: 2 vCPU, 4 GB RAM, and at least 20 GB disk. Increase storage for resumes and generated documents.
- A domain or subdomain whose A record points to the VM's public IPv4 address.
- Inbound TCP ports 80 and 443 open in the VM firewall/security group. UDP 443 is optional for HTTP/3.
- Do not expose backend port 8000 or MCP port 8765 directly.

## Deploy

After the deployment changes are merged into `main`, run the following commands on the Linux VM:

```bash
git clone https://github.com/SRIRAMCJ/CareerPilot-AI.git
cd CareerPilot-AI
cp .env.production.example .env.production
chmod 600 .env.production
```

Edit `.env.production` and set your real domain and email. Generate three independent secrets:

```bash
openssl rand -hex 32
openssl rand -hex 32
openssl rand -hex 32
```

Use one for `DASHBOARD_PASSWORD`, one for `CAREERPILOT_PROXY_TOKEN`, and one for `CAREERPILOT_MCP_AUTH_TOKEN`. Do not reuse values. The proxy token must be the same in the frontend, backend, and MCP services (Compose wires this automatically). Keep `.env.production` off Git and out of screenshots.

Start the stack:

```bash
docker compose --env-file .env.production up -d --build
docker compose ps
docker compose logs -f backend frontend mcp caddy
```

Caddy obtains and renews the TLS certificate automatically once DNS resolves and ports 80/443 are reachable.

## URLs and client connection

- Dashboard: `https://YOUR_DOMAIN/` — browser prompts for the dashboard username/password.
- MCP endpoint: `https://YOUR_DOMAIN/mcp` — Streamable HTTP, with `Authorization: Bearer YOUR_MCP_TOKEN`.
- API: private Docker network only; do not publish it.

In an MCP client that supports remote Streamable HTTP servers, add the MCP endpoint URL and configure the bearer token as its Authorization header. Never paste the token into a prompt or public repository.

## Gmail OAuth (optional)

1. Configure the Google OAuth client with the exact redirect URI `https://YOUR_DOMAIN/api/v1/gmail/auth/callback`.
2. Set `GMAIL_ENABLED=true`, `GMAIL_CLIENT_ID`, and `GMAIL_CLIENT_SECRET` in `.env.production`.
3. Recreate the backend container: `docker compose --env-file .env.production up -d --force-recreate backend`.
4. Complete the OAuth flow from the protected dashboard.

The OAuth token file is stored on the persistent data volume. The callback is exempt from dashboard Basic Auth so Google can return the user, but the backend proxy token and one-time OAuth state are still validated.

## Operations and backups

- Update: `git pull && docker compose --env-file .env.production up -d --build`.
- Inspect: `docker compose --env-file .env.production ps` and `docker compose --env-file .env.production logs -f`.
- Back up: use SQLite's online backup mechanism and back up the `careerpilot_data` Docker volume. Back up Caddy's `caddy_data` volume to preserve certificate state.
- Rotate all three secrets by updating `.env.production` and recreating the affected services.
- Keep the VM patched and restrict SSH to trusted IPs.

## Current product scope and limitations

- This is a **single-user deployment**, matching the current profile and SQLite data model. It is not a multi-tenant SaaS.
- Keep one backend replica and one persistent data volume. Do not put SQLite on an arbitrary network filesystem or scale multiple API replicas.
- Browser-assisted application submission remains disabled. Gmail sending and external job applications still require explicit human approval in the dashboard.
- MCP does not expose email sending, job submission, arbitrary URL fetching, or account deletion.
- Job descriptions and recruiter email contents are untrusted data. Review generated resume and cover-letter claims before use.
