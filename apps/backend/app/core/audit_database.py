import json
import sqlite3
from typing import Any

from app.core import database


def record_event(event_type: str, entity_type: str, entity_id: int | None, details: dict[str, Any] | None = None) -> None:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        connection.execute(
            """INSERT INTO audit_events (event_type, entity_type, entity_id, details_json)
            VALUES (?, ?, ?, ?)""",
            (event_type, entity_type, entity_id, json.dumps(details or {}, ensure_ascii=False)),
        )


def list_events(limit: int = 100) -> list[dict[str, Any]]:
    database.initialize_database()
    with sqlite3.connect(database.database_path()) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """SELECT id, event_type, entity_type, entity_id, details_json, created_at
            FROM audit_events ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    events = []
    for row in rows:
        item = dict(row)
        item["details"] = json.loads(item.pop("details_json"))
        events.append(item)
    return events
