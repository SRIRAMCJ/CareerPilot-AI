from __future__ import annotations

import pytest

from careerpilot_mcp.remote import BearerTokenAuthMiddleware


@pytest.mark.asyncio
async def test_remote_mcp_rejects_missing_bearer_token() -> None:
    called = False

    async def app(scope, receive, send):
        nonlocal called
        called = True

    messages = []

    async def send(message):
        messages.append(message)

    middleware = BearerTokenAuthMiddleware(app, "secret-token")
    await middleware(
        {"type": "http", "headers": []},
        lambda: None,
        send,
    )

    assert called is False
    assert messages[0]["status"] == 401
    assert (b"www-authenticate", b"Bearer") in messages[0]["headers"]


@pytest.mark.asyncio
async def test_remote_mcp_accepts_valid_bearer_token() -> None:
    called = False

    async def app(scope, receive, send):
        nonlocal called
        called = True

    async def send(message):
        return None

    middleware = BearerTokenAuthMiddleware(app, "secret-token")
    await middleware(
        {"type": "http", "headers": [(b"authorization", b"Bearer secret-token")]},
        lambda: None,
        send,
    )

    assert called is True
