from __future__ import annotations

import pandas as pd

from src.services.model_artifact_service import ModelArtifactStatus
from src.services.topic_model_runtime import (
    _topic_label_from_model,
    apply_optional_topic_model,
    build_bertopic_inference_text,
)


def test_build_bertopic_inference_text_applies_cleaning() -> None:
    text, token_count, is_sparse = build_bertopic_inference_text(
        "How To Fix 3 Thumbnail Problems",
        "Subscribe here!\nThis breaks down packaging and click through rate. https://example.com",
        "thumbnail|ctr|packaging",
    )

    assert "subscribe" not in text
    assert "https" not in text
    assert "how" not in text
    assert "this" not in text
    assert "thumbnail" in text
    assert "3" not in text
    assert token_count >= 5
    assert is_sparse is False


def test_build_bertopic_inference_text_ignores_contaminated_legacy_tags() -> None:
    text, _, _ = build_bertopic_inference_text(
        "Arc Raiders update changed the economy",
        "Blueprint prices and loot progression explained for the new patch.",
        "fortnite|battle royale|victory royale|ninja",
    )

    assert "arc" in text
    assert "economy" in text
    assert "fortnite" not in text
    assert "victory" not in text


def test_topic_labels_drop_stopword_only_terms() -> None:
    class _FakeTopicModel:
        def get_topic(self, topic_id: int):
            return [("need", 0.5), ("after", 0.4), ("back", 0.3), ("economy", 0.2), ("blueprints", 0.1)]

    _, label = _topic_label_from_model(_FakeTopicModel(), 4)

    assert label == "Economy / Blueprints"


def test_apply_optional_topic_model_returns_rows(monkeypatch) -> None:
    sample_df = pd.DataFrame(
        [
            {
                "video_id": "v1",
                "video_title": "How To Improve Packaging",
                "video_description": "packaging and ctr ideas",
                "video_tags": "packaging|ctr",
            }
        ]
    )

    class _FakeTopicModel:
        def transform(self, texts):
            assert len(texts) == 1
            return [18], None

        def get_topic(self, topic_id: int):
            assert topic_id == 18
            return [("packaging", 0.4), ("ctr", 0.3), ("thumbnail", 0.2), ("hooks", 0.1)]

    monkeypatch.setattr(
        "src.services.topic_model_runtime.ensure_bertopic_artifact_ready",
        lambda: ModelArtifactStatus(
            state="ready",
            enabled=True,
            configured=True,
            ready=True,
            model_type="bertopic_global",
            bundle_version="2026.03.27",
            local_model_path="/tmp/bertopic_model.pkl",
        ),
    )
    monkeypatch.setattr("src.services.topic_model_runtime._load_topic_model", lambda path: _FakeTopicModel())

    result = apply_optional_topic_model(sample_df)

    assert result.success is True
    assert result.bundle_version == "2026.03.27"
    assert result.topic_rows[0]["model_topic_id"] == 18
    assert result.topic_rows[0]["model_topic_label"] == "Packaging / Ctr / Thumbnail / Hooks"


def test_low_confidence_topic_assignment_abstains(monkeypatch) -> None:
    sample_df = pd.DataFrame(
        [{"video_id": "v1", "video_title": "Specific packaging breakdown for creators", "video_description": "thumbnail hooks and audience promise", "video_tags": "packaging|thumbnail"}]
    )

    class _FakeTopicModel:
        def transform(self, texts):
            return [18], [0.12]

        def get_topic(self, topic_id: int):
            return []

    monkeypatch.setattr(
        "src.services.topic_model_runtime.ensure_bertopic_artifact_ready",
        lambda: ModelArtifactStatus(
            state="ready", enabled=True, configured=True, ready=True,
            model_type="bertopic_global", bundle_version="test", local_model_path="/tmp/model.pkl"
        ),
    )
    monkeypatch.setattr("src.services.topic_model_runtime._load_topic_model", lambda path: _FakeTopicModel())

    result = apply_optional_topic_model(sample_df)

    assert result.topic_rows[0]["model_topic_id"] == -1
    assert result.topic_rows[0]["model_topic_label"] == "Unassigned"
    assert result.topic_rows[0]["topic_abstained"] is True
