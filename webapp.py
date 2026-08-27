"""
Memory Notes for AI - Web Application
Integrated with:
- Isotope Hero WebGPU Shader Canvas (Shaders library via ESM)
- Originkit Liquid Carve 'Get Started' Button
- Classic 'See more' Button
- Live Emerging Architecture Pipeline Canvas (Neon DB -> FastMCP Broker -> AI Apps)
"""

import asyncpg
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route

import db_control
import security
import tenant_pools


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""<!DOCTYPE html>
<html class="scroll-smooth" lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title} - Memory Notes</title>

<!-- Fonts: Geist & JetBrains Mono -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" />

<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
    tailwind.config = {{
        darkMode: "class",
        theme: {{
            extend: {{
                colors: {{
                    "surface-white": "#FFFFFF",
                    "surface-container": "#F1EDEC",
                    "surface-container-low": "#F6F3F2",
                    "on-surface": "#1C1B1B",
                    "on-surface-variant": "#434652",
                    "border-muted": "#E2E2E7",
                    "secondary-container": "#FDD400",
                    "secondary-fixed": "#FFE170",
                    "primary": "#003178",
                    "error": "#BA1A1A"
                }},
                fontFamily: {{
                    sans: ["Geist", "sans-serif"],
                    mono: ["JetBrains Mono", "monospace"]
                }}
            }}
        }}
    }}
</script>

