"""
Memory Notes for AI - Web Application
Full production SaaS landing page featuring custom brutalist profile cards,
interactive manifesto switcher, layered depth cards, magnetic corner CTA buttons,
live terminal switcher, architecture pipeline, and developer deep dives.
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
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Hanken+Grotesk:wght@600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&family=Poppins:wght@500;600;700&family=Syne:wght@600;700;800&display=swap" rel="stylesheet"/>

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
        /* ---------------- HERO SPOTLIGHT GRID ---------------- */
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

        /* ---------------- STYLE 1: BRUTALIST PROFILE CARD ---------------- */
        .card-profile {{
            background: #f5f5f0;
            border: 4px solid #0a0a0a;
            box-shadow: 6px 6px 0 #0a0a0a;
            position: relative;
            overflow: hidden;
            width: 100%;
            max-width: 320px;
            margin: 0 auto;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .card-profile:hover {{
            transform: translate(-3px, -3px);
            box-shadow: 9px 9px 0 #0a0a0a;
        }}
        .prof-photo {{
            height: 120px;
            background: #f5e642;
            border-bottom: 4px solid #0a0a0a;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: flex-end;
        }}
        .prof-photo::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: repeating-linear-gradient(
                45deg,
                transparent 0px,
                transparent 8px,
                rgba(0, 0, 0, 0.12) 8px,
                rgba(0, 0, 0, 0.12) 10px
            );
        }}
        .prof-photo-num {{
            font-family: "Bebas Neue", sans-serif;
            font-size: 5.5rem;
            line-height: 0.85;
            color: rgba(0, 0, 0, 0.08);
            position: absolute;
            right: -8px;
            bottom: -10px;
            letter-spacing: -0.02em;
            pointer-events: none;
        }}
        .prof-avatar {{
            width: 60px;
            height: 60px;
            background: #0a0a0a;
            border: 4px solid #0a0a0a;
            border-bottom: none;
            border-left: none;
            margin-left: 16px;
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: "Bebas Neue", sans-serif;
            font-size: 1.6rem;
            color: #f5e642;
            flex-shrink: 0;
        }}
        .prof-status-badge {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 2;
            background: #00e060;
            border: 2px solid #0a0a0a;
            box-shadow: 2px 2px 0 #0a0a0a;
            font-size: 0.55rem;
            font-weight: 800;
            letter-spacing: 0.15em;
            padding: 2px 6px;
            text-transform: uppercase;
        }}
        .prof-body {{
            padding: 14px 16px 0;
        }}
        .prof-handle {{
            font-size: 0.55rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            color: #71717A;
            text-transform: uppercase;
            margin-bottom: 2px;
        }}
        .prof-name {{
            font-family: "Bebas Neue", sans-serif;
            font-size: 1.9rem;
            line-height: 0.9;
            color: #0a0a0a;
            letter-spacing: -0.01em;
            margin-bottom: 8px;
        }}
        .prof-bio {{
            font-size: 0.72rem;
            font-weight: 500;
            color: #1c1b1b;
            border-left: 4px solid #e8180a;
            padding-left: 8px;
            line-height: 1.45;
            margin-bottom: 12px;
        }}
        .prof-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            border-top: 3px solid #0a0a0a;
        }}
        .pstat {{
            padding: 8px 6px;
            border-right: 2px solid #0a0a0a;
            text-align: center;
        }}
        .pstat:last-child {{
            border-right: none;
        }}
        .pstat .psv {{
            font-family: "Bebas Neue", sans-serif;
            font-size: 1.4rem;
            line-height: 1;
            color: #0a0a0a;
            display: block;
        }}
        .pstat .psl {{
            font-size: 0.46rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: #71717A;
            text-transform: uppercase;
            display: block;
            margin-top: 2px;
        }}
        .prof-btn {{
            display: block;
            width: 100%;
            padding: 10px;
            background: #0a0a0a;
            color: #f5e642;
            border: none;
            border-top: 3px solid #0a0a0a;
            font-family: "Bebas Neue", sans-serif;
            font-size: 1rem;
            letter-spacing: 0.18em;
            cursor: pointer;
            text-align: center;
            transition: background 0.15s, color 0.15s;
        }}
        .prof-btn:hover {{
            background: #f5e642;
            color: #0a0a0a;
        }}

        /* ---------------- STYLE 2: MANIFESTO & ACID TOGGLE ---------------- */
        .manifesto-showcase {{
            --bg-outer: transparent;
            --bg-inner: #fdfdfa;
            --text-main: #0a0a0a;
            --accent: #ff2a00;
            --shadow-color: #0a0a0a;
            --geo-radius: 0%;
            --geo-bg: repeating-linear-gradient(45deg, var(--text-main) 0 2px, transparent 2px 10px);
            --geo-pos-x: -10%;
            --geo-pos-y: -10%;
            --font-display: "Impact", "Arial Black", sans-serif;
            --font-body: "Inter", sans-serif;
            --font-mono: "JetBrains Mono", monospace;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
        }}
        .manifesto-showcase:has(.rebel-toggle:checked) {{
            --bg-inner: #111111;
            --text-main: #ccff00;
            --accent: #ff007f;
            --shadow-color: #ff007f;
            --geo-radius: 50%;
            --geo-bg: radial-gradient(circle, var(--accent) 0%, transparent 70%);
            --geo-pos-x: 20%;
            --geo-pos-y: 20%;
        }}
        .manifesto-showcase .rebel-toggle {{
            display: none;
        }}
        .manifesto-showcase .presentation-stage {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            padding: 10px;
            perspective: 1000px;
        }}
        .manifesto-showcase .aesthetic-switch {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 16px;
            margin-bottom: 1.2rem;
            background: var(--text-main);
            color: var(--bg-inner);
            font-family: var(--font-mono);
            font-weight: bold;
            font-size: 0.72rem;
            letter-spacing: 1px;
            cursor: pointer;
            border: 2px solid var(--text-main);
            box-shadow: 3px 3px 0px var(--accent);
            transition: all 0.25s ease;
            z-index: 50;
            text-transform: uppercase;
        }}
        .manifesto-showcase .aesthetic-switch:hover {{
            transform: translate(-2px, -2px);
            box-shadow: 5px 5px 0px var(--accent);
        }}
        .manifesto-showcase .mode-chaos {{
            display: none;
        }}
        .manifesto-showcase .rebel-toggle:checked ~ .presentation-stage .mode-clean {{
            display: none;
        }}
        .manifesto-showcase .rebel-toggle:checked ~ .presentation-stage .mode-chaos {{
            display: inline;
        }}
        .manifesto-showcase .poster-card {{
            position: relative;
            width: 260px;
            height: 360px;
            background-color: var(--bg-inner);
            border: 3px solid var(--text-main);
            box-shadow: 8px 8px 0px var(--shadow-color);
            overflow: hidden;
            transition: all 0.5s cubic-bezier(0.83, 0, 0.17, 1);
            transform-style: preserve-3d;
        }}
        .manifesto-showcase .poster-card:hover {{
            transform: rotateY(5deg) rotateX(2deg) scale(1.02);
            box-shadow: 12px 12px 0px var(--shadow-color);
        }}
        .manifesto-showcase .css-mesh-grain {{
            position: absolute;
            inset: 0;
            background-image: radial-gradient(var(--text-main) 1px, transparent 1px);
            background-size: 4px 4px;
            opacity: 0.15;
            pointer-events: none;
            z-index: 10;
        }}
        .manifesto-showcase .drafting-grid {{
            position: absolute;
            inset: 0;
            background-image: linear-gradient(to right, var(--text-main) 1px, transparent 1px),
                              linear-gradient(to bottom, var(--text-main) 1px, transparent 1px);
            background-size: 20% 20%;
            opacity: 0.1;
            pointer-events: none;
        }}
        .manifesto-showcase .geo-orb {{
            position: absolute;
            top: var(--geo-pos-y);
            right: var(--geo-pos-x);
            width: 60%;
            height: 45%;
            background: var(--geo-bg);
            border-radius: var(--geo-radius);
            transition: all 0.8s cubic-bezier(0.83, 0, 0.17, 1);
            mix-blend-mode: multiply;
            opacity: 0.8;
        }}
        .manifesto-showcase .type-container {{
            position: absolute;
            top: 10%;
            left: 5%;
            display: flex;
            flex-direction: column;
            z-index: 5;
        }}
        .manifesto-showcase .huge-text {{
            font-family: var(--font-display);
            font-size: 3.3rem;
            line-height: 0.82;
            letter-spacing: -0.04em;
            color: var(--text-main);
            text-transform: uppercase;
            mix-blend-mode: exclusion;
            position: relative;
            transition: color 0.5s ease;
        }}
        .manifesto-showcase .word-2 {{
            margin-left: 10%;
            color: transparent;
            -webkit-text-stroke: 2px var(--text-main);
        }}
        .manifesto-showcase .tape-ribbon {{
            position: absolute;
            top: 50%;
            left: -30%;
            width: 160%;
            background: var(--accent);
            color: var(--bg-inner);
            transform: rotate(-12deg) scale(1.05);
            padding: 0.5rem 0;
            font-family: var(--font-mono);
            font-size: 0.75rem;
            font-weight: 900;
            white-space: nowrap;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            z-index: 20;
            display: flex;
            overflow: hidden;
            transition: all 0.5s ease;
        }}
        .manifesto-showcase .tape-scroll {{
            display: flex;
            width: max-content;
            animation: manifestoScrollText 10s linear infinite;
        }}
        .manifesto-showcase .tape-scroll span {{
            padding-right: 1rem;
        }}
        @keyframes manifestoScrollText {{
            to {{
                transform: translateX(-50%);
            }}
        }}
        .manifesto-showcase .poster-footer {{
            position: absolute;
            bottom: 5%;
            left: 5%;
            right: 5%;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            z-index: 5;
            border-top: 2px solid var(--text-main);
            padding-top: 0.5rem;
        }}
        .manifesto-showcase .barcode {{
            width: 48px;
            height: 22px;
            background: repeating-linear-gradient(to right, var(--text-main) 0, var(--text-main) 2px, transparent 2px, transparent 4px, var(--text-main) 4px, var(--text-main) 6px, transparent 6px, transparent 10px, var(--text-main) 10px, var(--text-main) 11px, transparent 11px, transparent 15px);
        }}
        .manifesto-showcase .manifesto-text {{
            max-width: 65%;
            text-align: right;
            color: var(--text-main);
        }}
        .manifesto-showcase .vol {{
            font-family: var(--font-mono);
            font-weight: bold;
            font-size: 0.52rem;
            text-transform: uppercase;
            margin-bottom: 2px;
        }}
        .manifesto-showcase .desc {{
            font-size: 0.48rem;
            line-height: 1.25;
            opacity: 0.85;
            margin: 0;
        }}
        .manifesto-showcase .rebel-toggle:checked ~ .presentation-stage .huge-text {{
            text-shadow: 3px 3px 0px var(--accent), -2px -2px 0px #00ffff;
            mix-blend-mode: normal;
        }}

        /* ---------------- STYLE 4: MAGNETIC CORNER DRAWER CTA BUTTON ---------------- */
        .btn-container {{
            --btn-color: #d8ff7c;
            --corner-color: #00000040;
            --corner-dist: 24px;
            --corner-multiplier: 1.5;
            --timing-function: cubic-bezier(0, 0, 0, 2.5);
            --duration: 250ms;
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
        }}
        .btn {{
            position: relative;
            min-width: 170px;
            min-height: calc(var(--corner-dist) * 2);
            border-radius: 14px;
            border: 2px solid #0a0a0a;
            padding: 0.4em 1.2em;
            background: linear-gradient(#fff4, #0001), var(--btn-color);
            box-shadow: 1px 1px 2px -1px #fff inset, 0 4px 6px #00000018;
            transition: transform var(--duration) var(--timing-function), filter var(--duration) var(--timing-function);
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-drawer {{
            position: absolute;
            display: flex;
            justify-content: center;
            min-height: 28px;
            border-radius: 12px;
            border: 1px solid #0a0a0a;
            padding: 0.2em 0.8em;
            font-size: 0.72em;
            font-weight: 700;
            font-family: "Poppins", monospace;
            color: #0a0a0a;
            background-color: #fbff13;
            opacity: 0;
            transition: transform calc(0.5 * var(--duration)) ease, filter var(--duration) var(--timing-function), opacity calc(0.5 * var(--duration)) ease;
            filter: blur(2px);
            pointer-events: none;
            white-space: nowrap;
        }}
        .transition-top {{
            top: 0;
            left: 0;
            border-radius: 10px 10px 0 0;
            align-items: start;
        }}
        .transition-bottom {{
            bottom: 0;
            right: 0;
            border-radius: 0 0 10px 10px;
            align-items: end;
        }}
        .btn-text {{
            display: inline-block;
            font-size: 1.15em;
            font-family: "Syne", "Inter", sans-serif;
            font-weight: 800;
            color: #0a0a0a;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .btn-corner {{
            position: absolute;
            width: 28px;
            fill: none;
            stroke: var(--corner-color);
            transition: transform var(--duration) var(--timing-function), filter var(--duration) var(--timing-function);
            pointer-events: none;
        }}
        .btn-corner:nth-of-type(1) {{
            top: 0;
            left: 0;
            transform: translate(calc(-1 * var(--corner-dist)), calc(-1 * var(--corner-dist))) rotate(90deg);
        }}
        .btn-corner:nth-of-type(2) {{
            top: 0;
            right: 0;
            transform: translate(var(--corner-dist), calc(-1 * var(--corner-dist))) rotate(180deg);
        }}
        .btn-corner:nth-of-type(3) {{
            bottom: 0;
            right: 0;
            transform: translate(var(--corner-dist), var(--corner-dist)) rotate(-90deg);
        }}
        .btn-corner:nth-of-type(4) {{
            bottom: 0;
            left: 0;
            transform: translate(calc(-1 * var(--corner-dist)), var(--corner-dist)) rotate(0deg);
        }}
        .btn-container:hover .btn {{
            transform: scale(1.04);
            filter: drop-shadow(0 10px 12px rgba(0,0,0,0.15));
        }}
        .btn-container:hover .transition-top {{
            transform: translateY(-22px) rotateZ(3deg);
            filter: blur(0px);
            opacity: 1;
        }}
        .btn-container:hover .transition-bottom {{
            transform: translateY(22px) rotateZ(3deg);
            filter: blur(0px);
            opacity: 1;
        }}
        .btn-container:hover .btn-corner:first-of-type {{
            transform: translate(calc(-1 * var(--corner-multiplier) * var(--corner-dist)), calc(-1 * var(--corner-multiplier) * var(--corner-dist))) rotate(90deg);
        }}
        .btn-container:hover .btn-corner:nth-of-type(2) {{
            transform: translate(calc(var(--corner-multiplier) * var(--corner-dist)), calc(-1 * var(--corner-multiplier) * var(--corner-dist))) rotate(180deg);
        }}
        .btn-container:hover .btn-corner:nth-of-type(3) {{
            transform: translate(calc(var(--corner-multiplier) * var(--corner-dist)), calc(var(--corner-multiplier) * var(--corner-dist))) rotate(-90deg);
        }}
        .btn-container:hover .btn-corner:nth-of-type(4) {{
            transform: translate(calc(-1 * var(--corner-multiplier) * var(--corner-dist)), calc(var(--corner-multiplier) * var(--corner-dist))) rotate(0deg);
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
# Landing Page (All 4 Card & Button Widgets + Full SaaS Sections)
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
    <!-- Hero Section (Interactive Spotlight Grid) -->
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
                <div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-3">
                    <!-- Widget 4: Magnetic Corner Button (CTA) -->
                    <div class="btn-container">
                        <div class="btn-drawer transition-top">free tier active</div>
                        <div class="btn-drawer transition-bottom">...100% private</div>
                        <a href="{' /dashboard' if user_id else '/signup'}" class="btn">
                            <span class="btn-text">{'Go to Canvas' if user_id else 'Start Writing'}</span>
                        </a>
                        <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                        <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                        <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                        <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                    </div>
                    <a href="#quickstart" class="bg-surface-white text-on-surface px-6 py-3 text-sm font-semibold border border-[#050505] hover:bg-surface-container-low transition-colors inline-block no-underline shadow-sm rounded">Try in 30 Seconds</a>
                </div>
            </div>
            
            <div class="flex-1 w-full max-w-md lg:max-w-none flex items-center justify-center">
                <div class="p-6 bg-surface-white border-2 border-on-surface rounded-xl shadow-[6px_6px_0px_#0a0a0a] text-left w-full max-w-md font-mono text-xs">
                    <div class="flex items-center justify-between pb-3 mb-3 border-b border-border-muted">
                        <span class="font-bold text-primary">● MCP MEMORY GATEWAY</span>
                        <span class="text-text-secondary">Connected</span>
                    </div>
                    <p class="text-text-secondary mb-1">&gt; AI Model query sync:</p>
                    <p class="text-on-surface font-semibold">&gt; search_notes(query="architecture design")</p>
                    <p class="text-green-600 font-semibold mt-2">✓ Synced instantly to local client.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Interactive Code / Terminal Block -->
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

    <!-- Architecture & Data Flow -->
    <section class="py-16 bg-surface-container-low border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12">
            <div class="text-center max-w-2xl mx-auto mb-12">
                <h2 class="text-2xl lg:text-3xl font-bold text-on-surface mb-2">Architecture & Data Flow</h2>
                <p class="text-sm text-on-surface-variant">A decentralized pipeline connecting local Android memory, serverless cloud databases, and AI models.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
                <div class="bg-surface-white border border-border-muted p-6 rounded-xl shadow-xs flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center mb-4 border border-border-muted">
                            <span class="material-symbols-outlined text-primary" data-icon="edit_note">edit_note</span>
                        </div>
                        <span class="text-xs font-mono font-bold text-primary block mb-1">01 / CAPTURE</span>
                        <h3 class="text-lg font-bold text-on-surface mb-2">Local Canvas & App</h3>
                        <p class="text-xs text-on-surface-variant leading-relaxed">Thoughts are captured distraction-free inside the Android app canvas and persisted locally in SQLite Room DB.</p>
                    </div>
                    <div class="mt-6 pt-4 border-t border-border-muted text-[11px] font-mono text-text-secondary">
                        Storage: SQLite / Room DB<br>Timestamp: Epoch ms (bigint)
                    </div>
                </div>

                <div class="bg-surface-white border-2 border-on-surface p-6 rounded-xl shadow-xs flex flex-col justify-between relative">
                    <span class="absolute -top-3 right-4 px-2 py-0.5 bg-secondary-container text-on-surface text-[10px] font-mono font-bold rounded border border-on-surface">BRIDGE</span>
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center mb-4 border border-border-muted">
                            <span class="material-symbols-outlined text-on-surface" data-icon="sync_alt">sync_alt</span>
                        </div>
                        <span class="text-xs font-mono font-bold text-on-surface block mb-1">02 / SYNC</span>
                        <h3 class="text-lg font-bold text-on-surface mb-2">FastMCP Protocol</h3>
                        <p class="text-xs text-on-surface-variant leading-relaxed">Vercel serverless functions route authenticated requests over streamable HTTP SSE. Last-Write-Wins resolves conflicts.</p>
                    </div>
                    <div class="mt-6 pt-4 border-t border-border-muted text-[11px] font-mono text-text-secondary">
                        Route: POST /mcp<br>Auth: Bearer Token (OAuth 2.1)
                    </div>
                </div>

                <div class="bg-surface-white border border-border-muted p-6 rounded-xl shadow-xs flex flex-col justify-between">
                    <div>
                        <div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center mb-4 border border-border-muted">
                            <span class="material-symbols-outlined text-primary" data-icon="database">database</span>
                        </div>
                        <span class="text-xs font-mono font-bold text-primary block mb-1">03 / PERSIST</span>
                        <h3 class="text-lg font-bold text-on-surface mb-2">Neon Cloud Postgres</h3>
                        <p class="text-xs text-on-surface-variant leading-relaxed">Dedicated user database instances with pg_trgm indices enable sub-10ms fuzzy similarity queries and instant AI context recall.</p>
                    </div>
                    <div class="mt-6 pt-4 border-t border-border-muted text-[11px] font-mono text-text-secondary">
                        Driver: asyncpg pool<br>Extension: pg_trgm similarity
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Visual Interactive Showcase (Widgets #2 & #3) -->
    <section class="py-16 bg-surface-white border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12">
            <div class="text-center max-w-2xl mx-auto mb-12">
                <span class="text-xs font-mono font-bold text-primary tracking-widest uppercase mb-1 block">Aesthetic Engine</span>
                <h2 class="text-2xl lg:text-3xl font-bold text-on-surface mb-2">Built for Pure Focus & Deep Utility</h2>
                <p class="text-sm text-on-surface-variant">Switch aesthetic modes or explore 3D spatial canvas layers built for power users.</p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
                <!-- Widget 2: Manifesto Showcase with Interactive Toggle -->
                <div class="flex flex-col items-center justify-center bg-surface-container-low border border-border-muted p-8 rounded-2xl shadow-sm">
                    <span class="text-xs font-mono text-text-secondary mb-4">// Interactive Aesthetic Switcher</span>
                    <div class="manifesto-showcase">
                        <input type="checkbox" id="rebel-toggle" class="rebel-toggle" />
                        <div class="presentation-stage">
                            <label for="rebel-toggle" class="aesthetic-switch">
                                <span class="switch-text mode-clean">BRUTALIZE AESTHETIC — CLICK ME</span>
                                <span class="switch-text mode-chaos">RESTORE MINIMALISM</span>
                            </label>
                            <div class="poster-card">
                                <div class="css-mesh-grain"></div>
                                <div class="drafting-grid"></div>
                                <div class="geo-orb"></div>
                                <div class="type-container">
                                    <div class="huge-text word-1">MEMORY</div>
                                    <div class="huge-text word-2">VAULT.</div>
                                </div>
                                <div class="tape-ribbon">
                                    <div class="tape-scroll">
                                        <span>NO JS // PURE SSE // BOLD AESTHETICS // REJECT MEDIOCRITY // </span>
                                        <span>NO JS // PURE SSE // BOLD AESTHETICS // REJECT MEDIOCRITY // </span>
                                    </div>
                                </div>
                                <div class="poster-footer">
                                    <div class="barcode"></div>
                                    <div class="manifesto-text">
                                        <p class="vol">VOL. 01 / MCP GATEWAY</p>
                                        <p class="desc">Structured memory context for AI models with zero lock-in.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Widget 3: 3D Depth Card Showcase -->
                <div class="flex flex-col items-center justify-center bg-surface-container-low border border-border-muted p-8 rounded-2xl shadow-sm">
                    <span class="text-xs font-mono text-text-secondary mb-6">// Spatial Workspace Canvas</span>
                    <div class="cursor-pointer group overflow-hidden p-5 duration-1000 hover:duration-1000 relative w-72 h-72 bg-neutral-900 rounded-2xl border-2 border-neutral-800 shadow-xl">
                        <div class="group-hover:-top-3 bg-transparent -top-12 -left-12 absolute shadow-yellow-800 shadow-inner rounded-xl transition-all ease-in-out group-hover:duration-1000 duration-1000 w-24 h-24"></div>
                        <div class="group-hover:top-60 bg-transparent top-44 left-14 absolute shadow-red-800 shadow-inner rounded-xl transition-all ease-in-out group-hover:duration-1000 duration-1000 w-24 h-24"></div>
                        <div class="group-hover:-left-12 bg-transparent top-24 left-56 absolute shadow-sky-800 shadow-inner rounded-xl transition-all ease-in-out group-hover:duration-1000 duration-1000 w-24 h-24"></div>
                        <div class="group-hover:-top-44 bg-transparent top-12 left-12 absolute shadow-red-800 shadow-inner rounded-xl transition-all ease-in-out group-hover:duration-1000 duration-1000 w-12 h-12"></div>
                        <div class="group-hover:left-44 bg-transparent top-12 left-12 absolute shadow-green-800 shadow-inner rounded-xl transition-all ease-in-out group-hover:duration-1000 duration-1000 w-44 h-44"></div>
                        <div class="group-hover:-left-2 bg-transparent -top-24 -left-12 absolute shadow-sky-800 shadow-inner rounded-xl transition-all ease-in-out group-hover:duration-1000 duration-1000 w-64 h-64"></div>
                        <div class="group-hover:top-44 bg-transparent top-24 left-12 absolute shadow-sky-500 shadow-inner rounded-xl transition-all ease-in-out group-hover:duration-1000 duration-1000 w-4 h-4"></div>
                        <div class="w-full h-full shadow-xl shadow-neutral-950 p-4 bg-neutral-800/80 backdrop-blur-sm rounded-xl flex-col gap-2 flex justify-center border border-neutral-700/50">
                            <span class="text-neutral-50 font-bold text-xl italic font-headline-md">Interactive Canvas</span>
                            <p class="text-neutral-300 text-xs leading-relaxed">
                                Move notes spatially across 2D coordinates. AI agents position contextually related thoughts together on your endless board.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Developer Deep Dives -->
    <section class="py-16 bg-surface-white border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12 space-y-16">
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

    <!-- Bento Capabilities Grid -->
    <section id="features" class="py-16 bg-surface-white border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12">
            <div class="mb-12">
                <h2 class="text-2xl lg:text-3xl font-bold text-on-surface mb-2">Core Capabilities</h2>
                <p class="text-sm text-on-surface-variant max-w-2xl">Tools designed for deep intellectual focus, stripping away the superfluous to leave only what matters.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
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

    <!-- Community & Developer Testimonials (Featuring Widget #1) -->
    <section class="py-16 bg-surface-container-low border-b border-border-muted">
        <div class="max-w-6xl mx-auto px-6 lg:px-12">
            <div class="text-center max-w-2xl mx-auto mb-12">
                <span class="text-xs font-mono font-bold text-primary tracking-widest uppercase mb-1 block">Community & Builders</span>
                <h2 class="text-2xl lg:text-3xl font-bold text-on-surface mb-2">Engineers & Creators on Memory Notes</h2>
                <p class="text-sm text-on-surface-variant">Join developers plugging their second brain directly into autonomous LLM agents.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
                <!-- Widget 1: Brutalist Profile Card -->
                <div class="card-profile">
                    <div class="prof-photo">
                        <div class="prof-photo-num">MK</div>
                        <div class="prof-avatar">MK</div>
                        <div class="prof-status-badge">● ONLINE</div>
                    </div>
                    <div class="prof-body">
                        <div class="prof-handle">@matthieu.k</div>
                        <div class="prof-name">MATTHIEU<br />KRANZ</div>
                        <div class="prof-bio">
                            Brutalist designer &amp; systems dev. Uses Memory Notes to sync daily project logs with Claude Desktop.
                        </div>
                    </div>
                    <div class="prof-stats">
                        <div class="pstat">
                            <span class="psv">482</span>
                            <span class="psl">Notes</span>
                        </div>
                        <div class="pstat">
                            <span class="psv">28k</span>
                            <span class="psl">Tokens</span>
                        </div>
                        <div class="pstat">
                            <span class="psv">★ 4.9</span>
                            <span class="psl">Rating</span>
                        </div>
                    </div>
                    <button class="prof-btn" onclick="window.location='/signup'">+ CLONE WORKSPACE</button>
                </div>

                <!-- Testimonial 2 -->
                <div class="bg-surface-white border-2 border-on-surface p-6 rounded-xl shadow-[4px_4px_0px_#0a0a0a]">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-10 h-10 rounded-full bg-surface-container border border-border-muted flex items-center justify-center font-bold text-xs">
                            AL
                        </div>
                        <div>
                            <div class="text-sm font-bold text-on-surface">Alex Liu</div>
                            <div class="text-xs text-text-secondary font-mono">Backend Lead @ Scale</div>
                        </div>
                    </div>
                    <p class="text-xs text-on-surface-variant leading-relaxed mb-4">
                        "The fact that my notes stay in my own private Neon Postgres database while Claude can search them via MCP without any proprietary middleman is game-changing."
                    </p>
                    <div class="text-[10px] font-mono text-primary font-bold">✓ VERIFIED ARCHITECTURE</div>
                </div>

                <!-- Testimonial 3 -->
                <div class="bg-surface-white border-2 border-on-surface p-6 rounded-xl shadow-[4px_4px_0px_#0a0a0a]">
                    <div class="flex items-center gap-3 mb-4">
                        <div class="w-10 h-10 rounded-full bg-surface-container border border-border-muted flex items-center justify-center font-bold text-xs">
                            SR
                        </div>
                        <div>
                            <div class="text-sm font-bold text-on-surface">Sarah R.</div>
                            <div class="text-xs text-text-secondary font-mono">Independent Researcher</div>
                        </div>
                    </div>
                    <p class="text-xs text-on-surface-variant leading-relaxed mb-4">
                        "Last-Write-Wins synchronization works flawlessly between my mobile phone and my desktop Cursor setup. Bidirectional MCP notes are the future."
                    </p>
                    <div class="text-[10px] font-mono text-primary font-bold">✓ 240+ WORKSPACES SYNCED</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing / Conversion Section (Featuring Widget #4) -->
    <section class="py-16 bg-surface-white border-b border-border-muted text-center">
        <div class="max-w-3xl mx-auto px-6">
            <h2 class="text-3xl font-bold text-on-surface mb-3">Own Your Personal Memory Layer</h2>
            <p class="text-sm text-on-surface-variant mb-6 leading-relaxed">
                Connect unlimited AI agents, store notes in your own database, and maintain absolute privacy.
            </p>
            
            <div class="inline-block my-2">
                <div class="btn-container">
                    <div class="btn-drawer transition-top">instant access</div>
                    <div class="btn-drawer transition-bottom">...free setup</div>
                    <a href="{' /dashboard' if user_id else '/signup'}" class="btn">
                        <span class="btn-text">{'Launch Gateway' if user_id else 'Create Free Account'}</span>
                    </a>
                    <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                    <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                    <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                    <svg class="btn-corner" xmlns="http://www.w3.org/2000/svg" viewBox="-1 1 32 32"><path d="M32,32C14.355,32,0,17.645,0,0h.985c0,17.102,13.913,31.015,31.015,31.015v.985Z"></path></svg>
                </div>
            </div>
            <p class="text-[11px] font-mono text-text-secondary mt-3">No credit card required. Works with Claude Desktop & Cursor.</p>
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
