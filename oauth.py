"""
Minimal OAuth 2.1 Authorization Server, bolted onto the MCP server.

Why this exists: Claude's web connector UI insists on a full OAuth handshake
(metadata discovery -> dynamic client registration -> authorize -> token)
even though the actual credential is just an API key. This implements just
enough real OAuth 2.1 + PKCE to satisfy that UI.

Multi-user design: "logging in" means typing YOUR OWN MCP_API_KEY (the one
generated for you on the dashboard after signup) into this page. We hash
whatever is submitted and look it up against the control-plane `users`
table -- any valid, currently-active key for any user is accepted here.
The access token handed back to the client at the end of the flow is that
same raw API key, so the existing per-user BearerAuthMiddleware on the MCP
endpoint (auth.py) is what actually enforces which user's data gets used.
"""

import time
import secrets
import hashlib
import base64
import os
from urllib.parse import urlencode

from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.routing import Route
from starlette.requests import Request

import db_control
import security

# Render auto-populates RENDER_EXTERNAL_URL for web services at runtime.
# BASE_URL is a manual fallback for local testing or other hosts.
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("BASE_URL")
if not BASE_URL:
    raise RuntimeError(
        "Could not determine this server's public URL. "
        "Set BASE_URL manually if RENDER_EXTERNAL_URL isn't available."
    )
BASE_URL = BASE_URL.rstrip("/")

# Only allow redirecting back to Claude - prevents this OAuth server being
# abused as an open redirector to phish other sites.
ALLOWED_REDIRECT_PREFIXES = (
    "https://claude.ai/",
    "https://claude.com/",
)

# In-memory single-use authorization codes. Fine for this use case: codes
# live for ~2 minutes and are exchanged immediately by Claude's backend
# right after the redirect.
_auth_codes: dict[str, dict] = {}
CODE_TTL_SECONDS = 120


def _cleanup_codes() -> None:
    now = time.time()
    for code in [c for c, v in _auth_codes.items() if v["expires_at"] < now]:
        _auth_codes.pop(c, None)


# ---------------------------------------------------------------------------
# Discovery metadata
# ---------------------------------------------------------------------------
async def protected_resource_metadata(request: Request):
    return JSONResponse({
        "resource": f"{BASE_URL}/mcp",
        "authorization_servers": [BASE_URL],
    })


async def authorization_server_metadata(request: Request):
    return JSONResponse({
        "issuer": BASE_URL,
        "authorization_endpoint": f"{BASE_URL}/authorize",
        "token_endpoint": f"{BASE_URL}/token",
        "registration_endpoint": f"{BASE_URL}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
    })


# ---------------------------------------------------------------------------
# Dynamic Client Registration (RFC 7591) - accept any client, no secret
# ---------------------------------------------------------------------------
async def register_client(request: Request):
    body = await request.json()
    redirect_uris = body.get("redirect_uris", [])
    client_id = secrets.token_urlsafe(16)
    return JSONResponse({
        "client_id": client_id,
        "client_id_issued_at": int(time.time()),
        "redirect_uris": redirect_uris,
        "token_endpoint_auth_method": "none",
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
    })


