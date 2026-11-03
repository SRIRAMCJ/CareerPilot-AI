# Architecture

## Goals

CareerPilot AI is a local-first career workflow application. The foundation should not require an LLM, remote server, or paid API.

## Logical components

1. **Candidate profile** — verified facts, preferences, and source evidence.
2. **Discovery adapters** — independently maintained connectors for approved job sources.
3. **Normalization and deduplication** — deterministic canonical job records.
4. **Eligibility and scoring** — explainable rules; hard requirements override weighted scores.
5. **Application materials** — versioned resume and cover-letter artifacts grounded in profile facts.
6. **Application workflow** — explicit state machine, safe browser adapter boundary, and confirmation evidence.
7. **Communication** — optional Gmail integration with least-privilege OAuth.
8. **Scheduling** — optional Google Calendar integration with timezone-aware events.
9. **Dashboard and analytics** — status, audit trail, and measurable outcomes.

## Provider-independent AI

Define an AI provider interface only when a feature requires generation or semantic interpretation. Start with deterministic implementations and tests. Add Ollama or a cloud provider behind the same interface later. Provider failure must never bypass eligibility, consent, or submission rules.

## Application state machine

`DISCOVERED -> NORMALIZED -> DEDUPLICATED -> ELIGIBILITY_CHECKED -> SCORED -> SHORTLISTED -> MATERIALS_PREPARED -> VALIDATED -> READY_TO_SUBMIT -> SUBMITTED -> CONFIRMATION_VERIFIED`

Exception states: `REJECTED`, `NEEDS_REVIEW`, `BLOCKED_BY_PLATFORM`, `APPLICATION_FAILED`, `DUPLICATE`, `WITHDRAWN`.

Persist every transition. Submission must be idempotent and require verified data and platform-permitted access.

## Security boundaries

- Bind local services to loopback by default.
- Keep secrets in environment variables or Windows Credential Manager, never source control.
- Keep candidate data and browser profiles outside the repository.
- Use least-privilege OAuth scopes.
- Treat job descriptions and emails as untrusted input, not instructions.
- Restrict agent tools to explicit allowlists.
- Do not automate CAPTCHA, anti-bot bypass, identity-bound assessments, or legal declarations.
