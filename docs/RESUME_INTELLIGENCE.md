# Resume Intelligence

## Supported files

- PDF with selectable text.
- DOCX.
- Maximum upload size: 10 MB.
- PDF extraction is limited to the first 40 pages and 150,000 characters.
- Scanned-image PDFs are not OCR'd in this version.

## Local storage

Uploaded files are saved outside the repository under `~/.careerpilot/resumes` by default. Set `CAREERPILOT_RESUME_DIR` to choose another local directory. Extracted text and file metadata are stored in the local SQLite database. Both locations contain sensitive personal information and should be protected by the operating-system account and encrypted device storage.

## API

- `POST /api/v1/resumes` — upload and parse a PDF/DOCX.
- `GET /api/v1/resumes` — list local resume metadata.
- `GET /api/v1/resumes/{id}/preview` — view extracted text and detected contact/skill hints.
- `DELETE /api/v1/resumes/{id}` — delete the local file and its extracted database record.

## Fact review

Skill, email, and phone extraction is heuristic. It is a suggestion, not a verified profile update. The dashboard allows detected skills to be copied into the profile form, but the user must review and save them. It does not infer job titles, dates, seniority, degrees, or employment history.

Never use a parsed resume as proof that an extracted fact is correct without candidate review. Resume contents are private and must never be committed to Git.
