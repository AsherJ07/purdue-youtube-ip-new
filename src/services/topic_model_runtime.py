from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd

from src.services.model_artifact_service import ModelArtifactStatus, ensure_bertopic_artifact_ready


SPARSE_TOKEN_THRESHOLD = 5
DESCRIPTION_CHAR_LIMIT = 600
TOPIC_CONFIDENCE_THRESHOLD = 0.35

_BOILERPLATE_PATTERNS = [
    r"subscribe.*",
    r"follow me.*",
    r"patreon.*",
    r"discord.*",
    r"merch.*",
    r"sponsor.*",
    r"affiliate.*",
    r"business.*",
    r"contact.*",
    r"link(s)? in (the )?description.*",
]

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE = re.compile(r"[@#][A-Za-z0-9_]+")
_PUNCT_RE = re.compile(r"[^A-Za-z0-9\s]+")
_MULTISPACE_RE = re.compile(r"\s+")
_STANDALONE_DIGITS_RE = re.compile(r"\b\d+\b")


@dataclass(frozen=True)
class TopicModelInferenceResult:
    success: bool
    topic_rows: tuple[Dict[str, Any], ...]
    bundle_version: str = ""
    topic_source: str = "heuristic"
    message: str = ""
    failure_reason: str = ""
    status: str = ""


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = _URL_RE.sub(" ", str(text))
    cleaned = _MENTION_RE.sub(" ", cleaned)
    cleaned = _PUNCT_RE.sub(" ", cleaned)
    cleaned = _MULTISPACE_RE.sub(" ", cleaned)
    return cleaned.strip().lower()


def _strip_boilerplate(description: str) -> str:
    if not description:
        return ""
    lines = []
    for raw_line in str(description).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if any(re.match(pattern, lower) for pattern in _BOILERPLATE_PATTERNS):
            continue
        lines.append(line)
    return " ".join(lines)


def build_bertopic_inference_text(title: str, description: str = "", tags: str = "") -> tuple[str, int, bool]:
    title_clean = _normalize_text(title)
    description_clean = _normalize_text(_strip_boilerplate(description))[:DESCRIPTION_CHAR_LIMIT]
    tag_items = [item.strip() for item in str(tags or "").replace("|", " ").split() if item.strip()]
    tags_clean = _normalize_text(" ".join(tag_items))

    combined = " ".join(part for part in [title_clean, title_clean, description_clean, tags_clean] if part)
    combined = _STANDALONE_DIGITS_RE.sub(" ", combined)
    combined = _MULTISPACE_RE.sub(" ", combined).strip()
    token_count = len(combined.split()) if combined else 0
    is_sparse = token_count < SPARSE_TOKEN_THRESHOLD
    return combined, token_count, is_sparse


def _load_topic_model(model_path: str):
    from bertopic import BERTopic

    return BERTopic.load(model_path)


def _topic_label_from_model(topic_model: Any, topic_id: int) -> tuple[str, str]:
    if topic_id == -1:
        return "-1_unassigned", "Unassigned"
    try:
        topic_terms = topic_model.get_topic(topic_id) or []
    except Exception:
        topic_terms = []
    keywords: List[str] = []
    for term, _score in topic_terms:
        cleaned = str(term).strip().lower().replace("_", " ")
        if not cleaned or cleaned in keywords or len(cleaned) < 3:
            continue
        keywords.append(cleaned)
        if len(keywords) == 4:
            break
    if not keywords:
        return f"{topic_id}_topic", f"Topic {topic_id}"
    raw = f"{topic_id}_" + "_".join(keywords)
    human = " / ".join(keyword.replace("_", " ").title() for keyword in keywords)
    return raw, human


def _assignment_confidences(probabilities: Any, count: int) -> List[float | None]:
    if probabilities is None:
        return [None] * count
    try:
        values = probabilities.tolist() if hasattr(probabilities, "tolist") else list(probabilities)
    except TypeError:
        return [None] * count
    result: List[float | None] = []
    for value in values[:count]:
        if isinstance(value, (list, tuple)):
            result.append(float(max(value)) if value else None)
        else:
            try:
                result.append(float(value))
            except (TypeError, ValueError):
                result.append(None)
    return result + [None] * max(0, count - len(result))


def apply_optional_topic_model(channel_df: pd.DataFrame) -> TopicModelInferenceResult:
    if channel_df.empty:
        return TopicModelInferenceResult(
            success=False,
            topic_rows=(),
            failure_reason="No channel videos were available for BERTopic inference.",
            status="empty",
        )

    artifact_status: ModelArtifactStatus = ensure_bertopic_artifact_ready()
    if not artifact_status.ready:
        return TopicModelInferenceResult(
            success=False,
            topic_rows=(),
            bundle_version=artifact_status.bundle_version,
            failure_reason=artifact_status.failure_reason or artifact_status.message,
            status=artifact_status.state,
        )

    try:
        topic_model = _load_topic_model(artifact_status.local_model_path)
    except Exception as exc:
        return TopicModelInferenceResult(
            success=False,
            topic_rows=(),
            bundle_version=artifact_status.bundle_version,
            failure_reason=f"BERTopic model could not be loaded: {exc}",
            status="load_failed",
        )

    texts: List[str] = []
    tokens: List[int] = []
    sparse_flags: List[bool] = []
    video_ids = channel_df["video_id"].astype(str).tolist()

    for row in channel_df.to_dict(orient="records"):
        inference_text, token_count, is_sparse = build_bertopic_inference_text(
            str(row.get("video_title", "")),
            str(row.get("video_description", "")),
            str(row.get("video_tags", "")),
        )
        texts.append(inference_text)
        tokens.append(token_count)
        sparse_flags.append(is_sparse)

    try:
        topic_ids, probabilities = topic_model.transform(texts)
    except Exception as exc:
        return TopicModelInferenceResult(
            success=False,
            topic_rows=(),
            bundle_version=artifact_status.bundle_version,
            failure_reason=f"BERTopic inference failed: {exc}",
            status="transform_failed",
        )

    rows: List[Dict[str, Any]] = []
    confidences = _assignment_confidences(probabilities, len(video_ids))
    for video_id, topic_id, confidence, inference_text, token_count, is_sparse in zip(
        video_ids, topic_ids, confidences, texts, tokens, sparse_flags
    ):
        assigned_id = int(topic_id)
        abstained = bool(
            is_sparse
            or assigned_id == -1
            or (confidence is not None and confidence < TOPIC_CONFIDENCE_THRESHOLD)
        )
        if abstained:
            assigned_id = -1
        raw_label, human_label = _topic_label_from_model(topic_model, assigned_id)
        rows.append(
            {
                "video_id": str(video_id),
                "model_topic_id": assigned_id,
                "model_topic_label_raw": raw_label,
                "model_topic_label": human_label,
                "topic_source": "bertopic_global",
                "bertopic_text": inference_text,
                "bertopic_token_count": token_count,
                "is_sparse_text": is_sparse,
                "topic_confidence": confidence,
                "topic_abstained": abstained,
            }
        )

    return TopicModelInferenceResult(
        success=True,
        topic_rows=tuple(rows),
        bundle_version=artifact_status.bundle_version,
        topic_source="bertopic_global",
        message="BERTopic topic assignments were applied successfully.",
        status="ready",
    )


__all__ = [
    "DESCRIPTION_CHAR_LIMIT",
    "SPARSE_TOKEN_THRESHOLD",
    "TOPIC_CONFIDENCE_THRESHOLD",
    "TopicModelInferenceResult",
    "apply_optional_topic_model",
    "build_bertopic_inference_text",
]
