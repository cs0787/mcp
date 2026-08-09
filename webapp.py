"""
Memory Notes for AI - Web Application
Features a Monochromatic Black & White 3D landing page, authentication, 
and user dashboard settings panel.
"""

import asyncpg
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route

import db_control
import security
import tenant_pools

PAGE_STYLE = """
  :root {
    --bg-dark: #050505;
    --card-bg: #0d0d0f;
    --card-border: #222226;
    --card-border-hover: #44444c;
    --text-main: #ffffff;
    --text-muted: #a1a1aa;
    --text-dim: #71717a;
    --accent-white: #ffffff;
    --accent-gray: #d4d4d8;
  }
  
  * { box-sizing: border-box; }
  body {
    background-color: var(--bg-dark);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
    margin: 0; padding: 0;
    color: var(--text-main);
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
  }

  /* Monochromatic Ambient Glow */
  .bg-glow {
    position: fixed; top: -180px; left: 50%; transform: translateX(-50%);
    width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.07) 0%, rgba(120, 120, 120, 0.03) 40%, transparent 70%);
    filter: blur(90px); pointer-events: none; z-index: 0;
  }

  .container { max-width: 1040px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1; }

  /* Typography */
  h1, h2, h3 { color: #ffffff; font-weight: 700; letter-spacing: -0.03em; }
  .gradient-text {
    background: linear-gradient(180deg, #ffffff 0%, #a1a1aa 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .muted { color: var(--text-muted); font-size: 14px; line-height: 1.6; }

  input {
    width: 100%; padding: 12px 16px; margin: 8px 0; font-size: 14px;
    background: #121215; border: 1px solid var(--card-border);
    color: #ffffff; border-radius: 8px; outline: none; transition: all 0.2s ease;
  }
  input:focus { border-color: #ffffff; box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.15); }

  /* Monochromatic Buttons */
  .btn {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 12px 24px; font-size: 14px; font-weight: 600; cursor: pointer;
    border: 1px solid #ffffff; border-radius: 8px;
    background: #ffffff; color: #000000;
    text-decoration: none; transition: all 0.2s ease;
    box-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
  }
  .btn:hover { background: #e4e4e7; border-color: #e4e4e7; transform: translateY(-1px); }
  .btn.secondary {
    background: #141417; color: var(--text-main);
    border: 1px solid var(--card-border); box-shadow: none;
  }
  .btn.secondary:hover { background: #1c1c20; border-color: var(--card-border-hover); }
  .btn.small { padding: 6px 14px; font-size: 13px; }
  .btn.danger { background: #1f1213; color: #f87171; border: 1px solid rgba(248, 113, 113, 0.3); box-shadow: none; }
  .btn.danger:hover { background: #2c1618; border-color: rgba(248, 113, 113, 0.6); }

  .card {
    background: var(--card-bg);
    border: 1px solid var(--card-border); border-radius: 14px;
    padding: 24px; margin: 20px 0; transition: border-color 0.2s ease;
  }
  .card:hover { border-color: var(--card-border-hover); }
  .error { color: #f87171; background: #180c0d; border: 1px solid rgba(248, 113, 113, 0.2); padding: 12px; border-radius: 8px; font-size: 14px; margin: 12px 0; }
  
  /* Navbar */
  .navbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 24px 0; border-bottom: 1px solid var(--card-border);
  }
  .brand { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 10px; color: #fff; text-decoration: none; letter-spacing: -0.02em; }
  .brand-logo { width: 30px; height: 30px; background: #ffffff; border-radius: 6px; display: grid; place-items: center; font-size: 16px; font-weight: 800; color: #000000; }

  /* Profile Avatar & Dropdown */
  .user-menu { position: relative; display: flex; align-items: center; gap: 12px; }
  .avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: #ffffff; color: #000000; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; border: 1px solid #ffffff; transition: transform 0.2s ease;
  }
  .avatar:hover { transform: scale(1.04); }
  .settings-dropdown {
    position: absolute; right: 0; top: 50px; width: 300px;
    background: #111114; border: 1px solid var(--card-border-hover);
    border-radius: 12px; padding: 16px; box-shadow: 0 16px 40px rgba(0,0,0,0.8);
    display: none; z-index: 100;
  }
  .settings-dropdown.active { display: block; }

  /* Monochromatic 3D Hero Section */
  .hero { text-align: center; padding: 90px 0 50px; perspective: 1000px; }
  .hero-title { font-size: 58px; line-height: 1.08; margin-bottom: 20px; letter-spacing: -0.04em; }
  .hero-subtitle { font-size: 19px; color: var(--text-muted); max-width: 640px; margin: 0 auto 36px; line-height: 1.5; }

  /* 3D Floating Monochrome Mockup Card */
  .hero-3d-card {
    max-width: 760px; margin: 40px auto 0; padding: 28px;
    background: linear-gradient(180deg, #121215 0%, #0a0a0c 100%);
    border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 16px;
    transform: rotateX(10deg) rotateY(-3deg) rotateZ(0.5deg);
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.9), 0 0 50px rgba(255, 255, 255, 0.03);
    transition: transform 0.4s ease, border-color 0.4s ease;
  }
  .hero-3d-card:hover { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg) scale(1.01); border-color: rgba(255, 255, 255, 0.35); }

  /* Features Grid */
  .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 60px 0; }
  .feature-card {
    background: var(--card-bg); border: 1px solid var(--card-border);
    border-radius: 12px; padding: 28px; transition: all 0.25s ease;
  }
  .feature-card:hover { border-color: var(--card-border-hover); transform: translateY(-3px); }
  .feature-icon { font-size: 24px; margin-bottom: 14px; display: inline-block; filter: grayscale(100%); }

  /* Key Box & Copy Section */
  .code-box {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    background: #000000; border: 1px solid var(--card-border);
    color: #e4e4e7; padding: 12px 16px; border-radius: 8px; font-size: 13px;
    word-break: break-all; display: flex; justify-content: space-between; align-items: center; gap: 10px;
  }
"""


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - Memory Notes AI</title>
  <style>{PAGE_STYLE}</style>
