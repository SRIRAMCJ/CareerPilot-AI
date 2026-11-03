# Public Job Source Connectors

CareerPilot currently supports public company job boards from Greenhouse, Lever, Ashby, and Workable.

## Greenhouse

1. Open the company's public Greenhouse job board.
2. Copy the board token/slug from the board URL.
3. Select **Greenhouse** in CareerPilot.
4. Enter the slug only (for example, `example-company`), not the full URL.

The backend requests the public endpoint:
`https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true`

## Ashby

1. Open the company's public Ashby job board.
2. Copy the board name from the URL after `jobs.ashbyhq.com/`.
3. Select **Ashby** in CareerPilot and enter that board name.

The backend requests the documented public posting endpoint:
`https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true`

Only listed postings are imported. The adapter normalizes workplace type, location, employment type, job URL, and publication date when present. Compensation is not yet parsed into numeric salary fields.

## Workable

1. Open the company's public Workable career page, usually under `apply.workable.com/{slug}`.
2. Copy the account slug from the URL.
3. Select **Workable** in CareerPilot and enter that slug.

CareerPilot requests Workable's documented public jobs endpoint at:
`https://www.workable.com/api/accounts/{slug}?details=true`

This public endpoint returns published jobs. The adapter normalizes company name, title, location, workplace type, employment type, date, description, and application URL when present. Workable's authenticated SPI API is not used and no API token is required for this public feed.

## Lever

1. Open the company's public Lever postings page.
2. Copy the site slug from the URL.
3. Select **Lever** in CareerPilot.
4. Enter the slug only.

The backend requests:
`https://api.lever.co/v0/postings/{slug}?mode=json`

## Current behavior

- Fetches a bounded set of public postings (maximum 100 per request).
- Normalizes title, company slug, location, work mode, source ID, URL, description, and a basic keyword-based skills list.
- Saves records to the local SQLite database.
- Uses source + source job ID to avoid duplicate records.
- Supports an optional keyword filter after fetching.
- Does not require a job-board account or candidate credentials.

## Limitations and safety

- These connectors do not cover every employer or job platform.
- LinkedIn, Naukri, Indeed, Foundit, and Google Jobs are not connected. CareerPilot will not scrape authenticated pages, bypass CAPTCHAs, defeat rate limits, or evade access controls.
- Company name is currently inferred from the board slug. Verify it when preparing applications.
- Extracted skills are keyword hints, not a complete or authoritative requirements analysis.
- A public listing may change or disappear; verify the original posting before applying.
- Fetch requests use fixed HTTPS provider hosts and validated board slugs. Do not change this to accept arbitrary URLs; that would introduce server-side request forgery risk.
- Discovery only saves opportunities. It never applies for a job or contacts an employer.
