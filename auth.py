"""
Minimal bearer-token auth for the MCP server.

Every request must include: Authorization: Bearer <MCP_API_KEY>
This is enough for a single-user personal connector. If you ever want to
share this server with others, swap this for real OAuth (the mcp SDK
supports OAuthAuthorizationServerProvider) instead of a shared secret.
"""

import os
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse

API_KEY = os.environ.get("MCP_API_KEY")
if not API_KEY:
    raise RuntimeError("MCP_API_KEY environment variable is not set")


class BearerAuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()

        if auth_header != f"Bearer {API_KEY}":
            response = JSONResponse(
                {"error": "Unauthorized"},
                status_code=401,
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
