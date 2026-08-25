"""
Memory Notes for AI - Web Application
Features Neon-style interactive animated pipeline architecture:
1. Android App -> Neon DB sync
2. AI Apps -> FastMCP Server requests
3. FastMCP -> Neon DB context retrieval & streaming
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
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@600;700&amp;family=Inter:wght@400;500;600;700&amp;family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {{
            darkMode: "class",
            theme: {{
                extend: {{
                    "colors": {{
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
                    "borderRadius": {{
                        "DEFAULT": "0.125rem",
                        "lg": "0.25rem",
                        "xl": "0.5rem",
                        "full": "0.75rem"
                    }},
                    "fontFamily": {{
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

        /* Neon Animated Timeline Lines */
        .pipeline-line {{
            transition: stroke-dashoffset 0.8s ease-in-out, opacity 0.4s ease, stroke 0.4s ease;
        }}
        .pulse-node {{
            transition: transform 0.3s ease, fill 0.3s ease, stroke 0.3s ease;
        }}
        .pill-badge {{
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease, border-color 0.3s ease;
        }}
        .pill-badge.active-badge {{
            transform: translateY(-2px) scale(1.04);
            box-shadow: 0 0 20px rgba(0, 229, 153, 0.4);
            border-color: #00e599 !important;
        }}

        @keyframes beamFlow {{
            to {{ stroke-dashoffset: -30; }}
        }}
        .flow-active {{
            stroke-dasharray: 6 6;
            animation: beamFlow 1s linear infinite;
        }}

        .feature-card {{
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border-color: #050505;
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

    // ==========================================
    // NEON-STYLE ANIMATED PIPELINE LOGIC
    // ==========================================
    let currentStep = 1;
    let autoPlay = true;
    let animTimer = null;

    function setPipelineStep(step, manual = false) {{
        if (manual) {{
            autoPlay = false;
            document.getElementById('playPauseBtn').innerText = '▶ Play';
        }}
        currentStep = step;

        // Update Controller Buttons
        [1, 2, 3].forEach(s => {{
            const btn = document.getElementById('step-btn-' + s);
            if (s === step) {{
                btn.className = 'px-3.5 py-1.5 rounded-lg border border-[#00e599] bg-[#00e599]/10 text-[#00e599] mono text-xs font-semibold shadow-[0_0_10px_rgba(0,229,153,0.2)] transition-all';
            }} else {{
                btn.className = 'px-3.5 py-1.5 rounded-lg border border-white/10 bg-white/5 text-white/50 hover:text-white mono text-xs font-medium transition-all';
            }}
        }});

        // Badges & Paths references
        const p1 = document.getElementById('path-android-neon');
        const p2a = document.getElementById('path-ai-claude');
        const p2b = document.getElementById('path-ai-chatgpt');
        const p3 = document.getElementById('path-mcp-neon-broker');

        const badgeAndroid = document.getElementById('badge-android');
        const badgeNeon = document.getElementById('badge-neon');
        const badgeMcp = document.getElementById('badge-mcp');
        const badgeClaude = document.getElementById('badge-claude');
        const badgeGpt = document.getElementById('badge-gpt');
        const statusText = document.getElementById('pipeline-status-text');

        // Reset active highlights
        [badgeAndroid, badgeNeon, badgeMcp, badgeClaude, badgeGpt].forEach(b => b.classList.remove('active-badge'));

        if (step === 1) {{
            // 1. Android Note Creation & Sync to Neon DB
            p1.setAttribute('stroke', '#00e599');
            p1.setAttribute('stroke-width', '2.5');
            p1.classList.add('flow-active');

            p2a.classList.remove('flow-active');
            p2a.setAttribute('stroke', '#27272a');
            p2b.classList.remove('flow-active');
            p2b.setAttribute('stroke', '#27272a');

            p3.classList.remove('flow-active');
            p3.setAttribute('stroke', '#27272a');

            badgeAndroid.classList.add('active-badge');
            badgeNeon.classList.add('active-badge');
            statusText.innerHTML = '<span class="text-[#00e599]">Step 1:</span> Note created in Android app &rarr; Synced with epoch timestamp to Neon Postgres.';
        }} 
        else if (step === 2) {{
            // 2. AI Apps send tool request to MCP Broker
            p1.classList.remove('flow-active');
            p1.setAttribute('stroke', '#00e599');
            p1.setAttribute('stroke-width', '1.5');

            p2a.classList.add('flow-active');
            p2a.setAttribute('stroke', '#f5c14e');
            p2a.setAttribute('stroke-width', '2.2');

            p2b.classList.add('flow-active');
            p2b.setAttribute('stroke', '#22d3ee');
            p2b.setAttribute('stroke-width', '2.2');

            p3.classList.remove('flow-active');
            p3.setAttribute('stroke', '#27272a');

            badgeClaude.classList.add('active-badge');
            badgeGpt.classList.add('active-badge');
            badgeMcp.classList.add('active-badge');
            statusText.innerHTML = '<span class="text-[#f5c14e]">Step 2:</span> Claude & Cursor trigger tool calls (<code class="text-white">search_notes</code>) &rarr; Received by FastMCP Server.';
        }} 
        else if (step === 3) {{
            // 3. FastMCP pulls context from Neon DB & streams to AI
            p1.classList.remove('flow-active');
            p1.setAttribute('stroke', '#00e599');

            p2a.classList.add('flow-active');
            p2a.setAttribute('stroke', '#00e599');
            p2b.classList.add('flow-active');
            p2b.setAttribute('stroke', '#00e599');

            p3.classList.add('flow-active');
            p3.setAttribute('stroke', '#00e599');
            p3.setAttribute('stroke-width', '3');

            badgeMcp.classList.add('active-badge');
            badgeNeon.classList.add('active-badge');
            badgeClaude.classList.add('active-badge');
            badgeGpt.classList.add('active-badge');
            statusText.innerHTML = '<span class="text-[#00e599]">Step 3:</span> FastMCP retrieves fuzzy trigram context from Neon DB &rarr; Streams payload directly into LLM context window.';
        }}
    }}

    function toggleAutoPlay() {{
        autoPlay = !autoPlay;
        document.getElementById('playPauseBtn').innerText = autoPlay ? '⏸ Pause' : '▶ Play';
    }}

    function runPipelineLoop() {{
        if (autoPlay) {{
            currentStep = (currentStep % 3) + 1;
            setPipelineStep(currentStep, false);
        }}
    }}

    document.addEventListener('DOMContentLoaded', () => {{
        setPipelineStep(1, false);
        animTimer = setInterval(runPipelineLoop, 3200);
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
            <div onclick="toggleSettings()" class="w-8 h-8 rounded-full bg-surface-dim overflow-hidden border border-border-muted cursor-pointer flex items-center justify-center font-bold text-xs select-none hover:border-black transition-colors">
                {initial}
            </div>
            <div id="settingsDropdown" class="settings-dropdown">
                <div class="font-bold text-sm text-on-surface mb-1">Signed in as</div>
                <div class="text-xs text-text-secondary truncate mb-3">{user_email}</div>
                <hr class="border-border-muted mb-3">
                <a href="/dashboard" class="block text-sm text-on-surface py-1.5 hover:text-primary font-semibold transition-colors">⚙️ Dashboard & Settings</a>
                <form method="POST" action="/logout" class="mt-2">
                    <button type="submit" class="w-full text-left text-sm text-error py-1.5 hover:opacity-80 transition-opacity">Log Out</button>
                </form>
            </div>
        </div>
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
                    <a href="{' /dashboard' if user_id else '/signup'}" class="bg-secondary-container text-on-surface px-6 py-3 text-sm font-semibold border-b-2 border-r-2 border-[#050505] active:translate-y-[1px] active:translate-x-[1px] transition-all inline-block no-underline shadow-sm">Start Writing Now</a>
                    <a href="#quickstart" class="bg-surface-white text-on-surface px-6 py-3 text-sm font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors inline-block no-underline shadow-sm">Try in 30 Seconds</a>
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

    <!-- ========================================================================= -->
    <!-- 2. NEON-STYLE LIVE ARCHITECTURE PIPELINE CANVAS -->
    <!-- ========================================================================= -->
    <section class="py-20 bg-[#050505] text-white border-b border-neutral-800">
        <div class="max-w-6xl mx-auto px-6 lg:px-12">
            
            <!-- Section Header & Interactive Controls -->
            <div class="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6 mb-8">
                <div>
                    <p class="mono text-[11px] tracking-[0.2em] uppercase text-[#00e599] mb-2 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-[#00e599] shadow-[0_0_10px_#00e599]"></span>
                        Live Context Pipeline
                    </p>
                    <h2 class="text-white text-3xl font-bold tracking-tight">
                        Instant Context Gateway
                    </h2>
                </div>

                <!-- Interactive Step Controller -->
                <div class="flex flex-wrap items-center gap-2 bg-[#121214] border border-white/10 p-1.5 rounded-xl">
                    <button id="step-btn-1" onclick="setPipelineStep(1, true)" class="px-3.5 py-1.5 rounded-lg mono text-xs font-semibold transition-all">
                        1. Mobile &rarr; Neon DB
                    </button>
                    <button id="step-btn-2" onclick="setPipelineStep(2, true)" class="px-3.5 py-1.5 rounded-lg mono text-xs font-medium transition-all">
                        2. AI &rarr; MCP Server
                    </button>
                    <button id="step-btn-3" onclick="setPipelineStep(3, true)" class="px-3.5 py-1.5 rounded-lg mono text-xs font-medium transition-all">
                        3. Context Stream
                    </button>
                    <button id="playPauseBtn" onclick="toggleAutoPlay()" class="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 mono text-xs text-white/70 transition-colors ml-1">
                        ⏸ Pause
                    </button>
                </div>
            </div>

            <!-- Pipeline Visual Display Frame -->
            <div class="w-full overflow-x-auto rounded-2xl border border-white/[0.08] bg-[#09090b] relative shadow-2xl select-none">
                <div class="relative min-w-[980px] w-full" style="aspect-ratio:1000/380;">

                    <svg viewBox="0 0 1000 380" preserveAspectRatio="xMidYMid meet" class="absolute inset-0 w-full h-full">
                        <defs>
                            <!-- Subtle Grid Pattern -->
                            <pattern id="neonGrid" width="40" height="380" patternUnits="userSpaceOnUse">
                                <line x1="0" y1="0" x2="0" y2="380" stroke="#ffffff" stroke-opacity="0.04" stroke-width="1" stroke-dasharray="2 4"/>
                            </pattern>
                            <!-- Glow Filters -->
                            <filter id="neonGreenGlow" x="-20%" y="-400%" width="140%" height="900%">
                                <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>
                                <feMerge>
                                    <feMergeNode in="blur"/>
                                    <feMergeNode in="SourceGraphic"/>
                                </feMerge>
                            </filter>
                        </defs>

                        <!-- Background vertical ticks -->
                        <rect x="0" y="0" width="1000" height="380" fill="url(#neonGrid)"/>

                        <!-- Center Baseline Ruler Ticks -->
                        <g stroke="#ffffff" stroke-opacity="0.15">
                            <line x1="80" y1="195" x2="80" y2="205"/>
                            <line x1="160" y1="195" x2="160" y2="205"/>
                            <line x1="240" y1="195" x2="240" y2="205"/>
                            <line x1="320" y1="195" x2="320" y2="205"/>
                            <line x1="400" y1="195" x2="400" y2="205"/>
                            <line x1="480" y1="195" x2="480" y2="205"/>
                            <line x1="560" y1="195" x2="560" y2="205"/>
                            <line x1="640" y1="195" x2="640" y2="205"/>
                            <line x1="720" y1="195" x2="720" y2="205"/>
                            <line x1="800" y1="195" x2="800" y2="205"/>
                            <line x1="880" y1="195" x2="880" y2="205"/>
                            <line x1="960" y1="195" x2="960" y2="205"/>
                        </g>

                        <!-- ================= PIPELINE PATHS ================= -->
                        <!-- Base Trunk Gray Guideline -->
                        <line x1="80" y1="200" x2="940" y2="200" stroke="#1f1f23" stroke-width="2"/>

                        <!-- 1. Android -> Neon DB Connection Line -->
                        <path id="path-android-neon" class="pipeline-line"
                              d="M 170 200 H 340" stroke="#00e599" stroke-width="2.5" fill="none" filter="url(#neonGreenGlow)"/>

                        <!-- 2. Neon DB <-> FastMCP Broker Context Channel Line -->
                        <path id="path-mcp-neon-broker" class="pipeline-line"
                              d="M 430 200 H 570" stroke="#27272a" stroke-width="2" fill="none"/>

                        <!-- 3. AI Claude -> FastMCP Curve -->
                        <path id="path-ai-claude" class="pipeline-line"
                              d="M 810 90 C 700 90, 640 160, 580 200" stroke="#27272a" stroke-width="2" fill="none"/>

                        <!-- 4. AI ChatGPT / Cursor -> FastMCP Curve -->
                        <path id="path-ai-chatgpt" class="pipeline-line"
                              d="M 810 310 C 700 310, 640 240, 580 200" stroke="#27272a" stroke-width="2" fill="none"/>

                        <!-- Junction Points -->
                        <circle cx="340" cy="200" r="4.5" fill="#050505" stroke="#00e599" stroke-width="2"/>
                        <circle cx="580" cy="200" r="5" fill="#050505" stroke="#00e599" stroke-width="2.5"/>
                    </svg>

                    <!-- ================= OVERLAY PILL BADGES ================= -->
                    
                    <!-- 1. Android App Badge -->
                    <div id="badge-android" class="pill-badge absolute -translate-y-1/2 flex items-center gap-2 pl-3 pr-4 py-2 rounded-full bg-white text-[#0a0a0a] mono text-xs font-bold shadow-[0_0_15px_rgba(255,255,255,0.15)] border-2 border-transparent"
                         style="left:2.5%; top:52.6%;">
                        <span class="w-2.5 h-2.5 rounded-full bg-[#00e599]"></span>
                        📱 Android App
                    </div>

                    <!-- 2. Neon DB Badge -->
                    <div id="badge-neon" class="pill-badge absolute -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 px-4 py-2 rounded-full bg-[#0e1713] text-[#00e599] border border-[#00e599]/30 mono text-xs font-semibold shadow-lg"
                         style="left:38%; top:52.6%;">
                        <span class="w-2 h-2 rounded-full bg-[#00e599]"></span>
                        ☁️ Neon DB
                    </div>

                    <!-- 3. FastMCP Broker Hub Badge -->
                    <div id="badge-mcp" class="pill-badge absolute -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 px-4 py-2 rounded-full bg-[#18181b] text-white border border-white/20 mono text-xs font-bold shadow-xl"
                         style="left:61%; top:52.6%;">
                        <span class="w-2.5 h-2.5 rounded-full bg-[#00e599] animate-pulse"></span>
                        ⚡ FastMCP Broker
                    </div>

                    <!-- 4. Claude AI Badge (Top Right) -->
                    <div id="badge-claude" class="pill-badge absolute -translate-y-1/2 flex items-center gap-2 px-4 py-2 rounded-full bg-[#1a1712] text-[#f5c14e] border border-[#f5c14e]/30 mono text-xs font-semibold shadow-md"
                         style="left:81%; top:23.6%;">
                        <span class="w-2 h-2 rounded-full bg-[#f5c14e]"></span>
                        🤖 Claude Desktop
                    </div>

                    <!-- 5. ChatGPT / Cursor Badge (Bottom Right) -->
                    <div id="badge-gpt" class="pill-badge absolute -translate-y-1/2 flex items-center gap-2 px-4 py-2 rounded-full bg-[#0c1a1c] text-[#22d3ee] border border-[#22d3ee]/30 mono text-xs font-semibold shadow-md"
                         style="left:81%; top:81.5%;">
                        <span class="w-2 h-2 rounded-full bg-[#22d3ee]"></span>
                        ✨ Cursor & ChatGPT
                    </div>

                </div>

                <!-- Active Status Ribbon Banner -->
                <div class="px-6 py-3 bg-[#0d0d10] border-t border-white/5 flex items-center justify-between mono text-xs">
                    <div id="pipeline-status-text" class="text-white/80">
                        <span class="text-[#00e599]">Step 1:</span> Note created in Android app &rarr; Synced with epoch timestamp to Neon Postgres.
                    </div>
                    <span class="text-white/30 hidden sm:inline">SSE / FastMCP Protocol</span>
                </div>
            </div>

            <!-- 3 Neon-Style Value Props Below Canvas -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div class="p-5 rounded-xl bg-[#09090b] border border-white/5">
                    <div class="mono text-xs text-[#00e599] font-bold mb-1">01 / LOCAL-FIRST SYNC</div>
                    <h3 class="text-sm font-semibold text-white mb-2">Instant Room Ingestion</h3>
                    <p class="text-xs text-neutral-400 leading-relaxed">Notes written on mobile save offline instantly to SQLite Room DB and stream upstream to Neon Postgres upon reconnect.</p>
                </div>
                <div class="p-5 rounded-xl bg-[#09090b] border border-white/5">
                    <div class="mono text-xs text-[#f5c14e] font-bold mb-1">02 / PROTOCOL BROKER</div>
                    <h3 class="text-sm font-semibold text-white mb-2">FastMCP Gateway</h3>
                    <p class="text-xs text-neutral-400 leading-relaxed">Serverless MCP server intercepts incoming tool calls from Claude or Cursor with OAuth / Bearer token validation.</p>
                </div>
                <div class="p-5 rounded-xl bg-[#09090b] border border-white/5">
                    <div class="mono text-xs text-[#22d3ee] font-bold mb-1">03 / CONTEXT INJECTION</div>
                    <h3 class="text-sm font-semibold text-white mb-2">Sub-10ms Trigram Recall</h3>
                    <p class="text-xs text-neutral-400 leading-relaxed">Executes pg_trgm similarity queries on Neon Postgres and injects matching notes directly into LLM prompts.</p>
                </div>
            </div>

        </div>
    </section>

    <!-- 3. Developer Feature Deep Dives -->
    <section class="py-16 bg-surface-white border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12 space-y-16">
            
            <!-- Spotlight 1: Zero-Latency Trigram Search -->
            <div class="flex flex-col lg:flex-row items-center gap-10">
                <div class="flex-1 space-y-3">
                    <div class="inline-block px-2 py-1 bg-surface-container rounded text-xs font-mono font-semibold text-primary">FULL-TEXT RECALL</div>
                    <h3 class="text-2xl font-bold text-on-surface">Zero-Latency Trigram Search</h3>
                    <p class="text-sm text-on-surface-variant leading-relaxed">
                        Traditional LLM retrieval fails when queries have typos or fragmented terms. Memory Notes harnesses PostgreSQL trigram matching (<code class="font-mono text-xs text-on-surface bg-surface-container-low px-1 py-0.5 rounded">pg_trgm</code>) to fuzzy-match title and body content across workspaces in milliseconds.
                    </p>
                    <ul class="text-xs font-mono text-text-secondary space-y-1 pt-2">
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

            <hr class="border-border-muted">

            <!-- Spotlight 2: Autonomous AI Memory Sync -->
            <div class="flex flex-col lg:flex-row-reverse items-center gap-10">
                <div class="flex-1 space-y-3">
                    <div class="inline-block px-2 py-1 bg-secondary-container rounded text-xs font-mono font-semibold text-on-surface">BI-DIRECTIONAL WRITES</div>
                    <h3 class="text-2xl font-bold text-on-surface">Autonomous AI Memory Sync</h3>
                    <p class="text-sm text-on-surface-variant leading-relaxed">
                        Claude and Cursor can not only inspect your past notes—they can create new workspace folders, append structured summaries, or update existing documents directly from conversation prompts.
                    </p>
                    <ul class="text-xs font-mono text-text-secondary space-y-1 pt-2">
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

    <!-- Core Bento Capabilities -->
    <section id="features" class="py-16 bg-surface-white border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12">
            <div class="mb-12">
                <h2 class="text-2xl lg:text-3xl font-bold text-on-surface mb-2">Core Capabilities</h2>
                <p class="text-sm text-on-surface-variant max-w-2xl">Tools designed for deep intellectual focus, stripping away the superfluous to leave only what matters.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                <!-- 1. Non-Linear Connectivity -->
                <div class="md:col-span-2 feature-card bg-surface-white border border-border-muted p-6 flex flex-col justify-between group rounded">
                    <div class="mb-6">
                        <span class="inline-block p-2.5 bg-surface-container rounded mb-4 border border-border-muted group-hover:border-[#050505] transition-colors">
                            <span class="material-symbols-outlined text-primary" data-icon="account_tree">account_tree</span>
                        </span>
                        <h3 class="text-xl font-semibold text-on-surface mb-1">Non-Linear Connectivity</h3>
                        <p class="text-sm text-on-surface-variant">Build an intricate web of knowledge. Link notes effortlessly to visualize relationships and emergent ideas.</p>
                    </div>
                    <div class="h-36 bg-surface-container-low border border-border-muted rounded flex items-center justify-center relative overflow-hidden p-4">
                        <svg class="w-full h-full text-border-muted" viewBox="0 0 400 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <line x1="50" y1="60" x2="160" y2="30" stroke="#737783" stroke-width="1.5" stroke-dasharray="3 3"/>
                            <line x1="160" y1="30" x2="280" y2="80" stroke="#1c1b1b" stroke-width="1.5"/>
                            <line x1="160" y1="30" x2="350" y2="40" stroke="#1c1b1b" stroke-width="1.5"/>
                            <line x1="50" y1="60" x2="200" y2="90" stroke="#737783" stroke-width="1.5"/>
                            <circle cx="50" cy="60" r="14" fill="#ffffff" stroke="#1c1b1b" stroke-width="2"/>
                            <circle cx="160" cy="30" r="18" fill="#fdd400" stroke="#1c1b1b" stroke-width="2"/>
                            <circle cx="280" cy="80" r="14" fill="#ffffff" stroke="#1c1b1b" stroke-width="2"/>
                            <circle cx="350" cy="40" r="12" fill="#ffffff" stroke="#1c1b1b" stroke-width="2"/>
                            <circle cx="200" cy="90" r="10" fill="#ffffff" stroke="#1c1b1b" stroke-width="2"/>
                        </svg>
                    </div>
                </div>
                
                <!-- 2. Zen Canvas -->
                <div class="feature-card bg-surface-white border border-border-muted p-6 flex flex-col group rounded">
                    <span class="inline-block p-2.5 bg-surface-container rounded mb-4 border border-border-muted group-hover:border-[#050505] transition-colors self-start">
                        <span class="material-symbols-outlined text-primary" data-icon="format_ink_highlighter">format_ink_highlighter</span>
                    </span>
                    <h3 class="text-xl font-semibold text-on-surface mb-1">Zen Canvas</h3>
                    <p class="text-sm text-on-surface-variant mb-6">A distraction-free writing environment that centers your thoughts and fades UI elements away.</p>
                    <div class="mt-auto h-36 bg-surface-container-low border border-border-muted rounded flex items-center justify-center p-4">
                        <svg class="w-full h-24" viewBox="0 0 200 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect x="10" y="10" width="180" height="60" rx="4" fill="#ffffff" stroke="#E2E2E7" stroke-width="1"/>
                            <rect x="25" y="24" width="90" height="6" rx="2" fill="#1c1b1b"/>
                            <rect x="25" y="38" width="150" height="4" rx="2" fill="#71717A"/>
                            <rect x="25" y="48" width="120" height="4" rx="2" fill="#E2E2E7"/>
                            <line x1="120" y1="23" x2="120" y2="31" stroke="#003178" stroke-width="2"/>
                        </svg>
                    </div>
                </div>

                <!-- 3. Lightning Search -->
                <div class="feature-card bg-surface-white border border-border-muted p-6 flex flex-col group rounded">
                    <span class="inline-block p-2.5 bg-surface-container rounded mb-4 border border-border-muted group-hover:border-[#050505] transition-colors self-start">
                        <span class="material-symbols-outlined text-primary" data-icon="search">search</span>
                    </span>
                    <h3 class="text-xl font-semibold text-on-surface mb-1">Lightning Search</h3>
                    <p class="text-sm text-on-surface-variant mb-6">Instantly retrieve any thought with our fast, full-text fuzzy search engine.</p>
                    <div class="mt-auto h-36 bg-surface-container-low border border-border-muted rounded flex flex-col justify-center p-3">
                        <div class="flex items-center gap-2 px-3 py-2 border border-border-muted rounded bg-surface-white text-xs text-on-surface shadow-xs">
                            <span class="material-symbols-outlined text-sm text-primary" data-icon="search">search</span>
                            <span class="font-mono text-xs font-semibold">trgm.match("query")</span>
                        </div>
                        <div class="mt-2 text-[10px] font-mono text-text-secondary px-1">
                            &gt; 3 matches indexed in 4ms
                        </div>
                    </div>
                </div>

                <!-- 4. Extensible Architecture -->
                <div class="md:col-span-2 feature-card bg-surface-white border border-border-muted p-6 flex flex-col md:flex-row gap-6 items-center group rounded">
                    <div class="flex-1">
                        <span class="inline-block p-2.5 bg-surface-container rounded mb-4 border border-border-muted group-hover:border-[#050505] transition-colors">
                            <span class="material-symbols-outlined text-primary" data-icon="code">code</span>
                        </span>
                        <h3 class="text-xl font-semibold text-on-surface mb-1">Open Protocol Standards</h3>
                        <p class="text-sm text-on-surface-variant">Built directly on top of Anthropic's Model Context Protocol (MCP) and Starlette ASGI for developer extensibility.</p>
                    </div>
                    <div class="flex-1 w-full h-36 bg-surface-container-low border border-border-muted rounded flex flex-col justify-center p-4 font-mono text-xs text-text-secondary leading-relaxed">
                        <div>Server: FastMCP / Python 3.12</div>
                        <div>Protocol: Streamable HTTP (SSE)</div>
                        <div class="text-primary font-semibold mt-1">Multi-Tenant Tenant Isolation</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</main>

<!-- Footer -->
<footer class="w-full py-8 px-6 lg:px-12 flex flex-col md:flex-row justify-between items-center max-w-6xl mx-auto bg-surface-white border-t border-border-muted">
    <div class="flex flex-col items-center md:items-start gap-1 mb-4 md:mb-0">
        <span class="text-sm font-bold text-on-surface">Memory Notes</span>
        <span class="text-xs text-text-secondary">© 2026 Memory Notes. Structured Freedom.</span>
    </div>
    <nav class="flex gap-4 text-xs text-text-secondary">
        <a class="hover:text-primary transition-colors no-underline" href="#">Privacy Policy</a>
        <a class="hover:text-primary transition-colors no-underline" href="#">Terms of Service</a>
        <a class="hover:text-primary transition-colors no-underline" href="#">Changelog</a>
    </nav>
</footer>
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
<main class="flex-grow py-10 px-6">
    <div class="max-w-3xl mx-auto">
        <div class="mb-6">
            <h1 class="text-2xl font-bold text-on-surface mb-1">Dashboard & Settings</h1>
            <p class="text-xs text-text-secondary">Manage your database connection string, API keys, and connector endpoint.</p>
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

        <!-- 2. Neon Connection String Settings -->
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
<main class="flex-grow flex items-center justify-center py-16 px-6">
    <div class="max-w-md w-full bg-surface-white border border-border-muted p-8 rounded-xl shadow-sm text-center">
        <h2 class="text-lg font-bold text-error mb-2">Error</h2>
        <div class="p-3 bg-red-50 text-red-700 text-xs rounded mb-6 border border-red-200">{message}</div>
        <a href="/dashboard" class="inline-block bg-secondary-container text-on-surface px-6 py-2.5 rounded text-xs font-semibold border border-[#050505] no-underline">Back to Dashboard</a>
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
