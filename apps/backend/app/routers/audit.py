from fastapi import APIRouter, Query

from app.core.audit_database import list_events

router = APIRouter(prefix="/api/v1/audit", tags=["audit log"])


@router.get("/events")
def get_audit_events(limit: int = Query(default=100, ge=1, le=500)) -> dict:
    return {"items": list_events(limit)}