</head>
<body>
  <div class="bg-glow"></div>
  <div class="container">
    {body}
  </div>
  <script>
    function copyToClipboard(text, btnId) {{
      navigator.clipboard.writeText(text).then(() => {{
        const btn = document.getElementById(btnId);
        const originalText = btn.innerText;
        btn.innerText = 'Copied';
        setTimeout(() => btn.innerText = originalText, 2000);
      }});
    }}
    function toggleSettings() {{
      const dropdown = document.getElementById('settingsDropdown');
      if (dropdown) dropdown.classList.toggle('active');
    }}
  </script>
</body>
</html>
""")


def _require_login(request: Request) -> str | None:
    return request.session.get("user_id")


def _safe_next(raw: str | None) -> str:
    if raw and raw.startswith("/") and not raw.startswith("//"):
        return raw
    return "/dashboard"


# ---------------------------------------------------------------------------
# Monochromatic 3D Landing Page
# ---------------------------------------------------------------------------
async def landing_page(request: Request):
    user_id = _require_login(request)
    nav_actions = '<a href="/dashboard" class="btn small">Dashboard</a>' if user_id else """
      <a href="/login" class="btn secondary small" style="margin-right: 8px;">Log In</a>
      <a href="/signup" class="btn small">Get Started</a>
    """

    return _page("Home", f"""
<header class="navbar">
  <a href="/" class="brand">
    <div class="brand-logo">M</div> Memory Notes AI
  </a>
  <div>{nav_actions}</div>
</header>

<section class="hero">
  <h1 class="hero-title">Long-Term <span class="gradient-text">Memory Gateway</span><br>for AI Models</h1>
  <p class="hero-subtitle">Connect Claude, ChatGPT, and AI agents directly to your personal Neon Postgres notes with encrypted per-tenant authorization.</p>
  <div>
    <a href="/signup" class="btn" style="font-size: 15px; padding: 13px 30px;">Get Started Free</a>
    <a href="/login" class="btn secondary" style="font-size: 15px; padding: 13px 30px; margin-left: 10px;">Sign In</a>
  </div>

  <div class="hero-3d-card">
    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 12px; margin-bottom: 16px;">
      <span style="font-family: monospace; font-size: 12px; color: #ffffff; letter-spacing: 0.05em;">● MCP PROTOCOL ONLINE</span>
      <span style="font-family: monospace; font-size: 12px; color: #a1a1aa;">NEON POSTGRES LINKED</span>
    </div>
    <div style="text-align: left; font-family: ui-monospace, monospace; font-size: 13px; line-height: 1.8;">
      <p style="color: #71717a; margin: 0;">&gt; Claude: "Fetch my project notes on system deployment..."</p>
      <p style="color: #ffffff; margin: 4px 0 0 0;">&gt; Executing search_notes(query="system deployment")...</p>
      <p style="color: #a1a1aa; margin: 4px 0 0 0;">&gt; 3 notes returned from Neon DB [0.012s]</p>
    </div>
  </div>
</section>

