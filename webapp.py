"""
The account website: signup, login, and a dashboard where a user pastes
their own Neon connection string and gets/regenerates their MCP API key.

Deliberately plain server-rendered HTML (no JS framework, no template
engine dependency) to match the rest of this small service. Sessions are
cookie-based via Starlette's SessionMiddleware (see server.py), separate
from the MCP API key entirely -- the API key is what AI apps use, the
session cookie is what a human's browser uses.
"""

import asyncpg
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route

import db_control
import security
import tenant_pools

PAGE_STYLE = """
  body { font-family: system-ui, sans-serif; max-width: 480px; margin: 60px auto; padding: 0 20px; color: #1a1a1a; }
  h2 { margin-bottom: 4px; }
  .muted { color: #666; font-size: 14px; }
  input { width: 100%; padding: 10px; margin: 8px 0; font-size: 15px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 6px; }
  button { width: 100%; padding: 10px; font-size: 15px; cursor: pointer; border: none; border-radius: 6px; background: #1a1a1a; color: #fff; margin-top: 6px; }
  button.secondary { background: #eee; color: #1a1a1a; }
  .error { color: #c00; }
  .card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 16px 0; }
  .key-box { font-family: ui-monospace, monospace; background: #f5f5f5; padding: 10px; border-radius: 6px; word-break: break-all; font-size: 13px; }
  a { color: #1a1a1a; }
  .top-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
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


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------
async def signup_get(request: Request):
    if _require_login(request):
        return RedirectResponse("/dashboard", status_code=302)
    return _page("Sign up", """
<h2>Create your account</h2>
<p class="muted">This account is for the MCP connector itself, separate from
your notes app login.</p>
<form method="POST" action="/signup">
  <input type="email" name="email" placeholder="Email" required autofocus>
  <input type="password" name="password" placeholder="Password (min 8 characters)" minlength="8" required>
  <button type="submit">Sign up</button>
</form>
<p class="muted">Already have an account? <a href="/login">Log in</a></p>
""")


async def signup_post(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))

    error = None
    if "@" not in email:
        error = "Enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."

    if error:
        return _page("Sign up", f"""
<h2>Create your account</h2>
<p class="error">{error}</p>
<form method="POST" action="/signup">
  <input type="email" name="email" placeholder="Email" value="{email}" required autofocus>
  <input type="password" name="password" placeholder="Password (min 8 characters)" minlength="8" required>
  <button type="submit">Sign up</button>
</form>
""")

    pool = db_control.get_control_pool()
    try:
        user_id = await db_control.create_user(pool, email, security.hash_password(password))
    except asyncpg.exceptions.UniqueViolationError:
        return _page("Sign up", """
<h2>Create your account</h2>
<p class="error">An account with that email already exists.</p>
<p><a href="/login">Log in instead</a></p>
""")

    # Issue the first API key immediately so signup -> working connector is
    # one step. It's shown once on the dashboard right after this redirect.
    raw_key = security.generate_api_key()
    await db_control.set_api_key_hash(pool, user_id, security.hash_api_key(raw_key))

    request.session["user_id"] = user_id
    request.session["flash_api_key"] = raw_key
    return RedirectResponse("/dashboard", status_code=302)


# ---------------------------------------------------------------------------
# Login / logout
# ---------------------------------------------------------------------------
async def login_get(request: Request):
    if _require_login(request):
        return RedirectResponse("/dashboard", status_code=302)
    return _page("Log in", """
<h2>Log in</h2>
<form method="POST" action="/login">
  <input type="email" name="email" placeholder="Email" required autofocus>
  <input type="password" name="password" placeholder="Password" required>
  <button type="submit">Log in</button>
</form>
<p class="muted">No account yet? <a href="/signup">Sign up</a></p>
""")


async def login_post(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_email(pool, email)

    if user is None or not security.verify_password(password, user["password_hash"]):
        return _page("Log in", f"""
<h2>Log in</h2>
<p class="error">Incorrect email or password.</p>
<form method="POST" action="/login">
  <input type="email" name="email" placeholder="Email" value="{email}" required autofocus>
  <input type="password" name="password" placeholder="Password" required>
  <button type="submit">Log in</button>
