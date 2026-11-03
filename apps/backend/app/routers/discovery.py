import httpx
from fastapi import APIRouter, HTTPException

from app.core.jobs_database import create_job
from app.schemas.discovery import DiscoveryRequest
from app.services.job_sources import discover_jobs

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])


@router.post("/search")
async def search_public_jobs(request: DiscoveryRequest) -> dict:
    """Fetch public postings from an explicitly selected Greenhouse or Lever board."""
    try:
        found = await discover_jobs(request.provider, request.company_slug, request.limit)
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=f"{request.provider.title()} returned HTTP {error.response.status_code}. Check the company board slug.",
        ) from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="The public job source could not be reached.") from error
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=502, detail="The public job source returned an unexpected response.") from error

    query = (request.query or "").casefold().strip()
    if query:
        found = [
            job for job in found
            if query in job["title"].casefold()
            or query in job["description"].casefold()
            or query in (job["location"] or "").casefold()
        ]

    saved = 0
    duplicates = 0
    for item in found:
        try:
            create_job(item)
            saved += 1
        except ValueError:
            duplicates += 1
    return {
        "provider": request.provider,
        "company_slug": request.company_slug,
        "fetched": len(found),
        "saved": saved,
        "duplicates": duplicates,
        "items": found,
    }
