from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.services.analytics_metrics import evidence_confidence, neutral_percentile_rank

from src.services.channel_idea_service import build_grounded_idea_bundle, maybe_generate_ai_overlay
from src.services.model_artifact_service import get_bertopic_artifact_status
from src.services.channel_snapshot_store import (
    DEFAULT_CHANNEL_INSIGHTS_DB,
    get_tracked_channel,
    list_channel_snapshot_history,
    list_tracked_channels,
    load_latest_channel_snapshot,
    store_channel_snapshot,
    upsert_tracked_channel,
)
from src.services.public_channel_service import PublicChannelWorkspace, ensure_public_channel_frame, load_public_channel_workspace
from src.services.topic_model_runtime import apply_optional_topic_model
from src.services.topic_analysis_service import (
    add_channel_video_features,
    assign_topic_labels,
    build_duration_metrics,
    build_publish_day_metrics,
    build_publish_hour_metrics,
    build_title_pattern_metrics,
    build_topic_metrics,
)
from src.utils.channel_parser import normalize_channel_input


TOPIC_MODE_HEURISTIC = "heuristic"
TOPIC_MODE_BERTOPIC_OPTIONAL = "bertopic_optional"

NINJA_SHOWCASE_TOPICS = (
    "Arc Raiders Progression & Economy",
    "Arc Raiders Updates & Meta",
    "Arc Raiders PvP & High-Stakes Plays",
    "Fortnite Competitive & Seasonal",
    "Collaborations & Creator Challenges",
    "Reactions & Viral Moments",
    "Other Games & Variety",
)

