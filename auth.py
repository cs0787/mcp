"""
Multi-user bearer-token auth for the MCP server.

Every MCP request must include: Authorization: Bearer <MCP_API_KEY>

Unlike the original single-user version, that key is no longer compared
against one fixed value from an env var. Instead:
  1. We hash the presented key and look it up in the control-plane `users`
     table (db_control.py) to find out WHICH user it belongs to.
  2. We decrypt that user's stored Neon connection string.
  3. We get-or-create an asyncpg pool for that specific user (tenant_pools.py).
  4. We stash the user id + pool in contextvars (tenant_context.py) for the
     duration of the request, so the MCP tool functions in server.py can
     read them back out without needing to know anything about HTTP/auth.

Routes used by the signup/login/dashboard website (see webapp.py) are
exempt from this middleware -- those use cookie sessions instead, since a
browser user hasn't generated an API key yet when they're signing up.
"""

import hashlib

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse

import db_control
import security
import tenant_pools
from tenant_context import current_user_id, current_pool

# Browser-facing account pages use session cookies, not the API key -- keep
# them out of this bearer check entirely.
WEBAPP_PATH_PREFIXES = ("/signup", "/login", "/logout", "/dashboard", "/static")


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

        # Let OAuth discovery/authorize/token endpoints through unauthenticated
        # (clients need to reach these before they have any token), and let
        # the account website through (it authenticates via session cookie).
        from oauth import EXEMPT_PATHS

        if path in EXEMPT_PATHS or path.startswith(WEBAPP_PATH_PREFIXES):
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

        # Best-effort -- a slow/failed bookkeeping write should never break
        # an otherwise-valid request.
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
