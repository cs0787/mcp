"""
exom - The Unified Second Brain & Memory Layer for All AI
Full Python Starlette ASGI Application with:
- Modular HTML Console rendering via console.html
- Direct Android APK distribution endpoints (/download and /exom.apk)
- Root image serving (/img1.jpeg - /img4.jpeg)
- Mobile & Desktop authentication gateway
- FastMCP Multi-Tenant Database & Control Plane Settings
"""

import os
import uuid
import asyncpg
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from starlette.routing import Route

import db_control
import security
import tenant_pools


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title} - exom</title>

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>

<!-- Lenis Smooth Scroll Script -->
<script src="https://unpkg.com/lenis@1.1.20/dist/lenis.min.js"></script>

<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
    tailwind.config = {{
        darkMode: "class",
        theme: {{
            extend: {{
                colors: {{
                    "inverse-on-surface": "#f3f0ef",
                    "error": "#ba1a1a",
                    "surface-container": "#f1edec",
                    "tertiary": "#602100",
                    "surface-dim": "#dcd9d9",
                    "surface-container-low": "#f6f3f2",
                    "on-primary-fixed-variant": "#00429c",
                    "outline": "#737783",
                    "on-secondary": "#ffffff",
                    "primary-fixed-dim": "#b0c6ff",
                    "on-surface": "#1c1b1b",
                    "primary-fixed": "#d9e2ff",
                    "tertiary-container": "#853100",
                    "surface-tint": "#2b5bb5",
                    "on-secondary-fixed": "#221b00",
                    "tertiary-fixed": "#ffdbcd",
                    "on-primary-container": "#a1bbff",
                    "on-tertiary-container": "#ffa781",
                    "surface-container-high": "#ebe7e7",
                    "inverse-surface": "#313030",
                    "primary-container": "#0d47a1",
                    "on-surface-variant": "#434652",
                    "on-tertiary": "#ffffff",
                    "error-container": "#ffdad6",
                    "inverse-primary": "#b0c6ff",
                    "surface-container-lowest": "#ffffff",
                    "on-background": "#1c1b1b",
                    "surface-bright": "#fcf8f8",
                    "primary": "#003178",
                    "on-error-container": "#93000a",
                    "on-primary-fixed": "#001945",
                    "secondary-fixed-dim": "#e9c400",
                    "on-primary": "#ffffff",
                    "secondary": "#705d00",
                    "text-tertiary": "#A1A1AA",
                    "background": "#fcf8f8",
                    "on-error": "#ffffff",
                    "surface-container-highest": "#e5e2e1",
                    "on-secondary-fixed-variant": "#544600",
                    "secondary-container": "#fdd400",
                    "on-tertiary-fixed-variant": "#7d2d00",
                    "surface-variant": "#e5e2e1",
                    "outline-variant": "#c3c6d4",
                    "on-tertiary-fixed": "#360f00",
                    "secondary-fixed": "#ffe170",
                    "text-secondary": "#71717A",
                    "tertiary-fixed-dim": "#ffb596",
                    "surface-white": "#FFFFFF",
                    "surface": "#fcf8f8",
                    "border-muted": "#E2E2E7",
                    "on-secondary-container": "#6f5c00"
                }}
            }}
        }}
    }}
</script>

