from __future__ import annotations

import streamlit as st

# Tileable neural-network motif (nodes + edges) + SVG; sits over grey mesh for a modern ML look.
NN_BG_LAYER_URL = (
    'url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMjAiIGhlaWdodD0iMjIwIiB2aWV3Qm94PSIwIDAgMjIwIDIyMCI+PGcgc3Ryb2tlPSJyZ2JhKDkwLDkwLDk4LDAuMTMpIiBzdHJva2Utd2lkdGg9IjEiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+PHBhdGggZD0iTTI1IDQ1IEw4NSAzNSBMMTQwIDU1IEwxOTUgNDIiLz48cGF0aCBkPSJNMjUgNDUgTDU1IDExNSBMMTAwIDE1NSBMMTY1IDE3NSIvPjxwYXRoIGQ9Ik04NSAzNSBMNTUgMTE1Ii8+PHBhdGggZD0iTTE0MCA1NSBMMTAwIDE1NSIvPjxwYXRoIGQ9Ik0xOTUgNDIgTDE2NSAxNzUiLz48cGF0aCBkPSJNMTAwIDE1NSBMNDAgMTkwIi8+PHBhdGggZD0iTTE0MCA1NSBMMTg1IDEyNSIvPjxwYXRoIGQ9Ik0xODUgMTI1IEwxNjUgMTc1Ii8+PC9nPjxjaXJjbGUgY3g9IjI1IiBjeT0iNDUiIHI9IjMuNSIgZmlsbD0icmdiYSgwLDExMywyMjcsMC4xNikiLz48Y2lyY2xlIGN4PSI4NSIgY3k9IjM1IiByPSIzIiBmaWxsPSJyZ2JhKDAsMTEzLDIyNywwLjEyKSIvPjxjaXJjbGUgY3g9IjE0MCIgY3k9IjU1IiByPSIzLjUiIGZpbGw9InJnYmEoMjMwLDAsMTgsMC4xNCkiLz48Y2lyY2xlIGN4PSIxOTUiIGN5PSI0MiIgcj0iMyIgZmlsbD0icmdiYSgwLDExMywyMjcsMC4xMikiLz48Y2lyY2xlIGN4PSI1NSIgY3k9IjExNSIgcj0iMyIgZmlsbD0icmdiYSgxMDAsMTAwLDExMCwwLjE4KSIvPjxjaXJjbGUgY3g9IjEwMCIgY3k9IjE1NSIgcj0iMy41IiBmaWxsPSJyZ2JhKDIzMCwwLDE4LDAuMTIpIi8+PGNpcmNsZSBjeD0iMTY1IiBjeT0iMTc1IiByPSIzIiBmaWxsPSJyZ2JhKDAsMTEzLDIyNywwLjE0KSIvPjxjaXJjbGUgY3g9IjQwIiBjeT0iMTkwIiByPSIyLjUiIGZpbGw9InJnYmEoOTAsOTAsOTgsMC4yMikiLz48Y2lyY2xlIGN4PSIxODUiIGN5PSIxMjUiIHI9IjIuNSIgZmlsbD0icmdiYSgwLDExMywyMjcsMC4xMykiLz48L3N2Zz4=")'
)


APP_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* —— YouTube Creator Insights — light, glass, Apple-adjacent premium feel —— */
:root {
    --apple-black: #1d1d1f;
    --apple-gray: #424245;
    --apple-gray-2: #6e6e73;
    --apple-bg: #f5f5f7;
    --apple-blue: #0071e3;
    --apple-red: #e60012;
    --yt-red: #ff0000;
    --yt-cyan: #0077ed;
    --glass-bg: rgba(255, 255, 255, 0.94);
    --glass-border: rgba(0, 0, 0, 0.1);
    --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.9) inset;
    --glass-shadow-lg: 0 20px 50px rgba(0, 0, 0, 0.1);
    --mesh-line: rgba(0, 0, 0, 0.06);
    --app-radius-lg: 22px;
    --app-radius-md: 16px;
    --app-radius-pill: 999px;
    --app-control-height: 46px;
    --app-page-width: 1200px;
    --app-section-width: 1120px;
    --app-font-display: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif;
    --app-font-body: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif;
    --app-font-mono: "IBM Plex Mono", ui-monospace, monospace;
}

/* Neural / ML-inspired mesh: soft gradients + grid nodes (no bitmap — production-safe) */
html, body {
    font-family: var(--app-font-body);
    -webkit-font-smoothing: antialiased;
}

[data-testid="stAppViewContainer"] {
    color: var(--apple-black) !important;
    background-color: var(--apple-bg) !important;
    background-image:
        {NN_BG_LAYER},
        radial-gradient(ellipse 100% 80% at 50% -30%, rgba(0, 113, 227, 0.11), transparent 55%),
        radial-gradient(ellipse 70% 50% at 100% 20%, rgba(230, 0, 18, 0.07), transparent 50%),
        radial-gradient(ellipse 60% 40% at 0% 90%, rgba(0, 119, 237, 0.08), transparent 45%),
        radial-gradient(circle at 18% 32%, rgba(0, 113, 227, 0.04) 0%, transparent 42%),
        radial-gradient(circle at 82% 68%, rgba(230, 0, 18, 0.035) 0%, transparent 40%),
        repeating-linear-gradient(0deg, transparent, transparent 39px, var(--mesh-line) 39px, var(--mesh-line) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, var(--mesh-line) 39px, var(--mesh-line) 40px),
        linear-gradient(180deg, #fafafa 0%, var(--apple-bg) 45%, #eef0f4 100%) !important;
    background-size: 220px 220px, auto, auto, auto, auto, auto, auto, auto, auto, auto !important;
    background-repeat: repeat, no-repeat, no-repeat, no-repeat, no-repeat, no-repeat, no-repeat, repeat, repeat, no-repeat !important;
    background-attachment: fixed !important;
}

section[data-testid="stMain"] > div {
    padding-top: 0.85rem !important;
    background: transparent !important;
}

[data-testid="stDecoration"] {
    height: 3px !important;
    min-height: 3px !important;
    background: linear-gradient(90deg, var(--apple-red), var(--apple-blue)) !important;
}

[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.78) !important;
    backdrop-filter: blur(18px) saturate(1.2) !important;
    -webkit-backdrop-filter: blur(18px) saturate(1.2) !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
    min-height: 2.5rem !important;
}

[data-testid="stToolbar"] button { color: var(--apple-black) !important; }

/* —— Sidebar: steel glass + nav “casing” (selected / hover) —— */
[data-testid="stSidebar"] {
    background: linear-gradient(
        165deg,
        rgba(252, 252, 254, 0.97) 0%,
        rgba(228, 230, 238, 0.94) 42%,
        rgba(248, 249, 252, 0.96) 100%
    ) !important;
    backdrop-filter: blur(28px) saturate(1.25) !important;
    -webkit-backdrop-filter: blur(28px) saturate(1.25) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.14) !important;
    box-shadow:
        inset -1px 0 0 rgba(255, 255, 255, 0.9),
        6px 0 32px rgba(0, 0, 0, 0.07) !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] {
    padding: 0.12rem 0.4rem 0.6rem !important;
    gap: 0.2rem !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] li {
    margin: 0 0 0.2rem !important;
    list-style: none !important;
}

