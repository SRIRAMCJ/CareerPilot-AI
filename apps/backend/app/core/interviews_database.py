import sqlite3
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core import database
from app.schemas.interview import InterviewCreate, InterviewUpdate


def _connect() -> sqlite3.Connection:
    database.initialize_database()
    connection = sqlite3.connect(database.database_path())
    connection.row_factory = sqlite3.Row
    return connection


def create_interview(item: InterviewCreate) -> dict[str, Any]:
    payload = item.model_dump(mode="json")
    with _connect() as connection:
        application = connection.execute(
            "SELECT id FROM applications WHERE id = ?", (item.application_id,)
        ).fetchone()
        if application is None:
            raise ValueError("The selected application tracker does not exist.")
        cursor = connection.execute(
            """INSERT INTO interview_events
            (application_id, title, event_type, starts_at, ends_at, timezone_name,
             meeting_url, notes, reminder_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (item.application_id, item.title, item.event_type, payload["starts_at"],
             payload["ends_at"], item.timezone_name,
             str(item.meeting_url) if item.meeting_url else None, item.notes, item.reminder_minutes),
        )
        row = connection.execute(
            """SELECT e.*, j.title AS job_title, j.company
            FROM interview_events e JOIN applications a ON a.id = e.application_id
            JOIN job_listings j ON j.id = a.job_id WHERE e.id = ?""",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(row)


def list_interviews() -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(
            """SELECT e.*, j.title AS job_title, j.company
            FROM interview_events e JOIN applications a ON a.id = e.application_id
            JOIN job_listings j ON j.id = a.job_id
            ORDER BY e.starts_at ASC"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_interview(event_id: int) -> dict[str, Any] | None:
    with _connect() as connection:
        row = connection.execute(
            """SELECT e.*, j.title AS job_title, j.company
            FROM interview_events e JOIN applications a ON a.id = e.application_id
            JOIN job_listings j ON j.id = a.job_id WHERE e.id = ?""",
            (event_id,),
        ).fetchone()
    return dict(row) if row else None


def update_interview(event_id: int, item: InterviewUpdate) -> dict[str, Any] | None:
    changes = item.model_dump(exclude_unset=True, mode="json")
    if not changes:
        return get_interview(event_id)
    current = get_interview(event_id)
    if current is None:
        return None
    merged = {**current, **changes}
    starts = datetime.fromisoformat(merged["starts_at"])
    ends = datetime.fromisoformat(merged["ends_at"])
    if starts.tzinfo is None or starts.utcoffset() is None or ends.tzinfo is None or ends.utcoffset() is None:
        raise ValueError("Interview dates must include timezone offsets.")
    if ends <= starts:
        raise ValueError("ends_at must be after starts_at.")
    try:
        ZoneInfo(merged["timezone_name"])
    except ZoneInfoNotFoundError as error:
        raise ValueError("Use a valid IANA timezone.") from error
    if "meeting_url" in changes and changes["meeting_url"] is not None:
        changes["meeting_url"] = str(changes["meeting_url"])
    assignments = ", ".join(f"{key} = ?" for key in changes)
    with _connect() as connection:
        cursor = connection.execute(
            f"UPDATE interview_events SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            [*changes.values(), event_id],
        )
        if cursor.rowcount == 0:
            return None
    return get_interview(event_id)


def delete_interview(event_id: int) -> bool:
    with _connect() as connection:
        cursor = connection.execute("DELETE FROM interview_events WHERE id = ?", (event_id,))
    return cursor.rowcount > 0
