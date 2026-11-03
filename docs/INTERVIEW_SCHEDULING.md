# Interview and Assessment Scheduling

CareerPilot supports a local event planner for interviews, recruiter calls, technical rounds, and assessments.

## Features

- Link each event to a tracked application.
- Store timezone-aware start and end times.
- Store an optional meeting URL and preparation notes.
- Choose an IANA timezone.
- Export an event as an `.ics` calendar file for import into Google Calendar, Outlook, Apple Calendar, or another calendar client.
- Edit and delete scheduled events.

The stored reminder preference is metadata only in this release; it does not run a background notification service. Calendar OAuth and automatic event creation are future integrations.

## API

- `POST /api/v1/interviews`
- `GET /api/v1/interviews`
- `PATCH /api/v1/interviews/{id}`
- `DELETE /api/v1/interviews/{id}`
- `GET /api/v1/interviews/{id}/calendar.ics`

Use ISO 8601 timestamps with offsets. The browser dashboard converts local date/time inputs to offset-aware UTC timestamps and records the browser's IANA timezone.

The user must attend interviews and complete identity-bound assessments personally. CareerPilot only organizes events and preparation notes.