# ---------------------------------------------------------------------------
# Authorize - shows a login page, then issues a short-lived code
# ---------------------------------------------------------------------------
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Second Brain - Authorize</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 420px; margin: 80px auto; padding: 0 20px; }}
  input {{ width: 100%; padding: 10px; margin: 12px 0; font-size: 16px; box-sizing: border-box; }}
  button {{ width: 100%; padding: 10px; font-size: 16px; cursor: pointer; }}
  .error {{ color: #c00; }}
</style>
</head>
<body>
  <h2>Authorize access to your notes</h2>
  <p>Enter the MCP API key from your <a href="/dashboard">dashboard</a> to allow this app to read your notes.</p>
  {error}
  <form method="POST" action="/authorize">
    <input type="hidden" name="client_id" value="{client_id}">
    <input type="hidden" name="redirect_uri" value="{redirect_uri}">
    <input type="hidden" name="state" value="{state}">
    <input type="hidden" name="code_challenge" value="{code_challenge}">
    <input type="hidden" name="code_challenge_method" value="{code_challenge_method}">
    <input type="password" name="api_key" placeholder="Your MCP API key" required autofocus>
    <button type="submit">Authorize</button>
  </form>
</body>
</html>
"""


async def authorize_get(request: Request):
    q = request.query_params
    redirect_uri = q.get("redirect_uri", "")
    if not redirect_uri.startswith(ALLOWED_REDIRECT_PREFIXES):
        return HTMLResponse("Invalid redirect_uri", status_code=400)

    html = LOGIN_PAGE.format(
        error="",
        client_id=q.get("client_id", ""),
        redirect_uri=redirect_uri,
        state=q.get("state", ""),
        code_challenge=q.get("code_challenge", ""),
        code_challenge_method=q.get("code_challenge_method", "S256"),
    )
    return HTMLResponse(html)


async def authorize_post(request: Request):
    form = await request.form()
    redirect_uri = form.get("redirect_uri", "")
    state = form.get("state", "")
    code_challenge = form.get("code_challenge", "")
    code_challenge_method = form.get("code_challenge_method", "S256")
    submitted_key = form.get("api_key", "")

    if not redirect_uri.startswith(ALLOWED_REDIRECT_PREFIXES):
        return HTMLResponse("Invalid redirect_uri", status_code=400)

    control_pool = db_control.get_control_pool()
    user = await db_control.get_user_by_api_key_hash(control_pool, security.hash_api_key(submitted_key))

    if user is None:
        html = LOGIN_PAGE.format(
            error='<p class="error">Incorrect key. Try again.</p>',
            client_id=form.get("client_id", ""),
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        return HTMLResponse(html, status_code=401)

    _cleanup_codes()
    code = secrets.token_urlsafe(32)
    _auth_codes[code] = {
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "expires_at": time.time() + CODE_TTL_SECONDS,
        # Handed back verbatim at the /token step below -- this is what lets
        # BearerAuthMiddleware later identify which user this session is for.
        "api_key": submitted_key,
    }

    params = {"code": code}
    if state:
        params["state"] = state
    return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=302)


# ---------------------------------------------------------------------------
# Token exchange
# ---------------------------------------------------------------------------
async def token(request: Request):
    form = await request.form()
    grant_type = form.get("grant_type")
    code = form.get("code")
    code_verifier = form.get("code_verifier", "")

    if grant_type != "authorization_code":
        return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)

    _cleanup_codes()
    entry = _auth_codes.pop(code, None)
    if not entry:
        return JSONResponse({"error": "invalid_grant"}, status_code=400)

    expected = entry["code_challenge"]
    digest = hashlib.sha256(code_verifier.encode()).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    if computed != expected:
        return JSONResponse(
            {"error": "invalid_grant", "error_description": "PKCE verification failed"},
            status_code=400,
        )

    return JSONResponse({
        "access_token": entry["api_key"],
        "token_type": "Bearer",
        "expires_in": 31536000,
    })


routes = [
    Route("/.well-known/oauth-protected-resource", protected_resource_metadata),
    Route("/.well-known/oauth-protected-resource/mcp", protected_resource_metadata),
    Route("/.well-known/oauth-authorization-server", authorization_server_metadata),
    Route("/register", register_client, methods=["POST"]),
    Route("/authorize", authorize_get, methods=["GET"]),
    Route("/authorize", authorize_post, methods=["POST"]),
    Route("/token", token, methods=["POST"]),
]

# Paths the bearer-auth middleware must NOT block, since OAuth clients hit
# these before they have any token at all.
EXEMPT_PATHS = {
    "/.well-known/oauth-protected-resource",
    "/.well-known/oauth-protected-resource/mcp",
    "/.well-known/oauth-authorization-server",
    "/register",
    "/authorize",
    "/token",
}
