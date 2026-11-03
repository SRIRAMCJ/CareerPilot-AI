from fastapi.testclient import TestClient

from app.core import database
from app.main import app

client = TestClient(app)


def test_profile_can_be_created_read_and_deleted(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "careerpilot-test.db"
    monkeypatch.setattr(database, "database_path", lambda: db_path)

    payload = {
        "full_name": "Test Candidate",
        "target_roles": ["AI Engineer", "GenAI Engineer"],
        "skills": ["Python", "FastAPI"],
        "minimum_salary": 25000,
    }

    created = client.put("/api/v1/profile", json=payload)
    assert created.status_code == 200
    assert created.json()["profile"]["full_name"] == "Test Candidate"

    fetched = client.get("/api/v1/profile")
    assert fetched.status_code == 200
    assert fetched.json()["profile"]["target_roles"] == ["AI Engineer", "GenAI Engineer"]

    deleted = client.delete("/api/v1/profile")
    assert deleted.status_code == 200
    assert client.get("/api/v1/profile").json() is None


def test_profile_rejects_unknown_fields(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "profile.db")

    response = client.put(
        "/api/v1/profile",
        json={"full_name": "Test Candidate", "invented_fact": "not allowed"},
    )
    assert response.status_code == 422
