# Development Roadmap

## Phase 1 — Foundation
- [ ] Repository structure and engineering standards
- [ ] FastAPI backend skeleton
- [ ] Next.js frontend skeleton
- [ ] Configuration and health endpoint
- [ ] Automated backend/frontend CI
- [ ] Local setup documentation

## Phase 2 — Candidate profile
- [ ] Profile schema and CRUD API
- [ ] Preferences and eligibility rules
- [ ] Resume upload/parsing with local storage
- [ ] Verified-fact provenance

## Phase 3 — Job discovery
- [ ] Common source-adapter contract
- [ ] Company career-page discovery prototype
- [ ] Job normalization
- [ ] Duplicate detection
- [ ] Source access and terms review per adapter

## Phase 4 — Matching
- [ ] Hard eligibility checks
- [ ] Explainable weighted scoring
- [ ] Search and filters
- [ ] Match reason display

## Phase 5 — Application preparation
- [ ] Resume versioning
- [ ] Cover letter generation behind AI provider abstraction
- [ ] Factual claim validation
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
- [ ] Google Calendar OAuth
- [ ] Timezone-aware scheduling and conflict detection

## Phase 8 — Analytics and hardening
- [ ] Application funnel metrics
- [ ] Audit exports
- [ ] Backup and restore
- [ ] Security and recovery tests

## Release gates

Do not enable real application submission until profile verification, deduplication, safety gates, audit logging, and submission confirmation tests pass. Real external integration tests must use explicitly authorized accounts and must not submit applications without the user's configured permission.
