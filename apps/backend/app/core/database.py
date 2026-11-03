import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from app.schemas.profile import CandidateProfile


def database_path() -> Path:
    """Resolve the private local database path; callers may override it in tests."""
    configured = os.getenv("CAREERPILOT_DATABASE_PATH")
    path = Path(configured) if configured else Path.cwd() / "data" / "careerpilot.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def initialize_database(path: Path | None = None) -> None:
    target = path or database_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(target) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS candidate_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_profile(profile: CandidateProfile, path: Path | None = None) -> dict[str, Any]:
    target = path or database_path()
    initialize_database(target)
    payload = profile.model_dump_json()
    with sqlite3.connect(target) as connection:
        connection.execute(
            """
            INSERT INTO candidate_profile (id, payload, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = CURRENT_TIMESTAMP
            """,
            (payload,),
        )
        row = connection.execute(
            "SELECT updated_at FROM candidate_profile WHERE id = 1"
        ).fetchone()
    return {"profile": profile.model_dump(), "updated_at": row[0]}


def read_profile(path: Path | None = None) -> dict[str, Any] | None:
    target = path or database_path()
    initialize_database(target)
    with sqlite3.connect(target) as connection:
        row = connection.execute(
            "SELECT payload, updated_at FROM candidate_profile WHERE id = 1"
        ).fetchone()
    if row is None:
        return None
    return {"profile": json.loads(row[0]), "updated_at": row[1]}


def delete_profile(path: Path | None = None) -> bool:
    target = path or database_path()
    initialize_database(target)
    with sqlite3.connect(target) as connection:
        cursor = connection.execute("DELETE FROM candidate_profile WHERE id = 1")
    return cursor.rowcount > 0
