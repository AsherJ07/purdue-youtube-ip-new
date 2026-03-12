from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Literal, MutableMapping, Optional, TypedDict

import streamlit as st
from streamlit.components.v2.get_bidi_component_manager import get_bidi_component_manager
from streamlit.runtime import Runtime


class OutlierSearchFormValues(TypedDict):
    query: str
    timeframe: str
    custom_start: str
    custom_end: str
    match_mode: str
    region: str
    language: str
    freshness_focus: str
    duration_preference: str
    language_strictness: str
    min_views: int
    min_subscribers: int
    max_subscribers: int
    include_hidden: bool
    exclude_keywords: str
    search_pages: int
    baseline_channels: int
    baseline_videos: int


class OutlierSearchFormAction(TypedDict):
    action: Literal["submit", "reset"]
    values: OutlierSearchFormValues


DEFAULT_FORM_KEY = "outlier_page_form_draft"
ASSET_ROOT = Path(__file__).with_name("outlier_search_form_assets")


_OUTLIER_SEARCH_FORM = None


def _get_component():
    global _OUTLIER_SEARCH_FORM
    if _OUTLIER_SEARCH_FORM is None:
        if Runtime.exists():
            manager = get_bidi_component_manager()
            manager.discover_and_register_components(start_file_watching=False)
            component_name = "youtube_ip_v3.outlier_search_form"
            css_value = "index.css"
            js_value = "index.js"
        else:
            component_name = "youtube_ip_v3.outlier_search_form.inline"
            css_value = f"/* inline asset */\n{ASSET_ROOT.joinpath('index.css').read_text(encoding='utf-8')}"
            js_value = f"// inline asset\n{ASSET_ROOT.joinpath('index.js').read_text(encoding='utf-8')}"

        _OUTLIER_SEARCH_FORM = st.components.v2.component(
            component_name,
            html='<div id="outlier-search-form-root"></div>',
            css=css_value,
            js=js_value,
            isolate_styles=False,
        )
    return _OUTLIER_SEARCH_FORM


def _iso_or_empty(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def session_state_to_form_values(state: MutableMapping[str, Any]) -> OutlierSearchFormValues:
    custom_dates = state.get("outlier_page_custom_dates")
    custom_start = ""
    custom_end = ""
    if custom_dates and isinstance(custom_dates, (list, tuple)) and len(custom_dates) == 2:
        custom_start = _iso_or_empty(custom_dates[0])
        custom_end = _iso_or_empty(custom_dates[1])

    return {
        "query": str(state.get("outlier_page_query", "") or ""),
        "timeframe": str(state.get("outlier_page_timeframe", "Last 30 Days") or "Last 30 Days"),
        "custom_start": custom_start,
        "custom_end": custom_end,
        "match_mode": str(state.get("outlier_page_match_mode", "Broad") or "Broad"),
        "region": str(state.get("outlier_page_region", "Any") or "Any"),
        "language": str(state.get("outlier_page_language", "Any") or "Any"),
        "freshness_focus": str(state.get("outlier_page_freshness", "Any") or "Any"),
        "duration_preference": str(state.get("outlier_page_duration", "Any") or "Any"),
        "language_strictness": str(
            state.get("outlier_page_language_strictness", "Strict") or "Strict"
        ),
        "min_views": int(state.get("outlier_page_min_views", 0) or 0),
        "min_subscribers": int(state.get("outlier_page_min_subscribers", 0) or 0),
        "max_subscribers": int(state.get("outlier_page_max_subscribers", 0) or 0),
        "include_hidden": bool(state.get("outlier_page_include_hidden", True)),
        "exclude_keywords": str(state.get("outlier_page_exclude_keywords", "") or ""),
        "search_pages": int(state.get("outlier_page_search_pages", 2) or 2),
        "baseline_channels": int(state.get("outlier_page_baseline_channels", 15) or 15),
        "baseline_videos": int(state.get("outlier_page_baseline_videos", 20) or 20),
    }


def apply_form_values_to_session_state(
    state: MutableMapping[str, Any],
    values: OutlierSearchFormValues,
) -> None:
    state["outlier_page_query"] = values["query"]
    state["outlier_page_timeframe"] = values["timeframe"]
    if values["timeframe"] == "Custom" and values["custom_start"] and values["custom_end"]:
        state["outlier_page_custom_dates"] = (
            date.fromisoformat(values["custom_start"]),
            date.fromisoformat(values["custom_end"]),
        )
    else:
        state["outlier_page_custom_dates"] = ()
    state["outlier_page_match_mode"] = values["match_mode"]
    state["outlier_page_region"] = values["region"]
    state["outlier_page_language"] = values["language"]
    state["outlier_page_freshness"] = values["freshness_focus"]
    state["outlier_page_duration"] = values["duration_preference"]
    state["outlier_page_language_strictness"] = values["language_strictness"]
    state["outlier_page_min_views"] = int(values["min_views"])
    state["outlier_page_min_subscribers"] = int(values["min_subscribers"])
    state["outlier_page_max_subscribers"] = int(values["max_subscribers"])
    state["outlier_page_include_hidden"] = bool(values["include_hidden"])
    state["outlier_page_exclude_keywords"] = values["exclude_keywords"]
    state["outlier_page_search_pages"] = int(values["search_pages"])
    state["outlier_page_baseline_channels"] = int(values["baseline_channels"])
    state["outlier_page_baseline_videos"] = int(values["baseline_videos"])
    state[DEFAULT_FORM_KEY] = dict(values)


def render_outlier_search_form(
    *,
    values: OutlierSearchFormValues,
    options: dict[str, Any],
    disabled_submit: bool,
    prefill_note: Optional[str] = None,
) -> Optional[OutlierSearchFormAction]:
    component = _get_component()
    result = component(
        key="outlier_search_form_component",
        data={
            "values": values,
            "options": options,
            "disabled": {"submit": disabled_submit},
            "prefillNote": prefill_note or "",
        },
        default={"draft": values},
        width="stretch",
        height="content",
        on_draft_change=lambda: None,
        on_submitted_change=lambda: None,
        on_reset_change=lambda: None,
    )

    draft = getattr(result, "draft", None)
    if isinstance(draft, dict):
        st.session_state[DEFAULT_FORM_KEY] = draft

    submitted = getattr(result, "submitted", None)
    if isinstance(submitted, dict):
        return {"action": "submit", "values": submitted}

    if getattr(result, "reset", None):
        return {"action": "reset", "values": values}

    return None