<style>
    html.lenis, html.lenis body {{
      height: auto;
    }}
    .lenis.lenis-smooth {{
      scroll-behavior: auto !important;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    .hero-interactive-grid {{
        --color: #E1E1E1;
        background-color: #F8F8F8;
        background-image: 
            linear-gradient(0deg, transparent 24%, var(--color) 25%, var(--color) 26%, transparent 27%, transparent 74%, var(--color) 75%, var(--color) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, var(--color) 25%, var(--color) 26%, transparent 27%, transparent 74%, var(--color) 75%, var(--color) 76%, transparent 77%, transparent);
        background-size: 55px 55px;
        position: relative;
        overflow: hidden;
    }}

    .vertical-mode-text {{
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        letter-spacing: 0.32em;
    }}

    .expand-card {{
        flex: 0 0 5.2rem;
        height: 28rem;
        border-radius: 26px;
        transition: all 0.5s cubic-bezier(0.25, 1, 0.35, 1);
    }}
    .expand-card.active {{
        flex: 0 0 calc(28rem * 1024 / 1165);
        width: calc(28rem * 1024 / 1165);
    }}
    @media (max-width: 900px) {{
        .expand-card {{
            flex: 0 0 4.2rem;
            height: 23rem;
            border-radius: 20px;
        }}
        .expand-card.active {{
            flex: 0 0 calc(23rem * 1024 / 1165);
            width: calc(23rem * 1024 / 1165);
        }}
    }}
</style>
</head>
<body class="bg-surface-white text-on-surface font-body-md min-h-screen flex flex-col selection:bg-primary-container selection:text-on-primary-container">

<script>
    window.lenis = new Lenis({{
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 1.0,
      touchMultiplier: 1.8,
      infinite: false,
    }});

    function raf(time) {{
      window.lenis.raf(time);
      requestAnimationFrame(raf);
    }}
    requestAnimationFrame(raf);

    function copyToClipboard(text, btnId) {{
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById(btnId);
            const orig = btn.innerText;
            btn.innerText = 'Copied!';
            setTimeout(() => btn.innerText = orig, 2000);
        }});
    }}
</script>

{body}
</body>
</html>
""")


def _require_login(request: Request) -> str | None:
    return request.session.get("user_id")[cite: 10]


def _safe_next(raw: str | None) -> str:
    if raw and raw.startswith("/") and not raw.startswith("//"):
        return raw
    return "/console"[cite: 10]


def _navbar(request: Request, user_email: str | None = None) -> str:
    if user_email:
        right_actions = """
        <a href="/download" class="text-xs sm:text-sm font-semibold text-on-surface hover:text-primary transition-colors no-underline">Get App</a>
        <a href="/console" class="bg-secondary-container text-on-surface px-3 sm:px-4 py-2 rounded text-xs sm:text-sm font-semibold hover:bg-secondary-fixed transition-colors no-underline">Console</a>
        """
    else:
        right_actions = """
        <a href="/download" class="text-xs sm:text-sm font-semibold text-on-surface hover:text-primary transition-colors no-underline">Get App</a>
        <a href="/login" class="bg-surface-white text-on-surface px-3 sm:px-4 py-2 rounded text-xs sm:text-sm font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors no-underline">Log In</a>
        <a href="/signup" class="bg-secondary-container text-on-surface px-3 sm:px-4 py-2 rounded text-xs sm:text-sm font-semibold hover:bg-secondary-fixed transition-colors no-underline">Get Started</a>
        """

    return f"""
<nav class="sticky top-0 z-50 flex justify-between items-center w-full px-4 sm:px-6 lg:px-12 py-3 bg-surface-white border-b border-border-muted">
    <div class="flex items-center gap-2 sm:gap-4">
        <a href="/" class="text-lg sm:text-xl font-bold text-on-surface no-underline tracking-tight">exom</a>
    </div>
    <div class="flex items-center gap-2 sm:gap-4">
        {right_actions}
    </div>
