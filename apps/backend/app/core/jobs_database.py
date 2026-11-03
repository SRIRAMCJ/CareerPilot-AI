import json
import sqlite3
from typing import Any

from app.core import database
from app.schemas.job import JobListingCreate


def _connect() -> sqlite3.Connection:
    database.initialize_database()
    connection = sqlite3.connect(database.database_path())
    connection.row_factory = sqlite3.Row
    return connection


def _decode(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["required_skills"] = json.loads(item["required_skills"])
    return item


def create_job(job: JobListingCreate) -> dict[str, Any]:
    payload = job.model_dump(mode="json")
    with _connect() as connection:
        try:
            cursor = connection.execute(
                """INSERT INTO job_listings
                (title, company, location, work_mode, job_type, source, source_job_id,
                 url, description, required_skills, salary_min, salary_max,
                 salary_currency, posted_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["title"], payload["company"], payload["location"],
                    payload["work_mode"], payload["job_type"], payload["source"],
                    payload["source_job_id"], str(payload["url"]) if payload["url"] else None,
                    payload["description"], json.dumps(payload["required_skills"]),
                    payload["salary_min"], payload["salary_max"], payload["salary_currency"],
                    payload["posted_date"],
                ),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError("This job already exists for the selected source.") from error
        row = connection.execute(
            "SELECT * FROM job_listings WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return _decode(row)


def get_job(job_id: int) -> dict[str, Any] | None:
    with _connect() as connection:
        row = connection.execute("SELECT * FROM job_listings WHERE id = ?", (job_id,)).fetchone()
    return _decode(row) if row else None


def list_jobs(search: str | None = None, status_filter: str | None = None,
              limit: int = 50) -> list[dict[str, Any]]:
    clauses: list[str] = []
    values: list[Any] = []
    if search:
        clauses.append("(title LIKE ? OR company LIKE ? OR location LIKE ?)")
        values.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if status_filter:
        clauses.append("status = ?")
        values.append(status_filter)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with _connect() as connection:
        rows = connection.execute(
            f"SELECT * FROM job_listings{where} ORDER BY created_at DESC LIMIT ?",
            (*values, limit),
        ).fetchall()
    return [_decode(row) for row in rows]
