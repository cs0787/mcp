"""
Multi-user bearer-token auth for the MCP server.

Every MCP request must include: Authorization: Bearer <MCP_API_KEY>
Routes used by the website (landing page, signup, login, dashboard) are exempt.
"""

import hashlib

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse

import db_control
import security
import tenant_pools
from tenant_context import current_user_id, current_pool

# Paths that do not require Bearer token auth
WEBAPP_EXACT_PATHS = {"/", ""}
WEBAPP_PATH_PREFIXES = ("/signup", "/login", "/logout", "/dashboard", "/static" , "/console")


def hash_token(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class BearerAuthMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        from oauth import EXEMPT_PATHS

        # Allow public web app pages and OAuth discovery endpoints through unauthenticated
        if (
            path in WEBAPP_EXACT_PATHS
            or path in EXEMPT_PATHS
            or any(path.startswith(prefix) for prefix in WEBAPP_PATH_PREFIXES)
        ):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()

        if not auth_header.startswith("Bearer "):
            await _reject(scope, receive, send, "Unauthorized")
            return

        raw_key = auth_header[len("Bearer "):].strip()

        control_pool = db_control.get_control_pool()
        owner = await db_control.get_active_key_owner(control_pool, hash_token(raw_key))
        if owner is None:
            await _reject(scope, receive, send, "Unauthorized")
            return

        if not owner["connection_string_encrypted"]:
            await _reject(
                scope,
                receive,
                send,
                "No Neon connection string is configured for this account yet. "
                "Add it from your dashboard before connecting an AI app.",
                status_code=412,
            )
            return

        try:
            connection_string = security.decrypt_text(owner["connection_string_encrypted"])
            user_pool = await tenant_pools.get_manager().get_pool(str(owner["user_id"]), connection_string)
        except Exception as e:
            await _reject(scope, receive, send, f"Could not connect to your database: {e}", status_code=502)
            return

        try:
            await db_control.touch_api_key_last_used(control_pool, str(owner["api_key_id"]))
        except Exception:
            pass

        user_id_token = current_user_id.set(str(owner["user_id"]))
        pool_token = current_pool.set(user_pool)
        try:
            await self.app(scope, receive, send)
        finally:
            current_user_id.reset(user_id_token)
            current_pool.reset(pool_token)


async def _reject(scope: Scope, receive: Receive, send: Send, message: str, status_code: int = 401) -> None:
    response = JSONResponse({"error": message}, status_code=status_code)
    await response(scope, receive, send)
