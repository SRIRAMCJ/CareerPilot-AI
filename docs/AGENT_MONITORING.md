# CareerPilot Agent monitoring and verification

## Job description quality check

Call `GET /api/v1/jobs/{job_id}/verify` after discovery and before matching or preparing an application. The endpoint checks required metadata, description length, HTTPS URL hygiene, provider identifiers and posted-date freshness. It records an audit event and returns missing fields and warnings.

A result of `ready_for_candidate_review` means the listing has sufficiently complete metadata for human review. It is **not** proof that the employer is legitimate, that the role is still open, or that the source page matches the stored text. Always open the original employer listing before preparing or submitting an application.

## Gmail recruiter triage

After Gmail OAuth is connected, call `GET /api/v1/gmail/triage?q=newer_than:2d&max_results=50`. It classifies message metadata/snippets into interview, assessment, offer, rejection, application update, recruiter contact or other. It attempts a conservative match against tracked company/job names. Classification is heuristic; open the original message before relying on dates, links or instructions.

## Recurring Windows monitoring

With CareerPilot running and Gmail connected, register a 30-minute local poll:

```powershell
.\scripts\register-gmail-monitor.ps1 -IntervalMinutes 30
```

The task runs under the current Windows account and appends triage results to `$HOME\.careerpilot\logs\gmail-triage.jsonl`. It does not send replies or create calendar events. Remove it with:

```powershell
Unregister-ScheduledTask -TaskName "CareerPilot-Gmail-Monitor" -Confirm:$false
```

The local task only runs while Windows can execute scheduled tasks and the CareerPilot API is available. Gmail OAuth credentials and tokens stay outside the repository.
