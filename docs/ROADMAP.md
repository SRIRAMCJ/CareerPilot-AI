# Development Roadmap

## Phase 1 — Foundation
- [x] Repository structure and engineering standards
- [x] FastAPI backend skeleton
- [x] Next.js frontend skeleton
- [x] Configuration and health endpoint
- [x] Automated backend/frontend CI workflows
- [x] Local setup documentation

## Phase 2 — Candidate profile
- [x] Profile schema and CRUD API
- [x] Role, location, work-mode, salary, experience, education, project, and certification fields
- [x] PDF/DOCX resume upload, parsing, local storage, preview, and deletion
- [ ] Verified-fact provenance and source-to-profile evidence mapping

## Phase 3 — Job discovery and verification
- [x] Public-source adapter boundary and Greenhouse, Lever, Ashby, Workable connectors
- [x] Persistent company-board watchlist and daily scan script
- [x] Manual job capture, duplicate detection, and local search
- [x] JD completeness, HTTPS URL hygiene, provider-ID and freshness quality check
- [ ] Live source re-fetch and comparison against the original employer page
- [ ] Broader employer-board catalog and adapter-specific terms review

## Phase 4 — Matching
- [x] Explainable weighted scoring and preference blockers
- [ ] Experience-level and seniority eligibility rules
- [ ] Semantic matching, advanced filters and ranking controls

## Phase 5 — Application preparation
- [x] Per-application DOCX resume and cover-letter draft generation
- [x] Factuality guardrails and candidate review
- [ ] Resume tailoring from parsed source sections
- [ ] Application answer evidence mapping and missing-field queue

## Phase 6 — Application workflow
- [x] Application tracker and status transition state machine
- [x] Visible browser-assisted safe-field form filling
- [x] Atomic one-attempt-per-application submission lock
- [x] Latest saved PDF/DOCX resume attached to a clearly labelled resume/CV input during browser preparation
- [ ] Platform-specific permitted application adapters
- [ ] Employer confirmation evidence and explicit approval queue UI
- [ ] Manual recovery for abandoned or unknown submission attempts

## Phase 7 — Communication and scheduling
- [x] Gmail OAuth, inbox search, threaded reply drafts and explicit send
- [x] Heuristic recruiter/interview/assessment/offer/rejection triage
- [x] Optional Windows Task Scheduler Gmail polling and local JSONL log
- [x] Interview and assessment scheduler with ICS export
- [ ] Persistent message deduplication and recruiter CRM
- [ ] Calendar conflict detection and direct Google Calendar OAuth
- [ ] Parse confirmed invitation details into a reviewable event draft

## Phase 8 — Autonomous orchestration and hardening
- [x] Local MCP server exposing scoped CareerPilot tools over stdio and optional Streamable HTTP
- [x] MCP client setup documentation and Windows installation script
- [ ] Unified agent planner, persistent task queue and approval checkpoints
- [ ] End-to-end daily workflow and notifications
- [ ] Application funnel analytics and audit exports
- [ ] Encrypted backup, restore and security/recovery tests
- [ ] Full end-to-end local runtime verification

## Release gates

Application submission and recruiter email sending remain explicit user-approved actions. Never bypass CAPTCHA, OTP, access restrictions, legal declarations, fees, or identity-bound assessments/interviews. A job quality score is not employer authentication. Verify the original listing and review all generated materials before external use.
