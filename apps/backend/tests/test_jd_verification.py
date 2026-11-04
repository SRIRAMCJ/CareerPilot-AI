from app.services.jd_verification import verify_job_description


def test_complete_jd_is_ready_for_candidate_review():
    result = verify_job_description({
        "id": 7, "title": "AI Engineer", "company": "Example Labs",
        "location": "Chennai", "description": "Python and machine learning " * 30,
        "source": "greenhouse", "source_job_id": "gh-123",
        "posted_date": "2026-11-01", "url": "https://boards.greenhouse.io/example/jobs/123",
    })
    assert result["status"] == "ready_for_candidate_review"
    assert result["completeness_score"] == 100
    assert result["candidate_review_required"] is True


def test_incomplete_or_insecure_jd_requires_verification():
    result = verify_job_description({
        "id": 8, "title": "Engineer", "company": "Example",
        "description": "Short description", "url": "http://localhost/apply",
    })
    assert result["status"] == "needs_verification"
    assert "application_url" in result["missing_fields"]
    assert "description" in result["missing_fields"]


def test_old_listing_gets_freshness_warning():
    result = verify_job_description({
        "id": 9, "title": "AI Engineer", "company": "Example",
        "description": "Detailed JD " * 80, "source": "lever",
        "source_job_id": "abc", "posted_date": "2026-01-01",
        "url": "https://jobs.example.com/123",
    })
    assert any("days old" in warning for warning in result["warnings"])
