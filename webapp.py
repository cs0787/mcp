"""
exom - Web Application & Mobile/Desktop Gateway
Full Python Starlette ASGI Application with:
- Dedicated console.html template loader
- Direct Android APK distribution endpoints (/download, /exom.apk, /MemoryBase.apk)
- Root image serving (/img1.jpeg - /img4.jpeg)
- Mobile & Desktop authentication gateway
- Unified 2D Second Brain graph endpoint
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
                }},
                borderRadius: {{
                    "DEFAULT": "0.125rem",
                    "lg": "0.25rem",
                    "xl": "0.5rem",
                    "full": "0.75rem"
                }},
                fontFamily: {{
                    "body-lg": ["Inter"],
                    "headline-lg-mobile": ["Hanken Grotesk"],
                    "headline-xl": ["Hanken Grotesk"],
                    "body-md": ["Inter"],
                    "headline-md": ["Hanken Grotesk"],
                    "headline-lg": ["Hanken Grotesk"],
                    "body-sm": ["Inter"],
                    "label-sm": ["JetBrains Mono"],
                    "label-md": ["JetBrains Mono"]
                }}
            }}
        }}
    }}
</script>

<style>
    html.lenis, html.lenis body {{ height: auto; }}
    .lenis.lenis-smooth {{ scroll-behavior: auto !important; }}
    .lenis.lenis-smooth [data-lenis-prevent] {{ overscroll-behavior: contain; }}
    .lenis.lenis-stopped {{ overflow: hidden; }}
    .lenis.lenis-smooth iframe {{ pointer-events: none; }}
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
    .hero-interactive-grid::after {{
        content: '';
        position: absolute;
        inset: 0;
        pointer-events: none;
        background-image: 
            linear-gradient(0deg, transparent 24%, #1a1313 25%, #756e6e 26%, transparent 27%, transparent 74%, #000000 75%, #000000 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, #000000 25%, #000000 26%, transparent 27%, transparent 74%, #000000 75%, #000000 76%, transparent 77%, transparent);
        background-size: 55px 55px;
        opacity: 0;
        transition: opacity 0.2s ease-in-out;
        -webkit-mask-image: radial-gradient(circle 160px at var(--x, -999px) var(--y, -999px), rgb(16, 15, 15) 0%, transparent 100%);
        mask-image: radial-gradient(circle 160px at var(--x, -999px) var(--y, -999px), rgb(36, 35, 35) 0%, transparent 100%);
    }}
    .hero-interactive-grid:hover::after {{ opacity: 1; }}

    .vertical-mode-text {{ writing-mode: vertical-rl; transform: rotate(180deg); letter-spacing: 0.32em; }}
    .expand-card {{ flex: 0 0 5.2rem; height: 28rem; border-radius: 26px; transition: all 0.5s cubic-bezier(0.25, 1, 0.35, 1); }}
    .expand-card.active {{ flex: 0 0 calc(28rem * 1024 / 1165); width: calc(28rem * 1024 / 1165); }}
    @media (max-width: 900px) {{
        .expand-card {{ flex: 0 0 4.2rem; height: 23rem; border-radius: 20px; }}
        .expand-card.active {{ flex: 0 0 calc(23rem * 1024 / 1165); width: calc(23rem * 1024 / 1165); }}
    }}

    .diagram-scaler-wrapper {{ width: 100%; max-width: min(1000px, calc((100vh - 200px) * 1000 / 524)); margin: 0 auto; position: relative; container-type: inline-size; }}
    .diagram-container {{ position: relative; width: 100%; aspect-ratio: 1000 / 524; background-color: #000000; overflow: hidden; }}
    .vertical-grid {{ position: absolute; inset: 0; display: flex; justify-content: space-between; padding: 0 3.5%; pointer-events: none; opacity: 0.12; }}
    .grid-line {{ width: 1px; height: 100%; background-color: #ffffff; }}
    svg.canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }}
    .line-green {{ stroke: #00e599; stroke-width: 1.5; fill: none; }}
    .line-green-dash {{ stroke: #00e599; stroke-width: 1.5; stroke-dasharray: 4 4; fill: none; }}
    .line-white-dash {{ stroke: #71767c; stroke-width: 1.5; stroke-dasharray: 4 4; fill: none; }}
    .line-white-solid {{ stroke: #71767c; stroke-width: 1.5; fill: none; }}
    .ruler-tick {{ stroke: #25282c; stroke-width: 1.5; transition: stroke 0.25s ease; }}
    .ruler-tick.lit {{ stroke: #00e599; }}
    .tick-active {{ stroke: #00e599; stroke-width: 1.5; }}
    .badge {{ position: absolute; transform: translate(-50%, -50%) scale(0.7); display: flex; align-items: center; gap: 0.6cqw; font-size: 1.2cqw; font-weight: 500; border-radius: 9999px; z-index: 2; user-select: none; white-space: nowrap; opacity: 0; filter: blur(3px); transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.3s ease; }}
    .badge.visible {{ opacity: 1; filter: blur(0px); transform: translate(-50%, -50%) scale(1); }}
    .badge-white {{ background: #ffffff; color: #000000; padding: 0.5cqw 1.2cqw; font-weight: 600; box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1); }}
    .badge-yellow {{ background: #fcee0a; color: #000000; padding: 0.6cqw 1.4cqw; font-weight: 700; font-size: 1.3cqw; box-shadow: 0 0 28px rgba(252, 238, 10, 0.45); }}
    .badge-dark {{ background: #25282e; color: #b1b8c0; border: 1px solid #383c44; padding: 0.4cqw 1.1cqw; font-size: 1.1cqw; }}
    .circle-icon {{ position: absolute; transform: translate(-50%, -50%) scale(0.4); border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 2; opacity: 0; transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }}
    .circle-icon.visible {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
    .check-node {{ width: 1.5cqw; height: 1.5cqw; background: #00e599; color: #000000; font-size: 0.9cqw; font-weight: 900; box-shadow: 0 0 10px rgba(0, 229, 153, 0.7); }}
    .outline-node {{ width: 2cqw; height: 2cqw; border-radius: 50%; background: #0b0d10; border: 1px solid #30353c; color: #8b949e; }}
    .hollow-node {{ width: 0.7cqw; height: 0.7cqw; background: #000000; border: 1.5px solid #00e599; border-radius: 50%; }}
    .meta-text {{ position: absolute; transform: translateX(-50%); font-size: 0.95cqw; color: #7d8590; text-align: center; line-height: 1.35; pointer-events: none; z-index: 2; opacity: 0; transition: opacity 0.3s ease; }}
    .meta-text.visible {{ opacity: 1; }}
    .timestamp {{ font-size: 0.95cqw; color: #555d68; letter-spacing: 0.3px; }}
    .glow-dot {{ fill: #00e599; filter: url(#glow); opacity: 0; transition: opacity 0.2s ease; }}
    .glow-dot.active {{ opacity: 1; }}

    :root {{ --font-main: 'Plus Jakarta Sans', sans-serif; --font-mono: 'JetBrains Mono', monospace; --neon-green: #00e599; --footer-bg: #F5F5F5; }}
    .showcase-container {{ position: relative; width: 100%; padding-bottom: 80px; font-family: var(--font-main); }}
    .sticky-nav-wrapper {{ position: absolute; top: 0; left: 0; right: 0; bottom: 80px; max-width: 1200px; margin: 0 auto; padding: 0 24px; pointer-events: none; z-index: 20; }}
    .sticky-sidebar {{ position: sticky; top: 90px; width: 260px; pointer-events: auto; padding-top: 8px; }}
    .menu-badge-btn {{ display: inline-flex; align-items: center; padding: 10px 18px; border-radius: 12px; color: #000000; background: #facc15; font-weight: 800; font-size: 13.5px; text-transform: uppercase; margin-bottom: 20px; }}
    .mobile-feature-badge {{ display: none; align-items: center; padding: 6px 12px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 14px; width: fit-content; }}
    .section-dark .mobile-feature-badge {{ background: rgba(255, 255, 255, 0.1); color: #00e599; border: 1px solid rgba(0, 229, 153, 0.3); }}
    .section-light .mobile-feature-badge {{ background: #f4f4f5; color: #18181b; border: 1px solid #e4e4e7; }}
    .nav-list {{ list-style: none; display: flex; flex-direction: column; gap: 12px; margin: 0; padding: 0; }}
    .nav-btn {{ display: flex; align-items: center; gap: 10px; font-size: 14.5px; font-weight: 500; color: #71717a; text-decoration: none; cursor: pointer; transition: color 0.2s; }}
    .nav-btn.active {{ color: #ffffff; font-weight: 700; }}
    .sticky-sidebar.theme-light .nav-btn.active {{ color: #000000; }}
    .nav-dot {{ width: 6px; height: 6px; border-radius: 50%; background-color: transparent; transition: all 0.2s; }}
    .nav-btn.active .nav-dot {{ background-color: var(--neon-green); box-shadow: 0 0 10px rgba(0, 229, 153, 0.9); transform: scale(1.3); }}
    .feature-section {{ width: 100%; min-height: 85vh; padding: 90px 0; display: flex; align-items: center; }}
    .section-inner {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; width: 100%; display: grid; grid-template-columns: 260px 1fr; column-gap: 56px; }}
    .section-content {{ grid-column: 2; max-width: 820px; }}
    .section-dark {{ background-color: #000000; color: #e2e8f0; }}
    .section-dark .hero-heading {{ color: #ffffff; }}
    .section-dark .lead-text {{ color: #a1a1aa; }}
    .section-light {{ background-color: #ffffff; color: #000000; }}
    .section-light .hero-heading {{ color: #000000; }}
    .section-light .lead-text {{ color: #52525b; }}
    .hero-heading {{ font-size: clamp(28px, 4vw, 48px); font-weight: 800; letter-spacing: -0.035em; line-height: 1.15; margin-bottom: 20px; }}
    .lead-text {{ font-size: 17px; line-height: 1.6; margin-bottom: 28px; }}
    .checklist {{ list-style: none; display: flex; flex-direction: column; gap: 12px; margin-bottom: 32px; padding-left: 0; }}
    .checklist li {{ display: flex; align-items: flex-start; gap: 10px; font-size: 15px; font-weight: 600; }}
    .checklist li .check-icon {{ color: var(--neon-green); font-weight: 800; }}
    .terminal-box {{ background: #09090b; border: 1px solid #27272a; border-radius: 12px; overflow: hidden; font-family: var(--font-mono); max-width: 740px; box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.7); }}
    .terminal-topbar {{ background: #18181b; padding: 10px 16px; display: flex; align-items: center; gap: 8px; }}
    .terminal-dots {{ display: flex; gap: 6px; }}
    .terminal-dots span {{ width: 10px; height: 10px; border-radius: 50%; }}
    .dot-red {{ background: #ef4444; }} .dot-yellow {{ background: #eab308; }} .dot-green {{ background: #22c55e; }}
    .terminal-title {{ font-size: 12px; color: #a1a1aa; font-weight: 500; margin-left: 6px; }}
    .terminal-code {{ padding: 20px; font-size: 13.5px; color: #e4e4e7; overflow-x: auto; line-height: 1.65; }}
    .hl-key {{ color: #38bdf8; }} .hl-str {{ color: #fbbf24; }} .hl-green {{ color: #4ade80; }} .hl-dim {{ color: #71717a; }}
    .neon-footer {{ background-color: var(--footer-bg); border-top: 1px solid #e5e5e5; color: #52525b; padding: 80px 24px 48px; font-family: var(--font-main); }}
    .footer-container {{ max-width: 1200px; margin: 0 auto; }}
    .footer-top {{ display: grid; grid-template-columns: 2fr repeat(4, 1fr); gap: 48px; margin-bottom: 64px; }}
    .footer-brand {{ display: flex; flex-direction: column; gap: 16px; }}
    .footer-logo {{ display: inline-flex; align-items: center; gap: 10px; text-decoration: none; color: #18181b; font-weight: 800; font-size: 20px; }}
    .footer-logo svg {{ width: 24px; height: 24px; }}
    .footer-tagline {{ font-size: 14px; color: #71717a; max-width: 270px; line-height: 1.5; }}
    .status-badge {{ display: inline-flex; align-items: center; gap: 8px; width: fit-content; padding: 6px 12px; border-radius: 9999px; background: #ffffff; border: 1px solid #e4e4e7; color: #3f3f46; font-size: 12px; font-weight: 600; text-decoration: none; }}
    .status-dot {{ width: 6px; height: 6px; border-radius: 50%; background-color: #16a34a; box-shadow: 0 0 8px #16a34a; }}
    .footer-col h4 {{ font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #18181b; margin-bottom: 20px; }}
    .footer-col ul {{ list-style: none; display: flex; flex-direction: column; gap: 12px; padding: 0; }}
    .footer-col ul li a {{ color: #71717a; text-decoration: none; font-size: 14px; font-weight: 500; transition: color 0.15s; }}
    .footer-col ul li a:hover {{ color: #18181b; font-weight: 600; }}
    .footer-bottom {{ border-top: 1px solid #e5e5e5; padding-top: 32px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px; font-size: 13px; color: #71717a; }}

    @media (max-width: 900px) {{
      .sticky-nav-wrapper {{ display: none !important; }}
      .mobile-feature-badge {{ display: inline-flex; }}
      .section-inner {{ display: block; padding: 0 20px; }}
      .section-content {{ width: 100%; }}
      .feature-section {{ padding: 60px 0; min-height: auto; }}
      .footer-top {{ grid-template-columns: 1fr 1fr; gap: 36px; }}
      .footer-brand {{ grid-column: 1 / -1; }}
      .footer-bottom {{ flex-direction: column; align-items: flex-start; }}
    }}
</style>
</head>
<body class="bg-surface-white text-on-surface font-body-md min-h-screen flex flex-col selection:bg-primary-container selection:text-on-primary-container">

<script>
    window.lenis = new Lenis({{
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      smoothWheel: true,
      infinite: false,
    }});
    function raf(time) {{ window.lenis.raf(time); requestAnimationFrame(raf); }}
    requestAnimationFrame(raf);

    function copyToClipboard(text, btnId) {{
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById(btnId);
            const orig = btn.innerText;
            btn.innerText = 'Copied!';
            setTimeout(() => btn.innerText = orig, 2000);
        }});
    }}
    function setTerminalTab(tab) {{
        ['claude', 'cursor', 'curl'].forEach(t => {{
            const btn = document.getElementById('tab-' + t);
            const block = document.getElementById('snippet-' + t);
            if (t === tab) {{
                btn.className = 'px-3 py-1.5 text-xs font-mono rounded bg-on-surface text-surface-white font-semibold transition-colors whitespace-nowrap';
                block.classList.remove('hidden');
            }} else {{
                btn.className = 'px-3 py-1.5 text-xs font-mono rounded text-text-secondary hover:text-on-surface bg-transparent transition-colors whitespace-nowrap';
                block.classList.add('hidden');
            }}
        }});
    }}
</script>

{body}
</body>
</html>
""")


