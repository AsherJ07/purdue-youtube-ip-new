from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import pandas as pd
import requests

from src.utils.api_keys import run_with_provider_keys


@dataclass(frozen=True)
class InsightCard:
    title: str
    body: str
    support: str = ""


@dataclass(frozen=True)
class OutlierAIReport:
    provider: str
    model: str
    executive_headline: str
    key_takeaway: str
    confidence_label: str
    confidence_notes: Tuple[str, ...]
    breakout_themes: Tuple[InsightCard, ...]
    title_patterns: Tuple[InsightCard, ...]
    repeatable_angles: Tuple[InsightCard, ...]
    notable_anomalies: Tuple[InsightCard, ...]
    next_steps: Tuple[str, ...]
    warnings: Tuple[str, ...]
    raw_fallback: str = ""


def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    candidate = str(text or "").strip()
    if not candidate:
        return None

    if "```json" in candidate:
        candidate = candidate.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in candidate:
        candidate = candidate.split("```", 1)[1].split("```", 1)[0].strip()
    else:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start >= 0 and end > start:
            candidate = candidate[start : end + 1]

    try:
        parsed = json.loads(candidate)
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def _safe_text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _card_tuple(payload: Any) -> Tuple[InsightCard, ...]:
    cards: List[InsightCard] = []
    if not isinstance(payload, list):
        return tuple(cards)
    for item in payload:
        if not isinstance(item, Mapping):
            continue
        title = _safe_text(item.get("title"))
        body = _safe_text(item.get("body"))
        if not title or not body:
            continue
        cards.append(
            InsightCard(
                title=title,
                body=body,
                support=_safe_text(item.get("support")),
            )
        )
    return tuple(cards)


def _string_tuple(payload: Any) -> Tuple[str, ...]:
    if not isinstance(payload, list):
        return tuple()
    return tuple(_safe_text(item) for item in payload if _safe_text(item))


def _fallback_report(provider: str, model: str, raw_text: str) -> OutlierAIReport:
    clipped = _safe_text(raw_text).replace("\n", " ")
    if len(clipped) > 420:
        clipped = clipped[:417].rstrip() + "..."
    return OutlierAIReport(
        provider=provider,
        model=model,
        executive_headline="AI Research Available in Fallback Mode",
        key_takeaway=clipped or "The provider returned an unstructured answer, so the report is being shown in simplified form.",
        confidence_label="Low",
        confidence_notes=("This output could not be parsed into the expected research schema.",),
        breakout_themes=tuple(),
        title_patterns=tuple(),
        repeatable_angles=tuple(),
        notable_anomalies=tuple(),
        next_steps=tuple(),
        warnings=("Structured parsing failed; review the fallback summary before acting on it.",),
        raw_fallback=raw_text,
    )


