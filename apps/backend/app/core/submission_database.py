import sqlite3
from pathlib import Path

from app.core.config import get_settings


def _database_path() -> Path:
    configured = get_settings().careerpilot_database_path
    path = Path(configured) if configured else Path.cwd() / "data" / "careerpilot.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _initialize() -> None:
    with sqlite3.connect(_database_path()) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS submission_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL UNIQUE REFERENCES applications(id),
                page_url TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('started', 'clicked', 'outcome_unknown')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                finished_at TEXT
            )"""
        )


def _connect() -> sqlite3.Connection:
    _initialize()
    connection = sqlite3.connect(_database_path(), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def claim_submission_attempt(application_id: int, page_url: str) -> dict | None:
    with _connect() as connection:
        cursor = connection.execute(
            """INSERT OR IGNORE INTO submission_attempts (application_id, page_url, status)
               VALUES (?, ?, 'started')""",
            (application_id, page_url),
        )
        if cursor.rowcount != 1:
            return None
        row = connection.execute(
            "SELECT * FROM submission_attempts WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return dict(row) if row else None


def finish_submission_attempt(attempt_id: int, status: str) -> dict | None:
    if status not in {"clicked", "outcome_unknown"}:
        raise ValueError("Unsupported submission attempt status.")
    with _connect() as connection:
        connection.execute(
            """UPDATE submission_attempts SET status = ?, finished_at = CURRENT_TIMESTAMP
               WHERE id = ? AND status = 'started'""",
            (status, attempt_id),
        )
        row = connection.execute(
            "SELECT * FROM submission_attempts WHERE id = ?", (attempt_id,)
        ).fetchone()
    return dict(row) if row else None


def get_submission_attempt(application_id: int) -> dict | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT * FROM submission_attempts WHERE application_id = ?",
            (application_id,),
        ).fetchone()
    return dict(row) if row else None
