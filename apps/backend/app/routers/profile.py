from fastapi import APIRouter, HTTPException, status

from app.core.audit_database import record_event
from app.core.database import delete_profile, read_profile, save_profile
from app.schemas.profile import CandidateProfile

router = APIRouter(prefix="/api/v1/profile", tags=["candidate profile"])


@router.get("")
def get_candidate_profile() -> dict | None:
    """Return the locally stored candidate profile, or null when not configured."""
    return read_profile()


@router.put("", status_code=status.HTTP_200_OK)
def put_candidate_profile(profile: CandidateProfile) -> dict:
    """Create or replace the single local candidate profile."""
    saved = save_profile(profile)
    record_event("profile.saved", "candidate_profile", 1, {"fields": list(profile.model_fields_set)})
    return saved


@router.delete("", status_code=status.HTTP_200_OK)
def remove_candidate_profile() -> dict[str, str]:
    """Delete locally stored profile data. This does not delete resume files."""
    if not delete_profile():
        raise HTTPException(status_code=404, detail="No candidate profile exists.")
    record_event("profile.deleted", "candidate_profile", 1)
    return {"status": "deleted"}