<style>
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    ::selection {{
        background: rgba(255, 45, 92, 0.9);
        color: #040407;
    }}

    /* Isotope Hero Layout */
    .isotope-hero-main {{
        position: relative;
        isolation: isolate;
        display: flex;
        flex-direction: column;
        min-height: 100dvh;
        overflow: hidden;
        background: #040407;
        color: #ffffff;
        font-family: 'Geist', sans-serif;
        -webkit-font-smoothing: antialiased;
    }}

    .shader-wrap {{
        position: absolute;
        inset: 0;
        z-index: 0;
    }}

    .bottom-scrim {{
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 28%;
        pointer-events: none;
        z-index: 1;
        background: linear-gradient(to top, rgba(4, 4, 7, 0.85), rgba(4, 4, 7, 0.3) 50%, transparent);
    }}

    /* Header Orbit Animation */
    .orbit {{
        transform-box: fill-box;
        transform-origin: center;
        animation: orbit-spin 14s linear infinite;
    }}
    .logo:hover .orbit {{
        animation-duration: 1.6s;
    }}
    @keyframes orbit-spin {{
        to {{ transform: rotate(360deg); }}
    }}

    .nav-link {{
        position: relative;
        color: rgba(255, 255, 255, 0.6);
        text-decoration: none;
        transition: color 0.25s ease;
    }}
    .nav-link.active, .nav-link:hover {{
        color: #ffffff;
    }}
    .nav-link::after {{
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: -5px;
        height: 1px;
        background: currentColor;
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .nav-link:hover::after, .nav-link:focus-visible::after {{
        transform: scaleX(1);
    }}

    /* Entrance Stagger Reveal */
    .reveal {{
        opacity: 0;
        transform: translateY(18px);
        animation: reveal-in 1.1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        animation-delay: var(--reveal-delay, 0s);
    }}
    @keyframes reveal-in {{
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    /* Neon Architecture Pipeline Elements */
    .seg-path {{
        transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease;
    }}
    .timeline-elem {{
        transition: opacity 0.45s ease, transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
        opacity: 0;
        transform: scale(0.4);
        pointer-events: none;
    }}
    .timeline-elem.visible {{
        opacity: 1;
        transform: scale(1);
        pointer-events: auto;
    }}
    .pill-memory-start {{
        opacity: 1 !important;
        transform: scale(1) !important;
        pointer-events: auto !important;
    }}

    @keyframes sparkleBurstSlow {{
        0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 229, 153, 0.9); }}
        40% {{ transform: scale(1.15); box-shadow: 0 0 35px 12px rgba(0, 229, 153, 1); filter: brightness(1.5); }}
        100% {{ transform: scale(1); box-shadow: 0 0 18px 2px rgba(0, 229, 153, 0.4); }}
    }}
    .sparkle-burst {{
        animation: sparkleBurstSlow 0.9s ease-out forwards;
    }}

    .settings-dropdown {{
        display: none;
        position: absolute;
        right: 0;
        top: 48px;
        width: 300px;
        background: #ffffff;
        border: 1px solid #E2E2E7;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        border-radius: 0.5rem;
        padding: 1rem;
        z-index: 100;
    }}
    .settings-dropdown.active {{
        display: block;
    }}

    @media (prefers-reduced-motion: reduce) {{
        .reveal {{ opacity: 1; transform: none; animation: none; }}
        .orbit {{ animation: none; }}
    }}
</style>
</head>
<body class="bg-[#040407] text-white font-sans min-h-screen flex flex-col">
{body}

<script type="module">
    // Load Shaders library via ESM in browser without node/react build step
    import React from 'https://esm.sh/react@18.3.1';
    import ReactDOM from 'https://esm.sh/react-dom@18.3.1/client';
    import {{ Shader, SolidColor, Exposure, Group, Text, GradientMap, TimeTrail, Repeater, Circle, LensDistortion }} from 'https://esm.sh/shaders@0.1.0/react';

    function ShaderHeroCanvas() {{
        const [textVisible, setTextVisible] = React.useState(true);

        React.useEffect(() => {{
            const mq = window.matchMedia('(min-width: 640px)');
            setTextVisible(mq.matches);
            const handler = (e) => setTextVisible(e.matches);
            mq.addEventListener('change', handler);
            return () => mq.removeEventListener('change', handler);
        }}, []);

        return React.createElement(
            Shader,
            {{ toneMapping: 'aces', style: {{ width: '100%', height: '100%', display: 'block' }} }},
            React.createElement(SolidColor, {{ color: '#050029' }}),
            React.createElement(
                Exposure,
                {{ exposure: 1.7 }},
                React.createElement(
                    Group,
                    {{ flow: {{ mode: 'column', gap: 13, align: 'center', anchor: 'center', anchorOffset: {{ x: 0, y: 0 }} }} }},
                    React.createElement(Text, {{
                        center: {{ x: 0.5, y: 0.39 }},
                        fontFamily: 'Geist',
                        fontSize: 0.085,
                        letterSpacing: -0.045,
                        origin: 'bottom-left',
                        text: 'structured freedom for your',
                        visible: textVisible
                    }}),
                    React.createElement(Text, {{
                        center: {{ x: 0.5, y: 0.53 }},
                        fontFamily: 'Geist',
                        fontSize: 0.28,
                        fontWeight: 600,
                        letterSpacing: -0.045,
                        origin: 'bottom-left',
                        text: 'thoughts',
                        visible: textVisible
                    }})
                )
            ),
            React.createElement(
                GradientMap,
                {{ palette: 'custom', colorHigh: '#ffffff', colorMid: '#0d0d0d', colorLow: '#1a1a1a', colorSpace: 'oklab', whitePoint: 0.5, visible: true }},
                React.createElement(
                    TimeTrail,
                    {{
                        driftX: {{ type: 'mouse', axis: 'x', outputMin: -1, outputMax: 1, smoothing: 0.25 }},
                        driftY: {{ type: 'mouse', axis: 'y', outputMin: -1, outputMax: 1, smoothing: 0.25, curve: 0 }},
                        motionThreshold: 0.01,
                        trailLength: 1,
                        trailSource: 'alpha'
                    }},
                    React.createElement(
                        Repeater,
                        {{
                            count: 14,
                            hueShift: 43,
                            jitterPosition: 0.835,
                            mode: 'radial',
                            radius: 0.095,
                            startAngle: {{ type: 'auto-animate', mode: 'loop', speed: 2, easing: 'linear', outputMin: 0, outputMax: 360 }}
                        }},
                        React.createElement(Circle, {{
                            center: {{ type: 'mouse-position', originX: 0.5, originY: 0.5, reach: 0.5, invertX: true, invertY: true, momentum: 0.7, smoothing: 0.75 }},
                            color: '#fc0808',
                            radius: {{ unit: 'px', value: 40 }},
                            visible: true
                        }})
                    )
                )
            ),
            React.createElement(LensDistortion, {{
                angle: 195,
                bias: 0.44,
                center: {{ type: 'mouse-position', originX: 0.5, originY: 0.5, smoothing: 0.3, reach: 0.54, momentum: 0.2 }},
                count: 22,
                dispersion: 0.79,
                dispersionColor: 0.74,
                dispersionShift: 0.67,
                focusCenter: 0.7,
                focusEdges: 0.56,
                grainMixer: 0.26,
                grainOverlay: 0.04,
                lensBulge: -0.27,
                noiseFrequency: 0.32,
                perspective: 0.61,
                spread: 0.05,
                swirl: 1,
                visible: true
            }})
        );
    }}

    const mount = document.getElementById('shader-root');
    if (mount) {{
        ReactDOM.createRoot(mount).render(React.createElement(ShaderHeroCanvas));
    }}
</script>

<script>
    function toggleSettings() {{
        const dropdown = document.getElementById('settingsDropdown');
        if (dropdown) dropdown.classList.toggle('active');
    }}
    function copyToClipboard(text, btnId) {{
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById(btnId);
            const orig = btn.innerText;
            btn.innerText = 'Copied!';
            setTimeout(() => btn.innerText = orig, 2000);
        }});
    }}
    function setTerminalTab(tab) {{
        const tabs = ['claude', 'cursor', 'curl'];
        tabs.forEach(t => {{
            const btn = document.getElementById('tab-' + t);
            const block = document.getElementById('snippet-' + t);
            if (t === tab) {{
                btn.className = 'px-3 py-1.5 text-xs font-mono rounded bg-white text-black font-semibold transition-colors';
                block.classList.remove('hidden');
            }} else {{
                btn.className = 'px-3 py-1.5 text-xs font-mono rounded text-neutral-400 hover:text-white bg-transparent transition-colors';
                block.classList.add('hidden');
            }}
        }});
    }}

    // Progressive Emerging Architecture Animation
    function resetTimelineToStart() {{
        document.querySelectorAll('.seg-path').forEach(p => {{
            const len = p.getAttribute('data-len') || '300';
            p.style.strokeDasharray = len;
            p.style.strokeDashoffset = len;
        }});

        const pillMem = document.getElementById('pill-memory-notes');
        const pillAi = document.getElementById('elem-ai-apps');
        if (pillMem) pillMem.classList.remove('sparkle-burst');
        if (pillAi) pillAi.classList.remove('sparkle-burst');

        document.querySelectorAll('.timeline-elem:not(.pill-memory-start)').forEach(el => {{
            el.classList.remove('visible');
        }});
    }}

    function drawSeg(id) {{
        const el = document.getElementById(id);
        if (el) el.style.strokeDashoffset = '0';
    }}

    function runFullSequence() {{
        resetTimelineToStart();
        const statusText = document.getElementById('anim-status-indicator');
        const pillMem = document.getElementById('pill-memory-notes');
        const pillAi = document.getElementById('elem-ai-apps');

        if (statusText) statusText.innerHTML = '<span class="text-[#00e599] font-bold">1. Ingestion:</span> Memory Notes sparkles &amp; shoots beam along scale to neon db &amp; mcp-server.';

        setTimeout(() => {{ if (pillMem) pillMem.classList.add('sparkle-burst'); }}, 200);
        setTimeout(() => {{ drawSeg('seg-scale-p1-a'); }}, 700);
        setTimeout(() => {{
            document.getElementById('elem-neon-db').classList.add('visible');
            document.getElementById('elem-junc-neon').classList.add('visible');
            drawSeg('seg-branch-p1-up');
        }}, 1400);
        setTimeout(() => {{
            document.getElementById('elem-db-icon').classList.add('visible');
            drawSeg('seg-branch-p1-curve');
        }}, 2000);
        setTimeout(() => {{
            document.getElementById('elem-request-data').classList.add('visible');
        }}, 2500);
        setTimeout(() => {{ drawSeg('seg-scale-p1-b'); }}, 2800);
        setTimeout(() => {{
            document.getElementById('elem-mcp-server').classList.add('visible');
        }}, 3400);
        setTimeout(() => {{
            drawSeg('seg-branch-p1-chk1');
            drawSeg('seg-branch-p1-chk2');
            drawSeg('seg-branch-p1-gear');
        }}, 3800);
        setTimeout(() => {{
            document.getElementById('chk-neg-start').classList.add('visible');
            document.getElementById('chk-neg-complete').classList.add('visible');
            document.getElementById('elem-gear').classList.add('visible');
        }}, 4400);

        setTimeout(() => {{
            if (statusText) statusText.innerHTML = '<span class="text-[#fde047] font-bold">2. Tool Request &amp; Sync:</span> AI Apps sparkles, beam enters mcp-server while tools are granted &amp; notes write back.';
            if (pillAi) {{
                pillAi.classList.add('visible');
                pillAi.classList.add('sparkle-burst');
            }}
            setTimeout(() => {{ drawSeg('seg-scale-p2'); }}, 600);
            setTimeout(() => {{
                document.getElementById('elem-junc-ai').classList.add('visible');
                drawSeg('seg-branch-p2-up');
                drawSeg('seg-branch-p2-down');
            }}, 1100);
            setTimeout(() => {{
                document.getElementById('elem-robot-icon').classList.add('visible');
                drawSeg('seg-branch-p2-curve');
                document.getElementById('elem-write-note').classList.add('visible');
            }}, 1600);
            setTimeout(() => {{
                document.getElementById('elem-request-tools').classList.add('visible');
                drawSeg('seg-branch-p2-write-curve');
            }}, 2100);
            setTimeout(() => {{
                drawSeg('seg-branch-p2-access');
                drawSeg('seg-branch-p2-return');
            }}, 2600);
            setTimeout(() => {{
                document.getElementById('chk-access-granted').classList.add('visible');
                document.getElementById('chk-note-processed').classList.add('visible');
            }}, 3100);
            setTimeout(() => {{
                document.getElementById('chk-note-saved').classList.add('visible');
                drawSeg('seg-branch-p2-arrow-neon');
            }}, 3700);
            setTimeout(() => {{
                document.getElementById('chk-sync-final').classList.add('visible');
                drawSeg('seg-branch-p2-arrow-mem');
                if (statusText) statusText.innerHTML = '<span class="text-[#00e599] font-bold">✓ Complete:</span> Real-time bidirectional memory pipeline active across Android, Neon, and AI models.';
            }}, 4300);
        }}, 6500);
    }}

    // Originkit Liquid Carve Button Simulation
    document.addEventListener('DOMContentLoaded', () => {{
        runFullSequence();

        const btn = document.getElementById('liquidCarveBtn');
        const followEl = document.getElementById('liquidFollowGroup');
        const squashEl = document.getElementById('liquidSquashGroup');
        const biteEl = document.getElementById('liquidBiteGroup');

        if (btn && followEl && squashEl && biteEl) {{
            const FOLLOW_TAU_MIN = 0.02;
            const FOLLOW_TAU_MAX = 0.4;
            const SQUASH_TAU = 0.09;
            const SQUASH_PER_PX_PER_SEC = 0.0011;
            const SQUASH_MAX = 1.6;
            const smoothness = 100;

            const t = smoothness / 100;
            const tau = FOLLOW_TAU_MIN + t * (FOLLOW_TAU_MAX - FOLLOW_TAU_MIN);

            let st = {{ x: 0, y: 0, tx: 0, ty: 0, squash: 1, angle: 0, scale: 0, targetScale: 0 }};
            let last = 0;
            let isHovered = false;

            btn.addEventListener('pointerenter', (e) => {{
                isHovered = true;
                const r = btn.getBoundingClientRect();
                const dx = e.clientX - (r.left + r.width / 2);
                const dy = e.clientY - (r.top + r.height / 2);
                st.x = st.tx = dx;
                st.y = st.ty = dy;
                st.targetScale = 1;
            }});

            btn.addEventListener('pointermove', (e) => {{
                if (!isHovered) return;
                const r = btn.getBoundingClientRect();
                st.tx = e.clientX - (r.left + r.width / 2);
                st.ty = e.clientY - (r.top + r.height / 2);
            }});

            btn.addEventListener('pointerleave', () => {{
                isHovered = false;
                st.targetScale = 0;
            }});

            function animateLiquid(now) {{
                const dt = last ? Math.min(0.05, (now - last) / 1000) : 1 / 60;
                last = now;

                const k = 1 - Math.exp(-dt / tau);
                const dx = (st.tx - st.x) * k;
                const dy = (st.ty - st.y) * k;
                st.x += dx;
                st.y += dy;

                st.scale += (st.targetScale - st.scale) * (1 - Math.exp(-dt / 0.1));

                const speed = Math.hypot(dx, dy) / dt;
                const wantSquash = Math.min(SQUASH_MAX, 1 + speed * SQUASH_PER_PX_PER_SEC);
                st.squash += (wantSquash - st.squash) * (1 - Math.exp(-dt / SQUASH_TAU));
                if (speed > 8) st.angle = (Math.atan2(dy, dx) * 180) / Math.PI;

                const cx = btn.offsetWidth / 2;
                const cy = btn.offsetHeight / 2;
                followEl.style.transform = `translate(${{cx + st.x}}px, ${{cy + st.y}}px)`;
                squashEl.style.transform = `rotate(${{st.angle}}deg) scale(${{st.squash}}, ${{1 / st.squash}})`;
                biteEl.style.transform = `scale(${{Math.max(0, st.scale)}})`;

                requestAnimationFrame(animateLiquid);
            }}
            requestAnimationFrame(animateLiquid);
        }}
    }});
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


