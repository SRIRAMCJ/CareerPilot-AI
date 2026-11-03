# Local Audit Activity

CareerPilot records a local audit event when key workflow actions occur.

## Recorded actions

- Candidate profile saved or deleted (field names only; values are not logged).
- Job listing saved.
- Company board added/removed and watchlist scans completed.
- Application created or updated (status and changed field names only; notes are not logged).
- Resume uploaded/deleted (file type, size, extracted text length; filename and content are not logged).
- Application pack or local AI cover-letter draft generated (material type/provider/model).
- Interview event created, updated, or deleted (event type and start time on creation; meeting URL and notes are not logged).

## API

`GET /api/v1/audit/events?limit=100`

The endpoint returns the newest events first, with a maximum page size of 500. The dashboard's **Activity log** displays the latest 100 entries.

The audit database is stored with the local SQLite data. It is not an immutable or tamper-proof audit system, and it is not a substitute for external-action confirmation evidence. Formal workflow transition history, signed audit exports, and retention controls remain future hardening work.
