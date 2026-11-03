from app.schemas.profile import CandidateProfile


def score_job(job: dict, profile: CandidateProfile) -> dict:
    """Return an explainable fit score and explicit preference blockers."""
    reasons: list[str] = []
    blocking_reasons: list[str] = []
    score = 0

    candidate_roles = [item.casefold() for item in profile.target_roles]
    title = str(job.get("title", "")).casefold()
    if candidate_roles and any(role in title or title in role for role in candidate_roles):
        score += 30
        reasons.append("Job title aligns with a target role")
    elif not candidate_roles:
        reasons.append("Target roles are not configured")
    else:
        reasons.append("Job title does not directly match a target role")

    candidate_locations = [item.casefold() for item in profile.preferred_locations]
    job_location = str(job.get("location") or "").casefold()
    mode = str(job.get("work_mode") or "").casefold()
    if candidate_locations:
        if any(location in job_location or job_location in location for location in candidate_locations):
            score += 20
            reasons.append("Location matches a preferred location")
        elif job_location:
            reasons.append("Location is outside the configured preferences")
            if mode != "remote":
                blocking_reasons.append("Location is outside configured preferences")
    elif job_location and profile.location and profile.location.casefold() in job_location:
        score += 10
        reasons.append("Job location matches the candidate's current location")

    candidate_modes = {item.casefold() for item in profile.preferred_work_modes}
    if candidate_modes:
        if mode and mode in candidate_modes:
            score += 15
            reasons.append("Work mode matches preference")
        elif mode:
            reasons.append("Work mode differs from preference")
            blocking_reasons.append("Work mode does not match configured preferences")

    candidate_skills = {
        item.strip().casefold()
        for item in [*profile.skills, *profile.tools_and_technologies]
        if item.strip()
    }
    required = {item.strip().casefold() for item in job.get("required_skills", []) if item.strip()}
    matched = sorted(candidate_skills & required)
    missing = sorted(required - candidate_skills)
    if required:
        score += round(35 * len(matched) / len(required))
        reasons.append(f"Matches {len(matched)} of {len(required)} listed required skills")
    else:
        reasons.append("No structured required skills were provided")

    minimum = profile.minimum_salary
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    if minimum is not None and salary_max is not None and salary_max < minimum:
        score = max(0, score - 20)
        reasons.append("Published salary ceiling is below the candidate's minimum")
        blocking_reasons.append("Published salary ceiling is below configured minimum")
    elif minimum is not None and salary_min is not None and salary_min >= minimum:
        reasons.append("Published salary range meets the candidate's minimum")

    return {
        "job_id": job["id"],
        "score": min(100, max(0, score)),
        "decision": (
            "not_eligible" if blocking_reasons
            else "strong_match" if score >= 70
            else "review" if score >= 40
            else "low_match"
        ),
        "eligible": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "matched_skills": matched,
        "missing_skills": missing,
        "reasons": reasons,
    }
