import asyncio

from app.services import job_sources
from app.services.job_sources import _skills, html_to_text


def test_html_to_text_removes_markup_and_normalizes_whitespace():
    assert html_to_text("<h1>Python</h1><p>Build   APIs</p>") == "Python Build APIs"


def test_skill_extraction_uses_token_boundaries():
    assert _skills("Experience with JavaScript and Python") == ["Python", "JavaScript"]


def test_ashby_adapter_normalizes_public_postings(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"jobs": [
                {
                    "id": "role-1", "title": "LLM Engineer", "location": "Remote",
                    "workplaceType": "Remote", "descriptionPlain": "Python and RAG",
                    "jobUrl": "https://jobs.ashbyhq.com/demo/role-1",
                    "publishedAt": "2026-11-01T10:00:00Z", "employmentType": "FullTime",
                    "isListed": True,
                },
                {"id": "hidden", "title": "Hidden", "isListed": False},
            ]}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(job_sources.httpx, "AsyncClient", lambda **kwargs: FakeClient())
    jobs = asyncio.run(job_sources.fetch_ashby("demo", 10))
    assert len(jobs) == 1
    assert jobs[0]["work_mode"] == "Remote"
    assert jobs[0]["posted_date"] == "2026-11-01"
    assert jobs[0]["required_skills"] == ["Python", "RAG"]