def _navbar(request: Request, user_email: str | None = None) -> str:
    if user_email:
        initial = user_email[0].upper()
        right_actions = f"""
        <div class="relative">
            <div onclick="toggleSettings()" class="w-8 h-8 rounded-full bg-neutral-800 text-white overflow-hidden border border-neutral-700 cursor-pointer flex items-center justify-center font-bold text-xs select-none hover:border-white transition-colors">
                {initial}
            </div>
            <div id="settingsDropdown" class="settings-dropdown">
                <div class="font-bold text-sm text-black mb-1">Signed in as</div>
                <div class="text-xs text-neutral-500 truncate mb-3">{user_email}</div>
                <hr class="border-border-muted mb-3">
                <a href="/dashboard" class="block text-sm text-black py-1.5 hover:text-primary font-semibold transition-colors">⚙️ Dashboard & Settings</a>
                <form method="POST" action="/logout" class="mt-2">
                    <button type="submit" class="w-full text-left text-sm text-error py-1.5 hover:opacity-80 transition-opacity">Log Out</button>
                </form>
            </div>
        </div>
        """
    else:
        right_actions = """
        <a href="/login" class="text-neutral-300 hover:text-white px-4 py-2 text-sm font-semibold transition-colors no-underline">Log In</a>
        <a href="/signup" class="bg-white text-black px-4 py-2 rounded text-sm font-semibold hover:bg-neutral-200 transition-colors no-underline">Sign Up</a>
        """

    return f"""
<header class="hero-header reveal z-50 w-full flex items-center justify-between px-6 py-6 sm:px-12" style="--reveal-delay: 0s;">
    <a href="/" class="logo flex items-center gap-2.5 text-[17px] font-bold tracking-tight text-white no-underline">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" class="logo-svg">
            <circle cx="12" cy="12" r="2.4" fill="currentColor" />
            <g class="orbit">
                <ellipse cx="12" cy="12" rx="10.5" ry="4.2" stroke="currentColor" stroke-width="1.4" transform="rotate(-24 12 12)" />
                <circle cx="20.6" cy="7.4" r="1.6" fill="currentColor" />
            </g>
        </svg>
        Memory Notes
    </a>

    <nav aria-label="Main" class="hero-nav hidden sm:flex items-center gap-8 text-sm font-medium text-white/60">
        <a href="#quickstart" class="nav-link">Connect</a>
        <a href="#pipeline" class="nav-link">Architecture</a>
        <a href="#features" class="nav-link">Features</a>
        <div class="flex items-center gap-3 ml-4">
            {right_actions}
        </div>
    </nav>
</header>
"""