def _require_login(request: Request) -> str | None:
    return request.session.get("user_id")


def _safe_next(raw: str | None) -> str:
    if raw and raw.startswith("/") and not raw.startswith("//"):
        return raw
    return "/console"


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
# File Serving Routes
# ---------------------------------------------------------------------------
async def download_apk(request: Request):
    for name in ("exom.apk", "MemoryBase.apk"):
        apk_path = os.path.join(os.path.dirname(__file__), name)
        if os.path.exists(apk_path):
            return FileResponse(path=apk_path, media_type="application/vnd.android.package-archive", filename="exom.apk")
    return HTMLResponse("<div style='font-family:sans-serif;padding:40px;text-align:center;'><h2>Build in progress</h2><p>The companion installer will be available shortly.</p><a href='/'>← Return Home</a></div>", status_code=404)


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

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_email(pool, email)

    if user is None or not security.verify_password(password, user["password_hash"]):
        return JSONResponse({"error": "Invalid email or password"}, status_code=401)

    decrypted_conn_str = None
    if user["connection_string_encrypted"]:
        try:
            decrypted_conn_str = security.decrypt_text(user["connection_string_encrypted"])
        except Exception:
            return JSONResponse({"error": "Failed to decrypt connection string"}, status_code=500)

    return JSONResponse({
        "status": "success",
        "user_id": str(user["id"]),
        "email": user["email"],
        "has_connection_string": decrypted_conn_str is not None,
        "connection_string": decrypted_conn_str,
    })


