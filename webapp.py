"""
Memory Notes for AI - Web Application
Features a 3D Neon landing page, authentication, and a dashboard settings panel.
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
    --bg-dark: #07090e;
    --card-bg: rgba(15, 23, 42, 0.65);
    --neon-cyan: #00f2fe;
    --neon-blue: #4facfe;
    --neon-purple: #7928ca;
    --border-glow: rgba(0, 242, 254, 0.25);
    --text-main: #f3f4f6;
    --text-muted: #9ca3af;
  }
  
  * { box-sizing: border-box; }
  body {
    background-color: var(--bg-dark);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0; padding: 0;
    color: var(--text-main);
    overflow-x: hidden;
  }

  /* 3D Canvas Background Effects */
  .bg-glow {
    position: fixed; top: -150px; left: 50%; transform: translateX(-50%);
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(0, 242, 254, 0.15) 0%, rgba(121, 40, 202, 0.1) 50%, transparent 70%);
    filter: blur(80px); pointer-events: none; z-index: 0;
  }

  .container { max-width: 1080px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1; }

  /* Typography & Buttons */
  h1, h2, h3 { color: #fff; font-weight: 700; letter-spacing: -0.02em; }
  .gradient-text {
    background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--neon-blue) 50%, #a855f7 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .muted { color: var(--text-muted); font-size: 14px; line-height: 1.6; }

  input {
    width: 100%; padding: 12px 16px; margin: 8px 0; font-size: 14px;
    background: rgba(3, 7, 18, 0.8); border: 1px solid rgba(255, 255, 255, 0.12);
    color: #fff; border-radius: 8px; outline: none; transition: all 0.2s;
  }
  input:focus { border-color: var(--neon-cyan); box-shadow: 0 0 12px rgba(0, 242, 254, 0.3); }

  .btn {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 12px 24px; font-size: 15px; font-weight: 600; cursor: pointer;
    border: none; border-radius: 8px;
    background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--neon-blue) 100%);
    color: #07090e; text-decoration: none; transition: all 0.25s ease;
    box-shadow: 0 4px 20px rgba(0, 242, 254, 0.3);
  }
  .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 28px rgba(0, 242, 254, 0.5); }
  .btn.secondary {
    background: rgba(255, 255, 255, 0.05); color: var(--text-main);
    border: 1px solid rgba(255, 255, 255, 0.15); box-shadow: none;
  }
  .btn.secondary:hover { background: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.3); }
  .btn.small { padding: 6px 14px; font-size: 13px; }
  .btn.danger { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); box-shadow: none; }
  .btn.danger:hover { background: rgba(239, 68, 68, 0.3); }

  .card {
    background: var(--card-bg); backdrop-filter: blur(16px);
    border: 1px solid var(--border-glow); border-radius: 16px;
    padding: 24px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }
  .error { color: #f87171; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 12px; border-radius: 8px; font-size: 14px; margin: 12px 0; }
  
  /* Navbar */
  .navbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
  .brand { font-size: 20px; font-weight: 700; display: flex; align-items: center; gap: 10px; color: #fff; text-decoration: none; }
  .brand-logo { width: 32px; height: 32px; background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple)); border-radius: 8px; display: grid; place-items: center; font-size: 18px; font-weight: bold; color: #000; }

  /* Profile Avatar & Dropdown */
  .user-menu { position: relative; display: flex; align-items: center; gap: 12px; }
  .avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
    color: #07090e; font-weight: bold; display: flex; align-items: center; justify-content: center;
    cursor: pointer; border: 2px solid rgba(0, 242, 254, 0.5); transition: transform 0.2s;
  }
  .avatar:hover { transform: scale(1.05); }
  .settings-dropdown {
    position: absolute; right: 0; top: 52px; width: 320px;
    background: #0d1322; border: 1px solid var(--border-glow);
    border-radius: 12px; padding: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    display: none; z-index: 100; backdrop-filter: blur(20px);
  }
  .settings-dropdown.active { display: block; }

  /* 3D Hero Section */
  .hero { text-align: center; padding: 100px 0 60px; perspective: 1000px; }
  .hero-title { font-size: 56px; line-height: 1.1; margin-bottom: 20px; }
  .hero-subtitle { font-size: 20px; color: var(--text-muted); max-width: 680px; margin: 0 auto 36px; }

  /* 3D Floating Mockup Card */
  .hero-3d-card {
    max-width: 780px; margin: 40px auto 0; padding: 30px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%);
    border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 20px;
    transform: rotateX(12deg) rotateY(-4deg) rotateZ(1deg);
    box-shadow: 0 30px 60px rgba(0, 242, 254, 0.15), 0 0 40px rgba(121, 40, 202, 0.2);
    transition: transform 0.5s ease;
  }
  .hero-3d-card:hover { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg) scale(1.02); }

  /* Features Grid */
  .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin: 60px 0; }
  .feature-card {
    background: var(--card-bg); border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px; padding: 28px; transition: all 0.3s ease;
  }
  .feature-card:hover { border-color: var(--neon-cyan); transform: translateY(-4deg); box-shadow: 0 10px 25px rgba(0, 242, 254, 0.15); }
  .feature-icon { font-size: 28px; margin-bottom: 16px; display: inline-block; }

  /* Key Box & Copy Section */
  .code-box {
    font-family: ui-monospace, monospace; background: rgba(3, 7, 18, 0.9);
    border: 1px solid rgba(0, 242, 254, 0.3); color: var(--neon-cyan);
    padding: 12px 16px; border-radius: 8px; font-size: 13px; word-break: break-all;
    display: flex; justify-content: space-between; align-items: center; gap: 10px;
  }
"""


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - Memory Notes for AI</title>
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
        btn.innerText = 'Copied!';
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
# 3D Landing Page
# ---------------------------------------------------------------------------
async def landing_page(request: Request):
    user_id = _require_login(request)
    nav_actions = '<a href="/dashboard" class="btn small">Go to Dashboard</a>' if user_id else """
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
  <p class="hero-subtitle">Equip Claude, ChatGPT, and AI agents with real-time vector search and persistent note memory directly connected to your Neon Postgres database.</p>
  <div>
    <a href="/signup" class="btn" style="font-size: 16px; padding: 14px 32px;">Get Started Free</a>
    <a href="/login" class="btn secondary" style="font-size: 16px; padding: 14px 32px; margin-left: 12px;">Sign In</a>
  </div>

  <div class="hero-3d-card">
    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 16px;">
      <span style="font-family: monospace; font-size: 13px; color: var(--neon-cyan);">✓ MCP Protocol Active</span>
      <span style="font-family: monospace; font-size: 13px; color: #a855f7;">Neon Postgres Connected</span>
    </div>
    <div style="text-align: left; font-family: ui-monospace, monospace; font-size: 14px; line-height: 1.8;">
      <p style="color: #9ca3af; margin: 0;">&gt; Claude: "What did I store about my system architecture design?"</p>
      <p style="color: var(--neon-cyan); margin: 4px 0 0 0;">&gt; Executing search_notes(query="system architecture design")...</p>
      <p style="color: #38bdf8; margin: 4px 0 0 0;">&gt; Found 3 matching notes in Neon DB [Latency: 18ms]</p>
    </div>
  </div>
</section>

<section class="grid-3">
  <div class="feature-card">
    <span class="feature-icon">⚡</span>
    <h3>Model Context Protocol</h3>
    <p class="muted">Native HTTP streamable MCP server implementation compatible with Claude Desktop, Claude Web, and custom LLM applications.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🔒</span>
    <h3>Multi-Tenant & Isolated</h3>
    <p class="muted">Your Neon connection string is encrypted at rest using Fernet encryption. Every user's notes remain strictly private and isolated.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🔍</span>
    <h3>Smart Fuzzy & Hybrid Search</h3>
    <p class="muted">Built-in support for Postgres trigram fuzzy matching (<code>pg_trgm</code>) and fallback keyword indexing for fast recall.</p>
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
<div style="max-width: 420px; margin: 80px auto;">
  <h2>Create Your Account</h2>
  <p class="muted">Set up your Memory Notes AI gateway account.</p>
  <form method="POST" action="/signup">
    <input type="hidden" name="next" value="{next_}">
    <input type="email" name="email" placeholder="Email address" required autofocus>
    <input type="password" name="password" placeholder="Password (min 8 characters)" minlength="8" required>
    <button type="submit" class="btn" style="width: 100%; margin-top: 12px;">Create Account</button>
  </form>
  <p class="muted" style="margin-top: 20px; text-align: center;">Already have an account? <a href="/login?next={next_}" style="color: var(--neon-cyan);">Log in</a></p>
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
<div style="max-width: 420px; margin: 80px auto;">
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
<div style="max-width: 420px; margin: 80px auto;">
  <h2>Create Your Account</h2>
  <div class="error">An account with that email already exists.</div>
  <p><a href="/login?next={next_}" style="color: var(--neon-cyan);">Log in instead</a></p>
</div>
""")

    request.session["user_id"] = user_id
    return RedirectResponse(next_, status_code=302)


