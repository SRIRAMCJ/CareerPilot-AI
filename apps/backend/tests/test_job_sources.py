from app.services.job_sources import html_to_text


def test_html_to_text_removes_markup_and_normalizes_whitespace():
    assert html_to_text("<h1>Python</h1><p>Build   APIs</p>") == "Python Build APIs"


from app.services.job_sources import _skills


def test_skill_extraction_uses_token_boundaries():
    assert _skills("Experience with JavaScript and Python") == ["Python", "JavaScript"]
