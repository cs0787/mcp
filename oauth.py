"""
Minimal OAuth 2.1 Authorization Server, adjusted for Vercel runtime.
Monochromatic UI styling.
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


def get_base_url(request: Request | None = None) -> str:
    base_url = os.environ.get("BASE_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not base_url and os.environ.get("VERCEL_URL"):
        base_url = f"https://{os.environ.get('VERCEL_URL')}"
    if not base_url and request:
        base_url = str(request.base_url).rstrip("/")
    if not base_url:
        base_url = "http://localhost:8000"
    return base_url.rstrip("/")


ALLOWED_REDIRECT_PREFIXES = (
    "https://claude.ai/",
    "https://claude.com/",
)

_auth_codes: dict[str, dict] = {}
CODE_TTL_SECONDS = 120


def _cleanup_codes() -> None:
    now = time.time()
    for code in [c for c, v in _auth_codes.items() if v["expires_at"] < now]:
        _auth_codes.pop(c, None)


async def protected_resource_metadata(request: Request):
    base_url = get_base_url(request)
    return JSONResponse({
        "resource": f"{base_url}/mcp",
        "authorization_servers": [base_url],
    })


async def authorization_server_metadata(request: Request):
    base_url = get_base_url(request)
    return JSONResponse({
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/authorize",
        "token_endpoint": f"{base_url}/token",
        "registration_endpoint": f"{base_url}/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
    })


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


CONSENT_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Authorize access</title>
<style>
  body {{
    background-color: #050505;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, sans-serif;
    max-width: 420px; margin: 80px auto; padding: 0 20px; color: #ffffff;
    -webkit-font-smoothing: antialiased;
  }}
  .card {{
    background: #0d0d0f; border: 1px solid #222226;
    border-radius: 14px; padding: 24px; box-shadow: 0 20px 40px rgba(0,0,0,0.8);
  }}
  h2 {{ color: #ffffff; font-weight: 700; letter-spacing: -0.03em; margin-top: 0; font-size: 22px; }}
  button {{
    width: 100%; padding: 12px; font-size: 14px; font-weight: 600; cursor: pointer;
    border-radius: 8px; margin-top: 10px; transition: all 0.2s ease;
  }}
  .allow {{ background: #ffffff; color: #000000; border: 1px solid #ffffff; }}
  .allow:hover {{ background: #e4e4e7; border-color: #e4e4e7; }}
  .deny {{ background: #141417; color: #a1a1aa; border: 1px solid #222226; }}
  .deny:hover {{ background: #1c1c20; color: #ffffff; }}
  .warn {{ color: #f87171; font-size: 14px; }}
  .muted {{ color: #a1a1aa; font-size: 14px; line-height: 1.5; }}
  .link-btn {{ all: unset; color: #ffffff; text-decoration: underline; cursor: pointer; font-size: 13px; }}
</style>
</head>
<body>
  <div class="card">
    <h2>Authorize Access</h2>
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
        <button type="button" class="allow" onclick="window.location='/dashboard'">Go to Dashboard</button>
        <form method="POST" action="/authorize">
          {hidden}
          <button type="submit" name="decision" value="deny" class="deny">Cancel</button>
        </form>
        """
    else:
        body = f"""
        <form method="POST" action="/authorize">
          {hidden}
          <button type="submit" name="decision" value="allow" class="allow">Allow Connection</button>
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
        return RedirectResponse("/dashboard", status_code=302)

    raw_key = security.generate_api_key()
    label = f"{client_id or 'AI app'} (connected {time.strftime('%Y-%m-%d')})"
    await db_control.create_api_key(control_pool, user_id, security.hash_api_key(raw_key), label)

    _cleanup_codes()
    code = secrets.token_urlsafe(32)
    _auth_codes[code] = {
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "expires_at": time.time() + CODE_TTL_SECONDS,
        "api_key": raw_key,
    }

    params = {"code": code}
    if state:
        params["state"] = state
    return RedirectResponse(f"{redirect_uri}?{urlencode(params)}", status_code=302)


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

EXEMPT_PATHS = {
    "/.well-known/oauth-protected-resource",
    "/.well-known/oauth-protected-resource/mcp",
    "/.well-known/oauth-authorization-server",
    "/register",
    "/authorize",
    "/token",
}