[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
    display: flex !important;
    align-items: center !important;
    gap: 0.45rem !important;
    border-radius: 14px !important;
    margin: 0.1rem 0 0 !important;
    padding: 0.55rem 0.75rem 0.55rem 0.65rem !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    background: rgba(255, 255, 255, 0.35) !important;
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.9) inset !important;
    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        transform 0.2s ease !important;
}

[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {
    background: rgba(255, 255, 255, 0.92) !important;
    border-color: rgba(0, 113, 227, 0.22) !important;
    box-shadow:
        0 1px 0 rgba(255, 255, 255, 1) inset,
        0 4px 14px rgba(0, 0, 0, 0.06) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] p {
    color: var(--apple-black) !important;
    font-weight: 600 !important;
}

/* Active page: YouTube-red + glass “case” */
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="true"] {
    background: linear-gradient(
        135deg,
        rgba(255, 0, 0, 0.12) 0%,
        rgba(255, 255, 255, 0.96) 55%,
        rgba(0, 113, 227, 0.06) 100%
    ) !important;
    border: 1px solid rgba(230, 0, 18, 0.35) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.98),
        0 0 0 1px rgba(255, 255, 255, 0.5),
        0 6px 20px rgba(230, 0, 18, 0.14) !important;
    transform: translateY(0) !important;
}

[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] span,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] p,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="true"] span,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="true"] p {
    color: var(--apple-black) !important;
    font-weight: 700 !important;
}

/* Some Streamlit builds mark the active item on the <li> */
[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] li[aria-current="page"] a[data-testid="stSidebarNavLink"] {
    background: linear-gradient(
        135deg,
        rgba(255, 0, 0, 0.12) 0%,
        rgba(255, 255, 255, 0.96) 55%,
        rgba(0, 113, 227, 0.06) 100%
    ) !important;
    border: 1px solid rgba(230, 0, 18, 0.35) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.98),
        0 0 0 1px rgba(255, 255, 255, 0.5),
        0 6px 20px rgba(230, 0, 18, 0.14) !important;
}

[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNavLink"] p,
[data-testid="stSidebar"] a {
    color: var(--apple-black) !important;
}

/* Premium masthead (same language as intro) */
.sidebar-brand-mast {
    margin: 0.1rem 0.35rem 0.75rem;
    padding: 0.85rem 1rem 1.1rem;
    border-radius: 18px;
    background: linear-gradient(
        165deg,
        rgba(255, 255, 255, 0.96) 0%,
        rgba(228, 230, 238, 0.9) 100%
    );
    border: 1px solid rgba(0, 0, 0, 0.12);
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.98),
        0 10px 36px rgba(0, 0, 0, 0.08);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}

.sidebar-brand-emblem {
    width: 100%;
    height: 108px;
    margin-bottom: 0.8rem;
    border-radius: 16px;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 50% 14%, rgba(255, 79, 79, 0.28), transparent 38%),
        radial-gradient(circle at 50% 108%, rgba(6, 14, 28, 0.6), transparent 42%),
        linear-gradient(165deg, #0d1c31 0%, #0a1324 52%, #060d19 100%);
    border: 1px solid rgba(255, 74, 74, 0.35);
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.12),
        0 0 28px rgba(230, 0, 18, 0.22),
        0 10px 26px rgba(0, 0, 0, 0.3);
}

.sidebar-brand-emblem::before {
    content: "";
    position: absolute;
    inset: 9px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    pointer-events: none;
}

.sidebar-brand-emblem-head {
    position: absolute;
    left: 50%;
    top: 24px;
    transform: translateX(-50%);
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(165deg, #ff5a5a 0%, #ff0000 52%, #b00010 100%);
    box-shadow:
        0 6px 18px rgba(230, 0, 18, 0.36),
        inset 0 -8px 16px rgba(0, 0, 0, 0.22);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
}

.sidebar-brand-emblem-head::before,
.sidebar-brand-emblem-head::after {
    content: "";
    position: absolute;
    top: 20px;
    width: 7px;
    height: 17px;
    border-radius: 6px;
    background: linear-gradient(180deg, #ff8888, #f44);
    opacity: 0.9;
}

.sidebar-brand-emblem-head::before { left: -10px; }
.sidebar-brand-emblem-head::after { right: -10px; }

.sidebar-brand-emblem-eye {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #bff0ff 0%, #7fd8ff 55%, #43bcff 100%);
    box-shadow: 0 0 8px rgba(117, 221, 255, 0.7);
}

.sidebar-brand-emblem-smile {
    position: absolute;
    left: 50%;
    top: 59px;
    transform: translateX(-50%);
    width: 22px;
    height: 11px;
    border: 3px solid #ff9b9b;
    border-top: 0;
    border-left-color: transparent;
    border-right-color: transparent;
    border-bottom-left-radius: 16px;
    border-bottom-right-radius: 16px;
    opacity: 0.95;
}

.sidebar-brand-row {
    display: flex;
    flex-direction: row;
    align-items: stretch;
    gap: 0.95rem;
}

.sidebar-brand-bar-col {
    display: flex;
    align-items: stretch;
    flex-shrink: 0;
}

.sidebar-brand-bar {
    width: 8px;
    min-height: 96px;
    border-radius: 4px;
    background: linear-gradient(180deg, #ff3333 0%, #ff0000 40%, #cc0000 100%);
    box-shadow:
        0 0 22px rgba(255, 0, 0, 0.5),
        0 6px 20px rgba(230, 0, 18, 0.25);
}

.sidebar-brand-copy {
    flex: 1;
    min-width: 0;
    text-align: left;
}

.sidebar-brand-yt {
    font-size: clamp(1.65rem, 4vw, 2.35rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.035em;
}

.sidebar-brand-yt-gradient {
    background: linear-gradient(135deg, #ff0000 0%, #e60012 55%, #cc0000 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.sidebar-brand-ci {
    font-size: 1.02rem;
    font-weight: 800;
    color: #1d1d1f;
    letter-spacing: -0.02em;
    margin-top: 0.2rem;
    line-height: 1.2;
}

.sidebar-brand-line {
    height: 3px;
    width: min(100%, 110px);
    margin: 0.55rem 0 0.4rem;
    border-radius: 999px;
    background: linear-gradient(90deg, transparent, #ff0000 20%, #ff0000 80%, transparent);
}

.sidebar-brand-sub {
    font-size: 10px;
    font-weight: 600;
    color: #6e6e73;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.sidebar-nav-label {
    margin: 0.35rem 0.75rem 0.55rem;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6e6e73;
}

[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button {
    background: linear-gradient(160deg, rgba(255, 255, 255, 1), rgba(220, 226, 238, 0.96)) !important;
    border: 1.5px solid rgba(0, 0, 0, 0.28) !important;
    color: var(--apple-black) !important;
    min-width: 34px !important;
    min-height: 34px !important;
    border-radius: 10px !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 1),
        0 0 0 1px rgba(255, 255, 255, 0.7),
        0 6px 18px rgba(0, 0, 0, 0.16) !important;
}

[data-testid="stSidebarCollapsedControl"] button:hover,
[data-testid="collapsedControl"] button:hover {
    border-color: rgba(230, 0, 18, 0.45) !important;
    background: linear-gradient(160deg, rgba(255, 255, 255, 1), rgba(233, 238, 248, 0.98)) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 1),
        0 0 0 2px rgba(0, 113, 227, 0.18),
        0 8px 22px rgba(0, 0, 0, 0.2) !important;
}

[data-testid="stSidebarCollapsedControl"] button:focus-visible,
[data-testid="collapsedControl"] button:focus-visible {
    outline: 2px solid rgba(0, 113, 227, 0.5) !important;
    outline-offset: 2px !important;
}

[data-testid="stSidebarCollapsedControl"] button svg,
[data-testid="collapsedControl"] button svg {
    color: #111216 !important;
    stroke: #111216 !important;
    fill: #111216 !important;
    stroke-width: 2px !important;
}

.block-container {
    max-width: var(--app-page-width) !important;
    padding-top: 1.75rem !important;
    padding-bottom: 2.75rem;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.18);
    border-radius: 4px;
}

/* —— Global feature hero (glass) —— */
.glass-page-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    max-width: 920px;
    margin: 0 auto 1.75rem;
    padding: 2rem 1.75rem 1.85rem;
    border-radius: var(--app-radius-lg);
    background:
        radial-gradient(circle at 12% 12%, rgba(230, 0, 18, 0.06), transparent 34%),
        radial-gradient(circle at 88% 18%, rgba(0, 113, 227, 0.07), transparent 36%),
        linear-gradient(165deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 243, 249, 0.94) 100%);
    backdrop-filter: blur(30px) saturate(1.28);
    -webkit-backdrop-filter: blur(30px) saturate(1.28);
    border: 1px solid rgba(0, 0, 0, 0.12);
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 1),
        0 28px 65px rgba(0, 0, 0, 0.12),
        0 12px 30px rgba(0, 113, 227, 0.08),
        0 16px 38px rgba(230, 0, 18, 0.09);
    position: relative;
    overflow: hidden;
}

.glass-page-hero::after {
    content: "";
    position: absolute;
    inset: 8px;
    border-radius: calc(var(--app-radius-lg) - 8px);
    border: 1px solid rgba(255, 255, 255, 0.78);
    pointer-events: none;
}

.product-eyebrow {
    margin: 0 0 1rem;
    font-size: 1.85rem;
    font-weight: 900;
    letter-spacing: -0.018em;
    line-height: 1.1;
    background: linear-gradient(180deg, #fdfdff 0%, #d3d9e4 36%, #6f7786 62%, #1f242c 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow:
        0 1px 0 rgba(255, 255, 255, 0.9),
        0 8px 24px rgba(0, 0, 0, 0.08);
    font-family: var(--app-font-display);
}

.product-eyebrow-sep {
    margin: 0 0.42rem;
    opacity: 0.72;
    color: #a0a6b4;
}

.product-eyebrow-red {
    color: var(--apple-red);
    font-weight: 800;
}

.feature-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.35rem 0.85rem;
    border-radius: var(--app-radius-pill);
    background: linear-gradient(140deg, rgba(255, 255, 255, 0.94), rgba(242, 245, 251, 0.92));
    border: 1px solid rgba(0, 0, 0, 0.12);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--apple-black);
    margin-bottom: 1rem;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.95),
        0 5px 16px rgba(0, 0, 0, 0.08),
        0 2px 8px rgba(0, 113, 227, 0.08);
}

