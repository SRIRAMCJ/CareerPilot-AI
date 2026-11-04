from fastapi.testclient import TestClient

from app.main import app, settings

client = TestClient(app)


def test_health_endpoint_remains_public_for_platform_probes() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_personal_api_requires_the_shared_proxy_token_in_production(monkeypatch) -> None:
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "careerpilot_proxy_token", "test-proxy-secret")

    unauthorized = client.get("/api/v1/system")
    assert unauthorized.status_code == 401

    authorized = client.get(
        "/api/v1/system",
        headers={"X-CareerPilot-Proxy-Token": "test-proxy-secret"},
    )
    assert authorized.status_code == 200
