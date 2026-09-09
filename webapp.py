"""
exom - The Unified Second Brain & Memory Layer for All AI
Full Python Starlette ASGI Application with:
- Dedicated console.html template loader
- In-console Account & Database Settings (eliminating standalone /dashboard)
- Categorized Second Brain partitions (Coding Architecture vs AI Chats)
- Direct Android APK distribution endpoints (/download, /exom.apk, /MemoryBase.apk)
- Root image serving (/img1.jpeg - /img4.jpeg)
- Mobile & Desktop authentication gateway
- Unified 2D Second Brain graph endpoint (merging notes and MCP nodes)
- Responsive Mobile Showcase (1024x1165 aspect ratio, unnumbered vertical labels)
- Lenis Smooth Scrolling (@studio-freight/lenis)
- Scrubbed, scroll-driven Instant Context Pipeline Animation
- Dual-mode Core Capabilities Scroll-Spy
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
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://unpkg.com/lenis@1.1.20/dist/lenis.min.js"></script>
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
    user = await db_control.get_user_by_email(pool, email)[cite: 2]

    if user is None or not security.verify_password(password, user["password_hash"]):[cite: 2]
        return JSONResponse({"error": "Invalid email or password"}, status_code=401)

    decrypted_conn_str = None
    if user["connection_string_encrypted"]:[cite: 2]
        try:
            decrypted_conn_str = security.decrypt_text(user["connection_string_encrypted"])
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
# Desktop Graph Gateway Endpoints
# ---------------------------------------------------------------------------
async def desktop_get_graph(request: Request):
    user_id = request.headers.get("x-user-id") or _require_login(request)
    if not user_id:
        return JSONResponse({"error": "Unauthorized: Missing user credentials"}, status_code=401)

    category = request.query_params.get("category", "all")
    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(pool, user_id)[cite: 2]

    if not user or not user["connection_string_encrypted"]:[cite: 2]
        return JSONResponse({"nodes": [], "edges": []})

    conn_str = security.decrypt_text(user["connection_string_encrypted"])
    user_pool = await tenant_pools.get_manager().get_pool(str(user["id"]), conn_str)[cite: 2]

    all_nodes = []
    edges = []

    if category in ("all", "chat"):
        mobile_notes = await user_pool.fetch(
            """
            SELECT id, coalesce(workspace_name, 'General') as workspace, 'chat_summary' as node_type,
                   title, content as summary, '' as rationale, '' as impact_analysis,
                   ARRAY[]::text[] as tags, 'Chat / Thought' as model_badge, updated_at
            FROM notes
            ORDER BY updated_at DESC
            """
        )
        chat_nodes = await user_pool.fetch(
            """
            SELECT id, workspace, node_type, title, summary, rationale, impact_analysis,
                   affected_components as tags, status as model_badge, updated_at
            FROM project_nodes
            WHERE node_type = 'chat_summary'
            ORDER BY created_at DESC
            """
        )
        all_nodes.extend(mobile_notes)
        all_nodes.extend(chat_nodes)

    if category in ("all", "coding"):
        code_nodes = await user_pool.fetch(
            """
            SELECT id, workspace, node_type, title, summary, rationale, impact_analysis,
                   affected_components as tags, status as model_badge, updated_at
            FROM project_nodes
            WHERE node_type IN ('codebase_change', 'hub', 'concept')
            ORDER BY created_at DESC
            """
        )
        all_nodes.extend(code_nodes)

    try:
        edges = await user_pool.fetch(
            """
            SELECT id, source_node_id, target_node_id, relation_type
            FROM project_edges
            """
        )
    except Exception:
        pass

    return JSONResponse({
        "nodes": [
            {
                "id": str(n["id"]),
                "type": n["node_type"],
                "category": "chat" if n["node_type"] in ("chat_summary", "thought", "note") else "coding",
                "workspace": n["workspace"],
                "title": n["title"] or "Untitled",
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
    user = await db_control.get_user_by_id(pool, user_id)[cite: 2]
    if not user or not user["connection_string_encrypted"]:[cite: 2]
        return JSONResponse({"error": "No database linked"}, status_code=400)

    conn_str = security.decrypt_text(user["connection_string_encrypted"])
    user_pool = await tenant_pools.get_manager().get_pool(str(user["id"]), conn_str)[cite: 2]

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
# Landing Page
# ---------------------------------------------------------------------------
async def landing_page(request: Request):
    user_id = _require_login(request)
    user_email = None
    if user_id:
        pool = db_control.get_control_pool()
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
    <section class="relative pt-12 sm:pt-20 pb-16 sm:pb-20 border-b border-border-muted hero-interactive-grid"
             onmousemove="const r = this.getBoundingClientRect(); this.style.setProperty('--x', (event.clientX - r.left) + 'px'); this.style.setProperty('--y', (event.clientY - r.top) + 'px');">
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
                        <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.551 0 .9993.4482.9993.9993s-.4483.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9994.4482.9994.9993s-.4483.9997-.9994.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.4114 13.8533 8.083 12 8.083s-3.5902.3284-5.1368.8667L4.8409 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589 0 18.761h24c-.3432-4.1021-2.6889-7.5743-6.1185-9.4396"/></svg>
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
                    <p class="text-primary mt-2">✓ 14 decisions &amp; concepts shared across Claude, Cursor &amp; DeepSeek.</p>
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

    <!-- Mobile Showcase -->
    <section id="mobile-showcase" class="py-16 sm:py-24 bg-[#050507] text-white border-b border-neutral-800 overflow-hidden relative">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-12 text-center mb-10">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.05] border border-white/[0.1] text-xs font-mono text-[#00e599] mb-3">
                <span class="w-2 h-2 rounded-full bg-[#00e599] animate-pulse"></span>
                Universal Companion Ecosystem
            </div>
            <h2 class="text-2xl sm:text-4xl font-bold tracking-tight text-white mb-3">
                Your Pocket Mind Palace
            </h2>
            <p class="text-sm sm:text-base text-neutral-400 max-w-xl mx-auto leading-relaxed">
                Connect your personal Neon PostgreSQL database once. Explore thoughts in 2D space, query reasoning models, and inspect architectural graphs anywhere.
            </p>
        </div>

        <div class="w-full flex items-center justify-center px-4 overflow-x-auto pb-4">
            <div id="skiperCardsWrapper" class="flex items-center justify-center gap-2.5 sm:gap-3.5 max-w-6xl w-full">
                
                <div class="expand-card active group relative cursor-pointer overflow-hidden bg-[#0c0d11] border border-white/[0.09] hover:border-[#00e599]/40 shadow-2xl transition-all" data-index="0">
                    <img src="/img1.jpeg" alt="Spatial Canvas" class="absolute inset-0 w-full h-full object-contain bg-black filter brightness-[0.85] group-[.active]:brightness-100 transition-all duration-500 pointer-events-none" />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent pointer-events-none z-10"></div>
                    <div class="card-collapsed-label absolute inset-0 flex flex-col justify-between items-center py-9 z-20 pointer-events-none transition-all duration-300 opacity-0 group-[.active]:opacity-0 group-[.active]:translate-y-4">
                        <span class="w-2 h-2 rounded-full bg-[#00e599] shadow-[0_0_10px_#00e599]"></span>
                        <span class="vertical-mode-text font-mono text-[11px] uppercase font-bold text-neutral-300">SPATIAL CANVAS</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-neutral-600"></span>
                    </div>
                    <div class="card-expanded-content absolute inset-0 flex flex-col justify-end p-5 sm:p-6 z-30 pointer-events-none transition-all duration-500 opacity-100 translate-y-0 group-[.active]:opacity-100 group-[.active]:translate-y-0">
                        <span class="text-[10px] font-mono text-[#00e599] font-bold uppercase tracking-wider mb-1">SPATIAL BRAIN</span>
                        <h3 class="text-base sm:text-lg font-bold text-white mb-1 tracking-tight">Infinite 2D Canvas</h3>
                        <p class="text-xs text-neutral-300 leading-relaxed line-clamp-2">Interactive thought clusters with frictionless zoom and hardware-accelerated mind palace rendering.</p>
                    </div>
                </div>

                <div class="expand-card group relative cursor-pointer overflow-hidden bg-[#0c0d11] border border-white/[0.09] hover:border-[#facc15]/40 shadow-2xl transition-all" data-index="1">
                    <img src="/img2.jpeg" alt="AI Copilot" class="absolute inset-0 w-full h-full object-contain bg-black filter brightness-[0.85] group-[.active]:brightness-100 transition-all duration-500 pointer-events-none" />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent pointer-events-none z-10"></div>
                    <div class="card-collapsed-label absolute inset-0 flex flex-col justify-between items-center py-9 z-20 pointer-events-none transition-all duration-300 opacity-100 group-[.active]:opacity-0 group-[.active]:translate-y-4">
                        <span class="w-2 h-2 rounded-full bg-[#facc15] shadow-[0_0_10px_#facc15]"></span>
                        <span class="vertical-mode-text font-mono text-[11px] uppercase font-bold text-neutral-300">DEEPSEEK R1</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-neutral-600"></span>
                    </div>
                    <div class="card-expanded-content absolute inset-0 flex flex-col justify-end p-5 sm:p-6 z-30 pointer-events-none transition-all duration-500 opacity-0 translate-y-4 group-[.active]:opacity-100 group-[.active]:translate-y-0">
                        <span class="text-[10px] font-mono text-[#facc15] font-bold uppercase tracking-wider mb-1">INTELLIGENCE</span>
                        <h3 class="text-base sm:text-lg font-bold text-white mb-1 tracking-tight">DeepSeek R1 Assistant</h3>
                        <p class="text-xs text-neutral-300 leading-relaxed line-clamp-2">Prompt-driven synthesis to organize thoughts, uncover latent connections, and expand concepts automatically.</p>
                    </div>
                </div>

                <div class="expand-card group relative cursor-pointer overflow-hidden bg-[#0c0d11] border border-white/[0.09] hover:border-blue-400/40 shadow-2xl transition-all" data-index="2">
                    <img src="/img3.jpeg" alt="Workspaces" class="absolute inset-0 w-full h-full object-contain bg-black filter brightness-[0.85] group-[.active]:brightness-100 transition-all duration-500 pointer-events-none" />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent pointer-events-none z-10"></div>
                    <div class="card-collapsed-label absolute inset-0 flex flex-col justify-between items-center py-9 z-20 pointer-events-none transition-all duration-300 opacity-100 group-[.active]:opacity-0 group-[.active]:translate-y-4">
                        <span class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_10px_#60a5fa]"></span>
                        <span class="vertical-mode-text font-mono text-[11px] uppercase font-bold text-neutral-300">WORKSPACES</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-neutral-600"></span>
                    </div>
                    <div class="card-expanded-content absolute inset-0 flex flex-col justify-end p-5 sm:p-6 z-30 pointer-events-none transition-all duration-500 opacity-0 translate-y-4 group-[.active]:opacity-100 group-[.active]:translate-y-0">
                        <span class="text-[10px] font-mono text-blue-400 font-bold uppercase tracking-wider mb-1">DOMAIN ISOLATION</span>
                        <h3 class="text-base sm:text-lg font-bold text-white mb-1 tracking-tight">Memory Workspaces</h3>
                        <p class="text-xs text-neutral-300 leading-relaxed line-clamp-2">Isolate repositories and personal thoughts into distinct spatial domains with discrete context boundaries.</p>
                    </div>
                </div>

                <div class="expand-card group relative cursor-pointer overflow-hidden bg-[#0c0d11] border border-white/[0.09] hover:border-purple-400/40 shadow-2xl transition-all" data-index="3">
                    <img src="/img4.jpeg" alt="Neon Cloud Sync" class="absolute inset-0 w-full h-full object-contain bg-black filter brightness-[0.85] group-[.active]:brightness-100 transition-all duration-500 pointer-events-none" />
                    <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent pointer-events-none z-10"></div>
                    <div class="card-collapsed-label absolute inset-0 flex flex-col justify-between items-center py-9 z-20 pointer-events-none transition-all duration-300 opacity-100 group-[.active]:opacity-0 group-[.active]:translate-y-4">
                        <span class="w-2 h-2 rounded-full bg-purple-400 shadow-[0_0_10px_#c084fc]"></span>
                        <span class="vertical-mode-text font-mono text-[11px] uppercase font-bold text-neutral-300">CLOUD SYNC</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-neutral-600"></span>
                    </div>
                    <div class="card-expanded-content absolute inset-0 flex flex-col justify-end p-5 sm:p-6 z-30 pointer-events-none transition-all duration-500 opacity-0 translate-y-4 group-[.active]:opacity-100 group-[.active]:translate-y-0">
                        <span class="text-[10px] font-mono text-purple-400 font-bold uppercase tracking-wider mb-1">ZERO-CONFIG SYNC</span>
                        <h3 class="text-base sm:text-lg font-bold text-white mb-1 tracking-tight">Neon Database Sync</h3>
                        <p class="text-xs text-neutral-300 leading-relaxed line-clamp-2">Your data stays in your personal PostgreSQL database. Direct HTTPS sync without vendor lock-in.</p>
                    </div>
                </div>

            </div>
        </div>

        <div class="text-center mt-8">
            <a href="/download" class="inline-flex items-center gap-2 bg-[#00e599] text-black font-semibold text-xs sm:text-sm px-6 py-3 rounded-xl hover:bg-[#00c985] transition-all shadow-[0_0_20px_rgba(0,229,153,0.3)] no-underline">
                <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.551 0 .9993.4482.9993.9993s-.4483.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9994.4482.9994.9993s-.4483.9997-.9994.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.4114 13.8533 8.083 12 8.083s-3.5902.3284-5.1368.8667L4.8409 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589 0 18.761h24c-.3432-4.1021-2.6889-7.5743-6.1185-9.4396"/></svg>
                Download Companion App
            </a>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', () => {{
                const cards = document.querySelectorAll('#skiperCardsWrapper .expand-card');
                cards.forEach((card) => {{
                    const activate = () => {{
                        cards.forEach(c => {{
                            c.classList.remove('active');
                            const label = c.querySelector('.card-collapsed-label');
                            const content = c.querySelector('.card-expanded-content');
                            if (label) {{
                                label.classList.remove('opacity-0', 'translate-y-4');
                                label.classList.add('opacity-100');
                            }}
                            if (content) {{
                                content.classList.remove('opacity-100', 'translate-y-0');
                                content.classList.add('opacity-0', 'translate-y-4');
                            }}
                        }});

                        card.classList.add('active');
                        const activeLabel = card.querySelector('.card-collapsed-label');
                        const activeContent = card.querySelector('.card-expanded-content');
                        if (activeLabel) {{
                            activeLabel.classList.remove('opacity-100');
                            activeLabel.classList.add('opacity-0', 'translate-y-4');
                        }}
                        if (activeContent) {{
                            activeContent.classList.remove('opacity-0', 'translate-y-4');
                            activeContent.classList.add('opacity-100', 'translate-y-0');
                        }}
                    }};

                    card.addEventListener('mouseenter', activate);
                    card.addEventListener('click', activate);
                }});
            }});
        </script>
    </section>

    <!-- Context Pipeline Animation -->
    <section id="pipeline" class="bg-[#000000] text-white border-b border-neutral-800 relative z-10">
        <div id="pipelineScrollWrapper" class="relative" style="height: 300vh;">
          <div id="pipelineSticky" class="sticky top-0 flex flex-col items-center justify-center" style="height: 100vh; overflow: hidden;">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12 w-full">

              <div class="mb-3 sm:mb-5 flex-shrink-0">
                  <p class="mono text-[10px] sm:text-[11px] tracking-[0.2em] uppercase text-[#00e599] mb-1.5 flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full bg-[#00e599] shadow-[0_0_10px_#00e599]"></span>
                      Universal Context Bus
                  </p>
                  <h2 class="text-white text-xl sm:text-3xl font-bold tracking-tight">
                      Instant Cross-Model Context Pipeline
                  </h2>
              </div>

              <div id="pipelineContainer" class="diagram-scaler-wrapper rounded-2xl border border-white/[0.08] shadow-2xl p-2 sm:p-4 bg-[#000000] overflow-hidden relative select-none flex-shrink-0">
                <div id="pipelineViewport" class="diagram-container">
                <div class="vertical-grid">
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                </div>

                <svg class="canvas" viewBox="0 0 1000 524">
                  <defs>
                    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                      <path d="M 1 2 L 7 5 L 1 8" fill="none" stroke="#00e599" stroke-width="1.5" stroke-linecap="round"/>
                    </marker>
                    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur stdDeviation="3.5" result="blur" />
                      <feMerge>
                        <feMergeNode in="blur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>

                  <path id="path-main" d="M 74 262 L 950 262" class="line-green" />
                  <path id="path-sync-arrow" d="M 132 262 L 188 262" class="line-green" marker-end="url(#arrow-green)" />

                  <g id="ticks">
                    <line x1="292" y1="256" x2="292" y2="268" class="ruler-tick" />
                    <line x1="316" y1="258" x2="316" y2="266" class="ruler-tick" />
                    <line x1="340" y1="256" x2="340" y2="268" class="ruler-tick" />
                    <line x1="364" y1="258" x2="364" y2="266" class="ruler-tick" />
                    <line x1="388" y1="256" x2="388" y2="268" class="ruler-tick" />
                    <line id="tick-19" x1="410" y1="244" x2="410" y2="268" class="ruler-tick tick-active" style="opacity: 0;" />
                    <line x1="434" y1="258" x2="434" y2="266" class="ruler-tick" />
                    <line x1="458" y1="256" x2="458" y2="268" class="ruler-tick" />
                    <line x1="482" y1="258" x2="482" y2="266" class="ruler-tick" />
                    <line x1="506" y1="256" x2="506" y2="268" class="ruler-tick" />
                    <line x1="530" y1="258" x2="530" y2="266" class="ruler-tick" />
                    <line x1="554" y1="256" x2="554" y2="268" class="ruler-tick" />
                    <line x1="578" y1="258" x2="578" y2="266" class="ruler-tick" />
                    <line x1="602" y1="256" x2="602" y2="268" class="ruler-tick" />
                    <line x1="626" y1="258" x2="626" y2="266" class="ruler-tick" />
                    <line x1="650" y1="256" x2="650" y2="268" class="ruler-tick" />
                    <line x1="674" y1="258" x2="674" y2="266" class="ruler-tick" />
                    <line x1="698" y1="256" x2="698" y2="268" class="ruler-tick" />
                    <line x1="722" y1="258" x2="722" y2="266" class="ruler-tick" />
                    <line id="tick-20" x1="743" y1="248" x2="743" y2="276" class="ruler-tick tick-active" style="opacity: 0;" />
                    <line x1="766" y1="258" x2="766" y2="266" class="ruler-tick" />
                    <line x1="790" y1="256" x2="790" y2="268" class="ruler-tick" />
                    <line x1="814" y1="258" x2="814" y2="266" class="ruler-tick" />
                    <line x1="838" y1="256" x2="838" y2="268" class="ruler-tick" />
                    <line x1="862" y1="258" x2="862" y2="266" class="ruler-tick" />
                  </g>

                  <path id="path-db-up" d="M 226 262 V 182" class="line-green-dash" />
                  <path id="path-req-data" d="M 226 162 V 138 Q 226 118 248 118 H 268" class="line-white-dash" />
                  <path id="path-data-to-mcp" d="M 390 118 H 410 Q 426 118 426 140 V 158 Q 426 172 444 172 H 455" class="line-white-dash" />

                  <path id="path-neg-1" d="M 450 85 V 157" class="line-green-dash" />
                  <path id="path-neg-2" d="M 591 85 V 157" class="line-green-dash" />

                  <path id="path-mcp-to-tools" d="M 584 172 H 598 Q 614 172 614 150 V 138 Q 614 118 632 118 H 648" class="line-white-dash" />
                  <path id="path-tools-to-apps" d="M 776 118 H 806 Q 828 118 828 138 V 162" class="line-white-dash" />
                  <path id="path-apps-down" d="M 828 182 V 262" class="line-green-dash" />

                  <path id="path-protocol" d="M 520 188 V 328" class="line-white-dash" />
                  <path id="path-granted" d="M 572 188 V 276 Q 572 298 598 298 H 618" class="line-white-solid" />

                  <path id="path-ai-to-note" d="M 918 278 V 356 Q 918 380 892 380 H 885" class="line-green-dash" />
                  <path id="path-note-to-proc" d="M 775 380 H 760 Q 747 380 747 408 V 418 Q 747 440 726 440 H 635" class="line-white-solid" />
                  <path id="path-lower-flow" d="M 615 440 L 280 440" class="line-green-dash" marker-end="url(#arrow-green)" />
                  <path id="path-ret-db" d="M 248 440 H 236 Q 236 400 236 360" class="line-green-dash" marker-end="url(#arrow-green)" />
                  <path id="path-ret-sync" d="M 248 440 H 76 V 340" class="line-green-dash" marker-end="url(#arrow-green)" />

                  <circle id="head-dot" class="glow-dot" r="3.5" cx="0" cy="0" />
                </svg>

                <div id="el-neg1-txt" class="meta-text" style="top: 10.3%; left: 45%;">negotiation<br>started</div>
                <div id="el-neg1-ico" class="circle-icon check-node" style="top: 21.2%; left: 45%;">✓</div>

                <div id="el-neg2-txt" class="meta-text" style="top: 10.3%; left: 59.1%;">negotiation<br>complete</div>
                <div id="el-neg2-ico" class="circle-icon check-node" style="top: 21.2%; left: 59.1%;">✓</div>

                <div id="el-db-ico" class="circle-icon outline-node" style="top: 32.8%; left: 22.6%;">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                </div>
                <div id="el-req-data" class="badge badge-dark" style="top: 22.5%; left: 32.7%;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg>
                  pull context
                </div>

                <div id="el-mcp" class="badge badge-yellow" style="top: 32.8%; left: 52%;">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
                  exom MCP core
                </div>

                <div id="el-req-tools" class="badge badge-dark" style="top: 22.5%; left: 71.3%;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"/></svg>
                  serve memory tools
                </div>

                <div id="el-bot-ico" class="circle-icon outline-node" style="top: 32.8%; left: 82.8%;">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>
                </div>
                <div id="el-hollow-top" class="circle-icon hollow-node" style="top: 43.5%; left: 82.8%;"></div>

                <div id="el-notes" class="badge badge-white" style="top: 50%; left: 7.4%;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
                  exom Brain
                </div>
                <div id="el-notes-sub" class="meta-text" style="top: 55%; left: 7.4%;">Universal Memory<br>Repository</div>
                <div id="el-sync-txt" class="meta-text" style="top: 52%; left: 15.6%; font-size: 10px;">sync</div>

                <div id="el-neondb" class="badge badge-white" style="top: 50%; left: 24%;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                  neon postgres
                </div>
                <div id="el-neondb-sub" class="meta-text" style="top: 55%; left: 24%;">User-Owned DB</div>
                <div id="el-neondb-time" class="meta-text timestamp" style="top: 60.7%; left: 24%;">18:24:00</div>

                <div id="el-time-mid" class="meta-text timestamp" style="top: 42.7%; left: 41%;">19:08:12</div>

                <div id="el-grant-ico" class="circle-icon check-node" style="top: 56.8%; left: 62.5%;">✓</div>
                <div id="el-grant-txt" class="meta-text" style="top: 61%; left: 62.5%;">context access<br>granted</div>

                <div id="el-time-right" class="meta-text timestamp" style="top: 56.8%; left: 74.3%;">20:32:04</div>

                <div id="el-ai-apps" class="badge badge-white" style="top: 50%; left: 91.8%;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"/></svg>
                  all AI apps
                </div>
                <div id="el-ai-apps-sub" class="meta-text" style="top: 55%; left: 91.8%;">Claude, Cursor, Agents</div>

                <div id="el-proto-ico" class="circle-icon outline-node" style="top: 64.5%; left: 52%;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                </div>
                <div id="el-proto-txt" class="meta-text" style="top: 69.6%; left: 52%;">protocol<br>negotiation</div>
                <div id="el-hollow-bot" class="circle-icon hollow-node" style="top: 63.7%; left: 91.8%;"></div>

                <div id="el-write" class="badge badge-dark" style="top: 72.5%; left: 83%;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                  record memory
                </div>

                <div id="el-proc-ico" class="circle-icon check-node" style="top: 84%; left: 62.5%;">✓</div>
                <div id="el-proc-txt" class="meta-text" style="top: 88.2%; left: 62.5%;">context indexed<br>by exom</div>

                <div id="el-saved-ico" class="circle-icon check-node" style="top: 84%; left: 26.5%;">✓</div>
                <div id="el-saved-txt" class="meta-text" style="top: 88.2%; left: 26.5%;">synced to<br>neon brain</div>

                <div id="el-sync-ico" class="circle-icon check-node" style="top: 84%; left: 7.6%;">✓</div>
                <div id="el-sync-bot-txt" class="meta-text" style="top: 88.2%; left: 7.6%;">real-time sync<br>(cross-device)</div>
                </div>
              </div>

            </div>
          </div>
        </div>

        <script>
              document.addEventListener('DOMContentLoaded', () => {{
                const allPaths = document.querySelectorAll('#pipelineViewport svg.canvas path:not(defs path)');
                const dot = document.getElementById('head-dot');
                const pipelineWrapper = document.getElementById('pipelineScrollWrapper');
                const ticks = document.querySelectorAll('#pipelineViewport #ticks line:not(.tick-active)');
                if (!allPaths.length || !pipelineWrapper) return;

                const pathLengths = {{}};
                allPaths.forEach(path => {{
                  const len = path.getTotalLength();
                  pathLengths[path.id] = len;
                  path.style.strokeDasharray = `${{len}} ${{len}}`;
                  path.style.strokeDashoffset = len;
                  path.style.transition = 'none';
                }});

                function setPathProgress(id, startP, endP, currentP) {{
                  const p = document.getElementById(id);
                  if (!p) return;
                  const len = pathLengths[id];
                  if (currentP < startP) {{
                    p.style.strokeDashoffset = len;
                  }} else if (currentP > endP) {{
                    p.style.strokeDashoffset = 0;
                  }} else {{
                    const localProg = (currentP - startP) / (endP - startP);
                    p.style.strokeDashoffset = len * (1 - localProg);
                  }}
                }}

                function setElementVisibility(id, triggerProg, currentP) {{
                  const el = document.getElementById(id);
                  if (!el) return;
                  el.classList.toggle('visible', currentP >= triggerProg);
                }}

                function updateScrollPipeline() {{
                  const rect = pipelineWrapper.getBoundingClientRect();
                  const scrollableDistance = rect.height - window.innerHeight;
                  const progress = scrollableDistance > 0
                    ? Math.min(Math.max(-rect.top / scrollableDistance, 0), 1)
                    : 0;

                  setElementVisibility('el-notes', 0.05, progress);
                  setElementVisibility('el-notes-sub', 0.07, progress);
                  setPathProgress('path-sync-arrow', 0.08, 0.12, progress);
                  setElementVisibility('el-sync-txt', 0.12, progress);

                  setPathProgress('path-main', 0.10, 0.55, progress);
                  
                  const pMain = document.getElementById('path-main');
                  if (progress >= 0.10 && progress <= 0.55 && pMain && dot) {{
                    dot.classList.add('active');
                    const localProg = (progress - 0.10) / (0.55 - 0.10);
                    const pt = pMain.getPointAtLength(localProg * pathLengths['path-main']);
                    dot.setAttribute('cx', pt.x);
                    dot.setAttribute('cy', pt.y);
                  }} else if (dot) {{
                    dot.classList.remove('active');
                  }}

                  ticks.forEach((tick, i) => {{
                    const tickProg = 0.15 + (i / ticks.length) * 0.35;
                    tick.classList.toggle('lit', progress >= tickProg);
                  }});

                  setElementVisibility('el-neondb', 0.18, progress);
                  setElementVisibility('el-neondb-sub', 0.20, progress);
                  setElementVisibility('el-neondb-time', 0.22, progress);

                  setPathProgress('path-db-up', 0.22, 0.26, progress);
                  setElementVisibility('el-db-ico', 0.26, progress);
                  setPathProgress('path-req-data', 0.26, 0.32, progress);
                  setElementVisibility('el-req-data', 0.32, progress);

                  setPathProgress('path-data-to-mcp', 0.32, 0.38, progress);
                  const t19 = document.getElementById('tick-19');
                  if (t19) t19.style.opacity = progress >= 0.36 ? '1' : '0';
                  setElementVisibility('el-time-mid', 0.37, progress);
                  setElementVisibility('el-mcp', 0.39, progress);

                  setPathProgress('path-neg-1', 0.39, 0.44, progress);
                  setElementVisibility('el-neg1-ico', 0.44, progress);
                  setElementVisibility('el-neg1-txt', 0.44, progress);

                  setPathProgress('path-protocol', 0.42, 0.48, progress);
                  setElementVisibility('el-proto-ico', 0.48, progress);
                  setElementVisibility('el-proto-txt', 0.48, progress);

                  setPathProgress('path-neg-2', 0.45, 0.50, progress);
                  setElementVisibility('el-neg2-ico', 0.50, progress);
                  setElementVisibility('el-neg2-txt', 0.50, progress);

                  setPathProgress('path-granted', 0.48, 0.54, progress);
                  setElementVisibility('el-grant-ico', 0.54, progress);
                  setElementVisibility('el-grant-txt', 0.54, progress);

                  setPathProgress('path-mcp-to-tools', 0.48, 0.54, progress);
                  setElementVisibility('el-req-tools', 0.54, progress);
                  setPathProgress('path-tools-to-apps', 0.54, 0.60, progress);
                  setElementVisibility('el-bot-ico', 0.60, progress);

                  setPathProgress('path-apps-down', 0.60, 0.65, progress);
                  setElementVisibility('el-hollow-top', 0.65, progress);
                  const t20 = document.getElementById('tick-20');
                  if (t20) t20.style.opacity = progress >= 0.64 ? '1' : '0';
                  setElementVisibility('el-time-right', 0.65, progress);
                  setElementVisibility('el-ai-apps', 0.67, progress);
                  setElementVisibility('el-ai-apps-sub', 0.69, progress);

                  setPathProgress('path-ai-to-note', 0.68, 0.74, progress);
                  setElementVisibility('el-hollow-bot', 0.72, progress);
                  setElementVisibility('el-write', 0.74, progress);

                  setPathProgress('path-note-to-proc', 0.74, 0.80, progress);
                  setElementVisibility('el-proc-ico', 0.80, progress);
                  setElementVisibility('el-proc-txt', 0.80, progress);

                  setPathProgress('path-lower-flow', 0.80, 0.90, progress);

                  setPathProgress('path-ret-db', 0.90, 0.94, progress);
                  setElementVisibility('el-saved-ico', 0.94, progress);
                  setElementVisibility('el-saved-txt', 0.94, progress);

                  setPathProgress('path-ret-sync', 0.92, 0.98, progress);
                  setElementVisibility('el-sync-ico', 0.98, progress);
                  setElementVisibility('el-sync-bot-txt', 0.98, progress);
                }}

                if (window.lenis) {{
                  window.lenis.on('scroll', updateScrollPipeline);
                }}
                window.addEventListener('scroll', updateScrollPipeline, {{ passive: true }});
                window.addEventListener('resize', updateScrollPipeline);
                updateScrollPipeline();
              }});
        </script>
    </div>
</section>

    <!-- Core Capabilities -->
    <div class="showcase-container">
      <div class="sticky-nav-wrapper">
        <nav class="sticky-sidebar" id="sidebar">
          <button class="menu-badge-btn" aria-hidden="true" tabindex="-1">CORE CAPABILITIES</button>
          <ul class="nav-list">
            <li><a class="nav-btn active" data-target="trigram-search"><span class="nav-dot"></span>Zero-Latency Recall</a></li>
            <li><a class="nav-btn" data-target="ai-memory-sync"><span class="nav-dot"></span>Autonomous Memory Sync</a></li>
            <li><a class="nav-btn" data-target="zen-canvas"><span class="nav-dot"></span>Spatial Mind Palace</a></li>
            <li><a class="nav-btn" data-target="non-linear"><span class="nav-dot"></span>Cross-Model Knowledge Graphs</a></li>
            <li><a class="nav-btn" data-target="open-protocol"><span class="nav-dot"></span>Open Protocol Standards</a></li>
          </ul>
        </nav>
      </div>

      <section id="trigram-search" class="feature-section section-dark" data-theme="dark">
        <div class="section-inner">
          <div class="section-content">
            <span class="mobile-feature-badge">01 • Fuzzy Trigram Search</span>
            <h2 class="hero-heading">Zero-Latency Recall. Retrieve decisions made across any AI.</h2>
            <p class="lead-text">exom uses PostgreSQL trigram matching (<code>pg_trgm</code>) to instantly recall prompts, architecture decisions, and code changes across all your past sessions in milliseconds.</p>
            <ul class="checklist">
              <li><span class="check-icon">✓</span> Typo-tolerant substring &amp; fuzzy similarity scoring</li>
              <li><span class="check-icon">✓</span> Automatic fallback to ILIKE if extensions are missing</li>
              <li><span class="check-icon">✓</span> Sub-4ms lookup times across 100,000+ thought vectors</li>
            </ul>

            <div class="terminal-box">
              <div class="terminal-topbar">
                <div class="terminal-dots"><span class="dot-red"></span><span class="dot-yellow"></span><span class="dot-green"></span></div>
                <span class="terminal-title">PostgreSQL Memory Lookup</span>
              </div>
              <div class="terminal-code">
<span class="hl-key">SELECT</span> id, title, similarity(title, $1) <span class="hl-key">AS</span> score <br>
<span class="hl-key">FROM</span> project_nodes <br>
<span class="hl-key">WHERE</span> title % $1 <span class="hl-key">OR</span> summary <span class="hl-key">ILIKE</span> <span class="hl-str">'%'</span>||$1||<span class="hl-str">'%'</span> <br>
<span class="hl-key">ORDER BY</span> score <span class="hl-key">DESC LIMIT</span> 10;<br><br>
<span class="hl-green">⚡ Context Resolved: 2.8ms | Passed to Claude System Prompt</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="ai-memory-sync" class="feature-section section-light" data-theme="light">
        <div class="section-inner">
          <div class="section-content">
            <span class="mobile-feature-badge">02 • Autonomous Sync</span>
            <h2 class="hero-heading">Autonomous Memory Sync. Continuous context without human copy-pasting.</h2>
            <p class="lead-text">Whenever Claude or Cursor designs a module or writes a change, exom logs the rationale, impact, and dependencies into your second brain chain automatically.</p>
            <ul class="checklist">
              <li><span class="check-icon">✓</span> Chronological sequence chaining (Step 1 -> Step 2 -> Step 3)</li>
              <li><span class="check-icon">✓</span> Plain-English rationale &amp; downstream impact analysis</li>
              <li><span class="check-icon">✓</span> Instant synchronization down to mobile and Windows desktop</li>
            </ul>

            <div class="terminal-box">
              <div class="terminal-topbar">
                <div class="terminal-dots"><span class="dot-red"></span><span class="dot-yellow"></span><span class="dot-green"></span></div>
                <span class="terminal-title">MCP Memory Tool Invocation</span>
              </div>
              <div class="terminal-code">
<span class="hl-dim">&gt; log_sequential_codebase_change( title="Auth Gateway", impact="No auth required on /api" )</span><br>
{{<br>
&nbsp;&nbsp;<span class="hl-key">"status"</span>: <span class="hl-str">"success"</span>,<br>
&nbsp;&nbsp;<span class="hl-key">"step_number"</span>: 14,<br>
&nbsp;&nbsp;<span class="hl-key">"message"</span>: <span class="hl-str">"Permanently committed to user second brain"</span><br>
}}<br><br>
<span class="hl-green">✓ Second brain updated • Available to all future AI chats</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="zen-canvas" class="feature-section section-dark" data-theme="dark">
        <div class="section-inner">
          <div class="section-content">
            <span class="mobile-feature-badge">03 • Spatial Mind Palace</span>
            <h2 class="hero-heading">Spatial Mind Palace. Visualize knowledge in 2D space.</h2>
            <p class="lead-text">Move beyond linear chat threads. Inspect your thoughts, notes, and architectural modifications on an interactive canvas with intuitive pan, zoom, and clustering.</p>
            <ul class="checklist">
              <li><span class="check-icon">✓</span> Hardware-accelerated 2D infinite canvas</li>
              <li><span class="check-icon">✓</span> Hub-and-Spoke concept groupings</li>
              <li><span class="check-icon">✓</span> Double-click inspection of rationale and project impact</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="non-linear" class="feature-section section-light" data-theme="light">
        <div class="section-inner">
          <div class="section-content">
            <span class="mobile-feature-badge">04 • Knowledge Graph</span>
            <h2 class="hero-heading">Cross-Model Knowledge Graphs. Semantic links across conversations.</h2>
            <p class="lead-text">Link disparate concepts together. Whether an architectural pattern was discussed in Cursor or a business strategy in Claude, exom bridges them into a unified web.</p>
            <ul class="checklist">
              <li><span class="check-icon">✓</span> Semantic relationship linking (references, builds_upon, refutes)</li>
              <li><span class="check-icon">✓</span> Ripple effect analysis for upstream and downstream decisions</li>
              <li><span class="check-icon">✓</span> DeepSeek-R1 copilot suggested connections</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="open-protocol" class="feature-section section-dark" data-theme="dark">
        <div class="section-inner">
          <div class="section-content">
            <span class="mobile-feature-badge">05 • Open Standards</span>
            <h2 class="hero-heading">Open Protocol Standards. Zero lock-in, user-owned storage.</h2>
            <p class="lead-text">Built strictly on Anthropic's Model Context Protocol (MCP) and Starlette ASGI. Your memory resides in your own serverless Neon PostgreSQL instance.</p>
            <ul class="checklist">
              <li><span class="check-icon">✓</span> FastMCP server runtime with SSE and HTTP streaming</li>
              <li><span class="check-icon">✓</span> End-to-end credential encryption with Fernet</li>
              <li><span class="check-icon">✓</span> Exportable PostgreSQL schema anytime</li>
            </ul>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer -->
    <footer class="neon-footer">
      <div class="footer-container">
        <div class="footer-top">
          <div class="footer-brand">
            <a href="/" class="footer-logo">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#facc15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="#facc15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="#facc15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>exom</span>
            </a>
            <p class="footer-tagline">The unified second brain across all AI. Connect your context once; access, synthesize, and expand knowledge seamlessly across models.</p>
            <a href="#" class="status-badge">
              <span class="status-dot"></span>
              MCP Gateway Online
            </a>
          </div>

          <div class="footer-col">
            <h4>Product</h4>
            <ul>
              <li><a href="#trigram-search">Instant Recall</a></li>
              <li><a href="#ai-memory-sync">Autonomous Sync</a></li>
              <li><a href="/download">Download Companion App</a></li>
              <li><a href="/console">Developer Console</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Integrations</h4>
            <ul>
              <li><a href="#">Claude Desktop</a></li>
              <li><a href="#">Cursor IDE</a></li>
              <li><a href="#">DeepSeek R1 Copilot</a></li>
              <li><a href="#">Model Context Protocol (MCP)</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Developers</h4>
            <ul>
              <li><a href="#">FastMCP Starlette ASGI</a></li>
              <li><a href="#">SSE Stream Handshakes</a></li>
              <li><a href="#">Neon Serverless SQL</a></li>
              <li><a href="#">GitHub Repository</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4>Platform</h4>
            <ul>
              <li><a href="#">About exom</a></li>
              <li><a href="#">Changelog</a></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Multi-Tenant Security</a></li>
            </ul>
          </div>
        </div>

        <div class="footer-bottom">
          <div>&copy; 2026 exom. All systems operational.</div>
          <div class="footer-bottom-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Security</a>
          </div>
        </div>
      </div>
    </footer>

    <!-- Fixed Core Capabilities Scroll-Spy Script -->
    <script>
      document.addEventListener('DOMContentLoaded', () => {{
        const navButtons = document.querySelectorAll('.nav-btn');
        const sections = document.querySelectorAll('.feature-section');
        const sidebar = document.getElementById('sidebar');

        function syncActiveNav() {{
          if (!sections.length || !navButtons.length) return;
          if (window.innerWidth <= 900) return;

          const scrollY = window.scrollY || window.pageYOffset;
          const viewportMiddle = scrollY + (window.innerHeight * 0.4);

          let currentSection = sections[0];
          sections.forEach((section) => {{
            const top = section.offsetTop;
            const height = section.offsetHeight;
            if (viewportMiddle >= top && viewportMiddle < top + height) {{
              currentSection = section;
            }}
          }});

          navButtons.forEach((btn) => {{
            btn.classList.toggle('active', btn.dataset.target === currentSection.id);
          }});

          const theme = currentSection.getAttribute('data-theme');
          if (sidebar) {{
            if (theme === 'light') {{
              sidebar.classList.add('theme-light');
            }} else {{
              sidebar.classList.remove('theme-light');
            }}
          }}
        }}

        if (window.lenis) {{
          window.lenis.on('scroll', syncActiveNav);
        }}
        window.addEventListener('scroll', syncActiveNav, {{ passive: true }});
        window.addEventListener('resize', syncActiveNav);
        syncActiveNav();

        navButtons.forEach((btn) => {{
          btn.addEventListener('click', (e) => {{
            e.preventDefault();
            const targetId = btn.dataset.target;
            const target = document.getElementById(targetId);
            if (target) {{
              navButtons.forEach((b) => b.classList.remove('active'));
              btn.classList.add('active');

              if (window.lenis) {{
                window.lenis.scrollTo(target, {{ offset: 0, duration: 1.2 }});
              }} else {{
                target.scrollIntoView({{ behavior: 'smooth' }});
              }}
            }}
          }});
        }});
      }});
    </script>
</main>
"""
    return _page("Home", body)


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
        user_id = await db_control.create_user(pool, email, security.hash_password(password))[cite: 2]
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
    user = await db_control.get_user_by_email(pool, email)[cite: 2]

    if user is None or not security.verify_password(password, user["password_hash"]):[cite: 2]
        body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-4 sm:px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-8 rounded-xl shadow-sm">
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

    request.session["user_id"] = str(user["id"])[cite: 2]
    return RedirectResponse("/console", status_code=302)