.feature-badge-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--apple-red), var(--apple-blue));
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.9);
}

.feature-headline {
    margin: 0 0 0.85rem;
    font-family: var(--app-font-display);
    font-size: clamp(1.65rem, 3.2vw, 2.35rem);
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1.12;
    color: #14161b;
    text-shadow: 0 8px 22px rgba(0, 0, 0, 0.08);
}

.feature-description {
    display: block;
    width: 100%;
    margin: 0 auto;
    max-width: 720px;
    text-align: center !important;
    font-size: 1.05rem;
    line-height: 1.55;
    color: var(--apple-gray);
    font-weight: 400;
}

.glass-page-hero > .feature-description {
    align-self: center;
    justify-self: center;
    text-align: center !important;
}

.feature-hero-tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1.35rem;
}

.feature-hero-tag {
    display: inline-flex;
    padding: 0.4rem 0.85rem;
    border-radius: var(--app-radius-pill);
    font-size: 12px;
    font-weight: 600;
    color: var(--apple-black);
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

@media (max-width: 980px) {
    .glass-page-hero {
        padding: 1.55rem 1.05rem 1.45rem;
    }
    .product-eyebrow {
        font-size: 1.25rem;
    }
}

.feature-hero-tag--accent-r {
    border-color: rgba(230, 0, 18, 0.35);
    color: #b3000c;
}

.feature-hero-tag--accent-b {
    border-color: rgba(0, 113, 227, 0.35);
    color: #0058b0;
}

/* Legacy shell classes (safe if referenced) */
.yt-app-hero-shell { overflow: visible !important; }

/* Section headers & cards — glass on mesh */
.yt-section-header {
    font-family: var(--app-font-display);
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    color: var(--apple-black);
}

.yt-section-underline {
    width: 72px;
    height: 3px;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--apple-red), var(--apple-blue));
    margin-bottom: 1rem;
}

.metric-row { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem; }

.metric-card {
    flex: 1 1 160px;
    padding: 1rem 1.1rem;
    border-radius: var(--app-radius-md);
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
    transition: transform 0.15s ease, box-shadow 0.15s;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.1);
}

.metric-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--apple-gray-2);
    margin-bottom: 0.2rem;
    font-weight: 600;
}

.metric-value {
    font-family: var(--app-font-display);
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--apple-black);
}

.metric-delta.positive { color: #0a7f2e; }
.metric-delta.negative { color: #c40018; }

/* Plotly charts use the same glass surface as the rest of the product.
   Plot and paper backgrounds stay transparent in Python; this container owns
   elevation, border, blur, and responsive clipping. */
[data-testid="stPlotlyChart"] {
    position: relative;
    overflow: hidden;
    margin: 0.45rem 0 1rem;
    padding: 0.2rem 0.38rem 0.05rem;
    border: 1px solid rgba(23, 23, 26, 0.10);
    border-radius: 20px;
    background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.86), rgba(248, 249, 252, 0.72));
    box-shadow:
        0 18px 52px rgba(26, 30, 40, 0.09),
        inset 0 1px 0 rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(18px) saturate(1.24);
    -webkit-backdrop-filter: blur(18px) saturate(1.24);
}

[data-testid="stPlotlyChart"]::after {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    border-radius: inherit;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.30);
}

[data-testid="stPlotlyChart"] > div,
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container {
    position: relative;
    z-index: 1;
    background: transparent !important;
}

[data-testid="stPlotlyChart"] .modebar {
    top: 8px !important;
    right: 8px !important;
    padding: 3px 5px !important;
    border: 1px solid rgba(23, 23, 26, 0.09) !important;
    border-radius: 999px !important;
    background: rgba(255, 255, 255, 0.90) !important;
    box-shadow: 0 5px 16px rgba(26, 30, 40, 0.09) !important;
}

[data-testid="stPlotlyChart"] .modebar-btn path {
    fill: #6e6e73 !important;
}

[data-testid="stPlotlyChart"] .modebar-btn:hover path,
[data-testid="stPlotlyChart"] .modebar-btn.active path {
    fill: #0071e3 !important;
}

