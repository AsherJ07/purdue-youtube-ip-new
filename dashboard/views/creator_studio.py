"""Unified creator workflow for channel strategy and thumbnail creation."""

from __future__ import annotations

import streamlit as st


SECTIONS = ["Channel Workspace", "Thumbnail Lab"]
SECTION_LABELS = {
    "Channel Workspace": "Channel workspace",
    "Thumbnail Lab": "Thumbnail lab",
}


def render() -> None:
    """Render one task-based studio without duplicating creative workflows."""
    if "creator_studio_section" not in st.session_state:
        st.session_state["creator_studio_section"] = SECTIONS[0]
    elif st.session_state["creator_studio_section"] not in SECTIONS:
        st.session_state["creator_studio_section"] = SECTIONS[0]

    section = st.segmented_control(
        "Workspace",
        SECTIONS,
        key="creator_studio_section",
        selection_mode="single",
        format_func=lambda value: SECTION_LABELS[value],
        width="stretch",
    )

    if section == "Thumbnail Lab":
        from dashboard.views import recommendations

        recommendations.render_thumbnail_workspace()
    else:
        from dashboard.views import ytuber

        ytuber.render()
