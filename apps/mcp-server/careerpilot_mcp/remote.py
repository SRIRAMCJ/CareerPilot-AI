"""Authentication middleware for the remotely hosted Streamable HTTP MCP endpoint."""

from __future__ import annotations

import hmac
import json
from typing import Any


class BearerTokenAuthMiddleware:
    """Require one configured bearer token before forwarding any HTTP MCP request."""

    def __init__(self, app: Any, token: str) -> None:
        if not token:
            raise ValueError("A non-empty MCP bearer token is required.")
        self.app = app
        self.expected = f"Bearer {token}".encode()

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        supplied = headers.get(b"authorization", b"")
        if not hmac.compare_digest(supplied, self.expected):
            body = json.dumps({"error": "Unauthorized"}).encode("utf-8")
            await send(
                {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode("ascii")),
                        (b"cache-control", b"no-store"),
                        (b"www-authenticate", b"Bearer"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        await self.app(scope, receive, send)
