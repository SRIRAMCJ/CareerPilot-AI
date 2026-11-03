from fastapi.testclient import TestClient

from app.core import database
from app.main import app

client = TestClient(app)


def configure_db(tmp_path, monkeypatch):
    path = tmp_path / "careerpilot-jobs.db"
    monkeypatch.setattr(database, "database_path", lambda: path)
    return path


def test_job_create_list_and_duplicate_detection(tmp_path, monkeypatch):
    configure_db(tmp_path, monkeypatch)
    payload = {
        "title": "GenAI Engineer",
        "company": "Example Labs",
        "location": "Chennai",
        "source": "manual",
        "source_job_id": "example-001",
        "required_skills": ["Python", "FastAPI"],
    }
    created = client.post("/api/v1/jobs", json=payload)
    assert created.status_code == 201
    assert created.json()["required_skills"] == ["Python", "FastAPI"]

    duplicate = client.post("/api/v1/jobs", json=payload)
    assert duplicate.status_code == 409
    assert len(client.get("/api/v1/jobs?search=GenAI").json()["items"]) == 1


def test_match_requires_profile_then_returns_explanation(tmp_path, monkeypatch):
    configure_db(tmp_path, monkeypatch)
    job = client.post("/api/v1/jobs", json={
        "title": "AI Engineer", "company": "Example Labs",
        "location": "Chennai", "work_mode": "Hybrid",
        "required_skills": ["Python", "FastAPI", "Kubernetes"],
    }).json()

    missing = client.get(f"/api/v1/jobs/{job['id']}/match")
    assert missing.status_code == 409

    profile = client.put("/api/v1/profile", json={
        "full_name": "Test Candidate",
        "target_roles": ["AI Engineer"],
        "preferred_locations": ["Chennai"],
        "preferred_work_modes": ["Hybrid"],
        "skills": ["Python", "FastAPI"],
    })
    assert profile.status_code == 200

    match = client.get(f"/api/v1/jobs/{job['id']}/match")
    assert match.status_code == 200
    assert match.json()["score"] >= 60
    assert match.json()["matched_skills"] == ["fastapi", "python"]
    assert match.json()["missing_skills"] == ["kubernetes"]


def test_match_marks_salary_and_work_mode_conflicts_as_ineligible(tmp_path, monkeypatch):
    configure_db(tmp_path, monkeypatch)
    job = client.post("/api/v1/jobs", json={
        "title": "AI Engineer", "company": "Example Labs", "location": "Bengaluru",
        "work_mode": "On-site", "salary_min": 300000, "salary_max": 500000,
        "required_skills": ["Python"],
    }).json()
    client.put("/api/v1/profile", json={
        "full_name": "Test Candidate",
        "target_roles": ["AI Engineer"],
        "preferred_locations": ["Chennai"],
        "preferred_work_modes": ["Remote"],
        "minimum_salary": 800000,
        "skills": ["Python"],
    })
    match = client.get(f"/api/v1/jobs/{job['id']}/match")
    assert match.status_code == 200
    assert match.json()["eligible"] is False
    assert match.json()["decision"] == "not_eligible"
    assert len(match.json()["blocking_reasons"]) == 3
