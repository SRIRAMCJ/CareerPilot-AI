from fastapi import APIRouter, HTTPException, Query, status

from app.core.applications_database import create_application, list_applications, update_application
from app.core.audit_database import record_event
from app.schemas.application import ApplicationCreate, ApplicationUpdate

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_application(item: ApplicationCreate) -> dict:
    try:
        created = create_application(item)
        record_event("application.created", "application", created["id"], {"job_id": created["job_id"], "status": created["status"]})
        return created
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("")
def get_applications(
    status_filter: str | None = Query(default=None, alias="status", max_length=40),
) -> dict:
    return {"items": list_applications(status_filter)}


@router.patch("/{application_id}")
def patch_application(application_id: int, item: ApplicationUpdate) -> dict:
    updated = update_application(application_id, item)
    if updated is None:
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    record_event("application.updated", "application", application_id, {"status": updated["status"], "updated_fields": list(item.model_fields_set)})
    return updated
