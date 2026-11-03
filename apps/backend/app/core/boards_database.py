import sqlite3

from app.core import database


def add_board(provider: str, slug: str) -> dict:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO job_source_boards (provider, company_slug) VALUES (?, ?)",
                (provider, slug),
            )
        except sqlite3.IntegrityError:
            row = connection.execute(
                "SELECT id, provider, company_slug, created_at FROM job_source_boards WHERE provider = ? AND company_slug = ?",
                (provider, slug),
            ).fetchone()
            return dict(zip(("id", "provider", "company_slug", "created_at"), row))
        row = connection.execute(
            "SELECT id, provider, company_slug, created_at FROM job_source_boards WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    return dict(zip(("id", "provider", "company_slug", "created_at"), row))


def list_boards() -> list[dict]:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        rows = connection.execute(
            "SELECT id, provider, company_slug, created_at FROM job_source_boards ORDER BY provider, company_slug"
        ).fetchall()
    keys = ("id", "provider", "company_slug", "created_at")
    return [dict(zip(keys, row)) for row in rows]


def delete_board(board_id: int) -> bool:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        cursor = connection.execute("DELETE FROM job_source_boards WHERE id = ?", (board_id,))
    return cursor.rowcount > 0
