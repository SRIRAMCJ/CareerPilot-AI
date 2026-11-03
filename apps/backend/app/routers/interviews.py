from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Response, status

from app.core.audit_database import record_event
from app.core.interviews_database import (
    create_interview, delete_interview, get_interview, list_interviews, update_interview,
)
from app.schemas.interview import InterviewCreate, InterviewUpdate

router = APIRouter(prefix="/api/v1/interviews", tags=["interview scheduling"])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_interview(item: InterviewCreate) -> dict:
    try:
        created = create_interview(item)
        record_event("interview.created", "interview", created["id"], {"application_id": created["application_id"], "event_type": created["event_type"], "starts_at": created["starts_at"]})
        return created
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("")
def get_interviews() -> dict:
    return {"items": list_interviews()}


@router.patch("/{event_id}")
def patch_interview(event_id: int, item: InterviewUpdate) -> dict:
    try:
        updated = update_interview(event_id, item)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if updated is None:
        raise HTTPException(status_code=404, detail="Interview event not found.")
    record_event("interview.updated", "interview", event_id, {"updated_fields": list(item.model_fields_set)})
    return updated


@router.delete("/{event_id}")
def remove_interview(event_id: int) -> dict:
    if not delete_interview(event_id):
        raise HTTPException(status_code=404, detail="Interview event not found.")
    record_event("interview.deleted", "interview", event_id)
    return {"status": "deleted", "id": event_id}


def _ics_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


@router.get("/{event_id}/calendar.ics")
def export_calendar_event(event_id: int) -> Response:
    event = get_interview(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Interview event not found.")
    start = datetime.fromisoformat(event["starts_at"].replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    end = datetime.fromisoformat(event["ends_at"].replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    description = _ics_escape(event["notes"] or f"{event['event_type']} for {event['job_title']} at {event['company']}")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CareerPilot AI//Interview Planner//EN",
        "CALSCALE:GREGORIAN", "BEGIN:VEVENT", f"UID:careerpilot-{event_id}@local",
        f"DTSTAMP:{stamp}", f"DTSTART:{start}", f"DTEND:{end}",
        f"SUMMARY:{_ics_escape(event['title'])}",
        f"DESCRIPTION:{description}",
        f"LOCATION:{_ics_escape(event['company'])}",
    ]
    if event["meeting_url"]:
        lines.append(f"URL:{event['meeting_url']}")
    if event["reminder_minutes"] > 0:
        lines.extend([
            "BEGIN:VALARM",
            f"TRIGGER:-PT{event['reminder_minutes']}M",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{_ics_escape(event['title'])}",
            "END:VALARM",
        ])
    lines.extend(["END:VEVENT", "END:VCALENDAR", ""])
    return Response(
        content="\r\n".join(lines),
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="careerpilot-event-{event_id}.ics"'},
    )