@media (max-width: 640px) {
    [data-testid="stPlotlyChart"] {
        margin-bottom: 0.75rem;
        padding: 0;
        border-radius: 16px;
    }

    [data-testid="stPlotlyChart"] .gtitle {
        font-size: 14px !important;
    }

    [data-testid="stPlotlyChart"] .xtitle,
    [data-testid="stPlotlyChart"] .ytitle {
        font-size: 10px !important;
    }

    /* Hover-only export controls obstruct chart titles on touch-width views. */
    [data-testid="stPlotlyChart"] .modebar {
        display: none !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    [data-testid="stPlotlyChart"] * {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
    }
}

.styled-dataframe thead tr th {
    background: linear-gradient(90deg, rgba(230, 0, 18, 0.12), rgba(0, 113, 227, 0.1)) !important;
    color: var(--apple-black) !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.styled-dataframe tbody tr:nth-child(odd) { background-color: rgba(0, 0, 0, 0.02); }
.styled-dataframe tbody tr:nth-child(even) { background-color: rgba(255, 255, 255, 0.7); }

/* Streamlit dataframe / data editor — steel glass table shell */
[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    border-radius: 14px !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    background: linear-gradient(165deg, rgba(255, 255, 255, 0.95), rgba(235, 238, 245, 0.9)) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.98),
        0 10px 32px rgba(0, 0, 0, 0.08) !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataEditor"] [role="columnheader"] {
    background: linear-gradient(180deg, rgba(240, 243, 249, 0.98), rgba(228, 232, 240, 0.95)) !important;
    color: #1d1d1f !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.12) !important;
    font-weight: 700 !important;
}

[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataEditor"] [role="gridcell"] {
    background: rgba(255, 255, 255, 0.9) !important;
    color: #1d1d1f !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
}

[data-testid="stDataFrame"] [role="row"]:nth-child(even) [role="gridcell"],
[data-testid="stDataEditor"] [role="row"]:nth-child(even) [role="gridcell"] {
    background: rgba(246, 248, 252, 0.92) !important;
}

[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"],
[data-testid="stDataEditor"] [role="row"]:hover [role="gridcell"] {
    background: rgba(231, 239, 255, 0.8) !important;
}

.stButton > button,
.stFormSubmitButton > button {
    min-height: var(--app-control-height) !important;
    border-radius: 999px !important;
    font-family: var(--app-font-display) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

button[kind="primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #ff1a1a, var(--yt-red)) !important;
    color: #fff !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    box-shadow: 0 6px 20px rgba(230, 0, 18, 0.35) !important;
}

.stButton > button:not([kind="primary"]),
button[kind="secondary"],
.stDownloadButton > button {
    background: rgba(255, 255, 255, 0.98) !important;
    color: var(--apple-black) !important;
    border: 1px solid rgba(0, 0, 0, 0.14) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
}

.stButton > button:not([kind="primary"]):hover,
button[kind="secondary"]:hover {
    border-color: rgba(0, 0, 0, 0.22) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1) !important;
}

.stTextInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    color: var(--apple-black) !important;
}

/* Normalize all text-like controls to avoid dark/navy edge wrappers */
[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div,
.stTextInput > div > div,
.stTextArea > div > div,
[data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stTextArea"] [data-baseweb="textarea"] > div {
    background: rgba(255, 255, 255, 0.98) !important;
    border: 1px solid rgba(0, 0, 0, 0.16) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.98),
        0 2px 8px rgba(0, 0, 0, 0.05) !important;
}

[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within,
[data-baseweb="input"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within,
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: rgba(230, 0, 18, 0.36) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 1),
        0 0 0 2px rgba(0, 113, 227, 0.14),
        0 4px 10px rgba(0, 0, 0, 0.08) !important;
}

[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
.stTextInput input,
.stTextArea textarea {
    color: #1d1d1f !important;
    -webkit-text-fill-color: #1d1d1f !important;
    background: transparent !important;
}

/* Password eye / inline icon buttons should not create dark blocks */
[data-baseweb="input"] button,
[data-baseweb="textarea"] button {
    background: rgba(255, 255, 255, 0.98) !important;
    border-left: 1px solid rgba(0, 0, 0, 0.12) !important;
    color: #6e6e73 !important;
}

.stTextInput input::placeholder { color: #86868b !important; }

[data-testid="stSegmentedControl"] {
    background: rgba(255, 255, 255, 0.96) !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) inset;
    overflow: hidden !important;
}

[data-testid="stSegmentedControl"] p,
[data-testid="stSegmentedControl"] label,
[data-testid="stSegmentedControl"] [role="radio"],
[data-testid="stSegmentedControl"] button {
    color: var(--apple-black) !important;
    opacity: 1 !important;
}

/* Unselected segmented items: keep white (never dark blocks) */
[data-testid="stSegmentedControl"] [role="radio"]:not([aria-checked="true"]),
[data-testid="stSegmentedControl"] button:not([aria-pressed="true"]),
[data-testid="stSegmentedControl"] label:not([data-selected="true"]) {
    background: rgba(255, 255, 255, 0.98) !important;
    color: #1d1d1f !important;
    border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
}

/* Baseweb segmented internals (unselected pills were still dark in some renders) */
[data-testid="stSegmentedControl"] [role="radiogroup"] > *,
[data-testid="stSegmentedControl"] [role="radiogroup"] > * > *,
[data-testid="stSegmentedControl"] [data-baseweb="button-group"] > *,
[data-testid="stSegmentedControl"] [data-baseweb="button-group"] button {
    background: linear-gradient(165deg, rgba(255, 255, 255, 1), rgba(240, 244, 250, 0.98)) !important;
    color: #1d1d1f !important;
    border-color: rgba(0, 0, 0, 0.1) !important;
}

/* Nested text wrappers inside unselected segmented options */
[data-testid="stSegmentedControl"] [aria-checked="false"] *,
[data-testid="stSegmentedControl"] [data-selected="false"] * {
    background: transparent !important;
    color: #1d1d1f !important;
    opacity: 1 !important;
}

[data-testid="stSegmentedControl"] [aria-checked="false"],
[data-testid="stSegmentedControl"] [data-selected="false"] {
    background: linear-gradient(165deg, rgba(255, 255, 255, 1), rgba(240, 244, 250, 0.98)) !important;
    color: #1d1d1f !important;
}

[data-testid="stSegmentedControl"] [aria-checked="true"],
[data-testid="stSegmentedControl"] [data-selected="true"] {
    background: linear-gradient(180deg, rgba(0, 113, 227, 0.2), rgba(230, 0, 18, 0.12)) !important;
    color: var(--apple-black) !important;
    font-weight: 600 !important;
    box-shadow: inset 0 0 0 1px rgba(230, 0, 18, 0.35) !important;
}

[data-testid="stSegmentedControl"] [aria-checked="true"] *,
[data-testid="stSegmentedControl"] [data-selected="true"] * {
    color: #8f000c !important;
    opacity: 1 !important;
}

.stToggle label, .stCheckbox label, .stRadio label, .stSelectbox label,
.stTextInput label, .stMultiSelect label, .stDateInput label, .stSlider label,
.stNumberInput label { color: var(--apple-black) !important; font-weight: 600 !important; }

/* Streamlit widget labels (Baseweb) — force dark ink on light mesh */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"] span,
label[data-testid="stWidgetLabel"] p {
    color: var(--apple-black) !important;
    opacity: 1 !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: var(--apple-gray);
}

/* Alerts: never white text on pale yellow/blue */
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span,
[data-testid="stAlert"] code {
    color: var(--apple-black) !important;
}

[data-testid="stAlert"] {
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
}

/* Multiselect tags — readable chips (not flat red-on-white failures) */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: linear-gradient(180deg, #fff5f5, #ffecec) !important;
    border: 1px solid rgba(230, 0, 18, 0.35) !important;
    color: var(--apple-black) !important;
}

[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
    color: var(--apple-black) !important;
}

.stDateInput input,
[data-testid="stDateInput"] input {
    color: var(--apple-black) !important;
}

/* Number steppers (+ / -): light steel buttons with strong icon contrast */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] [data-baseweb="input"] button {
    background: linear-gradient(160deg, rgba(255, 255, 255, 1), rgba(233, 238, 248, 0.96)) !important;
    color: #14161b !important;
    border: 1px solid rgba(15, 23, 42, 0.12) !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 1) !important;
}

