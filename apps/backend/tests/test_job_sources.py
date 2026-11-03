from app.services.job_sources import html_to_text


def test_html_to_text_removes_markup_and_normalizes_whitespace():
    assert html_to_text("<h1>Python</h1><p>Build   APIs</p>") == "Python Build APIs"