# ---------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------
async def landing_page(request: Request):
    user_id = _require_login(request)
    user_email = None
    if user_id:
        pool = db_control.get_control_pool()
        user = await db_control.get_user_by_id(pool, user_id)
        if user:
            user_email = user["email"]

    base_url = str(request.base_url).rstrip("/")
    nav_html = _navbar(request, user_email)

    claude_config_snippet = f"""{{
  "mcpServers": {{
    "memory-notes": {{
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
      "name": "memory-notes",
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
<!-- ISOTOPE HERO SECTION -->
<main class="isotope-hero-main">
    <!-- WebGPU Shader Canvas Container -->
    <div id="shader-root" class="shader-wrap" aria-hidden="true"></div>

    <!-- Bottom legibility scrim -->
    <div class="bottom-scrim" aria-hidden="true"></div>

    <!-- Header / Nav -->
    {nav_html}

    <!-- Bottom Copy Row & Call to Actions -->
    <div class="hero-copy-row">
        <h1 class="hero-heading reveal sm:sr-only" style="--reveal-delay: 0.1s;">
            <span class="block text-xl tracking-tight text-white/75 mb-2">structured freedom for your</span>
            <span class="block text-6xl sm:text-7xl font-semibold tracking-tighter text-white leading-none">thoughts</span>
        </h1>

        <p class="hero-description reveal max-w-2xl text-base sm:text-lg text-white/55 leading-relaxed m-0" style="--reveal-delay: 0.2s;">
            A private notes app and long-term memory bridge for Claude, Cursor, and custom AI agents. Read and write thoughts dynamically.
        </p>

        <div class="hero-cta-group reveal flex flex-wrap items-center justify-center gap-4 mt-8" style="--reveal-delay: 0.36s;">
            <!-- 1. Originkit Liquid Carve 'Get Started' Button -->
            <a id="liquidCarveBtn" href="{' /dashboard' if user_id else '/signup'}" class="relative inline-flex items-center justify-center px-6 py-3 rounded text-sm font-semibold overflow-hidden no-underline cursor-pointer border-b-2 border-r-2 border-[#050505] active:translate-y-[1px] active:translate-x-[1px] shadow-sm select-none">
                <svg class="absolute inset-0 w-full h-full pointer-events-none" style="overflow: visible; z-index: 1;">
                    <defs>
                        <filter id="goo-filter-liquid">
                            <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur"/>
                            <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -9"/>
                        </filter>
                        <mask id="bite-mask-liquid">
                            <rect width="100%" height="100%" fill="#fff"/>
                            <g id="liquidFollowGroup" style="transform: translate(-999px, -999px);">
                                <g id="liquidSquashGroup" style="transform-origin: center;">
                                    <g id="liquidBiteGroup" style="transform: scale(0); transform-origin: center;">
                                        <circle cx="0" cy="0" r="42.5" fill="#000"/>
                                    </g>
                                </g>
                            </g>
                        </mask>
                    </defs>
                    <!-- Reveal Background Layer -->
                    <g filter="url(#goo-filter-liquid)">
                        <rect width="100%" height="100%" fill="#F2F3F8"/>
                    </g>
                    <!-- Masked Yellow Surface Layer -->
                    <g filter="url(#goo-filter-liquid)">
                        <rect width="100%" height="100%" fill="#F5C906" mask="url(#bite-mask-liquid)"/>
                    </g>
                </svg>
                <span class="relative z-10 pointer-events-none font-bold text-sm text-[#080808] tracking-tight">Get Started</span>
            </a>

            <!-- 2. Clean Classic 'See more' Button -->
            <a href="#quickstart" class="bg-surface-white text-on-surface px-6 py-3 text-sm font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors inline-block no-underline shadow-sm rounded">
                See more
            </a>
        </div>
    </div>
</main>

<!-- 1. Live Interactive Code / Terminal Block -->
<section id="quickstart" class="py-16 bg-[#09090b] text-white border-b border-neutral-800">
    <div class="max-w-6xl mx-auto px-6 lg:px-12">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
            <div>
                <h2 class="text-2xl lg:text-3xl font-bold text-white mb-2">Connect in 30 Seconds</h2>
                <p class="text-sm text-neutral-400">Add your MCP Memory endpoint to your AI client configuration file.</p>
            </div>
            <div class="flex items-center bg-[#18181b] border border-neutral-800 p-1 rounded-lg gap-1">
                <button id="tab-claude" onclick="setTerminalTab('claude')" class="px-3 py-1.5 text-xs font-mono rounded bg-white text-black font-semibold transition-colors">Claude Desktop</button>
                <button id="tab-cursor" onclick="setTerminalTab('cursor')" class="px-3 py-1.5 text-xs font-mono rounded text-neutral-400 hover:text-white bg-transparent transition-colors">Cursor / IDE</button>
                <button id="tab-curl" onclick="setTerminalTab('curl')" class="px-3 py-1.5 text-xs font-mono rounded text-neutral-400 hover:text-white bg-transparent transition-colors">cURL / HTTP</button>
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

            <div id="snippet-container" class="p-5 overflow-x-auto text-neutral-300 leading-relaxed">
                <pre id="snippet-claude"><code>{claude_config_snippet}</code></pre>
                <pre id="snippet-cursor" class="hidden"><code>{cursor_config_snippet}</code></pre>
                <pre id="snippet-curl" class="hidden"><code>{curl_config_snippet}</code></pre>
            </div>
        </div>
    </div>
</section>

<!-- 2. EXACT NEON-STYLE ARCHITECTURE CANVAS -->
<section id="pipeline" class="py-20 bg-[#000000] text-white border-b border-neutral-800 overflow-hidden select-none">
    <div class="max-w-7xl mx-auto px-6 lg:px-12">
        
        <div class="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6 mb-8">
            <div>
                <p class="mono text-[11px] tracking-[0.2em] uppercase text-[#00e599] mb-2 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-[#00e599] shadow-[0_0_10px_#00e599]"></span>
                    Live Branching Architecture
                </p>
                <h2 class="text-white text-3xl font-bold tracking-tight">
                    Instant Context Pipeline
                </h2>
            </div>

            <div class="flex items-center gap-3">
                <button onclick="runFullSequence()" class="px-4 py-2 rounded-xl bg-[#121214] hover:bg-[#1c1c20] border border-white/10 text-white/80 hover:text-white mono text-xs font-semibold flex items-center gap-2 transition-all">
                    <span class="material-symbols-outlined text-sm" data-icon="replay">replay</span>
                    Replay Animation
                </button>
            </div>
        </div>

        <div class="transition-opacity opacity-100 relative w-full rounded-2xl border border-white/[0.08] bg-[#000000] shadow-2xl p-2 overflow-x-auto">
            <div class="size-full aspect-[1184/500] min-w-[1050px] relative w-full">

                <svg viewBox="0 0 1184 500" preserveAspectRatio="xMidYMid meet" class="absolute inset-0 w-full h-full">
                    <defs>
                        <pattern id="neonGridPattern" width="36" height="500" patternUnits="userSpaceOnUse">
                            <line x1="0" y1="0" x2="0" y2="500" stroke="#ffffff" stroke-opacity="0.035" stroke-width="1" stroke-dasharray="2 5"/>
                        </pattern>
                        <filter id="neonGreenGlow" x="-20%" y="-400%" width="140%" height="900%">
                            <feGaussianBlur in="SourceGraphic" stdDeviation="3.8" result="blur"/>
                            <feMerge>
                                <feMergeNode in="blur"/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                        <marker id="greenArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                            <path d="M 0 1 L 8 5 L 0 9 z" fill="#00e599"/>
                        </marker>
                    </defs>

                    <rect x="0" y="0" width="1184" height="500" fill="url(#neonGridPattern)"/>

                    <g stroke="#ffffff" stroke-opacity="0.16">
                        <line x1="320" y1="246" x2="320" y2="254"/>
                        <line x1="356" y1="246" x2="356" y2="254"/>
                        <line x1="392" y1="246" x2="392" y2="254"/>
                        <line x1="428" y1="246" x2="428" y2="254"/>
                        <line x1="464" y1="246" x2="464" y2="254"/>
                        <line x1="500" y1="246" x2="500" y2="254"/>
                        <line x1="536" y1="246" x2="536" y2="254"/>
                        <line x1="572" y1="246" x2="572" y2="254"/>
                        <line x1="608" y1="246" x2="608" y2="254"/>
                        <line x1="644" y1="246" x2="644" y2="254"/>
                        <line x1="680" y1="246" x2="680" y2="254"/>
                        <line x1="716" y1="246" x2="716" y2="254"/>
                        <line x1="752" y1="246" x2="752" y2="254"/>
                        <line x1="788" y1="246" x2="788" y2="254"/>
                        <line x1="824" y1="246" x2="824" y2="254"/>
                        <line x1="860" y1="246" x2="860" y2="254"/>
                        <line x1="896" y1="246" x2="896" y2="254"/>
                        <line x1="932" y1="246" x2="932" y2="254"/>
                        <line x1="968" y1="246" x2="968" y2="254"/>
                    </g>

                    <line x1="140" y1="250" x2="1080" y2="250" stroke="#1f1f23" stroke-width="2"/>
                    <path d="M 145 250 H 195" stroke="#00e599" stroke-width="2" marker-end="url(#greenArrow)"/>

                    <path id="seg-scale-p1-a" class="seg-path" data-len="130" d="M 140 250 H 268" stroke="#00e599" stroke-width="2.8" stroke-dasharray="130" stroke-dashoffset="130" filter="url(#neonGreenGlow)" fill="none"/>
                    <path id="seg-scale-p1-b" class="seg-path" data-len="330" d="M 268 250 H 592" stroke="#00e599" stroke-width="2.8" stroke-dasharray="330" stroke-dashoffset="330" filter="url(#neonGreenGlow)" fill="none"/>
                    <path id="seg-branch-p1-up" class="seg-path" data-len="80" d="M 268 250 V 175" stroke="#00e599" stroke-width="1.4" stroke-dasharray="3 3" stroke-dashoffset="80" fill="none"/>
                    <path id="seg-branch-p1-curve" class="seg-path" data-len="400" d="M 268 148 C 268 110 295 110 320 110 H 460 C 495 110 505 160 520 160 H 570" stroke="#52525b" stroke-width="1.6" stroke-dasharray="400" stroke-dashoffset="400" fill="none"/>
                    <path id="seg-branch-p1-chk1" class="seg-path" data-len="60" d="M 520 160 V 105" stroke="#00e599" stroke-width="1.2" stroke-dasharray="3 3" stroke-dashoffset="60" fill="none"/>
                    <path id="seg-branch-p1-chk2" class="seg-path" data-len="60" d="M 664 160 V 105" stroke="#00e599" stroke-width="1.2" stroke-dasharray="3 3" stroke-dashoffset="60" fill="none"/>
                    <path id="seg-branch-p1-gear" class="seg-path" data-len="120" d="M 592 180 V 295" stroke="#ffffff" stroke-width="1.4" stroke-dasharray="3 3" stroke-dashoffset="120" fill="none"/>

                    <path id="seg-scale-p2" class="seg-path" data-len="430" d="M 1020 250 H 592" stroke="#00e599" stroke-width="2.8" stroke-dasharray="430" stroke-dashoffset="430" filter="url(#neonGreenGlow)" fill="none"/>
                    <path id="seg-branch-p2-up" class="seg-path" data-len="80" d="M 940 250 V 175" stroke="#00e599" stroke-width="1.4" stroke-dasharray="3 3" stroke-dashoffset="80" fill="none"/>
                    <path id="seg-branch-p2-curve" class="seg-path" data-len="400" d="M 940 148 C 940 110 915 110 885 110 H 740 C 700 110 690 160 670 160 H 614" stroke="#52525b" stroke-width="1.6" stroke-dasharray="400" stroke-dashoffset="400" fill="none"/>
                    <path id="seg-branch-p2-access" class="seg-path" data-len="140" d="M 645 160 C 705 160 705 235 705 275" stroke="#71717a" stroke-width="1.5" stroke-dasharray="140" stroke-dashoffset="140" fill="none"/>
                    <path id="seg-branch-p2-down" class="seg-path" data-len="150" d="M 1035 265 V 360 H 980" stroke="#00e599" stroke-width="1.4" stroke-dasharray="3 3" stroke-dashoffset="150" fill="none"/>
                    <path id="seg-branch-p2-write-curve" class="seg-path" data-len="120" d="M 870 360 C 830 360 830 420 790 420" stroke="#52525b" stroke-width="1.6" stroke-dasharray="120" stroke-dashoffset="120" fill="none"/>
                    <path id="seg-branch-p2-return" class="seg-path" data-len="710" d="M 790 420 H 85" stroke="#00e599" stroke-width="1.8" stroke-dasharray="710" stroke-dashoffset="710" fill="none"/>
                    <path id="seg-branch-p2-arrow-neon" class="seg-path" data-len="150" d="M 300 420 V 270" stroke="#00e599" stroke-width="1.4" stroke-dasharray="3 3" stroke-dashoffset="150" marker-end="url(#greenArrow)" fill="none"/>
                    <path id="seg-branch-p2-arrow-mem" class="seg-path" data-len="150" d="M 85 420 V 270" stroke="#00e599" stroke-width="1.4" stroke-dasharray="3 3" stroke-dashoffset="150" marker-end="url(#greenArrow)" fill="none"/>

                    <g id="elem-junc-neon" class="timeline-elem">
                        <circle cx="268" cy="250" r="3.5" fill="#000000" stroke="#00e599" stroke-width="2"/>
                    </g>
                    <g id="elem-db-icon" class="timeline-elem">
                        <circle cx="268" cy="162" r="14" fill="#18181b" stroke="#3f3f46" stroke-width="1.5"/>
                        <path d="M263 157 C263 155 265 154 268 154 C271 154 273 155 273 157 C273 159 271 160 268 160 C265 160 263 159 263 157 Z M263 162 C263 164 265 165 268 165 C271 165 273 164 273 162 M263 167 C263 169 265 170 268 170 C271 170 273 169 273 167" stroke="#ffffff" stroke-width="1.2" fill="none"/>
                    </g>
                    <g id="chk-neg-start" class="timeline-elem">
                        <circle cx="520" cy="105" r="7" fill="#092f1f" stroke="#00e599" stroke-width="2"/>
                        <path d="M517 105 L519 107 L523 103" stroke="#00e599" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <text x="520" y="55" fill="#a1a1aa" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">negotiation<tspan x="520" dy="14">started</tspan></text>
                    </g>
                    <g id="chk-neg-complete" class="timeline-elem">
                        <circle cx="664" cy="105" r="7" fill="#092f1f" stroke="#00e599" stroke-width="2"/>
                        <path d="M661 105 L663 107 L667 103" stroke="#00e599" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <text x="664" y="55" fill="#a1a1aa" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">negotiation<tspan x="664" dy="14">complete</tspan></text>
                    </g>
                    <g id="elem-gear" class="timeline-elem">
                        <circle cx="592" cy="310" r="14" fill="#18181b" stroke="#3f3f46" stroke-width="1.5"/>
                        <path d="M592 305 A5 5 0 1 0 592 315 A5 5 0 1 0 592 305 M592 302 V304 M592 316 V318 M584 310 H586 M598 310 H600" stroke="#ffffff" stroke-width="1.4" fill="none"/>
                        <text x="592" y="342" fill="#a1a1aa" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">protocol<tspan x="592" dy="14">negotiation</tspan></text>
                    </g>
                    <g id="elem-junc-ai" class="timeline-elem">
                        <circle cx="940" cy="250" r="3.5" fill="#000000" stroke="#00e599" stroke-width="2"/>
                    </g>
                    <g id="elem-robot-icon" class="timeline-elem">
                        <circle cx="940" cy="162" r="14" fill="#18181b" stroke="#3f3f46" stroke-width="1.5"/>
                        <path d="M936 159 H944 V167 H936 Z M940 155 V159 M933 163 H936 M944 163 H947 M938 162 H939 M941 162 H942" stroke="#ffffff" stroke-width="1.2" fill="none"/>
                    </g>
                    <g id="chk-access-granted" class="timeline-elem">
                        <circle cx="705" cy="275" r="7" fill="#092f1f" stroke="#00e599" stroke-width="2"/>
                        <path d="M702 275 L704 277 L708 273" stroke="#00e599" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <text x="705" y="306" fill="#a1a1aa" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">tools &amp; data<tspan x="705" dy="14">access granted</tspan></text>
                    </g>
                    <g id="chk-note-processed" class="timeline-elem">
                        <circle cx="705" cy="420" r="7" fill="#092f1f" stroke="#00e599" stroke-width="2"/>
                        <path d="M702 420 L704 422 L708 418" stroke="#00e599" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <text x="705" y="452" fill="#a1a1aa" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">note processed<tspan x="705" dy="14">by mcp-server</tspan></text>
                    </g>
                    <g id="chk-note-saved" class="timeline-elem">
                        <circle cx="300" cy="420" r="7" fill="#092f1f" stroke="#00e599" stroke-width="2"/>
                        <path d="M297 420 L299 422 L303 418" stroke="#00e599" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <text x="300" y="452" fill="#a1a1aa" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">note saved<tspan x="300" dy="14">in neon db</tspan></text>
                    </g>
                    <g id="chk-sync-final" class="timeline-elem">
                        <circle cx="85" cy="420" r="7" fill="#092f1f" stroke="#00e599" stroke-width="2"/>
                        <path d="M82 420 L84 422 L88 418" stroke="#00e599" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <text x="85" y="452" fill="#a1a1aa" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">sync<tspan x="85" dy="14">(auto / manual)</tspan></text>
                    </g>
                </svg>

                <!-- HTML CAPSULE PILLS OVERLAY -->
                <div id="pill-memory-notes" class="timeline-elem pill-memory-start absolute -translate-y-1/2 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white text-[#0a0a0a] mono text-xs font-bold shadow-[0_0_20px_rgba(255,255,255,0.2)] border-2 border-transparent select-none z-10" style="left:1.5%; top:48%;">
                    <svg class="w-3.5 h-3.5 text-[#0a0a0a]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                    Memory Notes
                </div>
                <div class="absolute mono text-[11px] text-white/50 text-center" style="left:2.2%; top:53%;">
                    Notes added<br>by you
                </div>
                <div class="absolute mono text-[10px] text-[#00e599] font-semibold" style="left:14%; top:49.8%;">
                    sync
                </div>

                <div id="elem-neon-db" class="timeline-elem absolute -translate-y-1/2 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white text-[#0a0a0a] mono text-xs font-bold shadow-[0_0_20px_rgba(255,255,255,0.2)] border-2 border-transparent select-none z-10" style="left:18.5%; top:48%;">
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 3.79 2 6v12c0 2.21 4.48 4 10 4s10-1.79 10-4V6c0-2.21-4.48-4-10-4zm0 2c4.97 0 8 1.46 8 2s-3.03 2-8 2-8-1.46-8-2 3.03-2 8-2zm0 16c-4.97 0-8-1.46-8-2v-2.23c2.08 1.34 5.09 2.23 8 2.23s5.92-.89 8-2.23V18c0 .54-3.03 2-8 2z"/></svg>
                    neon db
                </div>
                <div class="absolute mono text-[11px] text-white/50 text-center" style="left:19.5%; top:53%;">
                    Stores all notes
                </div>

                <div id="elem-request-data" class="timeline-elem absolute -translate-y-1/2 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#383a42] text-white mono text-xs font-medium select-none border border-white/10 shadow-md z-10" style="left:27%; top:22%;">
                    <svg class="w-3.5 h-3.5 text-white/70" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 3.79 2 6v12c0 2.21 4.48 4 10 4s10-1.79 10-4V6c0-2.21-4.48-4-10-4zm0 2c4.97 0 8 1.46 8 2s-3.03 2-8 2-8-1.46-8-2 3.03-2 8-2zm0 16c-4.97 0-8-1.46-8-2v-2.23c2.08 1.34 5.09 2.23 8 2.23s5.92-.89 8-2.23V18c0 .54-3.03 2-8 2z"/></svg>
                    request data
                </div>

                <div id="elem-mcp-server" class="timeline-elem absolute -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 px-4 py-2 rounded-full bg-[#fde047] text-[#0a0a0a] mono text-xs font-extrabold shadow-[0_0_25px_rgba(253,224,71,0.4)] select-none border-2 border-white/40 z-20" style="left:50%; top:31%;">
                    <svg class="w-4 h-4 text-[#0a0a0a]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
                    mcp-server
                </div>

                <div id="elem-request-tools" class="timeline-elem absolute -translate-y-1/2 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#383a42] text-white mono text-xs font-medium select-none border border-white/10 shadow-md z-10" style="left:64%; top:22%;">
                    <svg class="w-3.5 h-3.5 text-white/70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                    request tools
                </div>

                <div id="elem-ai-apps" class="timeline-elem absolute -translate-y-1/2 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white text-[#0a0a0a] mono text-xs font-bold shadow-[0_0_20px_rgba(255,255,255,0.2)] border-2 border-transparent select-none z-10" style="left:86%; top:48%;">
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>
                    ai apps
                </div>
                <div class="absolute mono text-[11px] text-white/50 text-center" style="left:86%; top:53%;">
                    AI Agents / Apps
                </div>

                <div id="elem-write-note" class="timeline-elem absolute -translate-y-1/2 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#383a42] text-white mono text-xs font-medium select-none border border-white/10 shadow-md z-10" style="left:76%; top:69%;">
                    <svg class="w-3.5 h-3.5 text-white/70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
                    write note
                </div>

                <div class="absolute -translate-x-1/2 mono text-[10px] text-white/35" style="left:22.5%; top:59%;">18:24:00</div>
                <div class="absolute -translate-x-1/2 mono text-[10px] text-white/35" style="left:41%; top:41%;">19:08:12</div>
                <div class="absolute -translate-x-1/2 mono text-[10px] text-white/35" style="left:73.5%; top:53.5%;">20:32:04</div>

            </div>

            <div class="px-6 py-3 bg-[#09090b] border-t border-white/5 flex items-center justify-between mono text-xs">
                <div id="anim-status-indicator" class="text-white/80">
                    <span class="text-[#00e599] font-bold">1. Ingestion:</span> Memory Notes sparkles &amp; shoots beam along scale to mcp-server.
                </div>
                <span class="text-white/30 hidden sm:inline">Model Context Protocol 2.1</span>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 pt-8 border-t border-white/[0.08]">
            <div>
                <div class="flex items-center gap-2 text-white font-semibold text-sm mb-2">
                    <span class="material-symbols-outlined text-base text-[#00e599]" data-icon="sync">sync</span>
                    Local-first Sync
                </div>
                <p class="text-xs text-neutral-400 leading-relaxed">
                    Capture notes distraction-free on Android. Records persist instantly to SQLite Room DB and stream upstream to Neon Postgres.
                </p>
            </div>
            <div>
                <div class="flex items-center gap-2 text-white font-semibold text-sm mb-2">
                    <span class="material-symbols-outlined text-base text-[#fde047]" data-icon="hub">hub</span>
                    FastMCP Protocol Broker
                </div>
                <p class="text-xs text-neutral-400 leading-relaxed">
                    Stateless FastMCP protocol server intercepts LLM tool requests, manages authenticated access, and queries Neon DB.
                </p>
            </div>
            <div>
                <div class="flex items-center gap-2 text-white font-semibold text-sm mb-2">
                    <span class="material-symbols-outlined text-base text-[#22d3ee]" data-icon="bolt">bolt</span>
                    Instant Context
                </div>
                <p class="text-xs text-neutral-400 leading-relaxed">
                    Sub-10ms trigram similarity queries inject personal notes and project history directly into Claude, Cursor, and ChatGPT.
                </p>
            </div>
        </div>

    </div>
</section>

<!-- 3. Developer Feature Deep Dives -->
<section id="features" class="py-16 bg-[#09090b] text-white border-b border-neutral-800">
    <div class="max-w-6xl mx-auto px-6 lg:px-12 space-y-16">
        
        <!-- Spotlight 1: Zero-Latency Trigram Search -->
        <div class="flex flex-col lg:flex-row items-center gap-10">
            <div class="flex-1 space-y-3">
                <div class="inline-block px-2 py-1 bg-white/10 rounded text-xs font-mono font-semibold text-[#00e599]">FULL-TEXT RECALL</div>
                <h3 class="text-2xl font-bold text-white">Zero-Latency Trigram Search</h3>
                <p class="text-sm text-neutral-400 leading-relaxed">
                    Traditional LLM retrieval fails when queries have typos or fragmented terms. Memory Notes harnesses PostgreSQL trigram matching (<code class="font-mono text-xs text-white bg-white/10 px-1 py-0.5 rounded">pg_trgm</code>) to fuzzy-match title and body content across workspaces in milliseconds.
                </p>
                <ul class="text-xs font-mono text-neutral-400 space-y-1 pt-2">
                    <li>✓ Typo-tolerant substring & fuzzy similarity score</li>
                    <li>✓ Automatic fallback to ILIKE if extensions are missing</li>
                </ul>
            </div>
            <div class="flex-1 w-full">
                <div class="bg-[#0f0f11] text-neutral-200 p-5 rounded-xl border border-neutral-800 font-mono text-xs shadow-md">
                    <div class="text-neutral-500 mb-2">// SQL Query Execution</div>
                    <div class="text-yellow-400">SELECT <span class="text-neutral-200">id, title, similarity(title, $1) AS score</span></div>
                    <div class="text-yellow-400">FROM <span class="text-neutral-200">notes</span></div>
                    <div class="text-yellow-400">WHERE <span class="text-neutral-200">title % $1 OR content ILIKE '%'||$1||'%'</span></div>
                    <div class="text-yellow-400">ORDER BY <span class="text-neutral-200">score DESC LIMIT 10;</span></div>
                    <div class="mt-3 pt-3 border-t border-neutral-800 text-green-400 text-[11px]">
                        ⚡ Query Execution: 3.4ms | 10 rows retrieved
                    </div>
                </div>
            </div>
        </div>

        <hr class="border-neutral-800">

        <!-- Spotlight 2: Autonomous AI Memory Sync -->
        <div class="flex flex-col lg:flex-row-reverse items-center gap-10">
            <div class="flex-1 space-y-3">
                <div class="inline-block px-2 py-1 bg-yellow-400/10 rounded text-xs font-mono font-semibold text-yellow-400">BI-DIRECTIONAL WRITES</div>
                <h3 class="text-2xl font-bold text-white">Autonomous AI Memory Sync</h3>
                <p class="text-sm text-neutral-400 leading-relaxed">
                    Claude and Cursor can not only inspect your past notes—they can create new workspace folders, append structured summaries, or update existing documents directly from conversation prompts.
                </p>
                <ul class="text-xs font-mono text-neutral-400 space-y-1 pt-2">
                    <li>✓ Explicit bigint epoch timestamping for Last-Write-Wins</li>
                    <li>✓ Reactive Jetpack Compose Room sync down to Android</li>
                </ul>
            </div>
            <div class="flex-1 w-full">
                <div class="bg-[#0f0f11] text-neutral-200 p-5 rounded-xl border border-neutral-800 font-mono text-xs shadow-md">
                    <div class="text-neutral-500 mb-2">// MCP Tool Invocation Output</div>
                    <div class="text-blue-400">&gt; create_note(<span class="text-neutral-300">title="Sprint Specs", workspace="Dev"</span>)</div>
                    <div class="text-neutral-400 mt-2">
                        {{<br>
                        &nbsp;&nbsp;"id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",<br>
                        &nbsp;&nbsp;"title": "Sprint Specs",<br>
                        &nbsp;&nbsp;"updated_at": 1786675973594<br>
                        }}
                    </div>
                    <div class="mt-3 pt-3 border-t border-neutral-800 text-green-400 text-[11px]">
                        ✓ Database record created • Dispatched to mobile sync engine
                    </div>
                </div>
            </div>
        </div>

    </div>
</section>
"""
    return _page("Home", body)


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------
async def signup_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    
    body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-6">
    <div class="max-w-md w-full bg-[#0d0d10] border border-neutral-800 p-8 rounded-xl shadow-sm text-white">
        <h2 class="text-2xl font-bold mb-1">Create Your Account</h2>
        <p class="text-xs text-neutral-400 mb-6">Set up your Memory Notes gateway account.</p>
        <form method="POST" action="/signup">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Email Address</label>
                <input type="email" name="email" placeholder="name@example.com" required autofocus class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white focus:outline-none focus:border-white">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Password (min 8 characters)</label>
                <input type="password" name="password" placeholder="••••••••" minlength="8" required class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white focus:outline-none focus:border-white">
            </div>
            <button type="submit" class="w-full bg-white text-black py-3 rounded text-sm font-semibold hover:bg-neutral-200 transition-colors">Sign Up</button>
        </form>
        <p class="text-xs text-neutral-400 text-center mt-6">Already have an account? <a href="/login?next={next_}" class="text-white font-semibold hover:underline">Log in</a></p>
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
<main class="flex-grow flex items-center justify-center py-16 px-6">
    <div class="max-w-md w-full bg-[#0d0d10] border border-neutral-800 p-8 rounded-xl shadow-sm text-white">
        <h2 class="text-2xl font-bold mb-1">Create Your Account</h2>
        <div class="p-3 bg-red-950 text-red-300 text-xs rounded mb-4 border border-red-800">{error}</div>
        <form method="POST" action="/signup">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Email Address</label>
                <input type="email" name="email" value="{email}" required autofocus class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Password</label>
                <input type="password" name="password" minlength="8" required class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white">
            </div>
            <button type="submit" class="w-full bg-white text-black py-3 rounded text-sm font-semibold">Sign Up</button>
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
<main class="flex-grow flex items-center justify-center py-16 px-6">
    <div class="max-w-md w-full bg-[#0d0d10] border border-neutral-800 p-8 rounded-xl shadow-sm text-white">
        <h2 class="text-2xl font-bold mb-1">Create Your Account</h2>
        <div class="p-3 bg-red-950 text-red-300 text-xs rounded mb-4 border border-red-800">An account with that email already exists.</div>
        <p class="text-xs"><a href="/login?next={next_}" class="text-white font-semibold underline">Log in instead</a></p>
    </div>