[data-testid="stNumberInput"] button:hover,
[data-testid="stNumberInput"] [data-baseweb="input"] button:hover {
    border-color: rgba(230, 0, 18, 0.4) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 1),
        0 0 0 2px rgba(0, 113, 227, 0.12) !important;
}

[data-testid="stNumberInput"] button svg,
[data-testid="stNumberInput"] [data-baseweb="input"] button svg {
    stroke: #111216 !important;
    color: #111216 !important;
    fill: #111216 !important;
}

.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.stTabs [data-baseweb="tab"] p { color: var(--apple-gray-2) !important; }
[aria-selected="true"] p { color: var(--apple-black) !important; font-weight: 600 !important; }

[data-testid="stExpander"] {
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: var(--app-radius-md) !important;
    background: rgba(255, 255, 255, 0.94) !important;
    backdrop-filter: blur(12px);
}

[data-testid="stExpander"] summary {
    color: var(--apple-black) !important;
    font-weight: 600 !important;
    padding-left: 0.7rem !important;
    border-left: 3px solid rgba(230, 0, 18, 0.55) !important;
}

.yt-card {
    border-radius: var(--app-radius-lg);
    padding: 1.15rem 1.3rem;
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.09);
    margin-bottom: 1.15rem;
}

.yt-callout-info {
    border-radius: var(--app-radius-md);
    padding: 1rem 1.15rem;
    background: rgba(0, 113, 227, 0.06);
    border: 1px solid rgba(0, 113, 227, 0.25);
    border-left: 4px solid var(--apple-blue);
    color: var(--apple-gray);
    line-height: 1.6;
    font-size: 14px;
}

.yt-callout-info strong { color: var(--apple-black); }
.yt-callout-info code {
    background: rgba(0, 0, 0, 0.06);
    color: #0058b0;
    padding: 0.12rem 0.4rem;
    border-radius: 6px;
    font-family: var(--app-font-mono);
    font-size: 12px;
}

.yt-callout-recommend {
    border-radius: var(--app-radius-md);
    padding: 1.1rem 1.2rem;
    background: rgba(230, 0, 18, 0.06);
    border: 1px solid rgba(230, 0, 18, 0.25);
    color: var(--apple-gray);
    margin-bottom: 1.25rem;
    line-height: 1.62;
}

.yt-callout-recommend h4 {
    margin: 0 0 0.5rem;
    color: #b3000c;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.yt-summary-panel {
    border-radius: var(--app-radius-lg);
    padding: 1.2rem 1.35rem;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.07);
    margin-bottom: 1.5rem;
    position: relative;
}

.yt-summary-panel::before {
    content: "";
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: linear-gradient(180deg, var(--apple-red), var(--apple-blue));
    border-radius: 4px 0 0 4px;
}

.yt-summary-panel h3 {
    margin: 0 0 0.65rem;
    padding-left: 0.5rem;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #0058b0;
}

.strategy-summary-list {
    margin: 0;
    padding-left: 1.4rem;
    color: var(--apple-gray);
    font-size: 14px;
    line-height: 1.65;
}

.strategy-summary-list strong { color: var(--apple-black); }

.app-section-title {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--apple-black);
}

.app-section-copy { color: var(--apple-gray); font-size: 14px; line-height: 1.6; }

.app-meta-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.75rem;
    border-radius: var(--app-radius-pill);
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.1);
    font-size: 12px;
    color: var(--apple-gray);
}

.keyword-chip {
    display: inline-flex;
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    margin: 0.1rem;
    font-size: 12px;
    font-weight: 500;
    background: rgba(0, 113, 227, 0.08);
    border: 1px solid rgba(0, 113, 227, 0.2);
    color: var(--apple-black);
}

.thumb-card {
    border-radius: 16px;
    overflow: hidden;
    background: #fff;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.1);
}

.thumb-card-footer { color: var(--apple-gray-2) !important; }

.metric-icon { display: none !important; }

div[data-testid="stCaption"] { color: var(--apple-gray-2) !important; }

div[data-testid="stMarkdownContainer"] h1 { color: var(--apple-black); font-weight: 800; }
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3 { color: var(--apple-black); font-weight: 700; }

.fade-in {
    animation: fadeIn 0.45s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.app-hero-kicker { color: var(--apple-blue); font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.app-hero-blurb { color: var(--apple-gray); font-size: 14px; line-height: 1.6; max-width: 820px; }

/* --- Global light-enforcement: remove remaining dark popup/control states --- */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="tooltip"],
[role="listbox"],
ul[role="listbox"],
div[role="listbox"] {
    background: linear-gradient(165deg, rgba(255, 255, 255, 0.99), rgba(240, 244, 250, 0.97)) !important;
    color: #1d1d1f !important;
    border: 1px solid rgba(0, 0, 0, 0.15) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.98),
        0 10px 28px rgba(0, 0, 0, 0.12) !important;
}

/* Tiny help/info icon buttons: keep light and visible */
[aria-label*="help" i],
[aria-label*="info" i],
[data-testid*="stTooltipHoverTarget"] button,
[data-testid*="stTooltipIcon"],
[data-testid*="stTooltipIcon"] *,
[data-testid*="stHelpIcon"],
[data-testid*="stHelp"] button {
    background: linear-gradient(165deg, rgba(255, 255, 255, 1), rgba(236, 241, 249, 0.98)) !important;
    color: #111216 !important;
    border: 1px solid rgba(0, 0, 0, 0.2) !important;
    border-radius: 8px !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 1),
        0 3px 10px rgba(0, 0, 0, 0.1) !important;
}

[aria-label*="help" i]:hover,
[aria-label*="info" i]:hover,
[data-testid*="stTooltipHoverTarget"] button:hover,
[data-testid*="stTooltipIcon"]:hover,
[data-testid*="stHelpIcon"]:hover,
[data-testid*="stHelp"] button:hover {
    background: linear-gradient(165deg, rgba(255, 255, 255, 1), rgba(242, 246, 253, 0.98)) !important;
    color: #111216 !important;
    border-color: rgba(230, 0, 18, 0.42) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 1),
        0 0 0 2px rgba(0, 113, 227, 0.14),
        0 6px 14px rgba(0, 0, 0, 0.12) !important;
}

[aria-label*="help" i] svg,
[aria-label*="info" i] svg,
[data-testid*="stTooltipHoverTarget"] button svg,
[data-testid*="stTooltipIcon"] svg,
[data-testid*="stHelpIcon"] svg,
[data-testid*="stHelp"] button svg {
    stroke: #111216 !important;
    fill: #111216 !important;
    color: #111216 !important;
}

