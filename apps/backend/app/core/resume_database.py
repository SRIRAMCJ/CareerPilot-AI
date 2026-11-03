import os
import sqlite3
from pathlib import Path

from app.core import database


def create_resume_record(
    filename: str, file_type: str, file_size: int, stored_path: str, extracted_text: str
) -> dict:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        cursor = connection.execute(
            """INSERT INTO resumes (filename, file_type, file_size, stored_path, extracted_text)
            VALUES (?, ?, ?, ?, ?)""",
            (filename, file_type, file_size, stored_path, extracted_text),
        )
        row = connection.execute(
            "SELECT id, filename, file_type, file_size, uploaded_at FROM resumes WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(zip(("id", "filename", "file_type", "file_size", "uploaded_at"), row))


def list_resume_records() -> list[dict]:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        rows = connection.execute(
            "SELECT id, filename, file_type, file_size, uploaded_at FROM resumes ORDER BY id DESC"
        ).fetchall()
    return [dict(zip(("id", "filename", "file_type", "file_size", "uploaded_at"), row)) for row in rows]


def get_resume_record(resume_id: int) -> dict | None:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
    return dict(row) if row else None


def delete_resume_record(resume_id: int) -> dict | None:
    row = get_resume_record(resume_id)
    if row is None:
        return None
    with sqlite3.connect(database.database_path()) as connection:
        connection.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    return row


def local_resume_directory() -> Path:
    configured = os.getenv("CAREERPILOT_RESUME_DIR")
    directory = Path(configured).expanduser() if configured else Path.home() / ".careerpilot" / "resumes"
    directory.mkdir(parents=True, exist_ok=True)
    return directory
