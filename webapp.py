"""
Memory Notes - Web Application
Full Python Starlette ASGI Application with:
- Monochromatic Tailwind CSS Design System
- Interactive Spotlight Grid Hero with Clean Standard Action Buttons ("Get Started" & "See more")
- Live Emerging Architecture Pipeline Canvas (Neon DB -> FastMCP Broker -> AI Apps)
- Multi-Tab Quick-Start Terminal Snippets (Claude Desktop / Cursor / cURL)
- Developer Feature Deep Dives & Full-Stack Auth / Multi-Tenant Dashboard
- Console Workspace 2D Infinite Canvas Node Interface for Logged-In Users
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

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

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
    .mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Hero Spotlight Grid */
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
    .hero-interactive-grid:hover::after {{
        opacity: 1;
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
</style>
</head>
<body class="bg-surface-white text-on-surface font-body-md min-h-screen flex flex-col selection:bg-primary-container selection:text-on-primary-container">
{body}
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
                btn.className = 'px-3 py-1.5 text-xs font-mono rounded bg-on-surface text-surface-white font-semibold transition-colors';
                block.classList.remove('hidden');
            }} else {{
                btn.className = 'px-3 py-1.5 text-xs font-mono rounded text-text-secondary hover:text-on-surface bg-transparent transition-colors';
                block.classList.add('hidden');
            }}
        }});
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
    return "/console"


def _navbar(request: Request, user_email: str | None = None) -> str:
    if user_email:
        right_actions = """
        <a href="/console" class="bg-secondary-container text-on-surface px-4 py-2 rounded text-sm font-semibold hover:bg-secondary-fixed transition-colors no-underline">Console</a>
        """
    else:
        right_actions = """
        <a href="/login" class="bg-surface-white text-on-surface px-4 py-2 rounded text-sm font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors no-underline">Log In</a>
        <a href="/signup" class="bg-secondary-container text-on-surface px-4 py-2 rounded text-sm font-semibold hover:bg-secondary-fixed transition-colors no-underline">Get Started</a>
        """

    return f"""
<nav class="sticky top-0 z-50 flex justify-between items-center w-full px-6 lg:px-12 py-3 bg-surface-white border-b border-border-muted">
    <div class="flex items-center gap-4">
        <a href="/" class="text-xl font-bold text-on-surface no-underline tracking-tight">Memory Notes</a>
    </div>
    <div class="flex items-center gap-4">
        {right_actions}
    </div>