async def login_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    return _page("Log in", f"""
<div style="max-width: 420px; margin: 80px auto;">
  <h2>Welcome Back</h2>
  <p class="muted">Access your Memory Notes control panel.</p>
  <form method="POST" action="/login">
    <input type="hidden" name="next" value="{next_}">
    <input type="email" name="email" placeholder="Email address" required autofocus>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit" class="btn" style="width: 100%; margin-top: 12px;">Log In</button>
  </form>
  <p class="muted" style="margin-top: 20px; text-align: center;">No account yet? <a href="/signup?next={next_}" style="color: var(--neon-cyan);">Sign up</a></p>
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
<div style="max-width: 420px; margin: 80px auto;">
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
<div class="card" style="border-color: var(--neon-cyan);">
  <strong style="color: var(--neon-cyan);">New MCP API Key Generated (Copy now):</strong>
  <div class="code-box" style="margin-top: 8px;">
    <span>{flash_key}</span>
    <button id="btnCopyKey" class="btn small" onclick="copyToClipboard('{flash_key}', 'btnCopyKey')">Copy Key</button>
  </div>
</div>
"""

    if user["connection_string_encrypted"]:
        masked = security.mask_connection_string(security.decrypt_text(user["connection_string_encrypted"]))
        conn_status = f'<p class="muted">Configured DB: <code style="color:#38bdf8;">{masked}</code></p>'
    else:
        conn_status = '<div class="error">No connection string added yet. Enter your Neon Postgres URL below to activate MCP responses.</div>'

    keys = await db_control.list_api_keys(pool, user_id)
    active_keys = [k for k in keys if k["revoked_at"] is None]
    if active_keys:
        rows = "".join(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
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
  
  <!-- Right Profile Avatar with Settings Icon -->
  <div class="user-menu">
    <div class="avatar" onclick="toggleSettings()" title="User Settings">
      {user_initial}
    </div>
    
    <div id="settingsDropdown" class="settings-dropdown">
      <div style="font-weight: 600; color: #fff; margin-bottom: 4px;">User Settings</div>
      <div class="muted" style="margin-bottom: 12px;">{user["email"]}</div>
      <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 12px 0;">
      <a href="#neon-section" onclick="toggleSettings()" style="display: block; color: var(--text-main); text-decoration: none; padding: 6px 0;">⚙️ Database Settings</a>
      <a href="#keys-section" onclick="toggleSettings()" style="display: block; color: var(--text-main); text-decoration: none; padding: 6px 0;">🔑 MCP API Keys</a>
      <form method="POST" action="/logout" style="margin-top: 12px;">
        <button type="submit" class="btn secondary small" style="width: 100%;">Log Out</button>
      </form>
    </div>
  </div>
</header>

<div style="margin-top: 24px;">
  <h2>Dashboard & Connection Panel</h2>
  <p class="muted">Manage your Neon database credentials, MCP API keys, and server endpoint details.</p>
</div>

{flash_html}

<!-- MCP Connection Endpoint Card -->
<div class="card">
  <strong style="font-size: 16px;">1. Claude & AI Connector Endpoint URL</strong>
  <p class="muted">Copy this URL and add it into Claude Desktop or any HTTP MCP client connector:</p>
  <div class="code-box">
    <span>{mcp_endpoint}</span>
    <button id="btnCopyUrl" class="btn small" onclick="copyToClipboard('{mcp_endpoint}', 'btnCopyUrl')">Copy URL</button>
  </div>
</div>

<!-- Neon Database Connection String -->
<div id="neon-section" class="card">
  <strong style="font-size: 16px;">2. Neon Connection String Settings</strong>
  <p class="muted">Paste your Neon PostgreSQL connection string (e.g. <code>postgresql://user:pass@ep-xxx.neon.tech/dbname</code>):</p>
  {conn_status}
  <form method="POST" action="/dashboard/connection-string" style="margin-top: 12px;">
    <input type="text" name="connection_string" placeholder="postgresql://user:password@ep-xxx.aws.neon.tech/dbname" required>
    <button type="submit" class="btn" style="margin-top: 8px;">Save Database Connection</button>
  </form>
</div>

<!-- MCP API Keys Management -->
<div id="keys-section" class="card">
  <strong style="font-size: 16px;">3. MCP API Keys (MCP_API_KEY)</strong>
  <p class="muted">Generate API tokens to authenticate direct requests to your MCP endpoint:</p>
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
<div style="max-width: 500px; margin: 60px auto;">
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
