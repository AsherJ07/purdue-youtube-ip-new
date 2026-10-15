"""Shared shell: per-page feature heroes (badge → headline → description → tags)."""

from __future__ import annotations

from html import escape
from typing import Dict, List, Tuple

import streamlit as st


# Badge (ALL CAPS), headline, description, optional feature tags (glass pills)
PAGE_HERO: Dict[str, Tuple[str, str, str, Tuple[str, ...]]] = {
    "Channel Analysis": (
        "BENCHMARKS",
        "Understand the evidence before choosing the idea.",
        "Compare reach and public interaction across channels, videos, and publishing periods.",
        (),
    ),
    "Channel Insights": (
        "CHANNEL INSIGHTS",
        "Move from channel evidence to one testable content decision.",
        "Find repeatable channel patterns and turn them into a focused content test.",
        (),
    ),
    "Creator Studio": (
        "CREATOR STUDIO",
        "Turn channel evidence into content people can publish.",
        "Analyze a channel, develop content ideas, and create thumbnail concepts in one workspace.",
        (),
    ),
    "Outlier Finder": (
        "OUTLIER RESEARCH",
        "Find unusual performance without mistaking noise for signal.",
        "Surface unusually strong videos while accounting for age, channel baseline, and evidence quality.",
        (),
    ),
    "Deployment": (
        "DEPLOYMENT",
        "Run locally or ship to Streamlit Cloud with the same entrypoint everywhere.",
        "Use `streamlit_app.py` as the main file, install from `requirements.txt`, add `YOUTUBE` / `GEMINI` / `OPENAI` keys in Secrets, and use `packages.txt` for ffmpeg on Cloud when tools need it.",
        ("streamlit_app.py", "requirements.txt", "Secrets & packages"),
    ),
}


def render_page_hero(page: str) -> None:
    """Top-of-page glass hero: eyebrow → badge → headline → description → optional tags."""
    row = PAGE_HERO.get(page)
    if not row:
        return
    badge, headline, desc, tags = row
    tags_html = ""
    if tags:
        parts: List[str] = []
        for idx, t in enumerate(tags):
            cls = "feature-hero-tag"
            if idx % 3 == 0:
                cls += " feature-hero-tag--accent-r"
            elif idx % 3 == 1:
                cls += " feature-hero-tag--accent-b"
            parts.append(f'<span class="{cls}">{escape(t)}</span>')
        tags_html = f'<div class="feature-hero-tags">{"".join(parts)}</div>'

    st.markdown(
        f"""
<div class="glass-page-hero fade-in">
  <p class="product-eyebrow">YouTube Creator Insights <span class="product-eyebrow-sep">·</span> Purdue × Google</p>
  <div class="feature-badge">
    <span class="feature-badge-dot" aria-hidden="true"></span>
    {escape(badge)}
  </div>
  <h1 class="feature-headline">{escape(headline)}</h1>
  <p class="feature-description">{escape(desc)}</p>
  {tags_html}
</div>
""",
        unsafe_allow_html=True,
    )
