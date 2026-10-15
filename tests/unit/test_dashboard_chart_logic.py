import pandas as pd

from dashboard.views.channel_analysis import (
    _publication_cohort_chart,
    _publication_cohort_summary,
)
from dashboard.views.outlier_finder import _breakout_scatter
from dashboard.views.ytuber import _suggested_topic_angles


def _cohort_frame(dates: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "video_id": [f"v{i}" for i in range(len(dates))],
            "video_publishedAt": pd.to_datetime(dates, utc=True),
            "views_per_day": [100.0 + (i * 25) for i in range(len(dates))],
        }
    )


def test_publication_cohorts_use_months_for_short_ranges() -> None:
    summary, grain = _publication_cohort_summary(
        _cohort_frame(["2024-01-01", "2024-01-20", "2025-02-01"])
    )

    assert grain == "month"
    assert summary["cohort"].tolist() == ["2024-01", "2025-02"]
    assert summary["videos"].tolist() == [2, 1]
    assert _publication_cohort_chart(summary, grain).layout.xaxis.title.text == "Publication month"


def test_publication_cohorts_use_years_for_long_ranges() -> None:
    summary, grain = _publication_cohort_summary(
        _cohort_frame(["2014-01-01", "2020-06-15", "2025-02-01"])
    )

    assert grain == "year"
    assert summary["cohort"].tolist() == ["2014", "2020", "2025"]
    assert _publication_cohort_chart(summary, grain).layout.xaxis.title.text == "Publication year"


def test_breakout_chart_shows_real_subscriber_values_on_log_axis() -> None:
    frame = pd.DataFrame(
        {
            "video_id": ["a", "b"],
            "channel_subscriber_count": [1_000, 100_000],
            "hidden_subscriber_count": [False, False],
            "views_per_day": [100, 300],
            "outlier_score": [60, 80],
            "age_bucket": ["8–30 days", "0–7 days"],
            "video_title": ["A", "B"],
            "channel_title": ["X", "Y"],
            "views": [1_000, 2_000],
            "age_days": [10, 5],
            "language_confidence_label": ["High", "High"],
        }
    )

    fig = _breakout_scatter(frame)

    assert fig.layout.xaxis.type == "log"
    plotted_subscribers = sorted(int(value) for trace in fig.data for value in trace.x)
    assert plotted_subscribers == [1_000, 100_000]


def test_topic_angles_are_readable_and_ranked_by_daily_reach() -> None:
    frame = pd.DataFrame(
        {
            "video_title": [
                "How They Prevented The Citicorp Disaster",
                "What Happens If You Keep Slowing Down?",
                "World's Largest Spiderweb",
            ],
            "views_per_day": [300, 100, 200],
        }
    )

    assert _suggested_topic_angles(frame, top_n=3) == [
        "Prevented citicorp disaster",
        "Largest spiderweb",
        "Slowing down",
    ]

