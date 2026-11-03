from fastapi import APIRouter, HTTPException, Query, status

from app.core.database import read_profile
from app.core.jobs_database import create_job, get_job, list_jobs
from app.schemas.job import JobListingCreate
from app.schemas.profile import CandidateProfile
from app.services.matching import score_job

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_job(job: JobListingCreate) -> dict:
    try:
        return create_job(job)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("")
def get_jobs(
    search: str | None = Query(default=None, max_length=120),
    status_filter: str | None = Query(default=None, alias="status", max_length=40),
    limit: int = Query(default=50, ge=1, le=200),
) -> dict:
    return {"items": list_jobs(search=search, status_filter=status_filter, limit=limit)}


@router.get("/{job_id}")
def get_one_job(job_id: int) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.get("/{job_id}/match")
def match_one_job(job_id: int) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    stored = read_profile()
    if stored is None:
        raise HTTPException(status_code=409, detail="Create a candidate profile before matching jobs.")
    profile = CandidateProfile.model_validate(stored["profile"])
    return score_job(job, profile)
