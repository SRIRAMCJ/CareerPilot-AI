"""Small HTTP client for the existing CareerPilot FastAPI service."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_URL = "http://127.0.0.1:8000"


class CareerPilotAPIError(RuntimeError):
    """Raised when the local CareerPilot API cannot complete a request."""


def api_base_url() -> str:
    return os.getenv("CAREERPILOT_API_URL", DEFAULT_API_URL).rstrip("/")


async def request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> Any:
    """Call the configured CareerPilot API and return its JSON response."""
    url = f"{api_base_url()}{path}"
    timeout = httpx.Timeout(30.0, connect=5.0)
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            response = await client.request(method, url, params=params, json=payload)
    except httpx.ConnectError as error:
        raise CareerPilotAPIError(
            "Cannot reach CareerPilot API. Start the local backend and verify "
            f"CAREERPILOT_API_URL (currently {api_base_url()})."
        ) from error
    except httpx.TimeoutException as error:
        raise CareerPilotAPIError("CareerPilot API request timed out.") from error

    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise CareerPilotAPIError(f"CareerPilot API returned HTTP {response.status_code}: {detail}")

    if response.status_code == 204 or not response.content:
        return {"status": "ok"}
    try:
        return response.json()
    except ValueError as error:
        raise CareerPilotAPIError("CareerPilot API returned an unexpected non-JSON response.") from error
