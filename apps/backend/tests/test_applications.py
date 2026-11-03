from fastapi.testclient import TestClient

from app.core import database
from app.main import app

client = TestClient(app)


def test_application_tracker_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "tracker.db")
    job = client.post("/api/v1/jobs", json={
        "title": "AI Engineer", "company": "Example Co", "source": "manual"
    }).json()

    created = client.post("/api/v1/applications", json={"job_id": job["id"], "status": "saved"})
    assert created.status_code == 201
    application_id = created.json()["id"]
    assert created.json()["job_title"] == "AI Engineer"

    duplicate = client.post("/api/v1/applications", json={"job_id": job["id"]})
    assert duplicate.status_code == 409

    updated = client.patch(f"/api/v1/applications/{application_id}", json={
        "status": "interview", "next_action": "Prepare technical round"
    })
    assert updated.status_code == 200
    assert updated.json()["status"] == "interview"

    assert len(client.get("/api/v1/applications?status=interview").json()["items"]) == 1


def test_application_requires_existing_job(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "tracker.db")
    response = client.post("/api/v1/applications", json={"job_id": 999})
    assert response.status_code == 409
