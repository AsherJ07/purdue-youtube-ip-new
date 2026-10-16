from pathlib import Path

import pandas as pd

from src.services.channel_insights_service import (
    NINJA_SHOWCASE_TOPICS,
    TOPIC_MODE_BERTOPIC_OPTIONAL,
    TOPIC_MODE_HEURISTIC,
    _apply_ninja_showcase_topics,
    _ninja_showcase_recommendations,
    load_channel_insights,
    refresh_channel_insights,
)
from src.services.public_channel_service import PublicChannelWorkspace
from src.services.topic_model_runtime import TopicModelInferenceResult


def test_refresh_channel_insights_persists_snapshot(monkeypatch, tmp_path: Path) -> None:
    sample_df = pd.DataFrame(
        [
            {
                "channel_id": "UC123",
                "channel_title": "Demo Channel",
                "video_id": "v1",
                "video_title": "How To Build Better Hooks",
                "video_description": "hooks for creators",
                "video_tags": "hooks|creator|youtube",
                "video_publishedAt": "2026-03-10T12:00:00Z",
                "views": 10000,
                "likes": 600,
                "comments": 45,
                "duration": "PT8M0S",
                "duration_seconds": 480,
            },
            {
                "channel_id": "UC123",
                "channel_title": "Demo Channel",
                "video_id": "v2",
                "video_title": "Shorts Strategy That Actually Converts",
                "video_description": "shorts strategy and topic testing",
                "video_tags": "shorts|strategy|topic",
                "video_publishedAt": "2026-03-01T12:00:00Z",
                "views": 6000,
                "likes": 340,
                "comments": 20,
                "duration": "PT45S",
                "duration_seconds": 45,
            },
        ]
    )

    workspace = PublicChannelWorkspace(
        channel_df=sample_df,
        source="youtube_api",
        channel_id="UC123",
        channel_title="Demo Channel",
        canonical_url="https://www.youtube.com/channel/UC123",
        query_used="@demo",
    )

    monkeypatch.setattr(
        "src.services.channel_insights_service.load_public_channel_workspace",
        lambda channel_input, force_refresh=False: workspace,
    )
    monkeypatch.setattr(
        "src.services.channel_insights_service.maybe_generate_ai_overlay",
        lambda *args, **kwargs: "",
    )

    db_path = tmp_path / "channel_insights.db"
    payload = refresh_channel_insights("@demo", db_path=db_path)
    loaded = load_channel_insights("UC123", db_path=db_path)

    assert payload["channel"]["channel_id"] == "UC123"
    assert loaded is not None
    assert loaded["summary"]["strongest_theme"]
    assert loaded["outliers_df"].empty  # fewer than four videos cannot define a quartile
    assert loaded["summary"]["topic_mode_used"] == TOPIC_MODE_HEURISTIC

def test_refresh_channel_insights_falls_back_when_optional_topic_model_fails(monkeypatch, tmp_path: Path) -> None:
    sample_df = pd.DataFrame(
        [
            {
                "channel_id": "UC123",
                "channel_title": "Demo Channel",
                "video_id": "v1",
                "video_title": "How To Build Better Hooks",
                "video_description": "hooks for creators",
                "video_tags": "hooks|creator|youtube",
                "video_publishedAt": "2026-03-10T12:00:00Z",
                "views": 10000,
                "likes": 600,
                "comments": 45,
                "duration": "PT8M0S",
                "duration_seconds": 480,
            }
        ]
    )

    workspace = PublicChannelWorkspace(
        channel_df=sample_df,
        source="youtube_api",
        channel_id="UC123",
        channel_title="Demo Channel",
        canonical_url="https://www.youtube.com/channel/UC123",
        query_used="@demo",
    )

    monkeypatch.setattr(
        "src.services.channel_insights_service.load_public_channel_workspace",
        lambda channel_input, force_refresh=False: workspace,
    )
    monkeypatch.setattr(
        "src.services.channel_insights_service.maybe_generate_ai_overlay",
        lambda *args, **kwargs: "",
    )
    monkeypatch.setattr(
        "src.services.channel_insights_service.apply_optional_topic_model",
        lambda df: TopicModelInferenceResult(
            success=False,
            topic_rows=(),
            bundle_version="2026.03.27",
            failure_reason="Bundle missing",
            status="download_required",
        ),
    )

    db_path = tmp_path / "channel_insights.db"
    payload = refresh_channel_insights("@demo", db_path=db_path, topic_mode=TOPIC_MODE_BERTOPIC_OPTIONAL)

    assert payload["summary"]["topic_mode_requested"] == TOPIC_MODE_BERTOPIC_OPTIONAL
    assert payload["summary"]["topic_mode_used"] == TOPIC_MODE_HEURISTIC
    assert payload["summary"]["topic_model_failure_reason"] == "Bundle missing"