/* If Streamlit renders icon wrappers (not button elements), inject bulb symbol */
[data-testid*="stTooltipIcon"],
[data-testid*="stHelpIcon"] {
    position: relative !important;
    border-radius: 999px !important;
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: transparent !important;
}
[data-testid="stWidgetLabel"] [data-testid*="stTooltipHoverTarget"] button,
[data-testid="stWidgetLabel"] [data-testid*="stTooltipIcon"],
[data-testid="stWidgetLabel"] [data-testid*="stHelpIcon"] {
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    border-radius: 999px !important;
    background: linear-gradient(165deg, #fffaf0, #fff3d9) !important;
    border: 1px solid rgba(230, 0, 18, 0.42) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    color: transparent !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stWidgetLabel"] [data-testid*="stTooltipHoverTarget"] button *,
[data-testid="stWidgetLabel"] [data-testid*="stTooltipIcon"] *,
[data-testid="stWidgetLabel"] [data-testid*="stHelpIcon"] * {
    opacity: 0 !important;
    color: transparent !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
[data-testid*="stTooltipIcon"]::before,
[data-testid*="stHelpIcon"]::before {
    content: "💡";
    font-size: 13px;
    line-height: 1;
}
[data-testid="stWidgetLabel"] [data-testid*="stTooltipHoverTarget"] button::before,
[data-testid="stWidgetLabel"] [data-testid*="stTooltipIcon"]::before,
[data-testid="stWidgetLabel"] [data-testid*="stHelpIcon"]::before {
    content: "💡";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -54%);
    font-size: 13px;
    line-height: 1;
    opacity: 1 !important;
}

/* Tooltip body/content should never go dark */
[data-baseweb="tooltip"] *,
[role="tooltip"] * {
    background: transparent !important;
    color: #1d1d1f !important;
}

[role="option"],
li[role="option"],
div[role="option"] {
    background: rgba(255, 255, 255, 0.98) !important;
    color: #1d1d1f !important;
}

[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"],
div[role="option"][aria-selected="true"] {
    background: linear-gradient(165deg, rgba(255, 243, 243, 0.98), rgba(240, 246, 255, 0.96)) !important;
    color: #8d000c !important;
}

[role="option"]:hover,
li[role="option"]:hover,
div[role="option"]:hover {
    background: rgba(233, 241, 255, 0.92) !important;
    color: #1d1d1f !important;
}

/* Date picker / range calendar — single light theme (no light-on-white from mixed rules) */
[data-baseweb="popover"]:has([data-baseweb="calendar"]),
[data-baseweb="datepicker"],
[data-baseweb="datepicker"] [role="dialog"],
[data-baseweb="calendar"] {
    background: linear-gradient(165deg, rgba(255, 255, 255, 0.99), rgba(240, 244, 250, 0.97)) !important;
    border: 1px solid rgba(0, 0, 0, 0.14) !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.98),
        0 12px 30px rgba(0, 0, 0, 0.12) !important;
}

/* Default: dark ink on light chrome for every calendar node (Baseweb range pickers vary DOM depth) */
[data-baseweb="calendar"] *,
[data-baseweb="datepicker"] [data-baseweb="calendar"] *,
[data-baseweb="datepicker"] [role="dialog"] * {
    color: #111216 !important;
    fill: #111216 !important;
    stroke: #111216 !important;
    -webkit-text-fill-color: #111216 !important;
    opacity: 1 !important;
}

/* Month/year nav strip + weekday row: explicit light surface so text is never “ghost” */
[data-baseweb="calendar"] > div:first-child,
[data-baseweb="calendar"] > div:nth-child(2),
[data-baseweb="datepicker"] [data-baseweb="calendar"] > div:first-child,
[data-baseweb="datepicker"] [data-baseweb="calendar"] > div:nth-child(2),
[data-baseweb="calendar"] [role="heading"],
[data-baseweb="datepicker"] [role="heading"],
[data-baseweb="calendar"] [class*="MonthHeader"],
[data-baseweb="calendar"] [class*="WeekdaysRow"],
[data-baseweb="calendar"] [class*="WeekdaysContainer"],
[data-baseweb="calendar"] [class*="header"],
[data-baseweb="calendar"] [class*="Header"] {
    background: linear-gradient(180deg, rgba(250, 251, 253, 1), rgba(236, 241, 248, 0.96)) !important;
    color: #111216 !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
}

[data-baseweb="calendar"] > div:first-child *,
[data-baseweb="calendar"] > div:nth-child(2) *,
[data-baseweb="datepicker"] [data-baseweb="calendar"] > div:first-child *,
[data-baseweb="datepicker"] [data-baseweb="calendar"] > div:nth-child(2) *,
[data-baseweb="calendar"] [role="heading"] *,
[data-baseweb="datepicker"] [role="heading"] * {
    color: #111216 !important;
    fill: #111216 !important;
    stroke: #111216 !important;
    -webkit-text-fill-color: #111216 !important;
}

[data-baseweb="calendar"] [role="columnheader"],
[data-baseweb="datepicker"] [role="columnheader"] {
    background: rgba(238, 242, 248, 0.95) !important;
    color: #111216 !important;
    font-weight: 600 !important;
}

/* Day grid: light panel (not navy) so all day numbers read clearly */
[data-baseweb="calendar"] [role="grid"],
[data-baseweb="calendar"] [role="row"],
[data-baseweb="calendar"] table {
    background: rgba(255, 255, 255, 0.98) !important;
}

[data-baseweb="calendar"] [role="gridcell"],
[data-baseweb="calendar"] [role="grid"] button {
    color: #111216 !important;
    background: transparent !important;
}

[data-baseweb="calendar"] button,
[data-baseweb="datepicker"] button {
    background: transparent !important;
    color: #111216 !important;
}

[data-baseweb="calendar"] button:hover,
[data-baseweb="datepicker"] button:hover {
    background: rgba(233, 241, 255, 0.95) !important;
    color: #111216 !important;
}

/* Selected / keyboard-focused day — include children so label stays white on red */
[data-baseweb="calendar"] [aria-selected="true"],
[data-baseweb="datepicker"] [aria-selected="true"],
[data-baseweb="calendar"] [data-selected="true"],
[data-baseweb="datepicker"] [data-selected="true"] {
    background: #e60012 !important;
    color: #ffffff !important;
    border-radius: 999px !important;
}

[data-baseweb="calendar"] [aria-selected="true"] *,
[data-baseweb="datepicker"] [aria-selected="true"] *,
[data-baseweb="calendar"] [data-selected="true"] *,
[data-baseweb="datepicker"] [data-selected="true"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-baseweb="calendar"] [aria-current="date"],
[data-baseweb="datepicker"] [aria-current="date"] {
    box-shadow: inset 0 0 0 1px rgba(0, 113, 227, 0.35) !important;
    border-radius: 999px !important;
}

/* Range picker footer (presets / “None”) — readable on white */
[data-baseweb="calendar"] [aria-label*="Choose a date range" i],
[data-baseweb="calendar"] [aria-label*="Choose a date range" i] *,
[data-baseweb="calendar"] [data-baseweb="select"] input,
[data-baseweb="calendar"] [data-baseweb="select"] > div {
    color: #111216 !important;
    -webkit-text-fill-color: #111216 !important;
    background: rgba(255, 255, 255, 0.98) !important;
}

/* Dropdown triggers / headers must stay light after blur */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: rgba(255, 255, 255, 0.98) !important;
    color: #1d1d1f !important;
    border: 1px solid rgba(0, 0, 0, 0.14) !important;
}

[data-baseweb="select"] input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
.stTextInput input,
.stTextArea textarea {
    color: #1d1d1f !important;
    background: transparent !important;
    caret-color: #1d1d1f !important;
}

/* Expander summary rows: no dark bars */
[data-testid="stExpander"] summary {
    background: linear-gradient(165deg, rgba(255, 255, 255, 0.97), rgba(238, 242, 250, 0.92)) !important;
    color: #1d1d1f !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 12px !important;
    padding: 0.52rem 0.7rem !important;
}

/* Sliders / bars */
[data-baseweb="slider"] [role="slider"] {
    background: #ff0000 !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.22) !important;
}
[data-baseweb="slider"] [data-testid*="track"],
[data-baseweb="slider"] [class*="track"] {
    background: linear-gradient(90deg, #ff0000, #0071e3) !important;
}

/* Sidebar collapse button wrapper visibility */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 10px !important;
}

/* —— 2026 product-system consolidation: calm surfaces, clear controls, visible focus —— */
:root {
    --ui-surface: rgba(255, 255, 255, 0.92);
    --ui-surface-solid: #ffffff;
    --ui-surface-subtle: #f6f8fb;
    --ui-border: #d9dee7;
    --ui-border-strong: #b8c0cc;
    --ui-text: #17181b;
    --ui-muted: #636a75;
    --ui-focus: rgba(0, 113, 227, 0.22);
    --ui-shadow-sm: 0 1px 2px rgba(17, 24, 39, 0.05);
    --ui-shadow-md: 0 10px 30px rgba(17, 24, 39, 0.07);
    --ui-radius: 12px;
    --ui-radius-lg: 18px;
}

html, body, [class*="css"] {
    color: var(--ui-text) !important;
    line-height: 1.5;
}

[data-testid="stAppViewContainer"] {
    background-image:
        {NN_BG_LAYER},
        radial-gradient(ellipse 85% 65% at 50% -25%, rgba(0, 113, 227, 0.08), transparent 58%),
        radial-gradient(ellipse 55% 45% at 100% 18%, rgba(230, 0, 18, 0.045), transparent 55%),
        repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(0, 0, 0, 0.035) 39px, rgba(0, 0, 0, 0.035) 40px),
        repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(0, 0, 0, 0.035) 39px, rgba(0, 0, 0, 0.035) 40px),
        linear-gradient(180deg, #fbfcfd 0%, #f5f6f8 54%, #eef1f5 100%) !important;
    background-size: 220px 220px, auto, auto, auto, auto, auto !important;
    background-repeat: repeat, no-repeat, no-repeat, repeat, repeat, no-repeat !important;
}

