"""
The account website: signup, login, and a dashboard with a professional 
Neon dark aesthetic.
"""

import asyncpg
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route

import db_control
import security
import tenant_pools

PAGE_STYLE = """
  body { background-color: #0b0f19; font-family: system-ui, -apple-system, sans-serif; max-width: 520px; margin: 60px auto; padding: 0 20px; color: #f3f4f6; }
  h2 { margin-bottom: 4px; color: #fff; font-weight: 600; letter-spacing: -0.5px; }
  .muted { color: #9ca3af; font-size: 14px; line-height: 1.5; }
  input { width: 100%; padding: 12px; margin: 8px 0; font-size: 14px; box-sizing: border-box; background: #030712; border: 1px solid rgba(255, 255, 255, 0.1); color: #fff; border-radius: 8px; outline: none; transition: border-color 0.2s; }
  input:focus { border-color: #00f2fe; box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); }
  button { width: 100%; padding: 12px; font-size: 15px; font-weight: 500; cursor: pointer; border: none; border-radius: 8px; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); color: #0b0f19; margin-top: 8px; transition: opacity 0.2s, transform 0.1s; box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2); }
  button:hover { opacity: 0.9; transform: translateY(-1px); }
  button.secondary { background: rgba(255, 255, 255, 0.05); color: #f3f4f6; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: none; }
  button.secondary:hover { background: rgba(255, 255, 255, 0.1); }
  button.small { width: auto; padding: 6px 12px; font-size: 13px; margin-top: 0; }
  button.danger { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); box-shadow: none; }
  button.danger:hover { background: rgba(239, 68, 68, 0.2); }
  .error { color: #f87171; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 10px; border-radius: 8px; font-size: 14px; margin: 10px 0; }
  .card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(0, 242, 254, 0.2); box-shadow: 0 0 25px rgba(0, 242, 254, 0.05); border-radius: 12px; padding: 20px; margin: 20px 0; }
  .key-box { font-family: ui-monospace, monospace; background: #030712; border: 1px solid rgba(0, 242, 254, 0.4); color: #00f2fe; padding: 12px; border-radius: 8px; word-break: break-all; font-size: 13px; margin-top: 8px; box-shadow: inset 0 0 10px rgba(0, 242, 254, 0.1); }
  a { color: #38bdf8; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .top-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 16px; }
  .key-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
  .key-row:last-child { border-bottom: none; }
  code { background: rgba(255, 255, 255, 0.05); padding: 2px 6px; border-radius: 4px; font-family: ui-monospace, monospace; font-size: 13px; color: #38bdf8; }
"""


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head><title>{title}</title><style>{PAGE_STYLE}</style></head>
<body>{body}</body>
</html>
""")


def _require_login(request: Request) -> str | None:
    return request.session.get("user_id")


def _safe_next(raw: str | None) -> str:
    if raw and raw.startswith("/") and not raw.startswith("//"):
        return raw
    return "/dashboard"


async def signup_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    return _page("Sign up", f"""
<h2>Create Account</h2>
<p class="muted">Set up your Neon MCP gateway credentials.</p>
<form method="POST" action="/signup">
  <input type="hidden" name="next" value="{next_}">
  <input type="email" name="email" placeholder="Email address" required autofocus>
  <input type="password" name="password" placeholder="Password (min 8 characters)" minlength="8" required>
  <button type="submit">Create Account</button>
</form>
<p class="muted" style="margin-top: 16px;">Already have an account? <a href="/login?next={next_}">Log in</a></p>
""")


async def signup_post(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    next_ = _safe_next(str(form.get("next", "")))

    error = None
    if "@" not in email:
        error = "Enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."

    if error:
        return _page("Sign up", f"""
<h2>Create Account</h2>
<div class="error">{error}</div>
<form method="POST" action="/signup">
  <input type="hidden" name="next" value="{next_}">
  <input type="email" name="email" placeholder="Email address" value="{email}" required autofocus>
  <input type="password" name="password" placeholder="Password (min 8 characters)" minlength="8" required>
  <button type="submit">Create Account</button>
</form>
""")

    pool = db_control.get_control_pool()
    try:
        user_id = await db_control.create_user(pool, email, security.hash_password(password))
    except asyncpg.exceptions.UniqueViolationError:
        return _page("Sign up", f"""
<h2>Create Account</h2>
<div class="error">An account with that email already exists.</div>
<p><a href="/login?next={next_}">Log in instead</a></p>
""")

    request.session["user_id"] = user_id
    return RedirectResponse(next_, status_code=302)


async def login_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    return _page("Log in", f"""
<h2>Welcome Back</h2>
<p class="muted">Access your MCP control panel.</p>
<form method="POST" action="/login">
  <input type="hidden" name="next" value="{next_}">
  <input type="email" name="email" placeholder="Email address" required autofocus>
  <input type="password" name="password" placeholder="Password" required>
  <button type="submit">Log In</button>
</form>
<p class="muted" style="margin-top: 16px;">No account yet? <a href="/signup?next={next_}">Sign up</a></p>
""")


async def login_post(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    next_ = _safe_next(str(form.get("next", "")))

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_email(pool, email)

    if user is None or not security.verify_password(password, user["password_hash"]):
        return _page("Log in", f"""
<h2>Welcome Back</h2>
<div class="error">Incorrect email or password.</div>
<form method="POST" action="/login">
  <input type="hidden" name="next" value="{next_}">
  <input type="email" name="email" placeholder="Email address" value="{email}" required autofocus>
  <input type="password" name="password" placeholder="Password" required>
  <button type="submit">Log In</button>