# ---------------------------------------------------------------------------
# Desktop Graph Gateway Endpoints
# ---------------------------------------------------------------------------
async def desktop_get_graph(request: Request):
    user_id = request.headers.get("x-user-id") or _require_login(request)
    if not user_id:
        return JSONResponse({"error": "Unauthorized: Missing user credentials"}, status_code=401)

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(pool, user_id)

    if not user or not user["connection_string_encrypted"]:
        return JSONResponse({"nodes": [], "edges": []})

    conn_str = security.decrypt_text(user["connection_string_encrypted"])
    user_pool = await tenant_pools.get_manager().get_pool(str(user["id"]), conn_str)

    mobile_notes = await user_pool.fetch(
        """
        SELECT id, coalesce(workspace_name, 'General') as workspace, 'thought' as node_type,
               title, content as summary, '' as rationale, '' as impact_analysis,
               ARRAY[]::text[] as tags, 'Universal Memory' as model_badge, updated_at
        FROM notes
        ORDER BY updated_at DESC
        """
    )

    project_nodes = []
    edges = []
    try:
        project_nodes = await user_pool.fetch(
            """
            SELECT id, workspace, node_type, title, summary, rationale, impact_analysis,
                   affected_components as tags, status as model_badge, updated_at
            FROM project_nodes
            ORDER BY created_at DESC
            """
        )
        edges = await user_pool.fetch(
            """
            SELECT id, source_node_id, target_node_id, relation_type
            FROM project_edges
            """
        )
    except Exception:
        pass

    all_nodes = list(mobile_notes) + list(project_nodes)

    return JSONResponse({
        "nodes": [
            {
                "id": str(n["id"]),
                "type": n["node_type"],
                "workspace": n["workspace"],
                "title": n["title"] or "Untitled Memory",
                "summary": n["summary"] or "",
                "rationale": n["rationale"] or "",
                "impact": n["impact_analysis"] or "",
                "tags": n["tags"] or [],
                "model": n["model_badge"],
                "updated_at": n["updated_at"]
            }
            for n in all_nodes
        ],
        "edges": [
            {
                "id": str(e["id"]),
                "source": str(e["source_node_id"]),
                "target": str(e["target_node_id"]),
                "label": e["relation_type"]
            }
            for e in edges
        ]
    })