/* Keep decoration subordinate to the work. */
.yt-page-hero {
    padding: clamp(2.4rem, 5vw, 4.6rem) clamp(1.25rem, 4vw, 3.25rem) !important;
    border-radius: var(--ui-radius-lg) !important;
    border-color: rgba(255, 255, 255, 0.86) !important;
    box-shadow: var(--ui-shadow-md) !important;
}

.yt-page-hero h1,
.yt-page-title {
    max-width: 980px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    text-wrap: balance;
}

.yt-page-hero p,
.yt-page-description {
    max-width: 760px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    text-align: center !important;
    color: #4f5661 !important;
    text-wrap: pretty;
}

.yt-section-header {
    margin-top: 2rem !important;
    margin-bottom: 0.15rem !important;
}

.yt-section-header span {
    font-size: clamp(1.25rem, 1.5vw, 1.55rem) !important;
    letter-spacing: -0.02em !important;
}

.yt-section-underline {
    width: 44px !important;
    height: 3px !important;
    border-radius: 3px !important;
    background: linear-gradient(90deg, var(--apple-red), var(--apple-blue)) !important;
    margin-bottom: 1rem !important;
}

/* Static information should not impersonate a clickable card. */
.metric-card {
    border: 1px solid rgba(17, 24, 39, 0.10) !important;
    border-radius: var(--ui-radius-lg) !important;
    background: var(--ui-surface) !important;
    box-shadow: var(--ui-shadow-sm) !important;
    transition: border-color 160ms ease, box-shadow 160ms ease !important;
}

.metric-card:hover {
    transform: none !important;
    border-color: rgba(17, 24, 39, 0.16) !important;
    box-shadow: var(--ui-shadow-sm) !important;
}

.metric-label {
    color: var(--ui-muted) !important;
    letter-spacing: 0.055em !important;
}

.metric-value {
    color: var(--ui-text);
    font-variant-numeric: tabular-nums;
}

/* Bordered Streamlit containers serve as deliberate filter / task panels. */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.74) !important;
    border: 1px solid rgba(17, 24, 39, 0.10) !important;
    border-radius: var(--ui-radius-lg) !important;
    box-shadow: var(--ui-shadow-sm) !important;
}

.filter-panel-heading {
    color: var(--ui-text);
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin: 0 0 0.7rem;
}

/* Inputs: one neutral shape, explicit boundaries, and a consistent focus ring. */
[data-testid="stWidgetLabel"] p {
    color: #30343a !important;
    font-size: 0.82rem !important;
    font-weight: 650 !important;
    letter-spacing: 0.005em !important;
}

[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"],
[data-testid="stDateInput"] [data-baseweb="input"] > div,
.stTextInput > div > div,
.stNumberInput > div > div,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    min-height: 46px !important;
    color: var(--ui-text) !important;
    background: var(--ui-surface-solid) !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: var(--ui-radius) !important;
    box-shadow: var(--ui-shadow-sm) !important;
    transition: border-color 150ms ease, box-shadow 150ms ease, background 150ms ease !important;
}

[data-baseweb="input"] > div:hover,
[data-baseweb="select"] > div:hover,
[data-baseweb="textarea"]:hover,
.stTextInput > div > div:hover,
.stNumberInput > div > div:hover,
.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: var(--ui-border-strong) !important;
}

[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"]:focus-within,
.stTextInput > div > div:focus-within,
.stNumberInput > div > div:focus-within,
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: var(--apple-blue) !important;
    box-shadow: 0 0 0 3px var(--ui-focus) !important;
}

[data-baseweb="input"] input,
[data-baseweb="select"] input,
[data-baseweb="textarea"] textarea,
.stTextInput input,
.stTextArea textarea {
    color: var(--ui-text) !important;
    font-size: 0.94rem !important;
    line-height: 1.45 !important;
    background: transparent !important;
}

[data-baseweb="textarea"] textarea,
.stTextArea textarea {
    min-height: 112px !important;
    padding-top: 0.7rem !important;
}

input::placeholder,
textarea::placeholder {
    color: #7a818d !important;
    opacity: 1 !important;
}

/* Restore the native, recognizable help icon; remove decorative emoji replacement. */
[data-testid="stWidgetLabel"] [data-testid*="stTooltipHoverTarget"] button,
[data-testid="stWidgetLabel"] [data-testid*="stTooltipIcon"],
[data-testid="stWidgetLabel"] [data-testid*="stHelpIcon"] {
    width: 28px !important;
    height: 28px !important;
    min-width: 28px !important;
    min-height: 28px !important;
    color: #626a75 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    overflow: visible !important;
}

[data-testid="stWidgetLabel"] [data-testid*="stTooltipHoverTarget"] button *,
[data-testid="stWidgetLabel"] [data-testid*="stTooltipIcon"] *,
[data-testid="stWidgetLabel"] [data-testid*="stHelpIcon"] * {
    opacity: 1 !important;
    color: currentColor !important;
    fill: currentColor !important;
}

[data-testid="stWidgetLabel"] [data-testid*="stTooltipHoverTarget"] button::before,
[data-testid*="stTooltipIcon"]::before,
[data-testid*="stHelpIcon"]::before {
    content: none !important;
}

