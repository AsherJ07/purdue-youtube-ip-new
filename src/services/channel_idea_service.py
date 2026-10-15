from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

import requests

from src.utils.api_keys import get_provider_key_count, run_with_provider_keys


@dataclass(frozen=True)
class ThemeRecommendation:
    theme: str
    rationale: str
    action: str
    confidence: str = "Low"
    sample_size: int = 0
    evidence: str = ""


@dataclass(frozen=True)
class IdeaSuggestion:
    title: str
    why_now: str


@dataclass(frozen=True)
class ChannelIdeaBundle:
    summary: str
    double_down: tuple[ThemeRecommendation, ...]
    avoid: tuple[ThemeRecommendation, ...]
    test_next: tuple[ThemeRecommendation, ...]
    video_ideas: tuple[IdeaSuggestion, ...]
    ai_overlay: str = ""


def _safe_text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _heuristic_theme_rows(topic_metrics: Sequence[Mapping[str, Any]]) -> tuple[List[ThemeRecommendation], List[ThemeRecommendation], List[ThemeRecommendation]]:
    sorted_topics = [
        row for row in topic_metrics
        if int(row.get("video_count", 0) or 0) >= 3
        and str(row.get("topic_label", "")).strip().lower() not in {"", "misc", "unassigned"}
    ]
    if not sorted_topics:
        fallback = ThemeRecommendation(
            "Not enough evidence yet",
            "No theme has at least three comparable videos.",
            "Publish or import more videos before using theme-level recommendations.",
            confidence="Low",
        )
        return [fallback], [], [fallback]

    winners: List[ThemeRecommendation] = []
    weak: List[ThemeRecommendation] = []
    test_next: List[ThemeRecommendation] = []

    by_reach = sorted(
        sorted_topics,
        key=lambda item: (item.get("median_views_per_day", 0), item.get("video_count", 0)),
        reverse=True,
    )
    for row in by_reach[:2]:
        n = int(row.get("video_count", 0) or 0)
        winners.append(
            ThemeRecommendation(
                theme=_safe_text(row.get("topic_label"), "Winning Theme"),
                rationale=f"Median views/day is {_safe_text(round(row.get('median_views_per_day', 0), 1))} with {int(row.get('video_count', 0) or 0)} tracked videos.",
                action="Run one adjacent-angle test while holding format and publishing window as constant as practical.",
                confidence="High" if n >= 10 else "Medium",
                sample_size=n,
                evidence=f"{n} videos; median lifetime-average daily views {float(row.get('median_views_per_day', 0) or 0):,.0f}.",
            )
        )

    for row in sorted(by_reach, key=lambda item: item.get("median_views_per_day", 0))[:1]:
        n = int(row.get("video_count", 0) or 0)
        weak.append(
            ThemeRecommendation(
                theme=_safe_text(row.get("topic_label"), "Weak Theme"),
                rationale=f"This cluster is lagging with lower median views/day and only {int(row.get('outlier_count', 0) or 0)} breakout videos.",
                action="Repackage one controlled test before reducing investment; this is an association, not a causal result.",
                confidence="High" if n >= 10 else "Medium",
                sample_size=n,
                evidence=f"{n} videos in the comparison set.",
            )
        )

    measured = [
        row for row in sorted_topics
        if row.get("trend_status") == "measured"
        and int(row.get("recent_video_count", 0) or 0) >= 3
        and int(row.get("previous_video_count", 0) or 0) >= 3
    ]
    for row in sorted(measured, key=lambda item: item.get("trend_score", float("-inf")), reverse=True)[:2]:
        n = int(row.get("video_count", 0) or 0)
        test_next.append(
            ThemeRecommendation(
                theme=_safe_text(row.get("topic_label"), "Next Theme"),
                rationale=f"Recent performance is stronger after shrinkage, supported by {int(row.get('recent_video_count', 0) or 0)} recent and {int(row.get('previous_video_count', 0) or 0)} prior uploads.",
                action="Test one new angle and compare its lifetime-average daily views against the same-age channel cohort.",
                confidence="High" if n >= 10 else "Medium",
                sample_size=n,
                evidence=f"Shrunk log lift {float(row.get('trend_score', 0) or 0):.2f}.",
            )
        )

    return winners, weak, test_next


def _heuristic_ideas(channel_title: str, test_next: Sequence[ThemeRecommendation]) -> List[IdeaSuggestion]:
    ideas: List[IdeaSuggestion] = []
    for item in list(test_next)[:4]:
        ideas.append(
            IdeaSuggestion(
                title=f"Test an adjacent angle in {item.theme}",
                why_now=f"{item.evidence} Treat this as a measured experiment, not a guaranteed outcome.",
            )
        )
    return ideas


def build_grounded_idea_bundle(
    channel_title: str,
    topic_metrics: Sequence[Mapping[str, Any]],
    outlier_rows: Sequence[Mapping[str, Any]],
    underperformer_rows: Sequence[Mapping[str, Any]],
) -> ChannelIdeaBundle:
    winners, weak, test_next = _heuristic_theme_rows(topic_metrics)
    ideas = _heuristic_ideas(channel_title, test_next)
    summary = (
        f"{channel_title} has enough repeated evidence for a small set of testable theme decisions. Each recommendation shows its sample and uncertainty."
        if topic_metrics
        else f"{channel_title} needs a larger recent sample before the recommendation engine becomes highly confident."
    )
    return ChannelIdeaBundle(
        summary=summary,
        double_down=tuple(winners),
        avoid=tuple(weak),
        test_next=tuple(test_next),
        video_ideas=tuple(ideas),
    )


def _gemini_generate_text(api_key: str, model: str, prompt: str) -> str:
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    response = requests.post(
        endpoint,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=90,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text[:400]}")
    body = response.json()
    return (
        body.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )


def _openai_generate_text(api_key: str, model: str, prompt: str) -> str:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a concise YouTube strategy assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        },
        timeout=90,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI API error ({response.status_code}): {response.text[:400]}")
    body = response.json()
    return body.get("choices", [{}])[0].get("message", {}).get("content", "")


def maybe_generate_ai_overlay(
    channel_title: str,
    summary_payload: Mapping[str, Any],
    topic_metrics: Sequence[Mapping[str, Any]],
    provider_preference: str = "gemini",
) -> str:
    available = [provider for provider in ("gemini", "openai") if get_provider_key_count(provider) > 0]
    if not available:
        return ""

    provider = provider_preference if provider_preference in available else available[0]
    model = "gemini-2.5-flash" if provider == "gemini" else "gpt-4o-mini"
    prompt = (
        "You are helping a YouTube creator decide what to make next based on public channel performance data. "
        "Give a concise markdown answer with three short sections: Double Down, Stop Doing, Test Next. "
        "Use only the analytics below.\n\n"
        f"Channel: {channel_title}\n"
        f"Summary: {json.dumps(dict(summary_payload), ensure_ascii=True)}\n"
        f"Topic Metrics: {json.dumps(list(topic_metrics)[:8], ensure_ascii=True)}"
    )
    if provider == "gemini":
        return run_with_provider_keys("gemini", lambda key: _gemini_generate_text(key, model, prompt))
    return run_with_provider_keys("openai", lambda key: _openai_generate_text(key, model, prompt))

