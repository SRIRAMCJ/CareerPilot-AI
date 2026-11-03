from fastapi.testclient import TestClient
from docx import Document
from io import BytesIO

from app.core import database
from app.core import resume_database
from app.main import app
from app.services.resume_parser import extract_facts, extract_text

client = TestClient(app)


def test_resume_text_extraction_and_fact_preview(tmp_path, monkeypatch):
    db_path = tmp_path / "resume.db"
    monkeypatch.setattr(database, "database_path", lambda: db_path)
    monkeypatch.setattr(resume_database, "local_resume_directory", lambda: tmp_path / "resumes")

    document = Document()
    document.add_paragraph("Sriram V")
    document.add_paragraph("AI Engineer | Python | FastAPI | RAG")
    document.add_paragraph("sriram@example.com")
    buffer = BytesIO()
    document.save(buffer)

    response = client.post(
        "/api/v1/resumes",
        files={"file": ("candidate.docx", buffer.getvalue(),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert "Python" in payload["extracted_skills"]
    assert payload["extracted_email"] == "sriram@example.com"

    preview = client.get(f"/api/v1/resumes/{payload['id']}/preview")
    assert preview.status_code == 200
    assert "AI Engineer" in preview.json()["text"]

    deleted = client.delete(f"/api/v1/resumes/{payload['id']}")
    assert deleted.status_code == 200
    assert client.get(f"/api/v1/resumes/{payload['id']}/preview").status_code == 404


def test_resume_rejects_fake_extension_and_content():
    response = client.post(
        "/api/v1/resumes",
        files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
    )
    assert response.status_code == 415


def test_resume_parser_extracts_only_observed_facts():
    facts = extract_facts("Python, SQL and RAG. Contact: test@example.com")
    assert facts["skills"] == ["Python", "SQL", "RAG"]
    assert facts["email"] == "test@example.com"
