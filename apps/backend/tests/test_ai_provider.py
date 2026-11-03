from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core import database
from app.main import app
from app.routers import materials
from app.services.ai_provider import _local_ollama_endpoint

client = TestClient(app)


def test_ollama_endpoint_requires_loopback_host():
    assert _local_ollama_endpoint("http://127.0.0.1:11434") == "http://127.0.0.1:11434/api/generate"
    with pytest.raises(ValueError):
        _local_ollama_endpoint("https://example.com")
    with pytest.raises(ValueError):
        _local_ollama_endpoint("http://192.168.1.10:11434")


def test_ai_cover_letter_endpoint_uses_configured_local_provider(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / "ai-materials.db")
    monkeypatch.setattr(materials, "get_settings", lambda: SimpleNamespace(
        ai_provider="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="test-model",
    ))

    async def fake_generate(profile, job, base_url, model):
        assert model == "test-model"
        assert job["title"] == "AI Engineer"
        return "Dear Hiring Team, I am interested in the role."

    monkeypatch.setattr(materials, "generate_cover_letter", fake_generate)
    job = client.post("/api/v1/jobs", json={
        "title": "AI Engineer", "company": "Example Labs", "source": "manual",
        "description": "Python and RAG experience preferred.",
    }).json()
    application = client.post("/api/v1/applications", json={"job_id": job["id"]}).json()
    client.put("/api/v1/profile", json={"full_name": "Test Candidate", "skills": ["Python"]})

    response = client.post(f"/api/v1/applications/{application['id']}/cover-letter/ai")
    assert response.status_code == 200
    assert "Dear Hiring Team" in response.json()["draft"]
    assert "verify every claim" in response.json()["warning"].lower()
