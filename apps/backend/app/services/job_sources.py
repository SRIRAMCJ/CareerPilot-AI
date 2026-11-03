import re
from html.parser import HTMLParser
from typing import Any

import httpx


class _HTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        clean = data.strip()
        if clean:
            self.parts.append(clean)


def html_to_text(value: str | None) -> str:
    parser = _HTMLText()
    parser.feed(value or "")
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def _skills(text: str) -> list[str]:
    vocabulary = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "SQL", "FastAPI",
        "Django", "Flask", "React", "Next.js", "Node.js", "AWS", "Azure", "GCP",
        "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Redis", "Git",
        "Machine Learning", "Deep Learning", "LLM", "RAG", "LangChain",
        "TensorFlow", "PyTorch", "Scikit-learn", "REST API", "GraphQL",
    ]
    lowered = text.casefold()
    return [skill for skill in vocabulary if skill.casefold() in lowered]


def _work_mode(location: str, description: str) -> str | None:
    combined = f"{location} {description}".casefold()
    if "remote" in combined:
        return "Remote"
    if "hybrid" in combined:
        return "Hybrid"
    if "on-site" in combined or "onsite" in combined:
        return "On-site"
    return None


async def fetch_greenhouse(slug: str, limit: int) -> list[dict[str, Any]]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
        response = await client.get(url, params={"content": "true"})
        response.raise_for_status()
        payload = response.json()
    jobs = []
    for item in payload.get("jobs", [])[:limit]:
        location = (item.get("location") or {}).get("name") or ""
        description = html_to_text(item.get("content"))
        jobs.append({
            "title": item.get("title") or "Untitled role",
            "company": slug.replace("-", " ").title(),
            "location": location or None,
            "work_mode": _work_mode(location, description),
            "source": f"greenhouse:{slug}",
            "source_job_id": str(item.get("id")),
            "url": item.get("absolute_url"),
            "description": description[:30000],
            "required_skills": _skills(description),
        })
    return jobs


async def fetch_lever(slug: str, limit: int) -> list[dict[str, Any]]:
    url = f"https://api.lever.co/v0/postings/{slug}"
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
        response = await client.get(url, params={"mode": "json"})
        response.raise_for_status()
        payload = response.json()
    jobs = []
    for item in payload[:limit]:
        categories = item.get("categories") or {}
        location = categories.get("location") or ""
        description = html_to_text(item.get("descriptionPlain") or item.get("description"))
        jobs.append({
            "title": item.get("text") or "Untitled role",
            "company": slug.replace("-", " ").title(),
            "location": location or None,
            "work_mode": _work_mode(location, description),
            "source": f"lever:{slug}",
            "source_job_id": str(item.get("id")),
            "url": item.get("hostedUrl"),
            "description": description[:30000],
            "required_skills": _skills(description),
        })
    return jobs


async def discover_jobs(provider: str, slug: str, limit: int) -> list[dict[str, Any]]:
    if provider == "greenhouse":
        return await fetch_greenhouse(slug, limit)
    if provider == "lever":
        return await fetch_lever(slug, limit)
    raise ValueError("Unsupported job source.")
