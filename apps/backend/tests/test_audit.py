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

    preparing = client.patch(
        f"/api/v1/applications/{application['id']}", json={"status": "preparing"}
    )
    assert preparing.status_code == 200
    ready = client.patch(
        f"/api/v1/applications/{application['id']}", json={"status": "ready_to_submit"}
    )
    assert ready.status_code == 200

    events = client.get("/api/v1/audit/events").json()["items"]
    assert any(event["event_type"] == "application.created" for event in events)
    updates = [event for event in events if event["event_type"] == "application.updated"]
    assert len(updates) == 2
    assert updates[0]["details"]["from_status"] == "preparing"
    assert updates[0]["details"]["to_status"] == "ready_to_submit"
