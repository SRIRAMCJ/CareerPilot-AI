# Development Roadmap

## Phase 1 — Foundation
- [x] Repository structure and engineering standards
- [x] FastAPI backend skeleton
- [x] Next.js frontend skeleton
- [x] Configuration and health endpoint
- [x] Automated backend/frontend CI (workflow configured; latest feature-run verification pending)
- [x] Local setup documentation

## Phase 2 — Candidate profile
- [x] Profile schema and CRUD API
- [x] Initial role, location, work-mode, and salary preferences
- [x] PDF/DOCX resume upload, parsing, local storage, and deletion
- [ ] Verified-fact provenance

## Phase 3 — Job discovery
- [x] Initial public-source adapter boundary
- [x] Greenhouse, Lever, Ashby, and Workable public board connectors
- [x] Initial listing normalization
- [x] Source ID duplicate detection
- [ ] Source access and terms review per adapter

## Phase 4 — Matching
- [ ] Hard eligibility checks
- [x] Initial explainable weighted scoring
- [ ] Search and filters
- [x] Match reason display

## Phase 5 — Application preparation
- [x] Per-application DOCX resume and cover-letter draft generation (profile-fact grounded; user review required)
- [x] Deterministic DOCX resume and cover-letter draft generation from verified profile facts
- [x] Generation restricted to saved candidate facts; user review required
- [ ] Application answer evidence mapping

## Phase 6 — Application workflow
- [ ] Explicit workflow state machine
- [ ] Authorized Playwright session support
- [ ] Per-platform permitted adapters
- [ ] Submission idempotency and confirmation evidence
- [ ] Review gates for sensitive declarations

## Phase 7 — Communication and scheduling
- [ ] Gmail OAuth with least privilege
- [ ] Recruiter email classification
- [ ] Draft replies
- [x] Local interview/assessment scheduler with timezone-aware ICS export
- [x] Local interview and assessment scheduler with timezone-aware ICS export
- [ ] Google Calendar OAuth
- [ ] Timezone-aware scheduling and conflict detection

## Phase 8 — Analytics and hardening
- [ ] Application funnel metrics
- [ ] Audit exports
- [ ] Backup and restore
- [ ] Security and recovery tests

## Release gates

Do not enable real application submission until profile verification, deduplication, safety gates, audit logging, and submission confirmation tests pass. Real external integration tests must use explicitly authorized accounts and must not submit applications without the user's configured permission.
