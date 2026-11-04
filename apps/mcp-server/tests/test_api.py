from careerpilot_mcp.api import DEFAULT_API_URL, api_base_url


def test_default_api_url(monkeypatch):
    monkeypatch.delenv("CAREERPILOT_API_URL", raising=False)
    assert api_base_url() == DEFAULT_API_URL


def test_custom_api_url_is_normalized(monkeypatch):
    monkeypatch.setenv("CAREERPILOT_API_URL", "http://127.0.0.1:9000/")
    assert api_base_url() == "http://127.0.0.1:9000"