</main>
"""
        return _page("Sign up", body)

    request.session["user_id"] = user_id
    return RedirectResponse(next_, status_code=302)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
async def login_get(request: Request):
    next_ = _safe_next(request.query_params.get("next"))
    if _require_login(request):
        return RedirectResponse(next_, status_code=302)
    
    body = f"""
{_navbar(request)}
<main class="flex-grow flex items-center justify-center py-16 px-6">
    <div class="max-w-md w-full bg-[#0d0d10] border border-neutral-800 p-8 rounded-xl shadow-sm text-white">
        <h2 class="text-2xl font-bold mb-1">Welcome Back</h2>
        <p class="text-xs text-neutral-400 mb-6">Log in to your account.</p>
        <form method="POST" action="/login">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Email Address</label>
                <input type="email" name="email" placeholder="name@example.com" required autofocus class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white focus:outline-none focus:border-white">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Password</label>
                <input type="password" name="password" placeholder="••••••••" required class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white focus:outline-none focus:border-white">
            </div>
            <button type="submit" class="w-full bg-white text-black py-3 rounded text-sm font-semibold hover:bg-neutral-200 transition-colors">Log In</button>
        </form>
        <p class="text-xs text-neutral-400 text-center mt-6">No account yet? <a href="/signup?next={next_}" class="text-white font-semibold hover:underline">Sign up</a></p>
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
<main class="flex-grow flex items-center justify-center py-16 px-6">
    <div class="max-w-md w-full bg-[#0d0d10] border border-neutral-800 p-8 rounded-xl shadow-sm text-white">
        <h2 class="text-2xl font-bold mb-1">Welcome Back</h2>
        <div class="p-3 bg-red-950 text-red-300 text-xs rounded mb-4 border border-red-800">Incorrect email or password.</div>
        <form method="POST" action="/login">
            <input type="hidden" name="next" value="{next_}">
            <div class="mb-4">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Email Address</label>
                <input type="email" name="email" value="{email}" required autofocus class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white">
            </div>
            <div class="mb-6">
                <label class="block text-xs font-semibold text-neutral-300 mb-1">Password</label>
                <input type="password" name="password" required class="w-full px-4 py-2 border border-neutral-700 bg-neutral-900 rounded text-sm text-white">
            </div>
            <button type="submit" class="w-full bg-white text-black py-3 rounded text-sm font-semibold">Log In</button>
        </form>
    </div>
