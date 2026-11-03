from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "careerpilot-api"}


def test_system_endpoint_keeps_external_automation_disabled_by_default() -> None:
    response = client.get("/api/v1/system")

    assert response.status_code == 200
    payload = response.json()
    assert payload["integrations"]["browser_automation"] is False
    assert payload["integrations"]["application_submission"] is False