<section class="grid-3">
  <div class="feature-card">
    <span class="feature-icon">▫️</span>
    <h3 style="margin-top: 0;">Model Context Protocol</h3>
    <p class="muted">Native HTTP streamable MCP transport standard designed for Claude Desktop, Claude Web, and custom LLMs.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">◾</span>
    <h3 style="margin-top: 0;">Isolated & Encrypted</h3>
    <p class="muted">Your Neon connection string is Fernet-encrypted at rest. Every request is isolated strictly to your database.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">▫️</span>
    <h3 style="margin-top: 0;">Fuzzy Trigram Search</h3>
    <p class="muted">Leverages Postgres <code>pg_trgm</code> fuzzy search for quick matching across notes, workspaces, and OCR data.</p>
  </div>
</section>
""")


# ---------------------------------------------------------------------------
# Auth Handlers
# ---------------------------------------------------------------------------
async def signup_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    return _page("Sign up", f"""
<div style="max-width: 400px; margin: 80px auto;">
  <h2>Create Your Account</h2>
  <p class="muted">Set up your Memory Notes gateway account.</p>
  <form method="POST" action="/signup">
    <input type="hidden" name="next" value="{next_}">
    <input type="email" name="email" placeholder="Email address" required autofocus>
    <input type="password" name="password" placeholder="Password (min 8 characters)" minlength="8" required>
    <button type="submit" class="btn" style="width: 100%; margin-top: 12px;">Create Account</button>
  </form>
  <p class="muted" style="margin-top: 20px; text-align: center;">Already have an account? <a href="/login?next={next_}" style="color: #ffffff;">Log in</a></p>
</div>
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
<div style="max-width: 400px; margin: 80px auto;">
  <h2>Create Your Account</h2>
  <div class="error">{error}</div>
  <form method="POST" action="/signup">
    <input type="hidden" name="next" value="{next_}">
    <input type="email" name="email" placeholder="Email address" value="{email}" required autofocus>
    <input type="password" name="password" placeholder="Password (min 8 characters)" minlength="8" required>
    <button type="submit" class="btn" style="width: 100%; margin-top: 12px;">Create Account</button>
  </form>
</div>
""")

    pool = db_control.get_control_pool()
    try:
        user_id = await db_control.create_user(pool, email, security.hash_password(password))
    except asyncpg.exceptions.UniqueViolationError:
        return _page("Sign up", f"""
<div style="max-width: 400px; margin: 80px auto;">
  <h2>Create Your Account</h2>
  <div class="error">An account with that email already exists.</div>
  <p><a href="/login?next={next_}" style="color: #ffffff;">Log in instead</a></p>
</div>
""")

    request.session["user_id"] = user_id
    return RedirectResponse(next_, status_code=302)


async def login_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    return _page("Log in", f"""
<div style="max-width: 400px; margin: 80px auto;">
  <h2>Welcome Back</h2>
  <p class="muted">Sign in to your Memory Notes control panel.</p>
  <form method="POST" action="/login">
    <input type="hidden" name="next" value="{next_}">
    <input type="email" name="email" placeholder="Email address" required autofocus>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit" class="btn" style="width: 100%; margin-top: 12px;">Log In</button>
  </form>
  <p class="muted" style="margin-top: 20px; text-align: center;">No account yet? <a href="/signup?next={next_}" style="color: #ffffff;">Sign up</a></p>
</div>
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
<div style="max-width: 400px; margin: 80px auto;">
  <h2>Welcome Back</h2>
  <div class="error">Incorrect email or password.</div>
  <form method="POST" action="/login">
    <input type="hidden" name="next" value="{next_}">
    <input type="email" name="email" placeholder="Email address" value="{email}" required autofocus>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit" class="btn" style="width: 100%; margin-top: 12px;">Log In</button>
  </form>