</nav>
"""


# ---------------------------------------------------------------------------
# Direct APK & Image Distribution Routes
# ---------------------------------------------------------------------------
async def download_apk(request: Request):
    for fname in ("MemoryBase.apk", "exom.apk"):
        apk_path = os.path.join(os.path.dirname(__file__), fname)
        if os.path.exists(apk_path):
            return FileResponse(path=apk_path, media_type="application/vnd.android.package-archive", filename="exom.apk")
    return HTMLResponse("<p style='text-align:center;padding:40px;font-family:sans-serif;'>Companion app installer is packaging. Check back shortly.</p>", status_code=404)


async def serve_root_image(request: Request):
    filename = request.url.path.lstrip("/")
    if ".." in filename or "/" in filename or "\\" in filename:
        return HTMLResponse("Forbidden", status_code=403)
    img_path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(img_path):
        return HTMLResponse(f"Image {filename} not found.", status_code=404)
    return FileResponse(img_path, media_type="image/jpeg")


# ---------------------------------------------------------------------------
# Mobile & Desktop Login Gateway
# ---------------------------------------------------------------------------
async def mobile_login(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return JSONResponse({"error": "Email and password are required"}, status_code=400)

    pool = db_control.get_control_pool()[cite: 2]
    user = await db_control.get_user_by_email(pool, email)[cite: 2]

    if user is None or not security.verify_password(password, user["password_hash"]):[cite: 2, 5]
        return JSONResponse({"error": "Invalid email or password"}, status_code=401)

    decrypted_conn_str = None
    if user["connection_string_encrypted"]:[cite: 2]
        try:
            decrypted_conn_str = security.decrypt_text(user["connection_string_encrypted"])[cite: 5]
        except Exception:
            return JSONResponse({"error": "Failed to decrypt connection string"}, status_code=500)

    return JSONResponse({
        "status": "success",
        "user_id": str(user["id"]),[cite: 2]
        "email": user["email"],[cite: 2]
        "has_connection_string": decrypted_conn_str is not None,
        "connection_string": decrypted_conn_str,
    })


# ---------------------------------------------------------------------------
# Console Page (Renders console.html) & Console Data API
# ---------------------------------------------------------------------------
async def console_page(request: Request):
    user_id = _require_login(request)[cite: 10]
    if not user_id:
        return RedirectResponse("/login?next=/console", status_code=302)[cite: 10]

    html_path = os.path.join(os.path.dirname(__file__), "console.html")
    if not os.path.exists(html_path):
        return HTMLResponse("console.html file not found in root directory.", status_code=404)

    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


async def console_data(request: Request):
    user_id = _require_login(request)[cite: 10]
    if not user_id:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    pool = db_control.get_control_pool()[cite: 2]
    user = await db_control.get_user_by_id(pool, user_id)[cite: 2]
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)

    user_email = user["email"][cite: 2]
    display_name = user_email.split("@")[0].capitalize()
    initial = display_name[0].upper()

    workspaces = []
    nodes = []
    edges = []
    selected_workspace = request.query_params.get("ws", "")

    if user["connection_string_encrypted"]:[cite: 2]
        try:
            conn_str = security.decrypt_text(user["connection_string_encrypted"])[cite: 5]
            user_pool = await tenant_pools.get_manager().get_pool(str(user["id"]), conn_str)[cite: 2, 8]

            ws_rows = await user_pool.fetch("SELECT DISTINCT workspace FROM project_nodes ORDER BY workspace ASC")
            workspaces = [r["workspace"] for r in ws_rows]

            if not selected_workspace and workspaces:
                selected_workspace = workspaces[0]

            if selected_workspace:
                node_rows = await user_pool.fetch(
                    """
                    SELECT id, node_type, sequence_index, title, summary, rationale, impact_analysis, affected_components, status, central_hub_id, created_at
                    FROM project_nodes
                    WHERE workspace = $1
                    ORDER BY sequence_index ASC NULLS LAST, created_at ASC
                    """,
                    selected_workspace,
                )
                nodes = [dict(r) for r in node_rows]

                edge_rows = await user_pool.fetch(
                    """
                    SELECT source_node_id, target_node_id, relation_type
                    FROM project_edges
                    WHERE workspace = $1
                    """,
                    selected_workspace,
                )
                edges = [dict(r) for r in edge_rows]
        except Exception:
            pass

    for n in nodes:
        n["id"] = str(n["id"])
        if n.get("central_hub_id"):
            n["central_hub_id"] = str(n["central_hub_id"])
        if hasattr(n.get("created_at"), "isoformat"):
            n["created_at"] = n["created_at"].isoformat()

    for e in edges:
        e["source_node_id"] = str(e["source_node_id"])
        e["target_node_id"] = str(e["target_node_id"])

    return JSONResponse({
        "user": {"email": user_email, "display_name": display_name, "initial": initial},
        "workspaces": workspaces,
        "selected_workspace": selected_workspace,
        "nodes": nodes,
        "edges": edges,
    })


# ---------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------
async def landing_page(request: Request):
    user_id = _require_login(request)[cite: 10]
    user_email = None
    if user_id:
        pool = db_control.get_control_pool()[cite: 2]
        user = await db_control.get_user_by_id(pool, user_id)[cite: 2]
        if user:
            user_email = user["email"][cite: 2]

    base_url = str(request.base_url).rstrip("/")
    nav_html = _navbar(request, user_email)

    claude_config_snippet = f"""{{
  "mcpServers": {{
    "exom": {{
      "url": "{base_url}/mcp",
      "headers": {{
        "Authorization": "Bearer sbmcp_your_api_key_here"
      }}
    }}
  }}
}}"""

    cursor_config_snippet = f"""// Cursor / Roo Code mcp.json
{{
  "servers": [
    {{
      "name": "exom",
      "transport": "sse",
      "url": "{base_url}/mcp",
      "headers": {{
        "Authorization": "Bearer sbmcp_your_api_key_here"
      }}
    }}
  ]
}}"""

    curl_config_snippet = f"""curl -X POST "{base_url}/mcp" \\
  -H "Authorization: Bearer sbmcp_your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{{"jsonrpc": "2.0", "method": "tools/call", "params": {{"name": "search_notes", "arguments": {{"query": "architecture"}}}}, "id": 1}}'"""

    body = f"""
{nav_html}
<main class="flex-grow">
    <!-- Hero Section -->
    <section class="relative pt-12 sm:pt-20 pb-16 sm:pb-20 border-b border-border-muted hero-interactive-grid">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-12 relative z-10 flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
            <div class="flex-1 space-y-4 text-center lg:text-left">
                <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-surface-white border border-border-muted text-xs font-mono text-on-surface-variant mb-2 shadow-xs">
                    <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    Unified Second Brain Layer Active
                </div>
                <h1 class="text-3xl sm:text-4xl lg:text-[54px] lg:leading-[60px] font-bold text-on-surface tracking-tight max-w-2xl">
                    One Persistent Memory Across Every AI.
                </h1>
                <p class="text-sm sm:text-base lg:text-lg text-on-surface-variant max-w-xl mx-auto lg:mx-0 leading-relaxed">
                    Stop re-explaining yourself. <strong>exom</strong> is your ambient second brain that automatically connects, synchronizes, and recalls context across Claude, Cursor, ChatGPT, and autonomous agents.
                </p>
                <div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 pt-3">
                    <a href="/download" class="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-[#050505] text-white px-5 py-3 text-sm font-semibold rounded border border-[#050505] hover:bg-neutral-800 transition-colors shadow-sm no-underline">
                        Get Companion App
                    </a>
                    <a href="{' /console' if user_id else '/signup'}" class="w-full sm:w-auto text-center bg-secondary-container text-on-surface px-6 py-3 text-sm font-semibold border-b-2 border-r-2 border-[#050505] active:translate-y-[1px] active:translate-x-[1px] transition-all inline-block no-underline shadow-sm">Launch Console</a>
                    <a href="#quickstart" class="w-full sm:w-auto text-center bg-surface-white text-on-surface px-6 py-3 text-sm font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors inline-block no-underline shadow-sm">Quickstart</a>
                </div>
            </div>
            
            <div class="flex-1 w-full max-w-md lg:max-w-none flex items-center justify-center">
                <div class="p-4 sm:p-6 bg-surface-white border border-border-muted rounded-xl shadow-md text-left w-full max-w-md font-mono text-xs">
                    <div class="flex items-center justify-between pb-3 mb-3 border-b border-border-muted">
                        <span class="font-bold text-primary">● EXOM NEURAL GATEWAY</span>
                        <span class="text-text-secondary">Synchronized</span>
                    </div>
                    <p class="text-text-secondary mb-1">&gt; Cross-agent recall query:</p>
                    <p class="text-on-surface font-semibold">&gt; get_codebase_context(workspace="Deployments")</p>
                    <p class="text-primary mt-2">✓ Context unified across Claude, Cursor &amp; DeepSeek.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Quickstart Section -->
    <section id="quickstart" class="py-12 sm:py-16 bg-surface-white border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-12">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
                <div>
                    <h2 class="text-2xl lg:text-3xl font-bold text-on-surface mb-2">Connect in 30 Seconds</h2>
                    <p class="text-sm text-on-surface-variant">Link exom's Model Context Protocol memory bridge to your preferred agent configuration.</p>
                </div>
                <div class="flex items-center bg-surface-container-low border border-border-muted p-1 rounded-lg gap-1 overflow-x-auto max-w-full">
                    <button id="tab-claude" onclick="setTerminalTab('claude')" class="px-3 py-1.5 text-xs font-mono rounded bg-on-surface text-surface-white font-semibold transition-colors whitespace-nowrap">Claude Desktop</button>
                    <button id="tab-cursor" onclick="setTerminalTab('cursor')" class="px-3 py-1.5 text-xs font-mono rounded text-text-secondary hover:text-on-surface bg-transparent transition-colors whitespace-nowrap">Cursor / IDE</button>
                    <button id="tab-curl" onclick="setTerminalTab('curl')" class="px-3 py-1.5 text-xs font-mono rounded text-text-secondary hover:text-on-surface bg-transparent transition-colors whitespace-nowrap">cURL / HTTP</button>
                </div>
            </div>

            <div class="bg-[#0f0f11] text-neutral-100 rounded-xl border border-neutral-800 shadow-xl overflow-hidden font-mono text-xs">
                <div class="flex items-center justify-between px-4 py-3 bg-[#17171a] border-b border-neutral-800">
                    <div class="flex items-center gap-2">
                        <span class="w-3 h-3 rounded-full bg-[#ff5f56] inline-block"></span>
                        <span class="w-3 h-3 rounded-full bg-[#ffbd2e] inline-block"></span>
                        <span class="w-3 h-3 rounded-full bg-[#27c93f] inline-block"></span>
                        <span class="ml-2 text-neutral-400 text-[11px]">mcp_configuration.json</span>
                    </div>
                    <button id="btnCopySnippet" onclick="copyToClipboard(document.querySelector('#snippet-container pre:not(.hidden)').innerText, 'btnCopySnippet')" class="px-3 py-1 rounded bg-[#26262b] hover:bg-[#323238] text-neutral-300 text-[11px] border border-neutral-700 transition-colors">
                        Copy Snippet
                    </button>
                </div>

                <div id="snippet-container" class="p-4 sm:p-5 overflow-x-auto text-neutral-300 leading-relaxed">
                    <pre id="snippet-claude"><code>{claude_config_snippet}</code></pre>
                    <pre id="snippet-cursor" class="hidden"><code>{cursor_config_snippet}</code></pre>
                    <pre id="snippet-curl" class="hidden"><code>{curl_config_snippet}</code></pre>
                </div>
            </div>
        </div>
    </section>
</main>
"""
    return _page("Home", body)


