"""
Minimal OAuth 2.1 Authorization Server, bolted onto the MCP server.

Why this exists: Claude's web connector UI insists on a full OAuth handshake
(metadata discovery -> dynamic client registration -> authorize -> token)
even though the actual credential this service uses is just an API key.
This implements just enough real OAuth 2.1 + PKCE to satisfy that UI.

Flow, from the user's point of view: they click "connect" in Claude, land
on /authorize here. If they're not logged in (no session cookie), they're
sent to /login?next=... first -- login/signup lives in webapp.py and sets
the same session cookie the dashboard uses. Once logged in, /authorize
shows a plain "Allow access to your notes?" consent screen (no typing a
key). Clicking Allow mints a FRESH API key scoped to this one connection
(labeled by client_id) and stores its hash in the api_keys table --
so revoking access to one connected app later, from the dashboard, doesn't
break any other app's connection.
"""

import time
import secrets
import hashlib
import base64
import html
import os
from urllib.parse import urlencode, quote

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
# Authorize - session-based consent screen, then issues a short-lived code
# ---------------------------------------------------------------------------
CONSENT_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Authorize access</title>
<style>
  body { background-color: #0b0f19; font-family: system-ui, -apple-system, sans-serif; max-width: 440px; margin: 80px auto; padding: 0 20px; color: #f3f4f6; }
  .card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(0, 242, 254, 0.2); box-shadow: 0 0 25px rgba(0, 242, 254, 0.1); border-radius: 12px; padding: 24px; }
  h2 { color: #fff; font-weight: 600; letter-spacing: -0.5px; margin-top: 0; }
  button { width: 100%; padding: 12px; font-size: 15px; font-weight: 500; cursor: pointer; border: none; border-radius: 8px; margin-top: 12px; transition: all 0.2s ease; }
  .allow { background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); color: #0b0f19; box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3); }
  .allow:hover { opacity: 0.9; transform: translateY(-1px); }
  .deny { background: transparent; color: #9ca3af; border: 1px solid rgba(255, 255, 255, 0.1); }
  .deny:hover { background: rgba(255, 255, 255, 0.05); color: #fff; }
  .warn { color: #f87171; }
  .muted { color: #9ca3af; font-size: 14px; line-height: 1.5; }
  .link-btn { all: unset; color: #38bdf8; text-decoration: underline; cursor: pointer; font-size: 13px; }
  .link-btn:hover { color: #7dd3fc; }
</style>
</head>
<body>
  <div class="card">
    <h2>Allow access to your notes?</h2>
    <p class="muted">
      Signed in as {email}.
      <form method="POST" action="/logout" style="display:inline">
        <input type="hidden" name="next" value="{authorize_next}">
        <button type="submit" class="link-btn">Not you?</button>
      </form>
    </p>
    {body}
  </div>
</body>
</html>
"""


def _hidden_fields(q) -> str:
    return f"""
    <input type="hidden" name="client_id" value="{q.get('client_id', '')}">
    <input type="hidden" name="redirect_uri" value="{q.get('redirect_uri', '')}">
    <input type="hidden" name="state" value="{q.get('state', '')}">
    <input type="hidden" name="code_challenge" value="{q.get('code_challenge', '')}">
    <input type="hidden" name="code_challenge_method" value="{q.get('code_challenge_method', 'S256')}">
    """


def _redirect_to_login(request: Request) -> RedirectResponse:
    next_url = request.url.path
    if request.url.query:
        next_url += "?" + request.url.query
    return RedirectResponse(f"/login?next={quote(next_url, safe='')}", status_code=302)


async def authorize_get(request: Request):
    q = request.query_params
    redirect_uri = q.get("redirect_uri", "")
    if not redirect_uri.startswith(ALLOWED_REDIRECT_PREFIXES):
        return HTMLResponse("Invalid redirect_uri", status_code=400)

    user_id = request.session.get("user_id")
    if not user_id:
        return _redirect_to_login(request)

    control_pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(control_pool, user_id)
    if user is None:
        request.session.clear()
        return _redirect_to_login(request)

    hidden = _hidden_fields(q)
    authorize_next = html.escape(request.url.path + "?" + request.url.query, quote=True)

    if not user["connection_string_encrypted"]:
        body = f"""
        <p class="warn">You haven't added a Neon connection string yet.</p>
        <p class="muted">Add one from your dashboard, then come back and authorize again.</p>
        <button type="button" class="allow" onclick="window.location='/dashboard'">Go to dashboard</button>
        <form method="POST" action="/authorize">
          {hidden}
          <button type="submit" name="decision" value="deny" class="deny">Cancel</button>
        </form>
        """
    else:
        body = f"""
        <form method="POST" action="/authorize">
          {hidden}
          <button type="submit" name="decision" value="allow" class="allow">Allow</button>
          <button type="submit" name="decision" value="deny" class="deny">Deny</button>
        </form>
        """

    html_out = CONSENT_PAGE.format(email=user["email"], authorize_next=authorize_next, body=body)
    return HTMLResponse(html_out)


async def authorize_post(request: Request):
    form = await request.form()
    redirect_uri = form.get("redirect_uri", "")
    state = form.get("state", "")
    code_challenge = form.get("code_challenge", "")
    code_challenge_method = form.get("code_challenge_method", "S256")
    client_id = form.get("client_id", "")
    decision = form.get("decision", "deny")

    if not redirect_uri.startswith(ALLOWED_REDIRECT_PREFIXES):
        return HTMLResponse("Invalid redirect_uri", status_code=400)

    if decision != "allow":
        params = {"error": "access_denied"}
        if state:
            params["state"] = state
        return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=302)

    user_id = request.session.get("user_id")
    if not user_id:
        # Session expired between showing the consent screen and submitting
        # it -- send them through login again with the same params.
        next_url = "/authorize?" + urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        })
        return RedirectResponse(f"/login?next={quote(next_url, safe='')}", status_code=302)

    control_pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(control_pool, user_id)
    if user is None or not user["connection_string_encrypted"]:
        # Shouldn't normally be reachable (the consent screen already gates
        # on this), but never hand out a token for a not-yet-usable account.
        return RedirectResponse("/dashboard", status_code=302)

    # Mint a FRESH key for this one connection rather than reusing a single
    # shared key -- each connected AI app can be revoked independently from
    # the dashboard without breaking the others.
    raw_key = security.generate_api_key()
    label = f"{client_id or 'AI app'} (connected {time.strftime('%Y-%m-%d')})"
    await db_control.create_api_key(control_pool, user_id, security.hash_api_key(raw_key), label)

    _cleanup_codes()
    code = secrets.token_urlsafe(32)
    _auth_codes[code] = {
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "expires_at": time.time() + CODE_TTL_SECONDS,
        # Handed back verbatim at the /token step below.
        "api_key": raw_key,
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
# these before they have any token at all. (/authorize itself relies on the
# session cookie, handled the same way the webapp.py pages are -- see
# WEBAPP_PATH_PREFIXES in auth.py.)
EXEMPT_PATHS = {
    "/.well-known/oauth-protected-resource",
    "/.well-known/oauth-protected-resource/mcp",
    "/.well-known/oauth-authorization-server",
    "/register",
    "/authorize",
    "/token",
}
