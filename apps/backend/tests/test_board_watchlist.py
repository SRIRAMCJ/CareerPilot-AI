from fastapi.testclient import TestClient

from app.core import database
from app.main import app
from app.routers import discovery

client = TestClient(app)


def test_board_watchlist_and_multi_board_scan(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "boards.db")

    first = client.post("/api/v1/discovery/boards", json={
        "provider": "greenhouse", "company_slug": "example-one"
    })
    assert first.status_code == 201
    duplicate = client.post("/api/v1/discovery/boards", json={
        "provider": "greenhouse", "company_slug": "EXAMPLE-ONE"
    })
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == first.json()["id"]

    client.post("/api/v1/discovery/boards", json={
        "provider": "lever", "company_slug": "example-two"
    })

    async def fake_discover(provider, slug, limit):
        return [{
            "title": f"{slug} AI Engineer", "company": slug,
            "source": f"{provider}:{slug}", "source_job_id": "job-1",
            "description": "Python and FastAPI", "required_skills": ["Python", "FastAPI"],
        }]

    monkeypatch.setattr(discovery, "discover_jobs", fake_discover)
    result = client.post("/api/v1/discovery/run", json={"limit_per_board": 10})
    assert result.status_code == 200
    assert result.json()["boards_scanned"] == 2
    assert result.json()["saved"] == 2

    removed = client.delete(f"/api/v1/discovery/boards/{first.json()['id']}")
    assert removed.status_code == 200
    assert len(client.get("/api/v1/discovery/boards").json()["items"]) == 1
