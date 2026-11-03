from fastapi.testclient import TestClient

from app.core import database
from app.main import app

client = TestClient(app)


def test_application_changes_are_audited(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "audit.db")
    job = client.post("/api/v1/jobs", json={
        "title": "AI Engineer", "company": "Example Labs", "source": "manual"
    }).json()
    application = client.post("/api/v1/applications", json={"job_id": job["id"]}).json()
    client.patch(f"/api/v1/applications/{application['id']}", json={"status": "ready_to_submit"})

    events = client.get("/api/v1/audit/events").json()["items"]
    assert any(event["event_type"] == "application.created" for event in events)
    assert any(event["event_type"] == "application.updated" for event in events)
    assert events[0]["details"]["status"] == "ready_to_submit"
