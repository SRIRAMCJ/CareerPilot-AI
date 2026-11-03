from app.routers.browser_automation import _field_value, _safe_job_url
from app.routers.integrations import job_board_search_links


def test_job_board_links_include_all_requested_providers():
    result = job_board_search_links(query="AI Engineer", location="Chennai")
    providers = {item["provider"] for item in result["items"]}
    assert providers == {"linkedin", "naukri", "indeed", "foundit"}
    assert all("AI+Engineer" in item["url"] or "AI%20Engineer" in item["url"] for item in result["items"])
    assert all("Chennai" in item["url"] for item in result["items"])


def test_browser_field_mapping_uses_only_verified_profile_values():
    profile = {"full_name": "Test Candidate", "email": "candidate@example.com",
               "phone": "9000000000", "location": "Chennai",
               "professional_summary": "Verified summary"}
    assert _field_value("email", profile) == "candidate@example.com"
    assert _field_value("first_name", profile) == "Test"
    assert _field_value("last_name", profile) == "Candidate"
    assert _field_value("password", profile) is None
    assert _field_value("captcha_response", profile) is None
    assert _field_value("gender", profile) is None


def test_browser_rejects_non_https_and_private_destinations():
    for url in ("http://example.com/apply", "https://127.0.0.1/apply", "https://localhost/apply"):
        try:
            _safe_job_url(url)
        except Exception:
            pass
        else:
            raise AssertionError(f"Unsafe URL was accepted: {url}")


def test_browser_accepts_public_https_job_url():
    assert _safe_job_url("https://jobs.example.com/apply/123") == "https://jobs.example.com/apply/123"
