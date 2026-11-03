import sqlite3

from app.core import database


def create_material(application_id: int, material_type: str, filename: str, stored_path: str) -> dict:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        cursor = connection.execute(
            """INSERT INTO generated_materials (application_id, material_type, filename, stored_path)
            VALUES (?, ?, ?, ?)""",
            (application_id, material_type, filename, stored_path),
        )
        connection.commit()
        row = connection.execute(
            "SELECT id, application_id, material_type, filename, created_at FROM generated_materials WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(zip(("id", "application_id", "material_type", "filename", "created_at"), row))


def list_materials(application_id: int) -> list[dict]:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        rows = connection.execute(
            """SELECT id, application_id, material_type, filename, created_at
            FROM generated_materials WHERE application_id = ? ORDER BY id DESC""",
            (application_id,),
        ).fetchall()
    keys = ("id", "application_id", "material_type", "filename", "created_at")
    return [dict(zip(keys, row)) for row in rows]


def get_material(material_id: int) -> dict | None:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("SELECT * FROM generated_materials WHERE id = ?", (material_id,)).fetchone()
    return dict(row) if row else None