async def desktop_batch_save_edges(request: Request):
    user_id = request.headers.get("x-user-id") or _require_login(request)
    if not user_id:
        return JSONResponse({"error": "Unauthorized: Missing user credentials"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    workspace = body.get("workspace", "Default")
    new_edges = body.get("edges", [])

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(pool, user_id)
    if not user or not user["connection_string_encrypted"]:
        return JSONResponse({"error": "No database linked"}, status_code=400)

    conn_str = security.decrypt_text(user["connection_string_encrypted"])
    user_pool = await tenant_pools.get_manager().get_pool(str(user["id"]), conn_str)

    async with user_pool.acquire() as conn:
        for edge in new_edges:
            try:
                s_id = uuid.UUID(str(edge["source"]))
                t_id = uuid.UUID(str(edge["target"]))
                await conn.execute(
                    """
                    INSERT INTO project_edges (workspace, source_node_id, target_node_id, relation_type)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT DO NOTHING
                    """,
                    workspace, s_id, t_id, str(edge.get("label", "semantic_link"))
                )
            except Exception:
                continue

    return JSONResponse({"status": "ok", "saved": len(new_edges)})


# ---------------------------------------------------------------------------
# Console Page (Loaded from external console.html template)
# ---------------------------------------------------------------------------
async def console_page(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(pool, user_id)
    if user is None:
        request.session.clear()
        return RedirectResponse("/login", status_code=302)

    user_email = user["email"]
    display_name = user_email.split("@")[0].capitalize()
    initial = display_name[0].upper()

    workspaces = []
    nodes = []
    edges = []
    selected_workspace = request.query_params.get("ws", "")

    if user["connection_string_encrypted"]:
        try:
            conn_str = security.decrypt_text(user["connection_string_encrypted"])
            user_pool = await tenant_pools.get_manager().get_pool(str(user["id"]), conn_str)
            
            ws_rows = await user_pool.fetch("SELECT DISTINCT workspace FROM project_nodes ORDER BY workspace ASC")
            workspaces = [r["workspace"] for r in ws_rows]
            
            if selected_workspace:
                node_rows = await user_pool.fetch(
                    """
                    SELECT id, node_type, sequence_index, title, summary, rationale, impact_analysis, affected_components, status, central_hub_id, created_at
                    FROM project_nodes
                    WHERE workspace = $1
                    ORDER BY sequence_index ASC NULLS LAST, created_at ASC
                    """,
                    selected_workspace
                )
                nodes = [dict(r) for r in node_rows]

                edge_rows = await user_pool.fetch(
                    """
                    SELECT source_node_id, target_node_id, relation_type
                    FROM project_edges
                    WHERE workspace = $1
                    """,
                    selected_workspace
                )
                edges = [dict(r) for r in edge_rows]
        except Exception:
            pass

    if workspaces:
        repo_list_html = "".join(f"""
            <li class="chat-item {'active' if ws == selected_workspace else ''}" onclick="window.location='/console?ws={ws}'">
                📁 {ws}
            </li>
        """ for ws in workspaces)
    else:
        repo_list_html = '<div class="p-3 text-xs text-[#8e8e8e]">No workspaces found. Connect MCP to an AI client to start committing memory.</div>'

    if selected_workspace:
        if nodes:
            nodes_html = ""
            svg_lines_html = ""
            card_width = 250
            card_height = 145
            pos_dict = {}
            linear_index = 0
            hub_index = 0
            
            for node in nodes:
                nid = str(node['id'])
                ntype = node.get('node_type', 'codebase_change')
                
                if ntype == 'hub':
                    x = 100 + (hub_index * 420)
                    y = 80
                    hub_index += 1
                elif ntype == 'concept':
                    x = 100 + (linear_index * 320)
                    y = 220
                    linear_index += 1
                else:
                    x = 100 + (linear_index * 320)
                    y = 400 + (70 if linear_index % 2 == 1 else -40)
                    linear_index += 1

                pos_dict[nid] = (x, y)

            for edge in edges:
                s_id = str(edge['source_node_id'])
                t_id = str(edge['target_node_id'])
                if s_id in pos_dict and t_id in pos_dict:
                    sx, sy = pos_dict[s_id]
                    tx, ty = pos_dict[t_id]
                    scx, scy = sx + (card_width / 2), sy + (card_height / 2)
                    tcx, tcy = tx + (card_width / 2), ty + (card_height / 2)
                    
                    stroke_color = "#3b82f6" if edge.get('relation_type') == 'belongs_to_hub' else "#00e599"
                    svg_lines_html += f'<line x1="{scx}" y1="{scy}" x2="{tcx}" y2="{tcy}" stroke="{stroke_color}" stroke-width="2" stroke-dasharray="4 4" />'

            for node in nodes:
                nid = str(node['id'])
                x, y = pos_dict[nid]
                title_esc = node['title'].replace('"', '&quot;')
                summary_esc = node['summary'].replace('"', '&quot;')
                why_esc = (node['rationale'] or 'No rationale provided').replace('"', '&quot;')
                impact_esc = (node['impact_analysis'] or 'None').replace('"', '&quot;')
                step_idx = node['sequence_index'] or '-'
                ntype = node.get('node_type', 'codebase_change')
                
                layer_badge = ""
                border_cls = "border-[#d4d4d8]"
                if ntype == 'hub':
                    layer_badge = '<span class="bg-amber-100 text-amber-800 text-[10px] font-mono px-1.5 py-0.5 rounded font-bold">HUB</span>'
                    border_cls = "border-amber-400 bg-amber-50/20"
                elif ntype == 'concept':
                    layer_badge = '<span class="bg-blue-100 text-blue-800 text-[10px] font-mono px-1.5 py-0.5 rounded font-bold">CONCEPT</span>'
                    border_cls = "border-blue-400 bg-blue-50/20"
                else:
                    layer_badge = f'<span class="node-step">Memory #{step_idx}</span>'

                nodes_html += f"""
                <div class="canvas-node {border_cls}" style="left: {x}px; top: {y}px; width: {card_width}px;" 
                     ondblclick="openNodeModal('{title_esc}', '{summary_esc}', '{why_esc}', '{impact_esc}')"
                     onclick="openNodeModal('{title_esc}', '{summary_esc}', '{why_esc}', '{impact_esc}')">
                    <div class="node-header">
                        {layer_badge}
                        <span class="node-status">✓</span>
                    </div>
                    <div class="node-title">{node['title']}</div>
                    <div class="node-snippet">{node['summary'][:90]}...</div>
                    <div class="node-footer">Double-click / Tap to inspect</div>
                </div>
                """
            
            canvas_content = f"""
            <div id="canvasViewport" style="transform-origin: 0 0; position: absolute; top: 0; left: 0;">
                <svg class="canvas-svg">{svg_lines_html}</svg>
                {nodes_html}
            </div>
            """
        else:
            canvas_content = """
            <div class="empty-canvas-state">
                <div class="empty-icon">⚡</div>
                <h3>No Context Nodes Found</h3>
                <p>Connect your AI client to exom to start streaming persistent memory.</p>
                <code>mcpServers -&gt; exom</code>
            </div>
            """
    else:
        canvas_content = """
        <div class="empty-canvas-state">
            <div class="empty-icon">📁</div>
            <h3>Universal Memory Vault</h3>
            <p>Select a workspace from the sidebar to inspect its connected architecture graph.</p>
        </div>
        """

    template_path = os.path.join(os.path.dirname(__file__), "console.html")
    if not os.path.exists(template_path):
        return HTMLResponse("console.html template missing from root directory.", status_code=500)

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    rendered = (
        template_html.replace("{{INITIAL}}", initial)
        .replace("{{DISPLAY_NAME}}", display_name)
        .replace("{{REPO_LIST_HTML}}", repo_list_html)
        .replace("{{CANVAS_CONTENT}}", canvas_content)
    )

    return HTMLResponse(rendered)


# ---------------------------------------------------------------------------
# Signup & Login
# ---------------------------------------------------------------------------
async def signup_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    
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
                <label class="block text-xs font-semibold text-on-surface mb-1">Password (min 8 characters)</label>
                <input type="password" name="password" placeholder="••••••••" minlength="8" required class="w-full px-4 py-2 border border-border-muted rounded text-sm focus:outline-none focus:border-primary">
            </div>
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-sm font-semibold border-b-2 border-r-2 border-[#050505] active:translate-y-[1px] active:translate-x-[1px] transition-all">Sign Up</button>
        </form>
        <p class="text-xs text-text-secondary text-center mt-6">Already have an account? <a href="/login?next={next_}" class="text-primary font-semibold hover:underline">Log in</a></p>
    </div>
</main>
"""
    return _page("Sign up", body)


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
        body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-4 sm:px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-6 sm:p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Create Your Account</h2>
        <div class="p-3 bg-red-50 text-red-700 text-xs rounded mb-4 border border-red-200">{error}</div>
        <form method="POST" action="/signup">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-on-surface mb-1">Email Address</label>
                <input type="email" name="email" value="{email}" required autofocus class="w-full px-4 py-2 border border-border-muted rounded text-sm">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-on-surface mb-1">Password</label>
                <input type="password" name="password" minlength="8" required class="w-full px-4 py-2 border border-border-muted rounded text-sm">
            </div>
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-xs font-semibold border border-[#050505]">Sign Up</button>
        </form>
    </div>
</main>
"""
        return _page("Sign up", body)

    pool = db_control.get_control_pool()
    try:
        user_id = await db_control.create_user(pool, email, security.hash_password(password))
    except asyncpg.exceptions.UniqueViolationError:
        body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-4 sm:px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-6 sm:p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Create Your Account</h2>
        <div class="p-3 bg-red-50 text-red-700 text-xs rounded mb-4 border border-red-200">An account with that email already exists.</div>
        <p class="text-xs"><a href="/login?next={next_}" class="text-primary font-semibold underline">Log in instead</a></p>
    </div>
</main>
"""
        return _page("Sign up", body)

    request.session["user_id"] = user_id
    return RedirectResponse("/console", status_code=302)


async def login_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    
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
                <input type="email" name="email" placeholder="name@example.com" required autofocus class="w-full px-4 py-2 border border-border-muted rounded text-sm focus:outline-none focus:border-primary">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-on-surface mb-1">Password</label>
                <input type="password" name="password" placeholder="••••••••" required class="w-full px-4 py-2 border border-border-muted rounded text-sm focus:outline-none focus:border-primary">
            </div>
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-sm font-semibold border-b-2 border-r-2 border-[#050505] active:translate-y-[1px] active:translate-x-[1px] transition-all">Log In</button>
        </form>
        <p class="text-xs text-text-secondary text-center mt-6">No account yet? <a href="/signup?next={next_}" class="text-primary font-semibold hover:underline">Sign up</a></p>
    </div>
</main>
"""
    return _page("Log in", body)


async def login_post(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    password = str(form.get("password", ""))
    next_ = _safe_next(str(form.get("next", "")))

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_email(pool, email)

    if user is None or not security.verify_password(password, user["password_hash"]):
        body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-4 sm:px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-6 sm:p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Welcome Back</h2>
        <div class="p-3 bg-red-50 text-red-700 text-xs rounded mb-4 border border-red-200">Incorrect email or password.</div>
        <form method="POST" action="/login">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-on-surface mb-1">Email Address</label>
                <input type="email" name="email" value="{email}" required autofocus class="w-full px-4 py-2 border border-border-muted rounded text-sm">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-on-surface mb-1">Password</label>
                <input type="password" name="password" required class="w-full px-4 py-2 border border-border-muted rounded text-sm">
            </div>
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-xs font-semibold border border-[#050505]">Log In</button>
        </form>
    </div>
</main>
"""
        return _page("Log in", body)

    request.session["user_id"] = str(user["id"])
    return RedirectResponse("/console", status_code=302)


async def logout(request: Request):
    form = await request.form()
    next_ = str(form.get("next", "")) if form.get("next") else None
    request.session.clear()
    if next_ and next_.startswith("/") and not next_.startswith("//"):
        return RedirectResponse(f"/login?next={next_}", status_code=302)
    return RedirectResponse("/login", status_code=302)


# ---------------------------------------------------------------------------
# Dashboard & Settings
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
<div class="mb-6 p-4 bg-surface-container-low border border-primary rounded-lg">
    <strong class="text-xs uppercase font-mono text-primary block mb-1">New exom MCP API Key (Shown Once — Copy Now):</strong>
    <div class="flex items-center gap-2 mt-2">
        <input type="text" readonly value="{flash_key}" id="newApiKeyField" class="w-full font-mono text-xs bg-surface-white border border-border-muted p-2 rounded">
        <button id="btnCopyKey" onclick="copyToClipboard('{flash_key}', 'btnCopyKey')" class="bg-secondary-container text-on-surface px-4 py-2 rounded text-xs font-semibold whitespace-nowrap border border-[#050505]">Copy</button>
    </div>
    <p class="text-xs text-text-secondary mt-2">Use this as your Bearer Token for Claude Desktop or Cursor configurations.</p>
</div>
"""

    if user["connection_string_encrypted"]:
        masked = security.mask_connection_string(security.decrypt_text(user["connection_string_encrypted"]))
        conn_status = f'<p class="text-xs text-text-secondary">Currently linked: <code class="text-on-surface font-mono">{masked}</code></p>'
    else:
        conn_status = '<div class="p-3 bg-red-50 text-red-700 text-xs rounded border border-red-200">No Neon PostgreSQL connection string set yet. Cross-model sync will fail until configured.</div>'

    keys = await db_control.list_api_keys(pool, user_id)
    active_keys = [k for k in keys if k["revoked_at"] is None]
    if active_keys:
        rows = "".join(f"""
<div class="flex items-center justify-between py-3 border-b border-border-muted last:border-0">
    <div>
        <div class="text-sm font-semibold text-on-surface">{k['label']}</div>
        <div class="text-xs text-text-secondary">Created {k['created_at'].strftime('%b %d, %Y')}{f" • Last used {k['last_used_at'].strftime('%b %d, %Y')}" if k['last_used_at'] else ""}</div>
    </div>
    <form method="POST" action="/dashboard/api-key/revoke" class="m-0">
        <input type="hidden" name="key_id" value="{k['id']}">
        <button type="submit" class="text-error text-xs font-semibold hover:underline" onclick="return confirm('Revoke this key? Apps using it will disconnect immediately.');">Revoke</button>
    </form>
</div>
""" for k in active_keys)
    else:
        rows = '<p class="text-xs text-text-secondary">No active API keys found.</p>'

    base_url = str(request.base_url).rstrip("/")
    mcp_endpoint = f"{base_url}/mcp"
    nav_html = _navbar(request, user["email"])

    body = f"""
{nav_html}
<main class="flex-grow py-10 px-6 bg-surface-white">
    <div class="max-w-3xl mx-auto">
        <div class="mb-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-on-surface mb-1">Database &amp; MCP Settings</h1>
                <p class="text-xs text-text-secondary">Manage your personal Neon PostgreSQL database connection string and exom API keys.</p>
            </div>
            <a href="/console" class="text-xs font-semibold text-primary underline">← Back to Console</a>
        </div>

        {flash_html}

        <!-- 1. Endpoint & Connection URL -->
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl mb-6 shadow-sm">
            <h2 class="text-base font-semibold text-on-surface mb-1">1. exom MCP Server Endpoint</h2>
            <p class="text-xs text-text-secondary mb-3">Provide this URL when configuring Claude Desktop, Cursor, or any MCP client connector.</p>
            <div class="flex items-center gap-2">
                <input type="text" readonly value="{mcp_endpoint}" id="mcpEndpointField" class="w-full font-mono text-xs bg-surface-container-low border border-border-muted p-2.5 rounded">
                <button id="btnCopyEndpoint" onclick="copyToClipboard('{mcp_endpoint}', 'btnCopyEndpoint')" class="bg-surface-white text-on-surface px-4 py-2.5 rounded text-xs font-semibold whitespace-nowrap border border-[#050505]">Copy URL</button>
            </div>
        </div>

        <!-- 2. Neon Database Connection String Settings -->
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl mb-6 shadow-sm">
            <h2 class="text-base font-semibold text-on-surface mb-1">2. Personal Neon Database Connection String</h2>
            <p class="text-xs text-text-secondary mb-3">Paste your PostgreSQL connection string. All companion apps, AI agents, and desktop clients synchronize with this instance.</p>
            {conn_status}
            <form method="POST" action="/dashboard/connection-string" class="mt-4">
                <div class="mb-3">
                    <input type="text" name="connection_string" placeholder="postgresql://user:password@ep-xxx.neon.tech/dbname" required class="w-full px-4 py-2.5 border border-border-muted rounded text-xs font-mono focus:outline-none focus:border-primary">
                </div>
                <button type="submit" class="bg-secondary-container text-on-surface px-6 py-2.5 rounded text-xs font-semibold border border-[#050505]">Save Connection String</button>
            </form>
        </div>

        <!-- 3. API Keys Management -->
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl shadow-sm">
            <h2 class="text-base font-semibold text-on-surface mb-1">3. exom MCP API Keys</h2>
            <p class="text-xs text-text-secondary mb-3">API keys are generated automatically through Claude OAuth, or you can create them manually for custom agents.</p>
            <div class="divide-y border-border-muted mb-4">
                {rows}
            </div>
            <form method="POST" action="/dashboard/api-key/create">
                <button type="submit" class="bg-surface-white text-on-surface px-6 py-2.5 rounded text-xs font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors">Generate New Manual API Key</button>
            </form>
        </div>
    </div>
</main>
"""
    return _page("Settings", body)


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
    body = f"""
<main class="flex-grow flex items-center justify-center py-16 px-6 bg-surface-white">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-8 rounded-xl shadow-sm text-center">
        <h2 class="text-lg font-bold text-error mb-2">Error</h2>
        <div class="p-3 bg-red-50 text-red-700 text-xs rounded mb-6 border border-red-200">{message}</div>
        <a href="/dashboard" class="inline-block bg-secondary-container text-on-surface px-6 py-2.5 rounded text-xs font-semibold border border-[#050505] no-underline">Back to Settings</a>
    </div>
</main>
"""
    return _page("Error", body)


# Route registry
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
    Route("/signup", signup_get, methods=["GET"]),
    Route("/signup", signup_post, methods=["POST"]),
    Route("/login", login_get, methods=["GET"]),
    Route("/login", login_post, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/console", console_page, methods=["GET"]),
    Route("/dashboard", dashboard_get, methods=["GET"]),
    Route("/dashboard/connection-string", update_connection_string, methods=["POST"]),
    Route("/dashboard/api-key/create", create_api_key, methods=["POST"]),
    Route("/dashboard/api-key/revoke", revoke_api_key, methods=["POST"]),
    Route("/api/desktop/graph", desktop_get_graph, methods=["GET"]),
    Route("/api/desktop/edges/batch", desktop_batch_save_edges, methods=["POST"]),
]
