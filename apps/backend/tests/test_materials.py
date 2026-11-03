from fastapi.testclient import TestClient

from app.core import database
from app.services import materials_generator
from app.main import app

client = TestClient(app)


def test_application_pack_is_generated_from_saved_facts(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "materials.db")
    monkeypatch.setattr(materials_generator, "generated_material_directory", lambda: tmp_path / "generated")

    job = client.post("/api/v1/jobs", json={
        "title": "AI Engineer", "company": "Example Labs", "source": "manual"
    }).json()
    application = client.post("/api/v1/applications", json={"job_id": job["id"]}).json()
    client.put("/api/v1/profile", json={
        "full_name": "Test Candidate",
        "email": "candidate@example.com",
        "current_role": "AI Engineer",
        "target_roles": ["GenAI Engineer"],
        "skills": ["Python", "RAG"],
        "projects": ["Built a local RAG prototype"],
    })

    generated = client.post(f"/api/v1/applications/{application['id']}/materials")
    assert generated.status_code == 200
    payload = generated.json()
    assert payload["material_type"] == "resume_and_cover_letter"

    download = client.get(payload["download_url"])
    assert download.status_code == 200
    assert download.content.startswith(b"PK")