</form>
""")

    request.session["user_id"] = str(user["id"])
    return RedirectResponse(next_, status_code=302)


async def logout(request: Request):
    form = await request.form()
    next_ = str(form.get("next", "")) if form.get("next") else None
    request.session.clear()
    if next_ and next_.startswith("/") and not next_.startswith("//"):
        return RedirectResponse(f"/login?next={next_}", status_code=302)
    return RedirectResponse("/login", status_code=302)


async def dashboard_get(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(pool, user_id)
    if user is None:
        request.session.clear()
        return RedirectResponse("/login", status_code=302)

    flash_key = request.session.pop("flash_api_key", None)
    flash_html = ""
    if flash_key:
        flash_html = f"""
<div class="card" style="border-color: #00f2fe;">
  <strong style="color: #00f2fe;">New MCP_API_KEY Generated (Save it now!):</strong>
  <div class="key-box">{flash_key}</div>
  <p class="muted" style="margin-top: 8px;">Use this token securely as your Bearer authorization string.</p>
</div>
"""

    if user["connection_string_encrypted"]:
        masked = security.mask_connection_string(security.decrypt_text(user["connection_string_encrypted"]))
        conn_status = f'<p class="muted">Linked Neon DB: <code>{masked}</code></p>'
    else:
        conn_status = '<div class="error">No Neon connection string added yet. Connect one below to activate your MCP queries.</div>'

    keys = await db_control.list_api_keys(pool, user_id)
    active_keys = [k for k in keys if k["revoked_at"] is None]
    if active_keys:
        rows = "".join(f"""
<div class="key-row">
  <div>
    <div style="font-weight: 500; color: #fff;">{k['label']}</div>
    <div class="muted">Created {k['created_at'].strftime('%b %d, %Y')}</div>
  </div>
  <form method="POST" action="/dashboard/api-key/revoke" style="margin: 0;">
    <input type="hidden" name="key_id" value="{k['id']}">
    <button type="submit" class="danger small" onclick="return confirm('Revoke this key?');">Revoke</button>
  </form>
</div>
""" for k in active_keys)
    else:
        rows = '<p class="muted">No active API keys found.</p>'

    base_url = str(request.base_url).rstrip("/")

    return _page("Dashboard & Settings", f"""
<div class="top-nav">
  <div>
    <h2>Settings & Control Panel</h2>
    <div class="muted">{user["email"]}</div>
  </div>
  <form method="POST" action="/logout" style="margin:0;"><button class="secondary small">Log out</button></form>
</div>

{flash_html}

<div class="card">
  <strong style="color: #fff; font-size: 16px;">1. Neon Connection String</strong>
  <p class="muted">Configure your secure database endpoint used by the MCP server.</p>
  {conn_status}
  <form method="POST" action="/dashboard/connection-string" style="margin-top: 12px;">
    <input type="text" name="connection_string" placeholder="postgresql://user:password@ep-xxx.neon.tech/dbname" required>
    <button type="submit">Save Connection String</button>
  </form>
</div>

<div class="card">
  <strong style="color: #fff; font-size: 16px;">2. MCP API Keys</strong>
  <p class="muted">Generate or manage your explicit <code>MCP_API_KEY</code> tokens for client authentication.</p>
  <div style="margin-top: 12px;">
    {rows}
  </div>
  <form method="POST" action="/dashboard/api-key/create" style="margin-top:16px;">
    <button type="submit" class="secondary">Generate New MCP_API_KEY</button>
  </form>
</div>

<div class="card">
  <strong style="color: #fff; font-size: 16px;">3. MCP Server Endpoint</strong>
  <p class="muted" style="margin-top: 8px;">Your connection endpoint for Claude or other clients:</p>
  <div class="key-box">{base_url}/mcp</div>
</div>
""")


async def update_connection_string(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    connection_string = str(form.get("connection_string", "")).strip()

    if not (connection_string.startswith("postgresql://") or connection_string.startswith("postgres://")):
        return _dashboard_error("Invalid format: Must start with postgresql://")

    ok, err = await tenant_pools.test_connection_string(connection_string)
    if not ok:
        return _dashboard_error(f"Connection test failed: {err}")

    pool = db_control.get_control_pool()
    await db_control.set_connection_string(pool, user_id, security.encrypt_text(connection_string))
    await tenant_pools.get_manager().invalidate(user_id)

    return RedirectResponse("/dashboard", status_code=302)


async def create_api_key(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    pool = db_control.get_control_pool()
    raw_key = security.generate_api_key()
    await db_control.create_api_key(pool, user_id, security.hash_api_key(raw_key), "Manual Dashboard Key")
    request.session["flash_api_key"] = raw_key

    return RedirectResponse("/dashboard", status_code=302)


async def revoke_api_key(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    key_id = str(form.get("key_id", ""))

    pool = db_control.get_control_pool()
    await db_control.revoke_api_key(pool, user_id, key_id)

    return RedirectResponse("/dashboard", status_code=302)


def _dashboard_error(message: str) -> HTMLResponse:
    return _page("Dashboard", f"""
<h2>Settings & Control Panel</h2>
<div class="error">{message}</div>
<p style="margin-top: 16px;"><a href="/dashboard">Back to dashboard</a></p>
""")


routes = [
    Route("/signup", signup_get, methods=["GET"]),
    Route("/signup", signup_post, methods=["POST"]),
    Route("/login", login_get, methods=["GET"]),
    Route("/login", login_post, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/dashboard", dashboard_get, methods=["GET"]),
    Route("/dashboard/connection-string", update_connection_string, methods=["POST"]),
    Route("/dashboard/api-key/create", create_api_key, methods=["POST"]),
    Route("/dashboard/api-key/revoke", revoke_api_key, methods=["POST"]),
]
