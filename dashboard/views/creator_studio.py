"""Unified creator workflow for strategy, thumbnails, and media exports."""

from __future__ import annotations

import streamlit as st


SECTIONS = ["Channel Workspace", "Thumbnail Lab", "Media Export"]


def render() -> None:
    """Render one task-based studio without duplicating creative workflows."""
    if "creator_studio_section" not in st.session_state:
        st.session_state["creator_studio_section"] = SECTIONS[0]

    section = st.segmented_control(
        "Creator Studio section",
        SECTIONS,
        key="creator_studio_section",
        selection_mode="single",
        label_visibility="collapsed",
    )

    descriptions = {
        "Channel Workspace": "Research a channel, turn evidence into content ideas, and build a practical publishing plan.",
        "Thumbnail Lab": "Generate focused thumbnail options or export the public thumbnail from an existing video.",
        "Media Export": "Prepare public thumbnails, transcripts, audio, or video assets from URLs and playlists.",
    }
    st.caption(descriptions.get(section or SECTIONS[0], descriptions[SECTIONS[0]]))

    if section == "Thumbnail Lab":
        from dashboard.views import recommendations

        recommendations.render_thumbnail_workspace()
    elif section == "Media Export":
        from dashboard.views import tools

        tools.render_media_workspace()
    else:
        from dashboard.views import ytuber

        ytuber.render()
