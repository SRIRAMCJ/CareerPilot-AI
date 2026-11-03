# Development Roadmap

## Phase 1 — Foundation
- [x] Repository structure and engineering standards
- [x] FastAPI backend skeleton
- [x] Next.js frontend skeleton
- [x] Configuration and health endpoint
- [x] Automated backend/frontend CI workflows (backend matrix, frontend lint and production build passing)
- [x] Local setup documentation

## Phase 2 — Candidate profile
- [x] Profile schema and CRUD API
- [x] Role, location, work-mode, salary, experience, education, project, and certification fields
- [x] PDF/DOCX resume upload, parsing, local storage, preview, and deletion
- [ ] Verified-fact provenance and source-to-profile evidence mapping

## Phase 3 — Job discovery
- [x] Public-source adapter boundary
- [x] Greenhouse, Lever, Ashby, and Workable public board connectors
- [x] Job listing normalization and keyword extraction
- [x] Source ID duplicate detection
- [x] Manual job capture and local title/company/location search
- [x] Persistent company-board watchlist and one-click multi-board scan
- [x] Optional Windows Task Scheduler daily scan script
- [ ] Broader employer-board catalog and adapter-specific access/terms review

## Phase 4 — Matching
- [x] Explainable weighted scoring
- [x] Role, location, work-mode, and salary eligibility blockers
- [x] Match reasons, matched skills, and missing-skill explanations
- [ ] Experience-level and seniority eligibility rules
- [ ] Advanced search filters and ranking controls

## Phase 5 — Application preparation
- [x] Per-application DOCX resume and cover-letter draft generation from saved profile facts
- [x] Factuality guardrails: no invented employers, dates, qualifications, metrics, or achievements
- [x] Candidate review before using generated materials
- [x] Optional loopback-only Ollama cover-letter drafting
- [ ] Resume tailoring based on full parsed source-resume sections
- [ ] Application answer evidence mapping

## Phase 6 — Application workflow
- [x] Application tracker with status, notes, next action, and follow-up date
- [x] Basic profile field filling in visible browser and a typed, disabled-by-default submit confirmation
- [x] Original job-page links and a ready-to-submit review status
- [x] Local audit event log for profile, discovery, job, application, resume, materials, and interview actions
- [x] Application status transition state machine with invalid-transition rejection
- [x] Atomic one-attempt-per-application submission lock and attempt status endpoint
- [x] Submission attempt audit events and unknown-outcome duplicate protection
- [ ] Tamper-evident audit trail and employer confirmation evidence
- [x] Visible local Playwright session support with a dedicated browser profile
- [ ] Per-platform permitted application adapters
- [ ] Human review gates for sensitive declarations

## Phase 7 — Communication and scheduling
- [x] Local interview and assessment scheduler
- [x] Timezone-aware events and ICS calendar export with reminder alarms
- [ ] Calendar conflict detection
- [ ] Google Calendar OAuth
- [x] Gmail OAuth with read, compose and send scopes (requires user credentials and consent)
- [x] Recruiter inbox search, threaded reply drafts, and explicit send action

## Phase 8 — Analytics and hardening
- [ ] Application funnel metrics
- [ ] Audit exports
- [ ] Encrypted backup and restore
- [ ] Security and recovery tests
- [ ] Full end-to-end local runtime verification

## Release gates

Real application submission must remain disabled until profile verification, deduplication, safety gates, audit logging, platform-permitted access, and submission confirmation tests pass. Never automate CAPTCHA bypass, legal declarations, fees, or identity-bound assessments/interviews. Real external integration tests must use explicitly authorized accounts and must not submit applications without the user's configured permission.
