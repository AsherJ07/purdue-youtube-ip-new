import math

import pandas as pd

from src.services.analytics_metrics import (
    lifetime_average_daily_views,
    neutral_percentile_rank,
    public_interaction_rate,
    shrunk_log_trend,
    weighted_available,
)


def test_public_interaction_rate_abstains_for_invalid_or_missing_inputs() -> None:
    rate = public_interaction_rate(
        pd.Series([100, 0, 100, 100]),
        pd.Series([4, 4, None, 2]),
        pd.Series([1, 1, 1, 3]),
    )
    assert rate.iloc[0] == 0.05
    assert math.isnan(rate.iloc[1])
    assert math.isnan(rate.iloc[2])
    assert rate.iloc[3] == 0.05


def test_lifetime_daily_views_has_one_hour_floor_and_preserves_unknown_age() -> None:
    result = lifetime_average_daily_views(pd.Series([24, 24]), pd.Series([0, None]))
    assert result.iloc[0] == 576
    assert math.isnan(result.iloc[1])


def test_percentile_is_neutral_for_tiny_cohorts() -> None:
    assert neutral_percentile_rank(pd.Series([99])).iloc[0] == 0.5
    ranks = neutral_percentile_rank(pd.Series([1, 2, 3]))
    assert ranks.iloc[-1] == 1.0


def test_weighted_available_does_not_impute_missing_signals() -> None:
    assert weighted_available([(1.0, 0.6), (None, 0.4)]) == 1.0


def test_trend_abstains_for_new_or_sparse_topics_and_shrinks_measured_lift() -> None:
    assert shrunk_log_trend(pd.Series([5, 6]), pd.Series([1, 2, 3])) == (None, "insufficient")
    assert shrunk_log_trend(pd.Series([5, 6, 7]), pd.Series([])) == (None, "new")
    score, state = shrunk_log_trend(pd.Series([20, 22, 24]), pd.Series([10, 11, 12]))
    assert state == "measured"
    assert 0 < score < math.log(2.1)
