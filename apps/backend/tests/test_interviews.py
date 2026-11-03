from fastapi.testclient import TestClient

from app.core import database
from app.main import app

client = TestClient(app)


def test_interview_schedule_and_calendar_export(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "interviews.db")
    job = client.post("/api/v1/jobs", json={
        "title": "AI Engineer", "company": "Example Labs", "source": "manual"
    }).json()
    application = client.post("/api/v1/applications", json={"job_id": job["id"]}).json()

    response = client.post("/api/v1/interviews", json={
        "application_id": application["id"],
        "title": "Technical interview",
        "event_type": "technical_round",
        "starts_at": "2026-11-12T10:00:00+05:30",
        "ends_at": "2026-11-12T11:00:00+05:30",
        "timezone_name": "Asia/Kolkata",
        "meeting_url": "https://meet.example.com/room",
        "notes": "Prepare project walkthrough",
    })
    assert response.status_code == 201
    event_id = response.json()["id"]

    calendar = client.get(f"/api/v1/interviews/{event_id}/calendar.ics")
    assert calendar.status_code == 200
    assert "BEGIN:VCALENDAR" in calendar.text
    assert "DTSTART:20261112T043000Z" in calendar.text

    assert client.patch(f"/api/v1/interviews/{event_id}", json={"title": "Final technical round"}).status_code == 200
    assert client.delete(f"/api/v1/interviews/{event_id}").status_code == 200


def test_interview_requires_timezone_aware_dates():
    response = client.post("/api/v1/interviews", json={
        "application_id": 1, "title": "Interview",
        "starts_at": "2026-11-12T10:00:00", "ends_at": "2026-11-12T11:00:00",
    })
    assert response.status_code == 422