</nav>
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
{nav_html}
<main class="flex-grow">
    <!-- Hero Section -->
    <section class="relative pt-20 pb-20 border-b border-border-muted hero-interactive-grid"
             onmousemove="const r = this.getBoundingClientRect(); this.style.setProperty('--x', (event.clientX - r.left) + 'px'); this.style.setProperty('--y', (event.clientY - r.top) + 'px');">
        <div class="max-w-6xl mx-auto px-6 lg:px-12 relative z-10 flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
            <div class="flex-1 space-y-4 text-center lg:text-left">
                <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-surface-white border border-border-muted text-xs font-mono text-on-surface-variant mb-2 shadow-xs">
                    <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    Model Context Protocol Active
                </div>
                <h1 class="text-4xl lg:text-[54px] lg:leading-[60px] font-bold text-on-surface tracking-tight max-w-2xl">
                    Structured Freedom for Your Thoughts.
                </h1>
                <p class="text-base lg:text-lg text-on-surface-variant max-w-xl mx-auto lg:mx-0 leading-relaxed">
                    A private notes app and long-term memory bridge for Claude, Cursor, and custom AI agents. Read and write thoughts dynamically.
                </p>
                <div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 pt-3">
                    <a href="{' /console' if user_id else '/signup'}" class="bg-secondary-container text-on-surface px-6 py-3 text-sm font-semibold border-b-2 border-r-2 border-[#050505] active:translate-y-[1px] active:translate-x-[1px] transition-all inline-block no-underline shadow-sm">Get Started</a>
                    <a href="#quickstart" class="bg-surface-white text-on-surface px-6 py-3 text-sm font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors inline-block no-underline shadow-sm">See more</a>
                </div>
            </div>
            
            <div class="flex-1 w-full max-w-md lg:max-w-none flex items-center justify-center">
                <div class="p-6 bg-surface-white border border-border-muted rounded-xl shadow-md text-left w-full max-w-md font-mono text-xs">
                    <div class="flex items-center justify-between pb-3 mb-3 border-b border-border-muted">
                        <span class="font-bold text-primary">● MCP MEMORY GATEWAY</span>
                        <span class="text-text-secondary">Connected</span>
                    </div>
                    <p class="text-text-secondary mb-1">&gt; AI Model query sync:</p>
                    <p class="text-on-surface font-semibold">&gt; search_notes(query="architecture design")</p>
                    <p class="text-primary mt-2">✓ Synced instantly to local client.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 1. Live Interactive Code / Terminal Block -->
    <section id="quickstart" class="py-16 bg-surface-white border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
                <div>
                    <h2 class="text-2xl lg:text-3xl font-bold text-on-surface mb-2">Connect in 30 Seconds</h2>
                    <p class="text-sm text-on-surface-variant">Add your MCP Memory endpoint to your AI client configuration file.</p>
                </div>
                <div class="flex items-center bg-surface-container-low border border-border-muted p-1 rounded-lg gap-1">
                    <button id="tab-claude" onclick="setTerminalTab('claude')" class="px-3 py-1.5 text-xs font-mono rounded bg-on-surface text-surface-white font-semibold transition-colors">Claude Desktop</button>
                    <button id="tab-cursor" onclick="setTerminalTab('cursor')" class="px-3 py-1.5 text-xs font-mono rounded text-text-secondary hover:text-on-surface bg-transparent transition-colors">Cursor / IDE</button>
                    <button id="tab-curl" onclick="setTerminalTab('curl')" class="px-3 py-1.5 text-xs font-mono rounded text-text-secondary hover:text-on-surface bg-transparent transition-colors">cURL / HTTP</button>
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

    <!-- 2. EXACT NEON-STYLE ARCHITECTURE CANVAS WITH EMBEDDED EXACT ANIMATION -->
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
            </div>

            <!-- Embedded Exact Animation Diagram Container -->
            <div class="w-full flex justify-center bg-[#000000] rounded-2xl border border-white/[0.08] p-4 overflow-x-auto shadow-2xl">
              <div class="diagram-container" style="transform: scale(0.95); transform-origin: center;">
                <!-- Grid Columns -->
                <div class="vertical-grid">
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                  <div class="grid-line"></div><div class="grid-line"></div><div class="grid-line"></div>
                </div>

                <!-- Vector Canvas -->
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

                  <!-- Main Central Timeline Track -->
                  <path id="path-main" d="M 74 262 L 950 262" class="line-green" />
                  <path id="path-sync-arrow" d="M 132 262 L 188 262" class="line-green" marker-end="url(#arrow-green)" />

                  <!-- Ruler Ticks -->
                  <g id="ticks">
                    <line x1="292" y1="256" x2="292" y2="268" class="ruler-tick" />
                    <line x1="316" y1="258" x2="316" y2="266" class="ruler-tick" />
                    <line x1="340" y1="256" x2="340" y2="268" class="ruler-tick" />
                    <line x1="364" y1="258" x2="364" y2="266" class="ruler-tick" />
                    <line x1="388" y1="256" x2="388" y2="268" class="ruler-tick" />
                    
                    <!-- 19:08:12 Tick -->
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

                    <!-- 20:32:04 Tick -->
                    <line id="tick-20" x1="743" y1="248" x2="743" y2="276" class="ruler-tick tick-active" style="opacity: 0;" />

                    <line x1="766" y1="258" x2="766" y2="266" class="ruler-tick" />
                    <line x1="790" y1="256" x2="790" y2="268" class="ruler-tick" />
                    <line x1="814" y1="258" x2="814" y2="266" class="ruler-tick" />
                    <line x1="838" y1="256" x2="838" y2="268" class="ruler-tick" />
                    <line x1="862" y1="258" x2="862" y2="266" class="ruler-tick" />
                  </g>

                  <!-- Upper Left Branch Flow -->
                  <path id="path-db-up" d="M 226 262 V 182" class="line-green-dash" />
                  <path id="path-req-data" d="M 226 162 V 138 Q 226 118 248 118 H 268" class="line-white-dash" />
                  <path id="path-data-to-mcp" d="M 390 118 H 410 Q 426 118 426 140 V 158 Q 426 172 444 172 H 455" class="line-white-dash" />

                  <!-- Negotiation Status Lines -->
                  <path id="path-neg-1" d="M 450 85 V 157" class="line-green-dash" />
                  <path id="path-neg-2" d="M 591 85 V 157" class="line-green-dash" />

                  <!-- Upper Right Branch Flow -->
                  <path id="path-mcp-to-tools" d="M 584 172 H 598 Q 614 172 614 150 V 138 Q 614 118 632 118 H 648" class="line-white-dash" />
                  <path id="path-tools-to-apps" d="M 776 118 H 806 Q 828 118 828 138 V 162" class="line-white-dash" />
                  <path id="path-apps-down" d="M 828 182 V 262" class="line-green-dash" />

                  <!-- Center Protocol Negotiation Line -->
                  <path id="path-protocol" d="M 520 188 V 328" class="line-white-dash" />

                  <!-- Access Granted Line -->
                  <path id="path-granted" d="M 572 188 V 276 Q 572 298 598 298 H 618" class="line-white-solid" />

                  <!-- Lower Return Flow -->
                  <path id="path-ai-to-note" d="M 918 278 V 356 Q 918 380 892 380 H 885" class="line-green-dash" />
                  <path id="path-note-to-proc" d="M 775 380 H 760 Q 747 380 747 408 V 418 Q 747 440 726 440 H 635" class="line-white-solid" />
                  <path id="path-lower-flow" d="M 615 440 L 280 440" class="line-green-dash" marker-end="url(#arrow-green)" />
                  <path id="path-ret-db" d="M 248 440 H 236 Q 236 400 236 360" class="line-green-dash" marker-end="url(#arrow-green)" />
                  <path id="path-ret-sync" d="M 248 440 H 76 V 340" class="line-green-dash" marker-end="url(#arrow-green)" />

                  <!-- Leading Glow Head -->
                  <circle id="head-dot" class="glow-dot" r="3.5" cx="0" cy="0" />
                </svg>

                <!-- Top Negotiation Status Badges -->
                <div id="el-neg1-txt" class="meta-text" style="top: 54px; left: 450px;">negotiation<br>started</div>
                <div id="el-neg1-ico" class="circle-icon check-node" style="top: 111px; left: 450px;">✓</div>

                <div id="el-neg2-txt" class="meta-text" style="top: 54px; left: 591px;">negotiation<br>complete</div>
                <div id="el-neg2-ico" class="circle-icon check-node" style="top: 111px; left: 591px;">✓</div>

                <!-- Upper Badges -->
                <div id="el-db-ico" class="circle-icon outline-node" style="top: 172px; left: 226px;">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                </div>

                <div id="el-req-data" class="badge badge-dark" style="top: 118px; left: 327px;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg>
                  request data
                </div>

                <!-- MCP SERVER -->
                <div id="el-mcp" class="badge badge-yellow" style="top: 172px; left: 520px;">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
                  mcp-server
                </div>

                <div id="el-req-tools" class="badge badge-dark" style="top: 118px; left: 713px;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"/></svg>
                  request tools
                </div>

                <div id="el-bot-ico" class="circle-icon outline-node" style="top: 172px; left: 828px;">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>
                </div>

                <div id="el-hollow-top" class="circle-icon hollow-node" style="top: 228px; left: 828px;"></div>

                <!-- Main Central Timeline Badges -->
                <div id="el-notes" class="badge badge-white" style="top: 262px; left: 74px;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
                  Memory Notes
                </div>
                <div id="el-notes-sub" class="meta-text" style="top: 288px; left: 74px;">Notes added<br>by you</div>

                <div id="el-sync-txt" class="meta-text" style="top: 272px; left: 156px; font-size: 10px;">sync</div>

                <div id="el-neondb" class="badge badge-white" style="top: 262px; left: 240px;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                  neon db
                </div>
                <div id="el-neondb-sub" class="meta-text" style="top: 288px; left: 240px;">Stores all notes</div>
                <div id="el-neondb-time" class="meta-text timestamp" style="top: 318px; left: 240px;">18:24:00</div>

                <div id="el-time-mid" class="meta-text timestamp" style="top: 224px; left: 410px;">19:08:12</div>

                <div id="el-grant-ico" class="circle-icon check-node" style="top: 298px; left: 625px;">✓</div>
                <div id="el-grant-txt" class="meta-text" style="top: 320px; left: 625px;">tools & data<br>access granted</div>

                <div id="el-time-right" class="meta-text timestamp" style="top: 298px; left: 743px;">20:32:04</div>

                <div id="el-ai-apps" class="badge badge-white" style="top: 262px; left: 918px;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"/></svg>
                  ai apps
                </div>
                <div id="el-ai-apps-sub" class="meta-text" style="top: 288px; left: 918px;">AI Agents / Apps</div>

                <!-- Center Bottom Protocol Negotiation Node -->
                <div id="el-proto-ico" class="circle-icon outline-node" style="top: 338px; left: 520px; width: 26px; height: 26px;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                </div>
                <div id="el-proto-txt" class="meta-text" style="top: 365px; left: 520px;">protocol<br>negotiation</div>

                <!-- Lower Flow Elements -->
                <div id="el-hollow-bot" class="circle-icon hollow-node" style="top: 334px; left: 918px;"></div>

                <div id="el-write" class="badge badge-dark" style="top: 380px; left: 830px;">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                  write note
                </div>

                <div id="el-proc-ico" class="circle-icon check-node" style="top: 440px; left: 625px;">✓</div>
                <div id="el-proc-txt" class="meta-text" style="top: 462px; left: 625px;">note processed<br>by mcp-server</div>

                <div id="el-saved-ico" class="circle-icon check-node" style="top: 440px; left: 265px;">✓</div>
                <div id="el-saved-txt" class="meta-text" style="top: 462px; left: 265px;">note saved<br>in neon db</div>

                <div id="el-sync-ico" class="circle-icon check-node" style="top: 440px; left: 76px;">✓</div>
                <div id="el-sync-bot-txt" class="meta-text" style="top: 462px; left: 76px;">sync<br>(auto / manual)</div>
              </div>
            </div>

            <!-- Embedding Exact Diagram Styles & Animation Controller -->
            <style>
              .diagram-container {{
                position: relative;
                width: 1000px;
                height: 524px;
                background-color: #000000;
                overflow: hidden;
              }}
              .vertical-grid {{
                position: absolute; inset: 0; display: flex; justify-content: space-between; padding: 0 35px; pointer-events: none; opacity: 0.12;
              }}
              .grid-line {{ width: 1px; height: 100%; background-color: #ffffff; }}
              svg.canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }}
              .line-green {{ stroke: #00e599; stroke-width: 1.5; fill: none; }}
              .line-green-dash {{ stroke: #00e599; stroke-width: 1.5; stroke-dasharray: 4 4; fill: none; }}
              .line-white-dash {{ stroke: #71767c; stroke-width: 1.5; stroke-dasharray: 4 4; fill: none; }}
              .line-white-solid {{ stroke: #71767c; stroke-width: 1.5; fill: none; }}
              .ruler-tick {{ stroke: #25282c; stroke-width: 1.5; transition: stroke 0.25s ease; }}
              .ruler-tick.lit {{ stroke: #00e599; }}
              .tick-active {{ stroke: #00e599; stroke-width: 1.5; }}
              .badge {{
                position: absolute; transform: translate(-50%, -50%) scale(0.65); display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 500; border-radius: 9999px; z-index: 2; user-select: none; white-space: nowrap; opacity: 0; filter: blur(3px);
                transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.35s ease;
              }}
              .badge.visible {{ opacity: 1; filter: blur(0px); transform: translate(-50%, -50%) scale(1); }}
              .badge-white {{ background: #ffffff; color: #000000; padding: 6px 14px; font-weight: 600; box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1); }}
              .badge-yellow {{ background: #fcee0a; color: #000000; padding: 7px 18px; font-weight: 700; font-size: 13px; box-shadow: 0 0 28px rgba(252, 238, 10, 0.45); }}
              .badge-dark {{ background: #25282e; color: #b1b8c0; border: 1px solid #383c44; padding: 5px 14px; font-size: 11.5px; }}
              .circle-icon {{
                position: absolute; transform: translate(-50%, -50%) scale(0.4); border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 2; opacity: 0;
                transition: opacity 0.35s ease, transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
              }}
              .circle-icon.visible {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
              .check-node {{ width: 15px; height: 15px; background: #00e599; color: #000000; font-size: 9px; font-weight: 900; box-shadow: 0 0 10px rgba(0, 229, 153, 0.7); }}
              .outline-node {{ width: 20px; height: 20px; border-radius: 50%; background: #0b0d10; border: 1px solid #30353c; color: #8b949e; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }}
              .hollow-node {{ width: 7px; height: 7px; background: #000000; border: 1.5px solid #00e599; border-radius: 50%; }}
              .meta-text {{
                position: absolute; transform: translateX(-50%); font-size: 9.5px; color: #7d8590; text-align: center; line-height: 1.35; pointer-events: none; z-index: 2; opacity: 0; transition: opacity 0.4s ease;
              }}
              .meta-text.visible {{ opacity: 1; }}
              .timestamp {{ font-size: 9.5px; color: #555d68; letter-spacing: 0.3px; }}
              .glow-dot {{ fill: #00e599; filter: url(#glow); opacity: 0; transition: opacity 0.2s ease; }}
              .glow-dot.active {{ opacity: 1; }}
            </style>
            <script>
              document.addEventListener('DOMContentLoaded', () => {{
                const allPaths = document.querySelectorAll('.diagram-container svg.canvas path:not(defs path)');
                const dot = document.getElementById('head-dot');
                if (!allPaths.length || !dot) return;

                function animateDraw(id, duration, delay = 0, ease = 'cubic-bezier(0.25, 1, 0.5, 1)', trackDot = false) {{
                  const p = document.getElementById(id);
                  if (!p) return;
                  const len = p.getTotalLength();
                  setTimeout(() => {{
                    p.style.transition = `stroke-dashoffset ${{duration}}s ${{ease}}`;
                    p.style.strokeDashoffset = '0';
                    if (trackDot) {{
                      dot.classList.add('active');
                      const start = performance.now();
                      function updateDot(time) {{
                        const progress = Math.min(1, (time - start) / (duration * 1000));
                        const point = p.getPointAtLength(progress * len);
                        dot.setAttribute('cx', point.x);
                        dot.setAttribute('cy', point.y);
                        if (progress < 1) requestAnimationFrame(updateDot);
                        else dot.classList.remove('active');
                      }}
                      requestAnimationFrame(updateDot);
                    }}
                  }}, delay * 1000);
                }}

                function reveal(id, delay) {{
                  setTimeout(() => {{
                    const el = document.getElementById(id);
                    if (el) el.classList.add('visible');
                  }}, delay * 1000);
                }}

                allPaths.forEach(path => {{
                  const len = path.getTotalLength();
                  path.style.strokeDasharray = `${{len}} ${{len}}`;
                  path.style.strokeDashoffset = len;
                }});

                reveal('el-notes', 0.1);
                reveal('el-notes-sub', 0.2);
                animateDraw('path-sync-arrow', 0.35, 0.3);
                reveal('el-sync-txt', 0.45);

                animateDraw('path-main', 2.0, 0.4, 'linear', true);

                document.querySelectorAll('.diagram-container #ticks line').forEach((tick, i) => {{
                  setTimeout(() => tick.classList.add('lit'), 400 + i * 75);
                }});

                reveal('el-neondb', 0.7);
                reveal('el-neondb-sub', 0.8);
                reveal('el-neondb-time', 0.9);

                animateDraw('path-db-up', 0.35, 0.95);
                reveal('el-db-ico', 1.15);
                animateDraw('path-req-data', 0.4, 1.25);
                reveal('el-req-data', 1.45);

                animateDraw('path-data-to-mcp', 0.5, 1.65);
                setTimeout(() => {{ const t19 = document.getElementById('tick-19'); if(t19) t19.style.opacity = '1'; }}, 1800);
                reveal('el-time-mid', 1.85);
                reveal('el-mcp', 2.05);

                animateDraw('path-neg-1', 0.35, 2.15);
                reveal('el-neg1-ico', 2.3);
                reveal('el-neg1-txt', 2.3);

                animateDraw('path-protocol', 0.4, 2.3);
                reveal('el-proto-ico', 2.55);
                reveal('el-proto-txt', 2.65);

                animateDraw('path-neg-2', 0.35, 2.75);
                reveal('el-neg2-ico', 2.9);
                reveal('el-neg2-txt', 2.9);

                animateDraw('path-granted', 0.4, 2.95);
                reveal('el-grant-ico', 3.25);
                reveal('el-grant-txt', 3.25);

                animateDraw('path-mcp-to-tools', 0.4, 2.95);
                reveal('el-req-tools', 3.25);
                animateDraw('path-tools-to-apps', 0.4, 3.45);
                reveal('el-bot-ico', 3.65);

                animateDraw('path-apps-down', 0.3, 3.75);
                reveal('el-hollow-top', 3.85);
                setTimeout(() => {{ const t20 = document.getElementById('tick-20'); if(t20) t20.style.opacity = '1'; }}, 3900);
                reveal('el-time-right', 3.95);
                reveal('el-ai-apps', 4.05);
                reveal('el-ai-apps-sub', 4.15);

                animateDraw('path-ai-to-note', 0.4, 4.25);
                reveal('el-hollow-bot', 4.45);
                reveal('el-write', 4.65);

                animateDraw('path-note-to-proc', 0.4, 4.85);
                reveal('el-proc-ico', 5.15);
                reveal('el-proc-txt', 5.25);

                animateDraw('path-lower-flow', 0.8, 5.35, 'linear');

                animateDraw('path-ret-db', 0.35, 6.05);
                reveal('el-saved-ico', 6.25);
                reveal('el-saved-txt', 6.25);

                animateDraw('path-ret-sync', 0.5, 6.45);
                reveal('el-sync-ico', 6.85);
                reveal('el-sync-bot-txt', 6.95);

                setTimeout(() => {{
                  document.querySelectorAll('.diagram-container .line-green-dash, .diagram-container .line-white-dash').forEach(p => {{
                    p.style.transition = 'none';
                    p.style.strokeDasharray = '4 4';
                    p.style.strokeDashoffset = '0';
                  }});
                }}, 7300);
              }});
            </script>
        </div>

    </div>
</section>

    <!-- Core Capabilities & Footer Showcase (Sticky Scroll Sections) -->
    <div class="showcase-container" style="font-family: 'Plus Jakarta Sans', sans-serif;">
      
      <div class="sticky-nav-wrapper">
        <nav class="sticky-sidebar" id="sidebar">
          <button class="menu-badge-btn" aria-hidden="true" tabindex="-1" style="background:#facc15; border:0; border-radius:12px; color:#000; padding:10px 18px; font-weight:800; font-size:13.5px; text-transform:uppercase; margin-bottom:20px;">CORE CAPABILITIES</button>
          <ul class="nav-list" style="list-style:none; display:flex; flex-direction:column; gap:12px; padding:0; margin:0;">
            <li>
              <a class="nav-btn active" data-target="trigram-search" style="display:flex; align-items:center; gap:10px; font-size:14.5px; font-weight:500; color:#71717a; text-decoration:none; cursor:pointer;">
                <span class="nav-dot"></span>Zero-Latency Trigram Search
              </a>
            </li>
            <li>
              <a class="nav-btn" data-target="ai-memory-sync" style="display:flex; align-items:center; gap:10px; font-size:14.5px; font-weight:500; color:#71717a; text-decoration:none; cursor:pointer;">
                <span class="nav-dot"></span>Autonomous AI Memory Sync
              </a>
            </li>
            <li>
              <a class="nav-btn" data-target="zen-canvas" style="display:flex; align-items:center; gap:10px; font-size:14.5px; font-weight:500; color:#71717a; text-decoration:none; cursor:pointer;">
                <span class="nav-dot"></span>Zen Canvas
              </a>
            </li>
            <li>
              <a class="nav-btn" data-target="non-linear" style="display:flex; align-items:center; gap:10px; font-size:14.5px; font-weight:500; color:#71717a; text-decoration:none; cursor:pointer;">
                <span class="nav-dot"></span>Non-Linear Connectivity
              </a>
            </li>
            <li>
              <a class="nav-btn" data-target="open-protocol" style="display:flex; align-items:center; gap:10px; font-size:14.5px; font-weight:500; color:#71717a; text-decoration:none; cursor:pointer;">
                <span class="nav-dot"></span>Open Protocol Standards
              </a>
            </li>
          </ul>
        </nav>
      </div>

      <section id="trigram-search" class="feature-section section-dark" data-theme="dark" style="width:100%; min-height:85vh; padding:90px 0; display:flex; align-items:center; background-color:#000000; color:#e2e8f0;">
        <div class="section-inner" style="max-width:1200px; margin:0 auto; padding:0 24px; width:100%; display:grid; grid-template-columns:260px 1fr; column-gap:56px;">
          <div class="section-content" style="grid-column:2; max-width:820px;">
            <h2 class="hero-heading" style="font-size:clamp(30px, 4vw, 48px); font-weight:800; letter-spacing:-0.035em; line-height:1.15; margin-bottom:20px; color:#ffffff;">Zero-Latency Trigram Search. Never miss a fragmented thought.</h2>
            <p class="lead-text" style="font-size:17px; line-height:1.6; margin-bottom:28px; color:#a1a1aa;">Memory Notes harnesses PostgreSQL trigram matching (<code>pg_trgm</code>) to fuzzy-match title and body content across workspaces in milliseconds.</p>
            
            <ul class="checklist" style="list-style:none; display:flex; flex-direction:column; gap:12px; margin-bottom:32px; padding:0;">
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Typo-tolerant substring & fuzzy similarity scoring</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Automatic fallback to ILIKE if extensions are missing</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Indexed lookups executing in under 4ms</li>
            </ul>

            <div class="terminal-box" style="background:#09090b; border:1px solid #27272a; border-radius:12px; overflow:hidden; font-family:'JetBrains Mono', monospace; max-width:740px; box-shadow:0 16px 36px -10px rgba(0, 0, 0, 0.7);">
              <div class="terminal-topbar" style="background:#18181b; padding:10px 16px; display:flex; align-items:center; gap:8px;">
                <div class="terminal-dots" style="display:flex; gap:6px;"><span class="dot-red" style="width:10px; height:10px; border-radius:50%; background:#ef4444;"></span><span class="dot-yellow" style="width:10px; height:10px; border-radius:50%; background:#eab308;"></span><span class="dot-green" style="width:10px; height:10px; border-radius:50%; background:#22c55e;"></span></div>
                <span class="terminal-title" style="font-size:12px; color:#a1a1aa; font-weight:500; margin-left:6px;">SQL Query Execution</span>
              </div>
              <div class="terminal-code" style="padding:20px; font-size:13.5px; color:#e4e4e7; overflow-x:auto; line-height:1.65;">
                <span style="color:#38bdf8;">SELECT</span> id, title, similarity(title, $1) <span style="color:#38bdf8;">AS</span> score <br>
                <span style="color:#38bdf8;">FROM</span> notes <br>
                <span style="color:#38bdf8;">WHERE</span> title % $1 <span style="color:#38bdf8;">OR</span> content <span style="color:#38bdf8;">ILIKE</span> <span style="color:#fbbf24;">'%'</span>||$1||<span style="color:#fbbf24;">'%'</span> <br>
                <span style="color:#38bdf8;">ORDER BY</span> score <span style="color:#38bdf8;">DESC LIMIT</span> 10;<br><br>
                <span style="color:#4ade80;">⚡ Query Execution: 3.4ms | 10 rows retrieved</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="ai-memory-sync" class="feature-section section-light" data-theme="light" style="width:100%; min-height:85vh; padding:90px 0; display:flex; align-items:center; background-color:#ffffff; color:#000000;">
        <div class="section-inner" style="max-width:1200px; margin:0 auto; padding:0 24px; width:100%; display:grid; grid-template-columns:260px 1fr; column-gap:56px;">
          <div class="section-content" style="grid-column:2; max-width:820px;">
            <h2 class="hero-heading" style="font-size:clamp(30px, 4vw, 48px); font-weight:800; letter-spacing:-0.035em; line-height:1.15; margin-bottom:20px; color:#000000;">Autonomous AI Memory Sync. Bi-directional writes from your agent.</h2>
            <p class="lead-text" style="font-size:17px; line-height:1.6; margin-bottom:28px; color:#52525b;">Claude and Cursor don't just inspect your past notes—they can create new workspace folders, append structured summaries, or update documents directly from prompt context.</p>
            
            <ul class="checklist" style="list-style:none; display:flex; flex-direction:column; gap:12px; margin-bottom:32px; padding:0;">
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#27272a;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Explicit bigint epoch timestamping for Last-Write-Wins (LWW)</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#27272a;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Reactive Jetpack Compose Room sync down to Android</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#27272a;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Automated schema compaction for continuous agent memory</li>
            </ul>

            <div class="terminal-box" style="background:#09090b; border:1px solid #27272a; border-radius:12px; overflow:hidden; font-family:'JetBrains Mono', monospace; max-width:740px; box-shadow:0 16px 36px -10px rgba(0, 0, 0, 0.7);">
              <div class="terminal-topbar" style="background:#18181b; padding:10px 16px; display:flex; align-items:center; gap:8px;">
                <div class="terminal-dots" style="display:flex; gap:6px;"><span class="dot-red" style="width:10px; height:10px; border-radius:50%; background:#ef4444;"></span><span class="dot-yellow" style="width:10px; height:10px; border-radius:50%; background:#eab308;"></span><span class="dot-green" style="width:10px; height:10px; border-radius:50%; background:#22c55e;"></span></div>
                <span class="terminal-title" style="font-size:12px; color:#a1a1aa; font-weight:500; margin-left:6px;">MCP Tool Invocation Output</span>
              </div>
              <div class="terminal-code" style="padding:20px; font-size:13.5px; color:#e4e4e7; overflow-x:auto; line-height:1.65;">
                <span style="color:#71717a;">> create_note( title="Sprint Specs", workspace="Dev" )</span><br>
                {<br>
                &nbsp;&nbsp;<span style="color:#38bdf8;">"id"</span>: <span style="color:#fbbf24;">"9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"</span>,<br>
                &nbsp;&nbsp;<span style="color:#38bdf8;">"title"</span>: <span style="color:#fbbf24;">"Sprint Specs"</span>,<br>
                &nbsp;&nbsp;<span style="color:#38bdf8;">"updated_at"</span>: 1786675973594<br>
                }<br><br>
                <span style="color:#4ade80;">✓ Database record created • Dispatched to mobile sync engine</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="zen-canvas" class="feature-section section-dark" data-theme="dark" style="width:100%; min-height:85vh; padding:90px 0; display:flex; align-items:center; background-color:#000000; color:#e2e8f0;">
        <div class="section-inner" style="max-width:1200px; margin:0 auto; padding:0 24px; width:100%; display:grid; grid-template-columns:260px 1fr; column-gap:56px;">
          <div class="section-content" style="grid-column:2; max-width:820px;">
            <h2 class="hero-heading" style="font-size:clamp(30px, 4vw, 48px); font-weight:800; letter-spacing:-0.035em; line-height:1.15; margin-bottom:20px; color:#ffffff;">Zen Canvas. Distraction-free writing surface.</h2>
            <p class="lead-text" style="font-size:17px; line-height:1.6; margin-bottom:28px; color:#a1a1aa;">A writing environment that strips away the superfluous, centering your thoughts and fading interface clutter away during deep focus.</p>
            
            <ul class="checklist" style="list-style:none; display:flex; flex-direction:column; gap:12px; margin-bottom:32px; padding:0;">
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Clean Markdown canvas with zero UI distraction</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Full keyboard-first command palette navigation</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Instant local-first caching for zero-latency typing</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="non-linear" class="feature-section section-light" data-theme="light" style="width:100%; min-height:85vh; padding:90px 0; display:flex; align-items:center; background-color:#ffffff; color:#000000;">
        <div class="section-inner" style="max-width:1200px; margin:0 auto; padding:0 24px; width:100%; display:grid; grid-template-columns:260px 1fr; column-gap:56px;">
          <div class="section-content" style="grid-column:2; max-width:820px;">
            <h2 class="hero-heading" style="font-size:clamp(30px, 4vw, 48px); font-weight:800; letter-spacing:-0.035em; line-height:1.15; margin-bottom:20px; color:#000000;">Non-Linear Connectivity. An interconnected web of knowledge.</h2>
            <p class="lead-text" style="font-size:17px; line-height:1.6; margin-bottom:28px; color:#52525b;">Link thoughts effortlessly with bi-directional wikilinks to visualize complex patterns, relationships, and emergent ideas.</p>
            
            <ul class="checklist" style="list-style:none; display:flex; flex-direction:column; gap:12px; margin-bottom:32px; padding:0;">
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#27272a;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Bi-directional backlinks and automatic connection mapping</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#27272a;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Interactive visual node graph for complex mental models</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#27272a;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Dynamic workspace clustering by topic and reference</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="open-protocol" class="feature-section section-dark" data-theme="dark" style="width:100%; min-height:85vh; padding:90px 0; display:flex; align-items:center; background-color:#000000; color:#e2e8f0;">
        <div class="section-inner" style="max-width:1200px; margin:0 auto; padding:0 24px; width:100%; display:grid; grid-template-columns:260px 1fr; column-gap:56px;">
          <div class="section-content" style="grid-column:2; max-width:820px;">
            <h2 class="hero-heading" style="font-size:clamp(30px, 4vw, 48px); font-weight:800; letter-spacing:-0.035em; line-height:1.15; margin-bottom:20px; color:#ffffff;">Open Protocol Standards. Zero lock-in, complete control.</h2>
            <p class="lead-text" style="font-size:17px; line-height:1.6; margin-bottom:28px; color:#a1a1aa;">Built directly on Anthropic's Model Context Protocol (MCP) and Starlette ASGI for developer independence and easy tooling integrations.</p>
            
            <ul class="checklist" style="list-style:none; display:flex; flex-direction:column; gap:12px; margin-bottom:32px; padding:0;">
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Server runtime powered by FastMCP and Python 3.12</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Streamable HTTP with Server-Sent Events (SSE)</li>
              <li style="display:flex; align-items:flex-start; gap:10px; font-size:15px; font-weight:600; color:#d4d4d8;"><span class="check-icon" style="color:#00e599; font-weight:800;">✓</span> Multi-tenant isolation with portable data export</li>
            </ul>
          </div>
        </div>
      </section>

    </div>

    <!-- Footer -->
    <footer class="neon-footer" style="background-color:#F5F5F5; border-top:1px solid #e5e5e5; color:#52525b; padding:80px 24px 48px; position:relative; z-index:30;">
      <div class="footer-container" style="max-width:1200px; margin:0 auto;">
        <div class="footer-top" style="display:grid; grid-template-columns:2fr repeat(4, 1fr); gap:48px; margin-bottom:64px;">
          
          <div class="footer-brand" style="display:flex; flex-direction:column; gap:16px;">
            <a href="/" class="footer-logo" style="display:inline-flex; align-items:center; gap:10px; text-decoration:none; color:#18181b; font-weight:800; font-size:20px;">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:24px; height:24px;">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#facc15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="#facc15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="#facc15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>Memory Notes</span>
            </a>
            <p class="footer-tagline" style="font-size:14px; color:#71717a; max-width:270px; line-height:1.5;">Structured freedom for your thoughts. A private notes application and long-term memory bridge for Claude, Cursor, and custom AI agents.</p>
            <a href="#" class="status-badge" style="display:inline-flex; align-items:center; gap:8px; width:fit-content; margin-top:8px; padding:6px 12px; border-radius:9999px; background:#ffffff; border:1px solid #e4e4e7; color:#3f3f46; font-size:12px; font-weight:600; text-decoration:none;">
              <span class="status-dot" style="width:6px; height:6px; border-radius:50%; background-color:#16a34a; box-shadow:0 0 8px #16a34a;"></span>
              MCP Gateway Connected
            </a>
          </div>

          <div class="footer-col">
            <h4 style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#18181b; margin-bottom:20px;">Product</h4>
            <ul style="list-style:none; display:flex; flex-direction:column; gap:12px; padding:0; margin:0;">
              <li><a href="#trigram-search" style="color:#71717a; text-decoration:none; font-size:14px;">Trigram Fuzzy Search</a></li>
              <li><a href="#ai-memory-sync" style="color:#71717a; text-decoration:none; font-size:14px;">Autonomous AI Sync</a></li>
              <li><a href="#zen-canvas" style="color:#71717a; text-decoration:none; font-size:14px;">Zen Canvas</a></li>
              <li><a href="#non-linear" style="color:#71717a; text-decoration:none; font-size:14px;">Graph Connectivity</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4 style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#18181b; margin-bottom:20px;">Resources</h4>
            <ul style="list-style:none; display:flex; flex-direction:column; gap:12px; padding:0; margin:0;">
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">MCP Protocol Guide</a></li>
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">Cursor Setup</a></li>
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">Claude Desktop Integration</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4 style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#18181b; margin-bottom:20px;">Developers</h4>
            <ul style="list-style:none; display:flex; flex-direction:column; gap:12px; padding:0; margin:0;">
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">FastMCP Starlette ASGI</a></li>
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">SSE Stream Handshakes</a></li>
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">Android Room Schema</a></li>
            </ul>
          </div>

          <div class="footer-col">
            <h4 style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#18181b; margin-bottom:20px;">Platform</h4>
            <ul style="list-style:none; display:flex; flex-direction:column; gap:12px; padding:0; margin:0;">
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">About</a></li>
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">Changelog</a></li>
              <li><a href="#" style="color:#71717a; text-decoration:none; font-size:14px;">Privacy Policy</a></li>
            </ul>
          </div>

        </div>

        <div class="footer-bottom" style="border-top:1px solid #e5e5e5; padding-top:32px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:20px; font-size:13px; color:#71717a;">
          <div>&copy; 2026 Memory Notes. Structured Freedom.</div>

          <div class="footer-bottom-links" style="display:flex; align-items:center; gap:24px;">
            <a href="#" style="color:#71717a; text-decoration:none;">Privacy Policy</a>
            <a href="#" style="color:#71717a; text-decoration:none;">Terms of Service</a>
            <a href="#" style="color:#71717a; text-decoration:none;">Security</a>
          </div>
        </div>
      </div>
    </footer>

    <script>
      const navButtons = document.querySelectorAll('.nav-btn');
      const sections = document.querySelectorAll('.feature-section');
      const sidebar = document.getElementById('sidebar');

      function syncActiveNav() {{
        const focalLine = window.innerHeight * 0.4;
        let currentSection = sections[0];

        sections.forEach((section) => {{
          const rect = section.getBoundingClientRect();
          if (rect.top <= focalLine && rect.bottom >= focalLine) {{
            currentSection = section;
          }}
        }});

        navButtons.forEach((btn) => {{
          btn.classList.toggle('active', btn.dataset.target === currentSection.id);
        }});

        const theme = currentSection.getAttribute('data-theme');
        if (theme === 'light') {{
          sidebar.classList.add('theme-light');
        }} else {{
          sidebar.classList.remove('theme-light');
        }}
      }}

      window.addEventListener('scroll', syncActiveNav, {{ passive: true }});
      window.addEventListener('resize', syncActiveNav);
      syncActiveNav();

      navButtons.forEach((btn) => {{
        btn.addEventListener('click', (e) => {{
          e.preventDefault();
          const target = document.getElementById(btn.dataset.target);
          if (target) {{
            target.scrollIntoView({{ behavior: 'smooth' }});
          }}
        }});
      }});
    </script>
""")
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
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Create Your Account</h2>
        <p class="text-xs text-text-secondary mb-6">Set up your Memory Notes gateway account.</p>
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
<main class="flex-grow flex items-center justify-center py-16 px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-8 rounded-xl shadow-sm">
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
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-sm font-semibold border border-[#050505]">Sign Up</button>
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
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Create Your Account</h2>
        <div class="p-3 bg-red-50 text-red-700 text-xs rounded mb-4 border border-red-200">An account with that email already exists.</div>
        <p class="text-xs"><a href="/login?next={next_}" class="text-primary font-semibold underline">Log in instead</a></p>
    </div>
</main>
"""
        return _page("Sign up", body)

    request.session["user_id"] = user_id
    return RedirectResponse("/console", status_code=302)


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
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-8 rounded-xl shadow-sm">
        <h2 class="text-2xl font-bold text-on-surface mb-1">Welcome Back</h2>
        <p class="text-xs text-text-secondary mb-6">Log in to your account.</p>
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
<main class="flex-grow flex items-center justify-center py-16 px-6">
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
            <button type="submit" class="w-full bg-secondary-container text-on-surface py-3 rounded text-sm font-semibold border border-[#050505]">Log In</button>
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
# Console Page (Custom Codebase Manager 2D Node Canvas UI)
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
                    SELECT id, sequence_index, title, summary, rationale, impact_analysis, affected_components, status, created_at
                    FROM project_nodes
                    WHERE workspace = $1 AND node_type = 'codebase_change'
                    ORDER BY sequence_index ASC
                    """,
                    selected_workspace
                )
                nodes = [dict(r) for r in node_rows]
        except Exception:
            pass

    if workspaces:
        repo_list_html = "".join(f"""
            <li class="chat-item {'active' if ws == selected_workspace else ''}" onclick="window.location='/console?ws={ws}'">
                📁 {ws}
            </li>
        """ for ws in workspaces)
    else:
        repo_list_html = '<div class="p-3 text-xs text-[#8e8e8e]">No repositories found. Connect MCP to Claude/Cursor to log changes.</div>'

    if selected_workspace:
        if nodes:
            nodes_html = ""
            svg_lines_html = ""
            card_width = 240
            card_height = 140
            spacing_x = 320
            start_x = 80
            start_y = 180

            for i, node in enumerate(nodes):
                x = start_x + (i * spacing_x)
                y = start_y + (60 if i % 2 == 1 else -40)
                
                if i > 0:
                    prev_x = start_x + ((i - 1) * spacing_x) + (card_width / 2)
                    prev_y = start_y + (60 if (i - 1) % 2 == 1 else -40) + (card_height / 2)
                    curr_cx = x + (card_width / 2)
                    curr_cy = y + (card_height / 2)
                    svg_lines_html += f'<line x1="{prev_x}" y1="{prev_y}" x2="{curr_cx}" y2="{curr_cy}" stroke="#52525b" stroke-width="2" stroke-dasharray="4 4" />'

                title_esc = node['title'].replace('"', '&quot;')
                summary_esc = node['summary'].replace('"', '&quot;')
                why_esc = (node['rationale'] or 'No rationale provided').replace('"', '&quot;')
                impact_esc = (node['impact_analysis'] or 'None').replace('"', '&quot;')
                step_idx = node['sequence_index'] or (i + 1)

                nodes_html += f"""
                <div class="canvas-node" style="left: {x}px; top: {y}px; width: {card_width}px;" 
                     ondblclick="openNodeModal('Step {step_idx}: {title_esc}', '{summary_esc}', '{why_esc}', '{impact_esc}')">
                    <div class="node-header">
                        <span class="node-step">Step {step_idx}</span>
                        <span class="node-status">✓</span>
                    </div>
                    <div class="node-title">{node['title']}</div>
                    <div class="node-snippet">{node['summary'][:90]}...</div>
                    <div class="node-footer">Double-click to expand note</div>
                </div>
                """
            
            canvas_content = f"""
            <svg class="canvas-svg">{svg_lines_html}</svg>
            {nodes_html}
            """
        else:
            canvas_content = f"""
            <div class="empty-canvas-state">
                <div class="empty-icon">⚡</div>
                <h3>No CodeBase Data</h3>
                <p>No CodeBase Data Connect mcp to AI models and store CodeBase Logs</p>
                <code>mcpServers -&gt; memory-notes</code>
            </div>
            """
    else:
        canvas_content = f"""
        <div class="empty-canvas-state">
            <div class="empty-icon">📁</div>
            <h3>Manage Code Base</h3>
            <p>Select a codebase from the sidebar to view its architecture nodes and logs.</p>
        </div>
        """

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Console - Codebase Manager</title>
<style>
:root {{
  --sidebar-bg: #171717;
  --text-main: #ececec;
  --text-muted: #8e8e8e;
  --hover-bg: rgba(255, 255, 255, 0.05);
  --border-color: rgba(255, 255, 255, 0.08);
}}

body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  height: 100vh;
  overflow: hidden;
}}

.container {{
  width: 100%;
  height: 100%;
  --color: #E1E1E1;
  background-color: #F3F3F3;
  background-image: linear-gradient(0deg, transparent 24%, var(--color) 25%, var(--color) 26%, transparent 27%, transparent 74%, var(--color) 75%, var(--color) 76%, transparent 77%, transparent),
      linear-gradient(90deg, transparent 24%, var(--color) 25%, var(--color) 26%, transparent 27%, transparent 74%, var(--color) 75%, var(--color) 76%, transparent 77%, transparent);
  background-size: 55px 55px;
  display: flex;
}}

#sidebar-toggle {{ display: none; }}

.toggle-btn {{
  background: black;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}}

.floating-toggle {{
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 10;
  display: none;
}}

#sidebar-toggle:checked ~ .floating-toggle {{ display: flex; }}

.sidebar {{
  width: 260px;
  background-color: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
  padding: 12px;
  z-index: 5;
  transition: transform 0.3s ease, width 0.3s ease;
}}

#sidebar-toggle:checked ~ .sidebar {{
  transform: translateX(-100%);
  width: 0;
  padding: 0;
  overflow: hidden;
}}

.sidebar-header {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 4px;
}}

.sidebar-brand {{ font-size: 14px; font-weight: 600; color: var(--text-main); }}
.sidebar-section-title {{ font-size: 12px; font-weight: 500; color: var(--text-muted); padding: 8px 12px; }}

.chat-list {{
  flex: 1;
  overflow-y: auto;
  list-style: none;
  padding: 0;
  margin: 0;
}}

.chat-item {{
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.2s ease, color 0.2s;
}}
.chat-item:hover, .chat-item.active {{
  background-color: var(--hover-bg);
  color: var(--text-main);
}}

.sidebar-footer {{
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
}}

.user-profile {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
}}

.user-info {{ display: flex; align-items: center; gap: 10px; font-size: 14px; }}
.user-name {{ color: white; }}
.avatar {{
  width: 24px; height: 24px; background-color: #3b82f6; color: white;
  border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;
}}
.plan-badge {{ font-size: 11px; color: var(--text-muted); }}

.logout-btn {{
  all: unset; color: #f87171; font-size: 12px; cursor: pointer; padding: 4px 12px; display: block;
}}
.logout-btn:hover {{ text-decoration: underline; }}

/* 2D Interactive Canvas Area */
.main-canvas {{
  flex: 1;
  position: relative;
  overflow: auto;
  cursor: grab;
  background: transparent;
}}
.main-canvas:active {{ cursor: grabbing; }}

.canvas-svg {{
  position: absolute;
  top: 0; left: 0;
  width: 5000px; height: 5000px;
  pointer-events: none;
}}

.canvas-node {{
  position: absolute;
  background: #ffffff;
  border: 1px solid #d4d4d8;
  border-radius: 8px;
  padding: 14px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  user-select: none;
}}
.canvas-node:hover {{
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  border-color: #000000;
}}
.node-header {{
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
}}
.node-step {{
  font-size: 10px; font-family: monospace; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #475569; font-weight: 600;
}}
.node-status {{ color: #16a34a; font-size: 12px; }}
.node-title {{ font-size: 13px; font-weight: 700; color: #09090b; margin-bottom: 4px; }}
.node-snippet {{ font-size: 11px; color: #71717a; line-height: 1.4; }}
.node-footer {{
  margin-top: 10px; padding-top: 6px; border-top: 1px solid #f1f5f9; font-size: 10px; color: #0284c7; text-align: right;
}}

/* Empty State */
.empty-canvas-state {{
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  text-align: center; max-width: 380px; background: white; border: 1px solid #e2e2e7; padding: 32px; border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.04);
}}
.empty-icon {{ font-size: 32px; margin-bottom: 12px; }}
.empty-canvas-state h3 {{ font-size: 16px; font-weight: bold; margin: 0 0 8px 0; color: #111; }}
.empty-canvas-state p {{ font-size: 12px; color: #666; line-height: 1.5; margin: 0 0 16px 0; }}
.empty-canvas-state code {{ display: block; background: #f4f4f5; padding: 8px; border-radius: 6px; font-family: monospace; font-size: 11px; color: #333; }}

/* Modal Popup for Node Details */
.modal-overlay {{
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 100; align-items: center; justify-content: center;
}}
.modal-overlay.active {{ display: flex; }}
.modal-card {{
  background: white; width: 500px; max-width: 90%; border-radius: 12px; border: 1px solid #e4e4e7; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); padding: 24px; position: relative;
}}
.modal-close {{
  position: absolute; top: 16px; right: 16px; background: none; border: none; font-size: 18px; cursor: pointer; color: #71717a;
}}
.modal-title {{ font-size: 16px; font-weight: bold; margin-bottom: 12px; color: #18181b; }}
.modal-section {{ margin-bottom: 12px; }}
.modal-label {{ font-size: 11px; font-weight: bold; text-transform: uppercase; color: #71717a; margin-bottom: 4px; }}
.modal-body {{ font-size: 13px; color: #3f3f46; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; line-height: 1.5; }}
</style>
</head>
<body>
<div class="container">
  <input type="checkbox" id="sidebar-toggle" />

  <aside class="sidebar">
    <div class="sidebar-header">
      <label for="sidebar-toggle" class="toggle-btn" title="Toggle Sidebar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="9" y1="3" x2="9" y2="21"></line>
        </svg>
      </label>
      <span class="sidebar-brand">Codebase Vault</span>
    </div>

    <div class="sidebar-section-title">Repositories &amp; Codebases</div>
    <ul class="chat-list">
      <li class="chat-item" style="border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:6px; padding-bottom:6px;">
        <a href="/dashboard" style="color:inherit; text-decoration:none;">⚙️ Database & Settings</a>
      </li>
      {repo_list_html}
    </ul>

    <div class="sidebar-footer">
      <div class="user-profile">
        <div class="user-info">
          <div class="avatar">{initial}</div>
          <span class="user-name">{display_name}</span>
        </div>
        <span class="plan-badge">MCP Active</span>
      </div>
      <form method="POST" action="/logout" style="margin-top:8px;">
        <button type="submit" class="logout-btn">Log Out</button>
      </form>
    </div>
  </aside>

  <label for="sidebar-toggle" class="toggle-btn floating-toggle" title="Toggle Sidebar">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
      <line x1="9" y1="3" x2="9" y2="21"></line>
    </svg>
  </label>

  <main class="main-canvas" id="canvasArea">
    {canvas_content}
  </main>
</div>

<!-- Node Details Modal -->
<div id="nodeModal" class="modal-overlay" onclick="closeNodeModal(event)">
  <div class="modal-card" onclick="event.stopPropagation()">
    <button class="modal-close" onclick="closeNodeModalDirect()">×</button>
    <div id="modalTitle" class="modal-title">Node Details</div>
    
    <div class="modal-section">
      <div class="modal-label">What Changed (Summary)</div>
      <div id="modalSummary" class="modal-body"></div>
    </div>

    <div class="modal-section">
      <div class="modal-label">Why (Rationale)</div>
      <div id="modalRationale" class="modal-body"></div>
    </div>

    <div class="modal-section">
      <div class="modal-label">Project Impact Analysis</div>
      <div id="modalImpact" class="modal-body"></div>
    </div>
  </div>
</div>

<script>
  const canvas = document.getElementById('canvasArea');
  let isDragging = false;
  let startX, startY, scrollLeft, scrollTop;

  canvas.addEventListener('mousedown', (e) => {{
    if(e.target.closest('.canvas-node')) return;
    isDragging = true;
    startX = e.pageX - canvas.offsetLeft;
    startY = e.pageY - canvas.offsetTop;
    scrollLeft = canvas.scrollLeft;
    scrollTop = canvas.scrollTop;
  }});

  canvas.addEventListener('mouseleave', () => {{ isDragging = false; }});
  canvas.addEventListener('mouseup', () => {{ isDragging = false; }});
  canvas.addEventListener('mousemove', (e) => {{
    if(!isDragging) return;
    e.preventDefault();
    const x = e.pageX - canvas.offsetLeft;
    const y = e.pageY - canvas.offsetTop;
    canvas.scrollLeft = scrollLeft - (x - startX);
    canvas.scrollTop = scrollTop - (y - startY);
  }});

  function openNodeModal(title, summary, rationale, impact) {{
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalSummary').innerText = summary;
    document.getElementById('modalRationale').innerText = rationale;
    document.getElementById('modalImpact').innerText = impact;
    document.getElementById('nodeModal').classList.add('active');
  }}

  function closeNodeModalDirect() {{
    document.getElementById('nodeModal').classList.remove('active');
  }}

  function closeNodeModal(e) {{
    if(e.target.id === 'nodeModal') {{
      document.getElementById('nodeModal').classList.remove('active');
    }}
  }}
</script>
</body>
</html>
""")


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
    <strong class="text-xs uppercase font-mono text-primary block mb-1">New API Key (Shown Once — Copy Now):</strong>
    <div class="flex items-center gap-2 mt-2">
        <input type="text" readonly value="{flash_key}" id="newApiKeyField" class="w-full font-mono text-xs bg-surface-white border border-border-muted p-2 rounded">
        <button id="btnCopyKey" onclick="copyToClipboard('{flash_key}', 'btnCopyKey')" class="bg-secondary-container text-on-surface px-4 py-2 rounded text-xs font-semibold whitespace-nowrap border border-[#050505]">Copy</button>
    </div>
    <p class="text-xs text-text-secondary mt-2">Use this as your Bearer Token for Claude or direct API configurations.</p>
</div>
"""

    if user["connection_string_encrypted"]:
        masked = security.mask_connection_string(security.decrypt_text(user["connection_string_encrypted"]))
        conn_status = f'<p class="text-xs text-text-secondary">Currently linked: <code class="text-on-surface font-mono">{masked}</code></p>'
    else:
        conn_status = '<div class="p-3 bg-red-50 text-red-700 text-xs rounded border border-red-200">No Neon connection string set yet. Claude connector will fail until configured.</div>'

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
                <h1 class="text-2xl font-bold text-on-surface mb-1">Database & API Settings</h1>
                <p class="text-xs text-text-secondary">Manage your Neon database connection string and MCP API keys.</p>
            </div>
            <a href="/console" class="text-xs font-semibold text-primary underline">← Back to Console</a>
        </div>

        {flash_html}

        <!-- 1. Endpoint & Connection URL -->
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl mb-6 shadow-sm">
            <h2 class="text-base font-semibold text-on-surface mb-1">1. MCP Server Endpoint</h2>
            <p class="text-xs text-text-secondary mb-3">Provide this URL when configuring your Claude Desktop or HTTP MCP client connector.</p>
            <div class="flex items-center gap-2">
                <input type="text" readonly value="{mcp_endpoint}" id="mcpEndpointField" class="w-full font-mono text-xs bg-surface-container-low border border-border-muted p-2.5 rounded">
                <button id="btnCopyEndpoint" onclick="copyToClipboard('{mcp_endpoint}', 'btnCopyEndpoint')" class="bg-surface-white text-on-surface px-4 py-2.5 rounded text-xs font-semibold whitespace-nowrap border border-[#050505]">Copy URL</button>
            </div>
        </div>

        <!-- 2. Neon Database Connection String Settings -->
        <div class="bg-surface-white border border-border-muted p-6 rounded-xl mb-6 shadow-sm">
            <h2 class="text-base font-semibold text-on-surface mb-1">2. Neon Database Connection String</h2>
            <p class="text-xs text-text-secondary mb-3">Paste the same PostgreSQL connection string your mobile notes app uses to sync.</p>
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
            <h2 class="text-base font-semibold text-on-surface mb-1">3. MCP API Keys</h2>
            <p class="text-xs text-text-secondary mb-3">API keys are generated automatically through Claude OAuth, or you can create them manually for custom apps.</p>
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
        return RedirectResponse(("/login"), status_code=302)

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
]