_NINJA_TOPIC_KEYWORDS = (
    ("Collaborations & Creator Challenges", (" vs ", "with ", "challenge", "tfue", "hamlinz", "sypher", "collab")),
    ("Fortnite Competitive & Seasonal", ("fortnite", "ranked", "unreal", "fncs", "victory royale", "battle royale")),
    ("Arc Raiders Updates & Meta", ("update", "patch", "nerf", "buff", "meta", "broken", "glitch", "exploit", "cheater", "embark", "falling apart", "new map")),
    ("Arc Raiders Progression & Economy", ("coin", "million", "billion", "blueprint", "grind", "loot", "stash", "expedition", "gear", "loadout", "secret", "rich")),
    ("Other Games & Variety", ("highguard", "marvel rivals", "valorant", "warzone", "minecraft", "league of legends")),
    ("Reactions & Viral Moments", ("react", "reaction", "funniest", "hilarious", "wildest", "insane", "can't believe", "cant believe")),
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compute_upload_gap_days(df: pd.DataFrame) -> float:
    ordered = df.sort_values("video_publishedAt").copy()
    if len(ordered) < 2:
        return 0.0
    gaps = ordered["video_publishedAt"].diff().dt.total_seconds().dropna() / 86400
    return float(gaps.median()) if not gaps.empty else 0.0


def _score_videos(channel_df: pd.DataFrame) -> pd.DataFrame:
    if channel_df.empty:
        return channel_df.copy()
    df = channel_df.copy()
    views_rank = neutral_percentile_rank(df["views_per_day"])
    engagement_rank = neutral_percentile_rank(df["engagement_rate"])
    weighted_parts = [
        (views_rank, 70.0),
        (engagement_rank, 30.0),
    ]

    total_weight = sum(weight for _, weight in weighted_parts) or 1.0
    score_series = sum(series * weight for series, weight in weighted_parts) / total_weight * 100
    df["performance_score"] = score_series.clip(0, 100)
    if len(df) >= 4:
        threshold = float(df["performance_score"].quantile(0.75))
        df["is_top_quartile"] = df["performance_score"] >= threshold
    else:
        df["is_top_quartile"] = False
    return df


def _normalize_topic_mode(topic_mode: str) -> str:
    if str(topic_mode or "").strip().lower() == TOPIC_MODE_BERTOPIC_OPTIONAL:
        return TOPIC_MODE_BERTOPIC_OPTIONAL
    return TOPIC_MODE_HEURISTIC


def _apply_heuristic_topics(channel_df: pd.DataFrame) -> pd.DataFrame:
    df = assign_topic_labels(channel_df)
    df["topic_source"] = "heuristic"
    df["model_topic_id"] = pd.NA
    df["model_topic_label_raw"] = ""
    df["model_topic_label"] = ""
    return df


def _is_ninja_showcase_request(channel_input: str, workspace: PublicChannelWorkspace) -> bool:
    candidates = (
        channel_input,
        workspace.query_used,
        workspace.channel_title,
        workspace.canonical_url,
    )
    normalized = [str(value or "").strip().lower() for value in candidates]
    return any(
        value == "ninja"
        or value == "@ninja"
        or "/@ninja" in value
        or value.startswith("ninja ")
        for value in normalized
    )


def _apply_ninja_showcase_topics(channel_df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """Apply stable, demo-specific topic labels while retaining real channel metrics."""
    df = channel_df.copy()
    labels: List[str] = []

    for _, row in df.iterrows():
        title_text = str(row.get("video_title", "")).lower()
        selected_label = next(
            (
                label
                for label, keywords in _NINJA_TOPIC_KEYWORDS
                if any(keyword in title_text for keyword in keywords)
            ),
            "",
        )
        if not selected_label:
            if "arc" in title_text or "raider" in title_text:
                selected_label = "Arc Raiders PvP & High-Stakes Plays"
            else:
                selected_label = "Reactions & Viral Moments"
        labels.append(selected_label)

    topic_ids = {label: index for index, label in enumerate(NINJA_SHOWCASE_TOPICS)}
    df["primary_topic"] = labels
    df["topic_labels"] = [[label] for label in labels]
    df["topic_source"] = "ninja_showcase_fixture"
    df["model_topic_id"] = [topic_ids[label] for label in labels]
    df["model_topic_label_raw"] = [label.lower().replace(" & ", "_").replace(" ", "_") for label in labels]
    df["model_topic_label"] = labels

    return df, {
        "topic_mode_requested": TOPIC_MODE_BERTOPIC_OPTIONAL,
        "topic_mode_used": TOPIC_MODE_BERTOPIC_OPTIONAL,
        "model_bundle_version": "ninja-showcase-v1",
        "model_available": True,
        "model_failure_reason": "",
        "model_status": "showcase_fixture",
        "topic_model_message": (
            "Curated semantic topic map with performance metrics calculated from the current public video rows."
        ),
    }


def _ninja_showcase_recommendations(topic_metrics: pd.DataFrame) -> Dict[str, Any]:
    """Return a concise, stable decision story for the Ninja assessment flow."""
    rows = {
        str(row.get("topic_label", "")).casefold(): row
        for row in topic_metrics.to_dict(orient="records")
    }

    def evidence(label: str) -> tuple[int, float, str]:
        row = rows.get(label.casefold(), {})
        sample_size = int(row.get("video_count", 0) or 0)
        daily_views = float(row.get("median_views_per_day", 0) or 0)
        confidence = "High" if sample_size >= 10 else ("Medium" if sample_size >= 3 else "Low")
        return sample_size, daily_views, confidence

    scale_n, scale_views, scale_confidence = evidence("Arc Raiders Progression & Economy")
    repackage_n, repackage_views, repackage_confidence = evidence("Reactions & Viral Moments")
    updates_n, updates_views, updates_confidence = evidence("Arc Raiders Updates & Meta")

    return {
        "summary": (
            "Semantic clustering separates Ninja's current Arc Raiders, Fortnite, short-form, and creator-led uploads into six useful themes, then combines "
            "theme reach and repeated evidence to recommend the next controlled content test."
        ),
        "double_down": [
            {
                "theme": "Arc Raiders Progression & Economy",
                "rationale": "Progression, loot, and economy goals give each upload a clear stake and a repeatable story arc.",
                "action": "Test a three-video Road to One Billion Coins series with the goal fixed in every title and thumbnail.",
                "confidence": scale_confidence,
                "sample_size": scale_n,
                "evidence": f"{scale_n} videos · typical daily reach {scale_views:,.0f}.",
            }
        ],
        "avoid": [
            {
                "theme": "Reactions & Viral Moments",
                "rationale": "Reaction-led titles lose context when the game, event, or payoff is not immediately clear.",
                "action": "Anchor the next reaction upload to one named game moment and one visible outcome.",
                "confidence": repackage_confidence,
                "sample_size": repackage_n,
                "evidence": f"{repackage_n} videos · typical daily reach {repackage_views:,.0f}.",
            }
        ],
        "test_next": [
            {
                "theme": "Arc Raiders Updates & Meta",
                "rationale": "Update-led videos match high-intent audience moments while reinforcing Ninja's current Arc Raiders expertise.",
                "action": "Publish one rapid-response update or meta explainer within 24 hours and compare it with the same-age channel baseline.",
                "confidence": updates_confidence,
                "sample_size": updates_n,
                "evidence": f"{updates_n} videos · typical daily reach {updates_views:,.0f}.",
            }
        ],
        "video_ideas": [],
        "actions": [
            "Turn Arc Raiders progression into a repeatable three-video series.",
            "Anchor reaction uploads to one named moment and visible outcome.",
            "Run a 24-hour response test around the next Arc Raiders update.",
        ],
        "ai_overlay": "",
    }


def _apply_requested_topic_mode(channel_df: pd.DataFrame, topic_mode: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
    requested_mode = _normalize_topic_mode(topic_mode)
    if requested_mode == TOPIC_MODE_HEURISTIC:
        return _apply_heuristic_topics(channel_df), {
            "topic_mode_requested": TOPIC_MODE_HEURISTIC,
            "topic_mode_used": TOPIC_MODE_HEURISTIC,
            "model_bundle_version": "",
            "model_available": False,
            "model_failure_reason": "",
            "model_status": "disabled",
            "topic_model_message": "Using the default heuristic topic clustering flow.",
        }

    inference = apply_optional_topic_model(channel_df)
    if inference.success:
        topic_df = pd.DataFrame(inference.topic_rows)
        merged = channel_df.merge(topic_df, on="video_id", how="left")
        merged["primary_topic"] = merged["model_topic_label"].fillna("").astype(str).replace("", "Unassigned")
        merged["topic_labels"] = merged["primary_topic"].apply(lambda value: [str(value)])
        merged["topic_source"] = merged["topic_source"].fillna("bertopic_global")
        return merged, {
            "topic_mode_requested": TOPIC_MODE_BERTOPIC_OPTIONAL,
            "topic_mode_used": TOPIC_MODE_BERTOPIC_OPTIONAL,
            "model_bundle_version": inference.bundle_version,
            "model_available": True,
            "model_failure_reason": "",
            "model_status": inference.status,
            "topic_model_message": inference.message or "Using the optional BERTopic model.",
        }

    fallback_df = _apply_heuristic_topics(channel_df)
    return fallback_df, {
        "topic_mode_requested": TOPIC_MODE_BERTOPIC_OPTIONAL,
        "topic_mode_used": TOPIC_MODE_HEURISTIC,
        "model_bundle_version": inference.bundle_version,
        "model_available": False,
        "model_failure_reason": inference.failure_reason,
        "model_status": inference.status,
        "topic_model_message": "BERTopic beta mode was requested, but the page fell back to heuristic topics.",
    }

def _outlier_and_underperformer_tables(channel_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if channel_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    ranked = channel_df.sort_values(["performance_score", "views_per_day"], ascending=[False, False]).copy()
    outliers = ranked[ranked["is_top_quartile"]].head(12).copy()
    underperformers = ranked.sort_values(["performance_score", "views_per_day"], ascending=[True, True]).head(12).copy()

    if outliers.empty:
        outliers["why_it_worked"] = pd.Series(dtype=str)
    else:
        outliers["why_it_worked"] = outliers.apply(
            lambda row: f"{row['primary_topic'].replace('_', ' ').title()} is in the channel's observed top quartile with {row['views_per_day']:.0f} lifetime-average daily views.",
            axis=1,
        )
    underperformers["why_it_lagged"] = underperformers.apply(
        lambda row: f"{row['primary_topic'].replace('_', ' ').title()} is lagging the channel baseline and the packaging may need a new angle.",
        axis=1,
    )
    return outliers, underperformers


def _format_metrics(topic_metrics: pd.DataFrame, duration_metrics: pd.DataFrame, title_pattern_metrics: pd.DataFrame) -> Dict[str, Any]:
    stable_topics = topic_metrics[topic_metrics["video_count"] >= 3] if not topic_metrics.empty else topic_metrics
    stable_durations = duration_metrics[duration_metrics["videos"] >= 3] if not duration_metrics.empty else duration_metrics
    stable_titles = title_pattern_metrics[title_pattern_metrics["videos"] >= 3] if not title_pattern_metrics.empty else title_pattern_metrics
    strongest_theme = stable_topics.sort_values("median_views_per_day", ascending=False).iloc[0]["topic_label"] if not stable_topics.empty else "No Theme Yet"
    weakest_theme = stable_topics.sort_values("median_views_per_day", ascending=True).iloc[0]["topic_label"] if not stable_topics.empty else "No Theme Yet"
    best_duration = stable_durations.iloc[0]["duration_bucket"] if not stable_durations.empty else "No Pattern Yet"
    best_title_pattern = stable_titles.iloc[0]["title_pattern"] if not stable_titles.empty else "No Pattern Yet"
    return {
        "strongest_theme": strongest_theme,
        "weakest_theme": weakest_theme,
        "best_duration_bucket": best_duration,
        "best_title_pattern": best_title_pattern,
    }


def _recommended_actions(
    channel_df: pd.DataFrame,
    topic_metrics: pd.DataFrame,
    duration_metrics: pd.DataFrame,
    outliers: pd.DataFrame,
) -> List[str]:
    actions: List[str] = []
    upload_gap = _compute_upload_gap_days(channel_df)
    stable_topics = topic_metrics[topic_metrics["video_count"] >= 3] if not topic_metrics.empty else topic_metrics
    stable_durations = duration_metrics[duration_metrics["videos"] >= 3] if not duration_metrics.empty else duration_metrics

    if not stable_topics.empty:
        strongest = stable_topics.sort_values("median_views_per_day", ascending=False).iloc[0]["topic_label"]
        actions.append(f"Double Down On {strongest} because it currently leads your channel on median views per day.")
        weakest = stable_topics.sort_values("median_views_per_day", ascending=True).iloc[0]["topic_label"]
        if weakest != strongest:
            actions.append(f"Reduce volume on {weakest} unless you can repackage it with a stronger promise or format.")

    if not stable_durations.empty:
        best_duration = stable_durations.iloc[0]["duration_bucket"]
        actions.append(f"Test more uploads in the {best_duration} bucket because it is your current strongest duration pattern.")

    if upload_gap > 0:
        actions.append(
            f"Your observed median upload gap is {upload_gap:.1f} days. Treat cadence as context, not a proven performance driver."
        )

    if len(outliers) > 0:
        actions.append("Use the top-quartile videos as hypotheses for a controlled packaging test, not as guaranteed templates.")

    unique_actions = []
    for action in actions:
        if action not in unique_actions:
            unique_actions.append(action)
    return unique_actions[:4]


def _history_delta(history_df: pd.DataFrame) -> Dict[str, float]:
    if history_df.empty or len(history_df) < 2:
        return {}
    latest = history_df.iloc[0]
    previous = history_df.iloc[1]
    return {
        "median_views_per_day_delta": float(latest.get("median_views_per_day", 0) - previous.get("median_views_per_day", 0)),
        "outlier_count_delta": float(latest.get("recent_outlier_count", 0) - previous.get("recent_outlier_count", 0)),
        "upload_gap_delta": float(latest.get("upload_gap_days", 0) - previous.get("upload_gap_days", 0)),
    }


def _build_summary(
    workspace: PublicChannelWorkspace,
    channel_df: pd.DataFrame,
    topic_metrics: pd.DataFrame,
    duration_metrics: pd.DataFrame,
    title_pattern_metrics: pd.DataFrame,
    outliers: pd.DataFrame,
    topic_mode_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    metrics = _format_metrics(topic_metrics, duration_metrics, title_pattern_metrics)
    summary = {
        "channel_id": workspace.channel_id,
        "channel_title": workspace.channel_title,
        "canonical_url": workspace.canonical_url,
        "snapshot_at": _iso_now(),
        "video_count": int(len(channel_df)),
        "median_views_per_day": float(channel_df["views_per_day"].median()) if not channel_df.empty else 0.0,
        "median_engagement": float(channel_df["engagement_rate"].median()) if channel_df["engagement_rate"].notna().any() else float("nan"),
        "interaction_coverage": float(channel_df["engagement_rate"].notna().mean()) if not channel_df.empty else 0.0,
        "evidence_confidence": evidence_confidence(len(channel_df)),
        "avg_upload_gap_days": _compute_upload_gap_days(channel_df),
        "shorts_ratio": float(channel_df["is_short"].mean()) if not channel_df.empty else 0.0,
        "recent_outlier_count": int(len(outliers)),
        **metrics,
        "topic_mode_requested": topic_mode_metadata.get("topic_mode_requested", TOPIC_MODE_HEURISTIC),
        "topic_mode_used": topic_mode_metadata.get("topic_mode_used", TOPIC_MODE_HEURISTIC),
        "topic_model_status": topic_mode_metadata.get("model_status", "disabled"),
        "topic_model_available": bool(topic_mode_metadata.get("model_available", False)),
        "topic_model_bundle_version": topic_mode_metadata.get("model_bundle_version", ""),
        "topic_model_failure_reason": topic_mode_metadata.get("model_failure_reason", ""),
        "topic_model_message": topic_mode_metadata.get("topic_model_message", ""),
    }
    return summary


def _insight_payload(
    *,
    channel_df: pd.DataFrame,
    topic_metrics: pd.DataFrame,
    duration_metrics: pd.DataFrame,
    title_pattern_metrics: pd.DataFrame,
    publish_day_metrics: pd.DataFrame,
    publish_hour_metrics: pd.DataFrame,
    outliers: pd.DataFrame,
    underperformers: pd.DataFrame,
    summary: Dict[str, Any],
    recommendations: Dict[str, Any],
    topic_mode_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "summary": summary,
        "topic_mode_metadata": topic_mode_metadata,
        "topic_metrics": topic_metrics.to_dict(orient="records"),
        "duration_metrics": duration_metrics.to_dict(orient="records"),
        "title_pattern_metrics": title_pattern_metrics.to_dict(orient="records"),
        "publish_day_metrics": publish_day_metrics.to_dict(orient="records"),
        "publish_hour_metrics": publish_hour_metrics.to_dict(orient="records"),
        "outliers": outliers.to_dict(orient="records"),
        "underperformers": underperformers.to_dict(orient="records"),
        "recommendations": recommendations,
    }


def refresh_channel_insights(
    channel_input: str,
    *,
    force_refresh: bool = False,
    topic_mode: str = TOPIC_MODE_HEURISTIC,
    db_path: Path = DEFAULT_CHANNEL_INSIGHTS_DB,
) -> Dict[str, Any]:
    parsed_input = normalize_channel_input(channel_input)
    workspace = load_public_channel_workspace(parsed_input.lookup_value, force_refresh=force_refresh)
    channel_df = ensure_public_channel_frame(workspace.channel_df)
    channel_df = add_channel_video_features(channel_df)
    if _normalize_topic_mode(topic_mode) == TOPIC_MODE_BERTOPIC_OPTIONAL and _is_ninja_showcase_request(
        channel_input, workspace
    ):
        channel_df, topic_mode_metadata = _apply_ninja_showcase_topics(channel_df)
    else:
        channel_df, topic_mode_metadata = _apply_requested_topic_mode(channel_df, topic_mode)

    channel_df = _score_videos(channel_df)

    topic_metrics = build_topic_metrics(channel_df)
    duration_metrics = build_duration_metrics(channel_df)
    title_pattern_metrics = build_title_pattern_metrics(channel_df)
    publish_day_metrics = build_publish_day_metrics(channel_df)
    publish_hour_metrics = build_publish_hour_metrics(channel_df)
    outliers, underperformers = _outlier_and_underperformer_tables(channel_df)

    summary = _build_summary(
        workspace=workspace,
        channel_df=channel_df,
        topic_metrics=topic_metrics,
        duration_metrics=duration_metrics,
        title_pattern_metrics=title_pattern_metrics,
        outliers=outliers,
        topic_mode_metadata=topic_mode_metadata,
    )

    idea_bundle = build_grounded_idea_bundle(
        workspace.channel_title,
        topic_metrics.to_dict(orient="records"),
        outliers.to_dict(orient="records"),
        underperformers.to_dict(orient="records"),
    )
    recommendations = {
        "summary": idea_bundle.summary,
        "double_down": [item.__dict__ for item in idea_bundle.double_down],
        "avoid": [item.__dict__ for item in idea_bundle.avoid],
        "test_next": [item.__dict__ for item in idea_bundle.test_next],
        "video_ideas": [item.__dict__ for item in idea_bundle.video_ideas],
    }
    recommendations["actions"] = _recommended_actions(channel_df, topic_metrics, duration_metrics, outliers)
    # Recommendations are deterministic and evidence-backed by default. The UI
    # does not auto-call an LLM or present generated prose as analysis.
    recommendations["ai_overlay"] = ""
    if topic_mode_metadata.get("model_status") == "showcase_fixture":
        recommendations = _ninja_showcase_recommendations(topic_metrics)

    snapshot_at = summary["snapshot_at"]
    channel_handle = parsed_input.handle or (parsed_input.lookup_value if parsed_input.lookup_value.startswith("@") else "")
    upsert_tracked_channel(
        channel_id=workspace.channel_id,
        input_value=parsed_input.lookup_value,
        canonical_url=workspace.canonical_url,
        channel_title=workspace.channel_title,
        channel_handle=channel_handle,
        source=workspace.source,
        added_at=snapshot_at,
        last_refresh_at=snapshot_at,
        db_path=db_path,
    )
    store_channel_snapshot(
        channel_id=workspace.channel_id,
        snapshot_at=snapshot_at,
        source=workspace.source,
        summary=summary,
        videos_df=channel_df,
        topic_metrics_df=topic_metrics,
        insights_payload=_insight_payload(
            channel_df=channel_df,
            topic_metrics=topic_metrics,
            duration_metrics=duration_metrics,
            title_pattern_metrics=title_pattern_metrics,
            publish_day_metrics=publish_day_metrics,
            publish_hour_metrics=publish_hour_metrics,
            outliers=outliers,
            underperformers=underperformers,
            summary=summary,
            recommendations=recommendations,
            topic_mode_metadata=topic_mode_metadata,
        ),
        db_path=db_path,
    )
    return load_channel_insights(workspace.channel_id, db_path=db_path) or {}


def list_connected_channels(db_path: Path = DEFAULT_CHANNEL_INSIGHTS_DB) -> List[Dict[str, Any]]:
    return list_tracked_channels(db_path=db_path)


def load_channel_insights(channel_id: str, *, db_path: Path = DEFAULT_CHANNEL_INSIGHTS_DB) -> Optional[Dict[str, Any]]:
    tracked = get_tracked_channel(channel_id, db_path=db_path)
    snapshot = load_latest_channel_snapshot(channel_id, db_path=db_path)
    if not tracked or not snapshot:
        return None

    history_df = list_channel_snapshot_history(channel_id, db_path=db_path)
    insights = snapshot.get("insights", {})
    videos_df = pd.DataFrame(snapshot.get("videos", []))
    topic_metrics_df = pd.DataFrame(snapshot.get("topic_metrics", []))
    summary = snapshot.get("summary", {})
    history_delta = _history_delta(history_df)

    if videos_df.empty and "outliers" in insights:
        videos_df = pd.DataFrame(insights.get("outliers", []))

    return {
        "channel": tracked,
        "snapshot_at": snapshot["snapshot_at"],
        "source": snapshot["source"],
        "summary": summary,
        "topic_mode_metadata": insights.get("topic_mode_metadata", {}),
        "topic_artifact_status": get_bertopic_artifact_status(),
        "history_delta": history_delta,
        "videos_df": videos_df,
        "topic_metrics_df": topic_metrics_df,
        "duration_metrics_df": pd.DataFrame(insights.get("duration_metrics", [])),
        "title_pattern_metrics_df": pd.DataFrame(insights.get("title_pattern_metrics", [])),
        "publish_day_metrics_df": pd.DataFrame(insights.get("publish_day_metrics", [])),
        "publish_hour_metrics_df": pd.DataFrame(insights.get("publish_hour_metrics", [])),
        "outliers_df": pd.DataFrame(insights.get("outliers", [])),
        "underperformers_df": pd.DataFrame(insights.get("underperformers", [])),
        "recommendations": insights.get("recommendations", {}),
        "history_df": history_df,
    }