# ---------------------------------------------------------------------------
# Signup & Login Handlers
# ---------------------------------------------------------------------------
async def signup_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):[cite: 10]
        return RedirectResponse(next_, status_code=302)[cite: 10]
    body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-4 sm:px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-6 sm:p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Create Your Account</h2>
        <p class="text-xs text-text-secondary mb-6">Initialize your exom second brain gateway.</p>
        <form method="POST" action="/signup">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-on-surface mb-1">Email Address</label>
                <input type="email" name="email" placeholder="name@example.com" required autofocus class="w-full px-4 py-2 border border-border-muted rounded text-sm focus:outline-none focus:border-primary">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-on-surface mb-1">Password</label>
                <input type="password" name="password" placeholder="••••••••" minlength="8" required class="w-full px-4 py-2 border border-border-muted rounded text-sm focus:outline-none focus:border-primary">
            </div>
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-sm font-semibold border border-[#050505]">Sign Up</button>
        </form>
    </div>
</main>
"""
    return _page("Sign up", body)


async def signup_post(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    next_ = _safe_next(str(form.get("next", "")))

    if "@" not in email or len(password) < 8:
        return RedirectResponse(f"/signup?next={next_}", status_code=302)

    pool = db_control.get_control_pool()[cite: 2]
    try:
        user_id = await db_control.create_user(pool, email, security.hash_password(password))[cite: 2, 5]
    except asyncpg.exceptions.UniqueViolationError:
        return RedirectResponse(f"/login?next={next_}", status_code=302)

    request.session["user_id"] = user_id[cite: 10]
    return RedirectResponse(next_, status_code=302)


async def login_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):[cite: 10]
        return RedirectResponse(next_, status_code=302)[cite: 10]
    body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-4 sm:px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-6 sm:p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Welcome Back</h2>
        <p class="text-xs text-text-secondary mb-6">Log in to your exom account.</p>
        <form method="POST" action="/login">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-on-surface mb-1">Email Address</label>
                <input type="email" name="email" placeholder="name@example.com" required autofocus class="w-full px-4 py-2 border border-border-muted rounded text-sm">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-on-surface mb-1">Password</label>
                <input type="password" name="password" required class="w-full px-4 py-2 border border-border-muted rounded text-sm">
            </div>
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-sm font-semibold border border-[#050505]">Log In</button>
        </form>
    </div>
</main>
"""
    return _page("Log in", body)


async def login_post(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    next_ = _safe_next(str(form.get("next", "")))

    pool = db_control.get_control_pool()[cite: 2]
    user = await db_control.get_user_by_email(pool, email)[cite: 2]

    if user is None or not security.verify_password(password, user["password_hash"]):[cite: 2, 5]
        return RedirectResponse(f"/login?next={next_}", status_code=302)

    request.session["user_id"] = str(user["id"])[cite: 2, 10]
    return RedirectResponse(next_, status_code=302)


async def logout(request: Request):
    request.session.clear()[cite: 10]
    return RedirectResponse("/login", status_code=302)[cite: 10]


# ---------------------------------------------------------------------------
# Dashboard & Settings Handlers
# ---------------------------------------------------------------------------
async def dashboard_get(request: Request):
    user_id = _require_login(request)[cite: 10]
    if not user_id:
        return RedirectResponse("/login", status_code=302)[cite: 10]

    pool = db_control.get_control_pool()[cite: 2]
    user = await db_control.get_user_by_id(pool, user_id)[cite: 2]
    if user is None:
        request.session.clear()[cite: 10]
        return RedirectResponse("/login", status_code=302)[cite: 10]

    flash_key = request.session.pop("flash_api_key", None)
    flash_html = ""
    if flash_key:
        flash_html = f"""
<div class="mb-6 p-4 bg-surface-container-low border border-primary rounded-lg">
    <strong class="text-xs uppercase font-mono text-primary block mb-1">New exom MCP API Key:</strong>
    <div class="flex items-center gap-2 mt-2">
        <input type="text" readonly value="{flash_key}" class="w-full font-mono text-xs bg-surface-white border p-2 rounded">
    </div>
</div>
"""

    base_url = str(request.base_url).rstrip("/")
    mcp_endpoint = f"{base_url}/mcp"

    body = f"""
{_navbar(request, user["email"])}
<main class="flex-grow py-10 px-6 bg-surface-white">
    <div class="max-w-3xl mx-auto">
        <div class="mb-6 flex justify-between items-center">
            <h1 class="text-2xl font-bold text-on-surface">Database &amp; MCP Settings</h1>
            <a href="/console" class="text-xs font-semibold text-primary underline">← Back to Console</a>
        </div>
        {flash_html}
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl mb-6">
            <h2 class="text-base font-semibold text-on-surface mb-2">MCP Endpoint</h2>
            <input type="text" readonly value="{mcp_endpoint}" class="w-full font-mono text-xs bg-surface-container-low border p-2 rounded">
        </div>
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl mb-6">
            <h2 class="text-base font-semibold text-on-surface mb-2">Personal Neon PostgreSQL Connection String</h2>
            <form method="POST" action="/dashboard/connection-string">
                <input type="text" name="connection_string" placeholder="postgresql://user:password@ep-xxx.neon.tech/dbname" required class="w-full px-4 py-2 border rounded text-xs font-mono mb-3">
                <button type="submit" class="bg-secondary-container text-on-surface px-6 py-2 rounded text-xs font-semibold border border-[#050505]">Save Connection String</button>
            </form>
        </div>
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl">
            <form method="POST" action="/dashboard/api-key/create">
                <button type="submit" class="bg-surface-white text-on-surface px-6 py-2.5 rounded text-xs font-semibold border border-[#050505]">Generate New API Key</button>
            </form>
        </div>
    </div>
</main>
"""
    return _page("Settings", body)


async def update_connection_string(request: Request):
    user_id = _require_login(request)[cite: 10]
    if not user_id:
        return RedirectResponse("/login", status_code=302)[cite: 10]

    form = await request.form()
    connection_string = str(form.get("connection_string", "")).strip()

    ok, err = await tenant_pools.test_connection_string(connection_string)[cite: 8]
    if not ok:
        return HTMLResponse(f"Database connection failed: {err}", status_code=400)

    pool = db_control.get_control_pool()[cite: 2]
    await db_control.set_connection_string(pool, user_id, security.encrypt_text(connection_string))[cite: 2, 5]
    await tenant_pools.get_manager().invalidate(user_id)[cite: 8]

    return RedirectResponse("/dashboard", status_code=302)


async def create_api_key(request: Request):
    user_id = _require_login(request)[cite: 10]
    if not user_id:
        return RedirectResponse("/login", status_code=302)[cite: 10]

    pool = db_control.get_control_pool()[cite: 2]
    raw_key = security.generate_api_key()[cite: 5]
    await db_control.create_api_key(pool, user_id, security.hash_api_key(raw_key), "Manual Key")[cite: 2, 5]
    request.session["flash_api_key"] = raw_key

    return RedirectResponse("/dashboard", status_code=302)


# ---------------------------------------------------------------------------
# Route Registry
# ---------------------------------------------------------------------------
routes = [
    Route("/", landing_page, methods=["GET"]),
    Route("/download", download_apk, methods=["GET"]),
    Route("/MemoryBase.apk", download_apk, methods=["GET"]),
    Route("/exom.apk", download_apk, methods=["GET"]),
    Route("/img1.jpeg", serve_root_image, methods=["GET"]),
    Route("/img2.jpeg", serve_root_image, methods=["GET"]),
    Route("/img3.jpeg", serve_root_image, methods=["GET"]),
    Route("/img4.jpeg", serve_root_image, methods=["GET"]),
    Route("/api/mobile/login", mobile_login, methods=["POST"]),
    Route("/console", console_page, methods=["GET"]),
    Route("/api/console/data", console_data, methods=["GET"]),
    Route("/signup", signup_get, methods=["GET"]),
    Route("/signup", signup_post, methods=["POST"]),
    Route("/login", login_get, methods=["GET"]),
    Route("/login", login_post, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/dashboard", dashboard_get, methods=["GET"]),
    Route("/dashboard/connection-string", update_connection_string, methods=["POST"]),
    Route("/dashboard/api-key/create", create_api_key, methods=["POST"]),
]
