# CareerPilot Acceptance Test

Run this checklist on the target Windows machine after setup. Use a test profile and a non-sensitive sample resume until the repository is private and local storage has been reviewed.

## 1. Start the application

1. Run `scripts/setup-local.ps1`.
2. Run `scripts/start-local.ps1`.
3. Confirm the dashboard loads at `http://localhost:3000`.
4. Confirm the API docs load at `http://127.0.0.1:8000/docs`.

## 2. Candidate profile and resume

1. Open **Career profile**.
2. Enter verified candidate facts and save.
3. Upload a selectable-text PDF or DOCX under 10 MB.
4. Confirm extracted text length, detected skills, and contact hints.
5. Add only accurate detected skills to the profile form and save.
6. Delete a test resume and confirm it disappears from the list.

## 3. Job discovery

1. Open **Job discovery**.
2. Add a company board slug for one supported provider: Greenhouse, Lever, Ashby, or Workable.
3. Add a second board from another provider.
4. Scan all boards.
5. Confirm the scan reports fetched, saved, duplicate, and per-board error counts.
6. Repeat the scan and confirm previously saved source IDs are counted as duplicates.
7. Search saved jobs by title, company, or location.

## 4. Matching and applications

1. Calculate a match after saving the candidate profile.
2. Review the score, reasons, matched skills, missing skills, and any eligibility blockers.
3. Track a suitable job.
4. Update its status, notes, next action, and follow-up date.
5. Open the original job page and verify the posting is still live.
6. Generate a DOCX application pack and download it.
7. Review every generated statement before using it.

## 5. Optional local AI

1. Start Ollama and ensure the selected model is installed.
2. Set `AI_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://127.0.0.1:11434`, and `OLLAMA_MODEL` in the root `.env`.
3. Restart the backend.
4. Generate a local AI cover-letter draft.
5. Verify every claim. A model prompt is not a guarantee against hallucinations.

## 6. Interview and assessment scheduling

1. Create an interview event linked to a tracked application.
2. Set timezone, start/end time, meeting link, notes, and reminder preference.
3. Export the `.ics` file.
4. Import it into a calendar application and verify the event and reminder.

## 7. Daily job scan

1. Add at least one company board to the watchlist.
2. Run `scripts/scan-watchlist.ps1` manually.
3. Confirm the log exists under `$HOME\.careerpilot\logs`.
4. Optionally register a daily task with `scripts/register-daily-scan.ps1 -Time "09:00"`.

## 8. Release limitations to verify

- LinkedIn, Naukri, Indeed, Foundit, and Google Jobs are not connected.
- Automated application submission and browser form filling are not implemented.
- Gmail and direct Google Calendar OAuth are not implemented.
- Scanned-image PDF OCR is not implemented.
- The formal application state machine, audit trail, encrypted backup/restore, and full runtime acceptance are still release work.

Do not use a real application or submit anything during acceptance testing.