async def logout(request: Request):
    form = await request.form()
    next_ = str(form.get("next", "")) if form.get("next") else None
    request.session.clear()
    if next_ and next_.startswith("/") and not next_.startswith("//"):
        return RedirectResponse(f"/login?next={next_}", status_code=302)
    return RedirectResponse("/login", status_code=302)


# ---------------------------------------------------------------------------
# Console Page (Template Loader)
# ---------------------------------------------------------------------------
async def console_page(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    pool = db_control.get_control_pool()
    user = await db_control.get_user_by_id(pool, user_id)[cite: 2]
    if user is None:
        request.session.clear()
        return RedirectResponse("/login", status_code=302)

    user_email = user["email"][cite: 2]
    first_name = user_email.split("@")[0].capitalize()
    last_name = ""
    initial = first_name[0].upper()

    coding_workspaces = []
    chat_workspaces = []
    connection_string = ""
    coding_nodes_count = 0
    chat_nodes_count = 0
    total_edges = 0

    if user["connection_string_encrypted"]:[cite: 2]
        try:
            connection_string = security.decrypt_text(user["connection_string_encrypted"])
            user_pool = await tenant_pools.get_manager().get_pool(str(user["id"]), connection_string)[cite: 2]

            # Coding Workspaces
            cw_rows = await user_pool.fetch(
                "SELECT DISTINCT workspace FROM project_nodes WHERE node_type IN ('codebase_change', 'hub', 'concept') ORDER BY workspace ASC"
            )
            coding_workspaces = [r["workspace"] for r in cw_rows]

            # Chat Workspaces
            chat_p_rows = await user_pool.fetch(
                "SELECT DISTINCT workspace FROM project_nodes WHERE node_type = 'chat_summary'"
            )
            notes_ws_rows = await user_pool.fetch(
                "SELECT DISTINCT coalesce(workspace_name, 'General') as ws FROM notes"
            )
            chat_workspaces = list(set([r["workspace"] for r in chat_p_rows] + [r["ws"] for r in notes_ws_rows]))

            # Metric Counts
            coding_nodes_count = await user_pool.fetchval(
                "SELECT count(*) FROM project_nodes WHERE node_type IN ('codebase_change', 'hub', 'concept')"
            ) or 0
            chat_nodes_count = (await user_pool.fetchval(
                "SELECT count(*) FROM project_nodes WHERE node_type = 'chat_summary'"
            ) or 0) + (await user_pool.fetchval("SELECT count(*) FROM notes") or 0)

            total_edges = await user_pool.fetchval("SELECT count(*) FROM project_edges") or 0
        except Exception:
            pass

    if not coding_workspaces:
        coding_workspaces = ["Deployments"]
    if not chat_workspaces:
        chat_workspaces = ["General", "Brainstorming"]

    # Render Coding Rows
    coding_rows = ""
    for ws in coding_workspaces:
        coding_rows += f"""
        <tr class="hover:bg-bw-hover transition-colors">
          <td class="py-4 px-5 font-mono text-white flex items-center gap-2">
            <span class="w-2 h-2 bg-accent-yellow"></span>
            <span>{ws}</span>
          </td>
          <td class="py-4 px-5 text-bw-muted">Git Architecture Chain</td>
          <td class="py-4 px-5"><span class="px-2 py-1 bg-white text-black font-bold text-[10px]">ACTIVE</span></td>
          <td class="py-4 px-5 text-right">
            <a href="/console?ws={ws}&category=coding" class="text-accent-yellow hover:text-white font-bold no-underline">
              View →
            </a>
          </td>
        </tr>
        """

    # Render Chat Rows
    chat_rows = ""
    for ws in chat_workspaces:
        chat_rows += f"""
        <tr class="hover:bg-bw-hover transition-colors">
          <td class="py-4 px-5 font-mono text-white flex items-center gap-2">
            <span class="w-2 h-2 bg-white"></span>
            <span>{ws}</span>
          </td>
          <td class="py-4 px-5 text-bw-muted">AI Chats &amp; Brainstorming</td>
          <td class="py-4 px-5"><span class="px-2 py-1 border border-bw-border text-bw-muted font-bold text-[10px]">SYNCED</span></td>
          <td class="py-4 px-5 text-right">
            <a href="/console?ws={ws}&category=chat" class="text-white hover:text-accent-yellow font-bold no-underline">
              View →
            </a>
          </td>
        </tr>
        """

    # API Keys Rows
    keys = await db_control.list_api_keys(pool, user_id)[cite: 2]
    active_keys = [k for k in keys if k["revoked_at"] is None][cite: 2]
    if active_keys:
        api_keys_rows = "".join(f"""
        <tr class="border-b border-bw-border">
          <td class="py-3 px-4 font-mono text-white">{k['label']}</td>
          <td class="py-3 px-4 font-mono text-bw-muted">{k['created_at'].strftime('%b %d, %Y')}</td>
          <td class="py-3 px-4 font-mono text-bw-muted">{k['last_used_at'].strftime('%b %d, %Y') if k['last_used_at'] else 'Never'}</td>
          <td class="py-3 px-4 text-right">
            <form method="POST" action="/dashboard/api-key/revoke" class="m-0 inline">
              <input type="hidden" name="key_id" value="{k['id']}">
              <button type="submit" class="text-accent-yellow hover:underline text-xs uppercase tracking-wider font-bold" onclick="return confirm('Revoke this key?');">Revoke</button>
            </form>
          </td>
        </tr>
        """ for k in active_keys)[cite: 2]
    else:
        api_keys_rows = '<tr><td colspan="4" class="p-4 text-center text-bw-muted text-xs font-mono">No active API keys found.</td></tr>'

    template_path = os.path.join(os.path.dirname(__file__), "console.html")
    if not os.path.exists(template_path):
        return HTMLResponse("console.html template missing from root directory.", status_code=500)

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    rendered = (
        template_html.replace("{{FIRST_NAME}}", first_name)
        .replace("{{LAST_NAME}}", last_name)
        .replace("{{USER_EMAIL}}", user_email)
        .replace("{{DISPLAY_NAME}}", first_name)
        .replace("{{INITIAL}}", initial)
        .replace("{{CODING_NODES_COUNT}}", str(coding_nodes_count))
        .replace("{{CHAT_NODES_COUNT}}", str(chat_nodes_count))
        .replace("{{TOTAL_EDGES}}", str(total_edges))
        .replace("{{TOTAL_CODING_PROJECTS}}", str(len(coding_workspaces)))
        .replace("{{TOTAL_CHAT_SESSIONS}}", str(len(chat_workspaces)))
        .replace("{{CODING_ROWS}}", coding_rows)
        .replace("{{CHAT_ROWS}}", chat_rows)
        .replace("{{API_KEYS_ROWS}}", api_keys_rows)
        .replace("{{CONNECTION_STRING}}", connection_string)
    )

    return HTMLResponse(rendered)


# ---------------------------------------------------------------------------
# Form Handlers for Direct In-Console Database & API Key Actions
# ---------------------------------------------------------------------------
async def update_connection_string(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    connection_string = str(form.get("connection_string", "")).strip()

    if not (connection_string.startswith("postgresql://") or connection_string.startswith("postgres://")):
        return HTMLResponse("<script>alert('Invalid format: Must start with postgresql://');window.location='/console';</script>")

    ok, err = await tenant_pools.test_connection_string(connection_string)
    if not ok:
        return HTMLResponse(f"<script>alert('Connection test failed: {err}');window.location='/console';</script>")

    pool = db_control.get_control_pool()
    await db_control.set_connection_string(pool, user_id, security.encrypt_text(connection_string))[cite: 2]
    await tenant_pools.get_manager().invalidate(user_id)

    return RedirectResponse("/console", status_code=302)


async def create_api_key(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    pool = db_control.get_control_pool()
    raw_key = security.generate_api_key()
    await db_control.create_api_key(pool, user_id, security.hash_api_key(raw_key), "Console Key")[cite: 2]

    return RedirectResponse("/console", status_code=302)


async def revoke_api_key(request: Request):
    user_id = _require_login(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    form = await request.form()
    key_id = str(form.get("key_id", ""))

    pool = db_control.get_control_pool()
    await db_control.revoke_api_key(pool, user_id, key_id)[cite: 2]

    return RedirectResponse("/console", status_code=302)


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
    Route("/signup", signup_get, methods=["GET"]),
    Route("/signup", signup_post, methods=["POST"]),
    Route("/login", login_get, methods=["GET"]),
    Route("/login", login_post, methods=["POST"]),
    Route("/logout", logout, methods=["POST"]),
    Route("/console", console_page, methods=["GET"]),
    Route("/dashboard/connection-string", update_connection_string, methods=["POST"]),
    Route("/dashboard/api-key/create", create_api_key, methods=["POST"]),
    Route("/dashboard/api-key/revoke", revoke_api_key, methods=["POST"]),
    Route("/api/desktop/graph", desktop_get_graph, methods=["GET"]),
    Route("/api/desktop/edges/batch", desktop_batch_save_edges, methods=["POST"]),
]
