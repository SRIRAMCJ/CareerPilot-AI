from datetime import date, datetime, timezone
from urllib.parse import urlparse


def verify_job_description(job: dict) -> dict:
    """Check JD completeness and source-link hygiene; never claim employer authenticity."""
    checks = {
        "title": bool(str(job.get("title") or "").strip()),
        "company": bool(str(job.get("company") or "").strip()),
        "location": bool(str(job.get("location") or "").strip()),
        "description": len(str(job.get("description") or "").strip()) >= 500,
        "source": bool(str(job.get("source") or "").strip()),
        "source_job_id": bool(str(job.get("source_job_id") or "").strip()),
        "posted_date": bool(job.get("posted_date")),
        "application_url": False,
    }
    url = str(job.get("url") or "").strip()
    if url:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        checks["application_url"] = (
            parsed.scheme == "https" and bool(host)
            and host not in {"localhost", "127.0.0.1", "::1"}
            and not host.endswith(".localhost")
        )
    score = round(sum(checks.values()) / len(checks) * 100)
    missing = [key for key, passed in checks.items() if not passed]
    warnings: list[str] = []
    posted = job.get("posted_date")
    age_days = None
    if posted:
        try:
            posted_day = date.fromisoformat(str(posted)[:10])
            age_days = (datetime.now(timezone.utc).date() - posted_day).days
            if age_days < 0:
                warnings.append("Posted date is in the future; verify the source listing.")
            elif age_days > 45:
                warnings.append(f"Listing is {age_days} days old; confirm it is still open.")
        except ValueError:
            warnings.append("Posted date could not be parsed.")
    else:
        warnings.append("Posted date is unavailable; freshness cannot be assessed.")
    if not checks["description"]:
        warnings.append("Full job description is missing or too short for reliable eligibility analysis.")
    if not checks["application_url"]:
        warnings.append("A valid HTTPS application/source URL is missing.")
    if not checks["source_job_id"]:
        warnings.append("No provider job ID is available for strong duplicate tracking.")
    status = "ready_for_candidate_review" if score >= 75 and checks["description"] and checks["application_url"] else "needs_verification"
    return {
        "job_id": job.get("id"), "status": status, "completeness_score": score,
        "checks": checks, "missing_fields": missing, "warnings": warnings,
        "posted_age_days": age_days, "source_url": url or None,
        "verification_scope": "Metadata, JD completeness, URL scheme and freshness checks only. This does not authenticate the employer or confirm that the vacancy remains open.",
        "candidate_review_required": True,
    }