</form>
""")

    request.session["user_id"] = str(user["id"])
    return RedirectResponse("/dashboard", status_code=302)


async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
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
<div class="card">
  <strong>Your MCP API key (shown once -- copy it now):</strong>
  <div class="key-box">{flash_key}</div>
  <p class="muted">Use this as the Bearer token / password when connecting an AI app.
  It won't be shown again -- regenerate below if you lose it.</p>
</div>
"""

    if user["connection_string_encrypted"]:
        masked = security.mask_connection_string(security.decrypt_text(user["connection_string_encrypted"]))
        conn_status = f'<p class="muted">Currently set to: <code>{masked}</code></p>'
    else:
        conn_status = '<p class="error">No connection string set yet -- your MCP connector will not work until you add one.</p>'

    base_url = str(request.base_url).rstrip("/")

    return _page("Dashboard", f"""
<div class="top-nav">
  <h2>Dashboard</h2>
  <form method="POST" action="/logout"><button class="secondary" style="width:auto;padding:6px 14px;">Log out</button></form>
</div>
<p class="muted">{user["email"]}</p>

{flash_html}

<div class="card">
  <strong>Your Neon connection string</strong>
  <p class="muted">Paste the SAME connection string your notes app uses to sync (the
  <code>postgresql://...</code> URL for your personal Neon database).</p>
  {conn_status}
  <form method="POST" action="/dashboard/connection-string">
    <input type="text" name="connection_string" placeholder="postgresql://user:password@ep-xxx.aws.neon.tech/dbname" required>
    <button type="submit">Save connection string</button>
  </form>
</div>

<div class="card">
  <strong>MCP API key</strong>
  <p class="muted">Regenerating immediately invalidates the old key.</p>
  <form method="POST" action="/dashboard/api-key/regenerate" onsubmit="return confirm('This invalidates your current key. Continue?');">
    <button type="submit" class="secondary">Regenerate API key</button>
  </form>
</div>

<div class="card">
  <strong>Connect an AI app</strong>
  <p class="muted">Server URL: <code>{base_url}/mcp</code></p>
  <p class="muted">Some apps ask for a Bearer token directly (paste your API key); others
  (like Claude's connector UI) will walk you through a login page that also
  asks for this same API key.</p>
</div>
""")


async def update_connection_string(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    connection_string = str(form.get("connection_string", "")).strip()

    if not (connection_string.startswith("postgresql://") or connection_string.startswith("postgres://")):
        return _dashboard_error(request, "That doesn't look like a Postgres connection string (should start with postgresql://).")

    ok, err = await tenant_pools.test_connection_string(connection_string)
    if not ok:
        return _dashboard_error(request, f"Couldn't connect with that string: {err}")

    pool = db_control.get_control_pool()
    await db_control.set_connection_string(pool, user_id, security.encrypt_text(connection_string))
    # Drop any cached pool built from the old connection string.
    await tenant_pools.get_manager().invalidate(user_id)

    return RedirectResponse("/dashboard", status_code=302)


async def regenerate_api_key(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    pool = db_control.get_control_pool()
    raw_key = security.generate_api_key()
    await db_control.set_api_key_hash(pool, user_id, security.hash_api_key(raw_key))
    request.session["flash_api_key"] = raw_key

    return RedirectResponse("/dashboard", status_code=302)


def _dashboard_error(request: Request, message: str) -> HTMLResponse:
    return _page("Dashboard", f"""
<h2>Dashboard</h2>
<p class="error">{message}</p>
<p><a href="/dashboard">Back to dashboard</a></p>
""")


routes = [
    Route("/signup", signup_get, methods=["GET"]),
    Route("/signup", signup_post, methods=["POST"]),
    Route("/login", login_get, methods=["GET"]),
    Route("/login", login_post, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/dashboard", dashboard_get, methods=["GET"]),
    Route("/dashboard/connection-string", update_connection_string, methods=["POST"]),
    Route("/dashboard/api-key/regenerate", regenerate_api_key, methods=["POST"]),
]
