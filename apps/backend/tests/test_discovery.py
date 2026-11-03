from fastapi.testclient import TestClient

from app.core import database
from app.main import app
from app.routers import discovery

client = TestClient(app)


def test_discovery_saves_normalized_jobs_and_reports_duplicates(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "discovery.db")

    async def fake_discover(provider, slug, limit):
        return [{
            "title": "GenAI Engineer",
            "company": "Example Company",
            "location": "Remote",
            "work_mode": "Remote",
            "source": f"{provider}:{slug}",
            "source_job_id": "remote-1",
            "url": "https://jobs.example.com/1",
            "description": "Build Python and FastAPI services.",
            "required_skills": ["Python", "FastAPI"],
        }]

    monkeypatch.setattr(discovery, "discover_jobs", fake_discover)
    request = {"provider": "greenhouse", "company_slug": "example-company", "limit": 10}

    first = client.post("/api/v1/discovery/search", json=request)
    assert first.status_code == 200
    assert first.json()["saved"] == 1
    assert first.json()["items"][0]["required_skills"] == ["Python", "FastAPI"]

    second = client.post("/api/v1/discovery/search", json=request)
    assert second.status_code == 200
    assert second.json()["saved"] == 0
    assert second.json()["duplicates"] == 1


def test_discovery_rejects_invalid_board_slug():
    response = client.post("/api/v1/discovery/search", json={
        "provider": "lever", "company_slug": "https://attacker.example/path"
    })
    assert response.status_code == 422
