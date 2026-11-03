import pytest

from app.services.ai_provider import _local_ollama_endpoint


def test_ollama_endpoint_requires_loopback_host():
    assert _local_ollama_endpoint("http://127.0.0.1:11434") == "http://127.0.0.1:11434/api/generate"
    with pytest.raises(ValueError):
        _local_ollama_endpoint("https://example.com")
    with pytest.raises(ValueError):
        _local_ollama_endpoint("http://192.168.1.10:11434")