</main>
"""
        return _page("Log in", body)

    request.session["user_id"] = str(user["id"])
    return RedirectResponse(next_, status_code=302)


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
<div class="mb-6 p-4 bg-neutral-900 border border-green-500 rounded-lg">
    <strong class="text-xs uppercase font-mono text-green-400 block mb-1">New API Key (Shown Once — Copy Now):</strong>
    <div class="flex items-center gap-2 mt-2">
        <input type="text" readonly value="{flash_key}" id="newApiKeyField" class="w-full font-mono text-xs bg-black text-white border border-neutral-700 p-2 rounded">
        <button id="btnCopyKey" onclick="copyToClipboard('{flash_key}', 'btnCopyKey')" class="bg-white text-black px-4 py-2 rounded text-xs font-semibold whitespace-nowrap">Copy</button>
    </div>
    <p class="text-xs text-neutral-400 mt-2">Use this as your Bearer Token for Claude or direct API configurations.</p>
</div>
"""

    if user["connection_string_encrypted"]:
        masked = security.mask_connection_string(security.decrypt_text(user["connection_string_encrypted"]))
        conn_status = f'<p class="text-xs text-neutral-400">Currently linked: <code class="text-white font-mono">{masked}</code></p>'
    else:
        conn_status = '<div class="p-3 bg-red-950 text-red-300 text-xs rounded border border-red-800">No Neon connection string set yet. Claude connector will fail until configured.</div>'

    keys = await db_control.list_api_keys(pool, user_id)
    active_keys = [k for k in keys if k["revoked_at"] is None]
    if active_keys:
        rows = "".join(f"""
<div class="flex items-center justify-between py-3 border-b border-neutral-800 last:border-0">
    <div>
        <div class="text-sm font-semibold text-white">{k['label']}</div>
        <div class="text-xs text-neutral-400">Created {k['created_at'].strftime('%b %d, %Y')}{f" • Last used {k['last_used_at'].strftime('%b %d, %Y')}" if k['last_used_at'] else ""}</div>
    </div>
    <form method="POST" action="/dashboard/api-key/revoke" class="m-0">
        <input type="hidden" name="key_id" value="{k['id']}">
        <button type="submit" class="text-red-400 text-xs font-semibold hover:underline" onclick="return confirm('Revoke this key? Apps using it will disconnect immediately.');">Revoke</button>
    </form>
</div>
""" for k in active_keys)
    else:
        rows = '<p class="text-xs text-neutral-400">No active API keys found.</p>'

    base_url = str(request.base_url).rstrip("/")
    mcp_endpoint = f"{base_url}/mcp"
    nav_html = _navbar(request, user["email"])

    body = f"""
{nav_html}
<main class="flex-grow py-10 px-6 bg-[#040407] text-white">
    <div class="max-w-3xl mx-auto">
        <div class="mb-6">
            <h1 class="text-2xl font-bold mb-1">Dashboard & Settings</h1>
            <p class="text-xs text-neutral-400">Manage your database connection string, API keys, and connector endpoint.</p>
        </div>

        {flash_html}

        <!-- 1. Endpoint & Connection URL -->
        <div class="bg-[#0d0d10] border border-neutral-800 p-6 rounded-xl mb-6 shadow-sm">
            <h2 class="text-base font-semibold mb-1">1. MCP Server Endpoint</h2>
            <p class="text-xs text-neutral-400 mb-3">Provide this URL when configuring your Claude Desktop or HTTP MCP client connector.</p>
            <div class="flex items-center gap-2">
                <input type="text" readonly value="{mcp_endpoint}" id="mcpEndpointField" class="w-full font-mono text-xs bg-black text-white border border-neutral-700 p-2.5 rounded">
                <button id="btnCopyEndpoint" onclick="copyToClipboard('{mcp_endpoint}', 'btnCopyEndpoint')" class="bg-white text-black px-4 py-2.5 rounded text-xs font-semibold whitespace-nowrap">Copy URL</button>
            </div>
        </div>

        <!-- 2. Neon Database Connection String Settings -->
        <div class="bg-[#0d0d10] border border-neutral-800 p-6 rounded-xl mb-6 shadow-sm">
            <h2 class="text-base font-semibold mb-1">2. Neon Database Connection String</h2>
            <p class="text-xs text-neutral-400 mb-3">Paste the same PostgreSQL connection string your mobile notes app uses to sync.</p>
            {conn_status}
            <form method="POST" action="/dashboard/connection-string" class="mt-4">
                <div class="mb-3">
                    <input type="text" name="connection_string" placeholder="postgresql://user:password@ep-xxx.neon.tech/dbname" required class="w-full px-4 py-2.5 border border-neutral-700 bg-black text-white rounded text-xs font-mono focus:outline-none focus:border-white">
                </div>
                <button type="submit" class="bg-white text-black px-6 py-2.5 rounded text-xs font-semibold hover:bg-neutral-200 transition-colors">Save Connection String</button>
            </form>
        </div>

        <!-- 3. API Keys Management -->
        <div class="bg-[#0d0d10] border border-neutral-800 p-6 rounded-xl shadow-sm">
            <h2 class="text-base font-semibold mb-1">3. MCP API Keys</h2>
            <p class="text-xs text-neutral-400 mb-3">API keys are generated automatically through Claude OAuth, or you can create them manually for custom apps.</p>
            <div class="divide-y border-neutral-800 mb-4">
                {rows}
            </div>
            <form method="POST" action="/dashboard/api-key/create">
                <button type="submit" class="bg-white text-black px-6 py-2.5 rounded text-xs font-semibold hover:bg-neutral-200 transition-colors">Generate New Manual API Key</button>
            </form>
        </div>
    </div>
</main>
"""
    return _page("Dashboard", body)


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
<main class="flex-grow flex items-center justify-center py-16 px-6 bg-[#040407] text-white">
    <div class="max-w-md w-full bg-[#0d0d10] border border-neutral-800 p-8 rounded-xl shadow-sm text-center">
        <h2 class="text-lg font-bold text-red-400 mb-2">Error</h2>
        <div class="p-3 bg-red-950 text-red-300 text-xs rounded mb-6 border border-red-800">{message}</div>
        <a href="/dashboard" class="inline-block bg-white text-black px-6 py-2.5 rounded text-xs font-semibold no-underline">Back to Dashboard</a>
    </div>
</main>
"""
    return _page("Error", body)


# Route registry
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
