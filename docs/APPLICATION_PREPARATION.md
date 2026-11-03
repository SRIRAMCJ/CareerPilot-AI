# Application Preparation

CareerPilot can generate a local DOCX application pack for a tracked job.

## What is generated

The DOCX contains:
- Candidate contact details and headline from the saved profile.
- Professional summary or a conservative template based on configured target roles and skills.
- Skills and tools from the profile.
- Experience, projects, education, and certifications entered by the candidate.
- A cover-letter draft addressed to the hiring team for the selected role and company.

## Factuality rules

The generator uses only the saved profile and tracked job title/company. It does not invent employers, dates, qualifications, metrics, achievements, or job-specific experience. It does not parse a resume and silently overwrite the candidate profile. Review every section and correct formatting before using the document.

The job board listing may have changed. Open the original job URL and verify the requirements before sending materials.

## API

- `POST /api/v1/applications/{application_id}/materials` — generate a DOCX pack.
- `GET /api/v1/applications/{application_id}/materials` — list generated packs.
- `GET /api/v1/materials/{material_id}/download` — download a pack.

Generated documents are stored under `~/.careerpilot/generated` by default. Set `CAREERPILOT_GENERATED_DIR` to change the local directory.

This feature prepares materials; it does not submit applications or send messages.