def _build_prompt(
    query_context: Mapping[str, Any],
    summary_stats: Mapping[str, Any],
    top_rows: Sequence[Mapping[str, Any]],
) -> str:
    return (
        "You are a YouTube strategist analyzing public outlier-video research. The search query defines the category boundary; your job is to discover what is winning inside that category.\n"
        "Return valid JSON only with this schema:\n"
        "{\n"
        '  "executive_headline": "short string",\n'
        '  "key_takeaway": "one concise sentence",\n'
        '  "confidence_label": "High|Medium|Low",\n'
        '  "confidence_notes": ["", ""],\n'
        '  "breakout_themes": [{"title":"", "body":"", "support":""}],\n'
        '  "title_patterns": [{"title":"", "body":"", "support":""}],\n'
        '  "repeatable_angles": [{"title":"", "body":"", "support":""}],\n'
        '  "notable_anomalies": [{"title":"", "body":"", "support":""}],\n'
        '  "next_steps": ["", "", ""],\n'
        '  "warnings": ["", ""]\n'
        "}\n\n"
        "Rules:\n"
        "- Keep each body under 35 words.\n"
        "- Never recommend making more content that merely repeats or paraphrases the niche query.\n"
        "- Example: for 'science shorts', 'make more science shorts' is invalid; specific patterns such as household chemistry tests, animal-scale mysteries, or optical illusions are valid only when supported by the supplied rows.\n"
        "- The executive headline must name a specific subtopic, premise, or audience curiosity found inside the niche; do not use the query itself as the conclusion.\n"
        "- Return exactly three distinct breakout_themes. Each title must be a specific 2-6 word subtopic, not a format label or the broad niche. Generic labels such as 'science experiments' are invalid.\n"
        "- Each breakout theme must be supported by at least two separate video rows. Cite both video titles and their views_per_day or outlier_score in the support field. If three repeated themes are not supported, state 'Insufficient repeated evidence' instead of inventing one.\n"
        "- Never infer culture, geography, audience identity, or viewer intent merely from a title's language, channel name, or metadata.\n"
        "- Return exactly one title_pattern, one repeatable_angle, and at most one notable_anomaly.\n"
        "- The repeatable_angle must name a concrete subject, mechanism, and viewer payoff that is meaningfully narrower than the query.\n"
        "- Return exactly three next_steps in this order: 'Concept: <specific video premise and working title>', 'Hook: <first 3-5 seconds>', and 'Success check: <metric and threshold grounded in the cohort>'.\n"
        "- Ban generic hooks such as 'Have you ever wondered', 'Did you know', 'Let's experiment', and 'You won't believe'. The hook must show the specific object, conflict, or result immediately.\n"
        "- The success threshold must reference the supplied cohort median and use the same metric; do not invent a lower arbitrary target.\n"
        "- Every support field must cite a video title or a metric from the payload.\n"
        "- Compare multiple rows before calling something a pattern; treat a one-video signal as an anomaly.\n"
        "- Use only evidence available in the payload.\n"
        "- Mention caveats if confidence is limited.\n"
        "- Do not mention hidden internal reasoning.\n\n"
        f"Query Context: {json.dumps(dict(query_context), ensure_ascii=True)}\n"
        f"Summary Stats: {json.dumps(dict(summary_stats), ensure_ascii=True)}\n"
        f"Top Outliers: {json.dumps(list(top_rows), ensure_ascii=True)}"
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
        raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text[:500]}")
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
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You produce concise structured research outputs."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=90,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI API error ({response.status_code}): {response.text[:500]}")
    body = response.json()
    return (
        body.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )


def _report_from_payload(provider: str, model: str, payload: Mapping[str, Any], raw_text: str) -> OutlierAIReport:
    return OutlierAIReport(
        provider=provider,
        model=model,
        executive_headline=_safe_text(payload.get("executive_headline"), "What Is Breaking Out Right Now"),
        key_takeaway=_safe_text(payload.get("key_takeaway"), "The scanned cohort shows a few packaging and format patterns that are outperforming their peer set."),
        confidence_label=_safe_text(payload.get("confidence_label"), "Medium"),
        confidence_notes=_string_tuple(payload.get("confidence_notes")),
        breakout_themes=_card_tuple(payload.get("breakout_themes")),
        title_patterns=_card_tuple(payload.get("title_patterns")),
        repeatable_angles=_card_tuple(payload.get("repeatable_angles")),
        notable_anomalies=_card_tuple(payload.get("notable_anomalies")),
        next_steps=_string_tuple(payload.get("next_steps")),
        warnings=_string_tuple(payload.get("warnings")),
        raw_fallback=raw_text if not payload else "",
    )


def generate_outlier_ai_report(
    provider: str,
    model: str,
    query_context: Mapping[str, Any],
    summary_stats: Mapping[str, Any],
    result_frame: pd.DataFrame,
) -> OutlierAIReport:
    provider_name = provider.lower().strip()
    top_rows = result_frame.head(20)[
        [
            "video_title",
            "channel_title",
            "outlier_score",
            "views",
            "views_per_day",
            "engagement_rate",
            "duration_bucket",
            "title_pattern",
            "language_confidence_label",
            "why_outlier",
            "research_cue",
        ]
    ].to_dict(orient="records")
    prompt = _build_prompt(query_context=query_context, summary_stats=summary_stats, top_rows=top_rows)

    if provider_name == "gemini":
        raw_text = run_with_provider_keys(
            "gemini",
            lambda key: _gemini_generate_text(key, model, prompt),
        )
    elif provider_name == "openai":
        raw_text = run_with_provider_keys(
            "openai",
            lambda key: _openai_generate_text(key, model, prompt),
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    parsed = _extract_json_block(raw_text)
    if not parsed:
        return _fallback_report(provider_name, model, raw_text)
    return _report_from_payload(provider_name, model, parsed, raw_text)
