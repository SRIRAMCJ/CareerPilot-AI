import sqlite3
from typing import Any

from app.core import database
from app.schemas.application import ApplicationCreate, ApplicationUpdate


_ALLOWED_TRANSITIONS = {
    "saved": {"shortlisted", "preparing", "withdrawn", "rejected"},
    "shortlisted": {"saved", "preparing", "withdrawn", "rejected"},
    "preparing": {"shortlisted", "ready_to_submit", "withdrawn", "rejected"},
    "ready_to_submit": {"preparing", "applied", "withdrawn"},
    "applied": {"assessment", "interview", "offer", "rejected", "withdrawn"},
    "assessment": {"interview", "offer", "rejected", "withdrawn"},
    "interview": {"assessment", "offer", "rejected", "withdrawn"},
    "offer": {"withdrawn"},
    "rejected": set(),
    "withdrawn": set(),
}


def validate_status_transition(current: str, target: str) -> None:
    if current == target:
        return
    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"Invalid application status transition: {current} -> {target}.")



def _connect() -> sqlite3.Connection:
    database.initialize_database()
    connection = sqlite3.connect(database.database_path())
    connection.row_factory = sqlite3.Row
    return connection


def _serialize(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def create_application(item: ApplicationCreate) -> dict[str, Any]:
    payload = item.model_dump(mode="json")
    with _connect() as connection:
        job = connection.execute("SELECT id FROM job_listings WHERE id = ?", (item.job_id,)).fetchone()
        if job is None:
            raise ValueError("The selected job does not exist.")
        existing = connection.execute(
            "SELECT id FROM applications WHERE job_id = ? AND status NOT IN ('rejected', 'withdrawn')",
            (item.job_id,),
        ).fetchone()
        if existing:
            raise ValueError("An active application tracker already exists for this job.")
        cursor = connection.execute(
            """INSERT INTO applications
            (job_id, status, notes, applied_date, next_action, follow_up_date)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (item.job_id, payload["status"], payload["notes"], payload["applied_date"],
             payload["next_action"], payload["follow_up_date"]),
        )
        row = connection.execute(
            """SELECT a.*, j.title AS job_title, j.company AS company, j.url AS job_url
            FROM applications a JOIN job_listings j ON j.id = a.job_id WHERE a.id = ?""",
            (cursor.lastrowid,),
        ).fetchone()
    return _serialize(row)


def list_applications(status_filter: str | None = None) -> list[dict[str, Any]]:
    query = """SELECT a.*, j.title AS job_title, j.company AS company, j.url AS job_url
               FROM applications a JOIN job_listings j ON j.id = a.job_id"""
    values: tuple[Any, ...] = ()
    if status_filter:
        query += " WHERE a.status = ?"
        values = (status_filter,)
    query += " ORDER BY a.updated_at DESC"
    with _connect() as connection:
        rows = connection.execute(query, values).fetchall()
    return [_serialize(row) for row in rows]


def update_application(application_id: int, item: ApplicationUpdate) -> dict[str, Any] | None:
    changes = item.model_dump(exclude_unset=True, mode="json")
    if not changes:
        return get_application(application_id)
    assignments = ", ".join(f"{key} = ?" for key in changes)
    values = [*changes.values(), application_id]
    with _connect() as connection:
        current = connection.execute("SELECT status FROM applications WHERE id = ?", (application_id,)).fetchone()
        if current is None:
            return None
        if "status" in changes and changes["status"] is not None:
            validate_status_transition(current["status"], changes["status"])
        cursor = connection.execute(
            f"UPDATE applications SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values,
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute(
            """SELECT a.*, j.title AS job_title, j.company AS company, j.url AS job_url
            FROM applications a JOIN job_listings j ON j.id = a.job_id WHERE a.id = ?""",
            (application_id,),
        ).fetchone()
    return _serialize(row)


def get_application(application_id: int) -> dict[str, Any] | None:
    with _connect() as connection:
        row = connection.execute(
            """SELECT a.*, j.title AS job_title, j.company AS company, j.url AS job_url
            FROM applications a JOIN job_listings j ON j.id = a.job_id WHERE a.id = ?""",
            (application_id,),
        ).fetchone()
    return _serialize(row) if row else None