def test_refresh_channel_insights_uses_optional_topic_model_when_available(monkeypatch, tmp_path: Path) -> None:
    sample_df = pd.DataFrame(
        [
            {
                "channel_id": "UC123",
                "channel_title": "Demo Channel",
                "video_id": "v1",
                "video_title": "How To Improve Packaging",
                "video_description": "packaging breakdown",
                "video_tags": "packaging|ctr",
                "video_publishedAt": "2026-03-10T12:00:00Z",
                "views": 10000,
                "likes": 600,
                "comments": 45,
                "duration": "PT8M0S",
                "duration_seconds": 480,
            }
        ]
    )

    workspace = PublicChannelWorkspace(
        channel_df=sample_df,
        source="youtube_api",
        channel_id="UC123",
        channel_title="Demo Channel",
        canonical_url="https://www.youtube.com/channel/UC123",
        query_used="@demo",
    )

    monkeypatch.setattr(
        "src.services.channel_insights_service.load_public_channel_workspace",
        lambda channel_input, force_refresh=False: workspace,
    )
    monkeypatch.setattr(
        "src.services.channel_insights_service.maybe_generate_ai_overlay",
        lambda *args, **kwargs: "",
    )
    monkeypatch.setattr(
        "src.services.channel_insights_service.apply_optional_topic_model",
        lambda df: TopicModelInferenceResult(
            success=True,
            topic_rows=(
                {
                    "video_id": "v1",
                    "model_topic_id": 18,
                    "model_topic_label_raw": "18_packaging_ctr_thumbnail_hooks",
                    "model_topic_label": "Packaging / Ctr / Thumbnail / Hooks",
                    "topic_source": "bertopic_global",
                    "bertopic_text": "packaging ctr thumbnail hooks",
                    "bertopic_token_count": 6,
                    "is_sparse_text": False,
                },
            ),
            bundle_version="2026.03.27",
            message="BERTopic topic assignments were applied successfully.",
            status="ready",
        ),
    )

    db_path = tmp_path / "channel_insights.db"
    payload = refresh_channel_insights("@demo", db_path=db_path, topic_mode=TOPIC_MODE_BERTOPIC_OPTIONAL)

    assert payload["summary"]["topic_mode_requested"] == TOPIC_MODE_BERTOPIC_OPTIONAL
    assert payload["summary"]["topic_mode_used"] == TOPIC_MODE_BERTOPIC_OPTIONAL
    assert payload["videos_df"]["topic_source"].iloc[0] == "bertopic_global"
    assert payload["videos_df"]["primary_topic"].iloc[0] == "Packaging / Ctr / Thumbnail / Hooks"


def test_ninja_showcase_topics_are_stable_and_relevant() -> None:
    sample_df = pd.DataFrame(
        [
            {"video_id": "v1", "video_title": "I Made One Billion Coins in Arc Raiders", "is_short": False},
            {"video_id": "v2", "video_title": "The New Arc Raiders Patch Is Broken", "is_short": False},
            {"video_id": "v3", "video_title": "My Wildest Arc Raiders PvP Fight", "is_short": False},
            {"video_id": "v4", "video_title": "Road to Unreal in Fortnite", "is_short": False},
            {"video_id": "v5", "video_title": "Reacting to the Luckiest Win", "is_short": True},
            {"video_id": "v6", "video_title": "Ninja vs SypherPK Challenge", "is_short": False},
            {"video_id": "v7", "video_title": "Trying Highguard for the First Time", "is_short": False},
        ]
    )

    result, metadata = _apply_ninja_showcase_topics(sample_df)

    assert set(result["primary_topic"]).issubset(set(NINJA_SHOWCASE_TOPICS))
    assert result["primary_topic"].nunique() >= 5
    assert result["topic_source"].eq("ninja_showcase_fixture").all()
    assert metadata["model_status"] == "showcase_fixture"
    assert metadata["topic_mode_used"] == TOPIC_MODE_BERTOPIC_OPTIONAL


def test_ninja_showcase_topics_ignore_polluted_legacy_tags() -> None:
    sample_df = pd.DataFrame(
        [
            {
                "video_id": f"v{index}",
                "video_title": f"Arc Raiders Patch Update {index}",
                "video_description": "subscribe for more",
                "video_tags": "fortnite|season|victory royale|battle pass",
                "is_short": False,
            }
            for index in range(100)
        ]
    )

    result, _ = _apply_ninja_showcase_topics(sample_df)
    assert result["primary_topic"].eq("Arc Raiders Updates & Meta").all()


def test_ninja_showcase_recommendations_are_specific_and_metric_backed() -> None:
    topic_metrics = pd.DataFrame(
        [
            {"topic_label": "Arc Raiders Progression & Economy", "video_count": 18, "median_views_per_day": 12450},
            {"topic_label": "Reactions & Viral Moments", "video_count": 31, "median_views_per_day": 7200},
            {"topic_label": "Arc Raiders Updates & Meta", "video_count": 12, "median_views_per_day": 9800},
        ]
    )

    recommendations = _ninja_showcase_recommendations(topic_metrics)

    assert recommendations["double_down"][0]["theme"] == "Arc Raiders Progression & Economy"
    assert recommendations["avoid"][0]["theme"] == "Reactions & Viral Moments"
    assert recommendations["test_next"][0]["theme"] == "Arc Raiders Updates & Meta"
    assert recommendations["double_down"][0]["sample_size"] == 18
    assert "12,450" in recommendations["double_down"][0]["evidence"]
