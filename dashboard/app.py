import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.layout import render_page_hero
from dashboard.components.sidebar import render_sidebar_footer, render_sidebar_header
from dashboard.components.intro_animation import inject_intro_animation
from dashboard.components.theme import inject_shared_theme
from dashboard.views import channel_analysis, channel_insights, creator_studio, outlier_finder


def _render_app_shell(page: str) -> None:
    """Glass feature hero: badge, headline, description, tags."""
    render_page_hero(page)


def _cleanup_retired_session_state() -> None:
    retired_prefixes = ("assistant_", "google_oauth_")
    retired_exact_keys = {"channel_insights_owned_channel", "app_page"}
    for key in list(st.session_state.keys()):
        if key in retired_exact_keys or key.startswith(retired_prefixes):
            st.session_state.pop(key, None)


def _page_channel_analysis() -> None:
    _render_app_shell("Channel Analysis")
    channel_analysis.render()


def _page_channel_insights() -> None:
    _render_app_shell("Channel Insights")
    channel_insights.render()


def _page_creator_studio() -> None:
    _render_app_shell("Creator Studio")
    creator_studio.render()


def _page_outlier_finder() -> None:
    _render_app_shell("Outlier Finder")
    outlier_finder.render()


PAGE_CHANNEL_ANALYSIS = st.Page(
    _page_channel_analysis,
    title="Channel Analysis",
    icon="📊",
    default=True,
)
PAGE_CHANNEL_INSIGHTS = st.Page(_page_channel_insights, title="Channel Insights", icon="💡")
PAGE_CREATOR_STUDIO = st.Page(_page_creator_studio, title="Creator Studio", icon="🎬")
PAGE_OUTLIER_FINDER = st.Page(_page_outlier_finder, title="Outlier Finder", icon="🎯")


def run() -> None:
    """Execute the multipage router. Must run on every Streamlit script rerun (not only on first import)."""
    st.set_page_config(
        page_title="YouTube Creator Insights | Purdue × Google",
        page_icon="📺",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_shared_theme()
    inject_intro_animation()
    _cleanup_retired_session_state()

    with st.sidebar:
        render_sidebar_header()

    pg = st.navigation(
        [
            PAGE_CHANNEL_ANALYSIS,
            PAGE_CHANNEL_INSIGHTS,
            PAGE_CREATOR_STUDIO,
            PAGE_OUTLIER_FINDER,
        ],
        expanded=True,
    )

    with st.sidebar:
        render_sidebar_footer()

    pg.run()


if __name__ == "__main__":
    run()