</div>
""")

    request.session["user_id"] = str(user["id"])
    return RedirectResponse(next_, status_code=302)


async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ---------------------------------------------------------------------------
# Dashboard & User Settings
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
<div class="card" style="border-color: #ffffff;">
  <strong style="color: #ffffff;">New MCP API Key Generated (Copy now):</strong>
  <div class="code-box" style="margin-top: 8px;">
    <span>{flash_key}</span>
    <button id="btnCopyKey" class="btn small" onclick="copyToClipboard('{flash_key}', 'btnCopyKey')">Copy Key</button>
  </div>
</div>
"""

    if user["connection_string_encrypted"]:
        masked = security.mask_connection_string(security.decrypt_text(user["connection_string_encrypted"]))
        conn_status = f'<p class="muted">Configured DB: <code style="color:#ffffff;">{masked}</code></p>'
    else:
        conn_status = '<div class="error">No connection string added yet. Enter your Neon Postgres URL below to activate MCP responses.</div>'

    keys = await db_control.list_api_keys(pool, user_id)
    active_keys = [k for k in keys if k["revoked_at"] is None]
    if active_keys:
        rows = "".join(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding: 12px 0; border-bottom: 1px solid var(--card-border);">
  <div>
    <div style="font-weight: 500; color: #fff;">{k['label']}</div>
    <div class="muted">Created {k['created_at'].strftime('%b %d, %Y')}</div>
  </div>
  <form method="POST" action="/dashboard/api-key/revoke" style="margin: 0;">
    <input type="hidden" name="key_id" value="{k['id']}">
    <button type="submit" class="btn danger small" onclick="return confirm('Revoke this key?');">Revoke</button>
  </form>
</div>
""" for k in active_keys)
    else:
        rows = '<p class="muted">No active API keys found.</p>'

    base_url = str(request.base_url).rstrip("/")
    mcp_endpoint = f"{base_url}/mcp"
    user_initial = user["email"][0].upper()

    return _page("Dashboard", f"""
<header class="navbar">
  <a href="/" class="brand">
    <div class="brand-logo">M</div> Memory Notes AI
  </a>
  
  <div class="user-menu">
    <div class="avatar" onclick="toggleSettings()" title="User Settings">
      {user_initial}
    </div>
    
    <div id="settingsDropdown" class="settings-dropdown">
      <div style="font-weight: 600; color: #fff; margin-bottom: 2px;">User Account</div>
      <div class="muted" style="margin-bottom: 12px; font-size: 13px;">{user["email"]}</div>
      <hr style="border: 0; border-top: 1px solid var(--card-border); margin: 10px 0;">
      <a href="#neon-section" onclick="toggleSettings()" style="display: block; color: var(--text-main); text-decoration: none; padding: 6px 0; font-size: 14px;">⚙️ Database Settings</a>
      <a href="#keys-section" onclick="toggleSettings()" style="display: block; color: var(--text-main); text-decoration: none; padding: 6px 0; font-size: 14px;">🔑 MCP API Keys</a>
      <form method="POST" action="/logout" style="margin-top: 12px;">
        <button type="submit" class="btn secondary small" style="width: 100%;">Log Out</button>
      </form>
    </div>
  </div>
</header>

<div style="margin-top: 28px;">
  <h2 style="font-size: 28px;">Control Panel</h2>
  <p class="muted">Configure your database credentials, API access tokens, and connector details.</p>
</div>

{flash_html}

<!-- MCP Connection Endpoint Card -->
<div class="card">
  <strong style="font-size: 15px;">1. Claude MCP Connector Endpoint</strong>
  <p class="muted">Provide this URL when adding a new connector in Claude Desktop or custom AI clients:</p>
  <div class="code-box">
    <span>{mcp_endpoint}</span>
    <button id="btnCopyUrl" class="btn small" onclick="copyToClipboard('{mcp_endpoint}', 'btnCopyUrl')">Copy URL</button>
  </div>
</div>

<!-- Neon Database Connection String -->
<div id="neon-section" class="card">
  <strong style="font-size: 15px;">2. Neon Database Connection String</strong>
  <p class="muted">Save your Neon PostgreSQL URL (e.g. <code>postgresql://user:pass@ep-xxx.neon.tech/dbname</code>):</p>
  {conn_status}
  <form method="POST" action="/dashboard/connection-string" style="margin-top: 12px;">
    <input type="text" name="connection_string" placeholder="postgresql://user:password@ep-xxx.aws.neon.tech/dbname" required>
    <button type="submit" class="btn" style="margin-top: 8px;">Save Database Connection</button>
  </form>
</div>

<!-- MCP API Keys Management -->
<div id="keys-section" class="card">
  <strong style="font-size: 15px;">3. MCP API Keys (MCP_API_KEY)</strong>
  <p class="muted">Active keys authorized for bearer authentication:</p>
  <div style="margin-top: 12px;">
    {rows}
  </div>
  <form method="POST" action="/dashboard/api-key/create" style="margin-top: 16px;">
    <button type="submit" class="btn secondary">Generate New MCP_API_KEY</button>
  </form>
</div>
""")


async def update_connection_string(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    connection_string = str(form.get("connection_string", "")).strip()

    if not (connection_string.startswith("postgresql://") or connection_string.startswith("postgres://")):
        return _dashboard_error("Invalid connection string format. Must start with postgresql://")

    ok, err = await tenant_pools.test_connection_string(connection_string)
    if not ok:
        return _dashboard_error(f"Failed to connect to Neon database: {err}")

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
    await db_control.create_api_key(pool, user_id, security.hash_api_key(raw_key), "Manual Key")
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
    return _page("Dashboard Error", f"""
<div style="max-width: 480px; margin: 60px auto;">
  <h2>Connection Error</h2>
  <div class="error">{message}</div>
  <p style="margin-top: 16px;"><a href="/dashboard" class="btn secondary small">Back to Dashboard</a></p>
</div>
""")


routes = [
    Route("/", landing_page, methods=["GET"]),
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
