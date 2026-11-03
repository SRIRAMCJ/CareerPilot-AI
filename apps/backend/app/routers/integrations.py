from urllib.parse import quote_plus

from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/integrations", tags=["job-board integrations"])

BOARD_TEMPLATES = {
    "linkedin": "https://www.linkedin.com/jobs/search/?keywords={query}&location={location}",
    "naukri": "https://www.naukri.com/{query}-jobs-in-{location}",
    "indeed": "https://in.indeed.com/jobs?q={query}&l={location}",
    "foundit": "https://www.foundit.in/srp/results?query={query}&locations={location}",
}


@router.get("/job-boards")
def job_board_search_links(
    query: str = Query(min_length=1, max_length=120),
    location: str = Query(default="India", max_length=100),
) -> dict:
    """Build search links; authenticated job-board pages are not scraped."""
    encoded_query = quote_plus(query.strip())
    encoded_location = quote_plus(location.strip())
    return {
        "query": query.strip(), "location": location.strip(),
        "items": [
            {"provider": provider, "url": template.format(
                query=encoded_query, location=encoded_location),
             "mode": "user_session"}
            for provider, template in BOARD_TEMPLATES.items()
        ],
        "notice": (
            "Open the board in your own browser session. CareerPilot does not collect board "
            "passwords, scrape private pages, or bypass CAPTCHA, access controls, or rate limits."
        ),
    }