/* Menus and calendars behave like anchored product surfaces, not modal artwork. */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background: var(--ui-surface-solid) !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 14px !important;
    box-shadow: 0 16px 42px rgba(17, 24, 39, 0.14) !important;
    overflow: hidden !important;
}

[role="option"],
li[role="option"] {
    min-height: 42px !important;
    color: var(--ui-text) !important;
    background: var(--ui-surface-solid) !important;
    border-radius: 8px !important;
    margin: 2px 4px !important;
}

[role="option"]:hover,
li[role="option"]:hover {
    background: #f0f5fc !important;
}

[role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"] {
    color: #8f0010 !important;
    background: #fff0f2 !important;
    font-weight: 650 !important;
}

/* Actions use shape and hierarchy instead of gloss. */
.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondary"] {
    min-height: 44px !important;
    border-radius: var(--ui-radius) !important;
    font-weight: 650 !important;
    box-shadow: var(--ui-shadow-sm) !important;
    transform: none !important;
    transition: background 150ms ease, border-color 150ms ease, box-shadow 150ms ease !important;
}

[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind^="primary"] {
    color: #ffffff !important;
    background: #e60012 !important;
    border: 1px solid #e60012 !important;
}

[data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] p,
.stButton > button[kind="primary"] [data-testid="stMarkdownContainer"] p,
[data-testid="stFormSubmitButton"] > button[kind^="primary"] [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
}

[data-testid="stBaseButton-primary"] p,
.stButton > button[kind="primary"] p,
[data-testid="stFormSubmitButton"] > button[kind^="primary"] p {
    color: #ffffff !important;
}

[data-testid="stBaseButton-primary"]:disabled p,
.stButton > button[kind="primary"]:disabled p,
[data-testid="stFormSubmitButton"] > button[kind^="primary"]:disabled p {
    color: #7a818d !important;
}

[data-testid="stBaseButton-primary"]:disabled,
.stButton > button[kind="primary"]:disabled,
[data-testid="stFormSubmitButton"] > button[kind^="primary"]:disabled {
    color: #7a818d !important;
    background: #e8ebf0 !important;
    border-color: #d9dee7 !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
}

[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button[kind^="primary"]:hover {
    background: #c90010 !important;
    border-color: #c90010 !important;
}

[data-testid="stBaseButton-secondary"],
.stButton > button[kind="secondary"],
.stDownloadButton > button {
    color: var(--ui-text) !important;
    background: var(--ui-surface-solid) !important;
    border: 1px solid var(--ui-border) !important;
}

[data-testid="stBaseButton-secondary"]:hover,
.stButton > button[kind="secondary"]:hover,
.stDownloadButton > button:hover {
    background: #f5f7fa !important;
    border-color: var(--ui-border-strong) !important;
}

button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible,
[tabindex]:focus-visible {
    outline: 3px solid var(--ui-focus) !important;
    outline-offset: 2px !important;
}

/* Segmented controls and tabs are navigation controls, not floating pills. */
[data-testid="stSegmentedControl"] [data-baseweb="button-group"] {
    width: fit-content !important;
    max-width: 100% !important;
    padding: 4px !important;
    gap: 3px !important;
    background: #edf1f6 !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 14px !important;
    box-shadow: none !important;
}

[data-testid="stSegmentedControl"] button {
    min-height: 40px !important;
    padding: 0.45rem 0.9rem !important;
    color: #4e5560 !important;
    background: transparent !important;
    border: 0 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[data-active="true"] {
    color: var(--ui-text) !important;
    background: #ffffff !important;
    box-shadow: 0 1px 3px rgba(17, 24, 39, 0.12) !important;
}

[data-testid="stSegmentedControl"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    overflow: visible !important;
}

[data-testid="stSegmentedControl"] [role="radiogroup"] {
    padding: 4px !important;
    gap: 3px !important;
    background: #edf1f6 !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 14px !important;
}

[data-testid="stSegmentedControl"] [aria-checked="false"],
[data-testid="stSegmentedControl"] [data-selected="false"] {
    color: #4e5560 !important;
    background: transparent !important;
    background-image: none !important;
    border: 0 !important;
    box-shadow: none !important;
}

[data-testid="stSegmentedControl"] [aria-checked="true"],
[data-testid="stSegmentedControl"] [data-selected="true"] {
    color: var(--ui-text) !important;
    background: #ffffff !important;
    background-image: none !important;
    border: 0 !important;
    box-shadow: 0 1px 3px rgba(17, 24, 39, 0.12) !important;
}

[data-testid="stSegmentedControl"] [aria-checked="true"] *,
[data-testid="stSegmentedControl"] [data-selected="true"] * {
    color: var(--ui-text) !important;
}

/* Streamlit 1.5x renders segmented controls as stButtonGroup. */
[data-testid="stButtonGroup"] [data-baseweb="button-group"] {
    width: 100% !important;
    max-width: 100% !important;
    padding: 4px !important;
    gap: 4px !important;
    background: #edf1f6 !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 14px !important;
}

[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_control"],
[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"] {
    min-height: 40px !important;
    color: #4e5560 !important;
    background: transparent !important;
    border: 0 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"] {
    color: var(--ui-text) !important;
    background: #ffffff !important;
    box-shadow: 0 1px 3px rgba(17, 24, 39, 0.12) !important;
}

[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"] p {
    color: var(--ui-text) !important;
    font-weight: 650 !important;
}

[data-baseweb="tab-list"] {
    gap: 4px !important;
    padding: 4px !important;
    background: rgba(237, 241, 246, 0.92) !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 14px !important;
    overflow-x: auto !important;
}

[data-baseweb="tab"] {
    min-height: 42px !important;
    padding: 0.5rem 0.9rem !important;
    color: #515863 !important;
    background: transparent !important;
    border-radius: 10px !important;
    white-space: nowrap !important;
}

[data-baseweb="tab"][aria-selected="true"] {
    color: var(--ui-text) !important;
    background: #ffffff !important;
    box-shadow: 0 1px 3px rgba(17, 24, 39, 0.10) !important;
}

[data-baseweb="tab-highlight"] {
    display: none !important;
}

/* Progressive disclosure stays quiet until requested. */
[data-testid="stExpander"] {
    border: 1px solid var(--ui-border) !important;
    border-radius: var(--ui-radius) !important;
    background: rgba(255, 255, 255, 0.70) !important;
    box-shadow: none !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] summary {
    min-height: 46px !important;
    padding: 0.6rem 0.8rem !important;
    color: var(--ui-text) !important;
    background: transparent !important;
    border: 0 !important;
    border-radius: 0 !important;
}

[data-testid="stExpander"] summary:hover {
    background: #f5f7fa !important;
}

/* Charts and tables share the same quiet analytical surface. */
[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    overflow: hidden !important;
    background: rgba(255, 255, 255, 0.88) !important;
    border: 1px solid rgba(17, 24, 39, 0.09) !important;
    border-radius: var(--ui-radius-lg) !important;
    box-shadow: var(--ui-shadow-sm) !important;
}

@media (max-width: 700px) {
    .yt-page-hero {
        padding: 2rem 1rem !important;
    }
    .metric-row {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
    [data-baseweb="tab-list"] {
        border-radius: 12px !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
    }
}
</style>
"""


def inject_shared_theme() -> None:
    css = APP_THEME_CSS.replace("{NN_BG_LAYER}", NN_BG_LAYER_URL)
    st.markdown(css, unsafe_allow_html=True)
