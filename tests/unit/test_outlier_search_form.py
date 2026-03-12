from datetime import date

from youtube_ip_v3.components.outlier_search_form import (
    apply_form_values_to_session_state,
    session_state_to_form_values,
)


def test_session_state_to_form_values_uses_expected_defaults() -> None:
    values = session_state_to_form_values({})

    assert values["query"] == ""
    assert values["timeframe"] == "Last 30 Days"
    assert values["match_mode"] == "Broad"
    assert values["region"] == "Any"
    assert values["language"] == "Any"
    assert values["min_views"] == 0
    assert values["include_hidden"] is True
    assert values["search_pages"] == 2
    assert values["baseline_channels"] == 15
    assert values["baseline_videos"] == 20


def test_session_state_to_form_values_serializes_custom_dates() -> None:
    state = {
        "outlier_page_custom_dates": (date(2026, 1, 1), date(2026, 1, 31)),
        "outlier_page_query": "AI automation",
    }

    values = session_state_to_form_values(state)

    assert values["query"] == "AI automation"
    assert values["custom_start"] == "2026-01-01"
    assert values["custom_end"] == "2026-01-31"


def test_apply_form_values_to_session_state_updates_existing_search_keys() -> None:
    state = {}
    values = {
        "query": "science shorts",
        "timeframe": "Custom",
        "custom_start": "2026-01-01",
        "custom_end": "2026-01-15",
        "match_mode": "Exact Phrase",
        "region": "US",
        "language": "en",
        "freshness_focus": "Last 14 Days",
        "duration_preference": "4-12 min",
        "language_strictness": "Strict",
        "min_views": 10000,
        "min_subscribers": 5000,
        "max_subscribers": 50000,
        "include_hidden": False,
        "exclude_keywords": "podcast, reaction",
        "search_pages": 3,
        "baseline_channels": 20,
        "baseline_videos": 25,
    }

    apply_form_values_to_session_state(state, values)

    assert state["outlier_page_query"] == "science shorts"
    assert state["outlier_page_timeframe"] == "Custom"
    assert state["outlier_page_custom_dates"] == (date(2026, 1, 1), date(2026, 1, 15))
    assert state["outlier_page_match_mode"] == "Exact Phrase"
    assert state["outlier_page_region"] == "US"
    assert state["outlier_page_language"] == "en"
    assert state["outlier_page_freshness"] == "Last 14 Days"
    assert state["outlier_page_duration"] == "4-12 min"
    assert state["outlier_page_language_strictness"] == "Strict"
    assert state["outlier_page_min_views"] == 10000
    assert state["outlier_page_min_subscribers"] == 5000
    assert state["outlier_page_max_subscribers"] == 50000
    assert state["outlier_page_include_hidden"] is False
    assert state["outlier_page_exclude_keywords"] == "podcast, reaction"
    assert state["outlier_page_search_pages"] == 3
    assert state["outlier_page_baseline_channels"] == 20
    assert state["outlier_page_baseline_videos"] == 25
    assert state["outlier_page_form_draft"]["query"] == "science shorts"
