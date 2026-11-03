import httpx
from fastapi import APIRouter, HTTPException

from app.core.audit_database import record_event
from app.core.boards_database import add_board, delete_board, list_boards
from app.core.jobs_database import create_job
from app.schemas.board import BoardCreate, DiscoveryRunRequest
from app.schemas.discovery import DiscoveryRequest
from app.schemas.job import JobListingCreate
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
            create_job(JobListingCreate.model_validate(item))
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


@router.post("/boards", status_code=201)
def save_company_board(request: BoardCreate) -> dict:
    board = add_board(request.provider, request.normalized_slug())
    record_event("discovery.board_saved", "job_source_board", board["id"], {"provider": board["provider"], "company_slug": board["company_slug"]})
    return board


@router.get("/boards")
def get_company_boards() -> dict:
    return {"items": list_boards()}


@router.delete("/boards/{board_id}")
def remove_company_board(board_id: int) -> dict:
    if not delete_board(board_id):
        raise HTTPException(status_code=404, detail="Company board not found.")
    record_event("discovery.board_removed", "job_source_board", board_id)
    return {"status": "deleted", "id": board_id}


@router.post("/run")
async def run_watchlist(request: DiscoveryRunRequest) -> dict:
    boards = list_boards()
    totals = {"fetched": 0, "saved": 0, "duplicates": 0}
    results = []
    for board in boards:
        try:
            found = await discover_jobs(
                board["provider"], board["company_slug"], request.limit_per_board
            )
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
                    create_job(JobListingCreate.model_validate(item))
                    saved += 1
                except ValueError:
                    duplicates += 1
            totals["fetched"] += len(found)
            totals["saved"] += saved
            totals["duplicates"] += duplicates
            results.append({
                **board, "fetched": len(found), "saved": saved,
                "duplicates": duplicates, "status": "ok",
            })
        except httpx.HTTPStatusError as error:
            results.append({
                **board, "status": "error",
                "error": f"Provider returned HTTP {error.response.status_code}.",
            })
        except httpx.HTTPError:
            results.append({
                **board, "status": "error", "error": "Public job source could not be reached.",
            })
        except (ValueError, TypeError):
            results.append({
                **board, "status": "error", "error": "Public job source returned an invalid response.",
            })
    summary = {
        "boards_scanned": sum(1 for item in results if item["status"] == "ok"),
        "boards_total": len(boards),
        **totals,
        "results": results,
    }
    record_event("discovery.watchlist_scanned", "job_source_board", None, {key: summary[key] for key in ("boards_scanned", "boards_total", "fetched", "saved", "duplicates")})
    return summary
