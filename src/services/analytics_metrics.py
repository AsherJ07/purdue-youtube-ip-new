"""Canonical, documented metrics used across the product.

All rates are stored as fractions (``0.05`` means 5%).  Invalid denominators
remain missing instead of being converted into plausible-looking values.
"""

from __future__ import annotations

import math
from typing import Iterable, Optional

import numpy as np
import pandas as pd


MIN_BASELINE_SAMPLE = 10
MIN_TREND_SAMPLE = 3
TREND_PRIOR_STRENGTH = 3.0


def public_interaction_rate(
    views: pd.Series, likes: pd.Series, comments: pd.Series
) -> pd.Series:
    """Return (likes + comments) / views where every input is observable.

    YouTube does not expose saves, shares, watch time, or private interactions
    through this public dataset, so this is deliberately not called a complete
    engagement rate.
    """
    v = pd.to_numeric(views, errors="coerce")
    l = pd.to_numeric(likes, errors="coerce")
    c = pd.to_numeric(comments, errors="coerce")
    valid = (v > 0) & l.notna() & c.notna() & (l >= 0) & (c >= 0)
    result = pd.Series(np.nan, index=v.index, dtype="float64")
    result.loc[valid] = (l.loc[valid] + c.loc[valid]) / v.loc[valid]
    return result


def lifetime_average_daily_views(views: pd.Series, age_days: pd.Series) -> pd.Series:
    """Return lifetime views divided by observed age in days.

    Values younger than one hour use a one-hour floor to prevent near-zero age
    from producing unbounded rates. Missing dates remain missing.
    """
    v = pd.to_numeric(views, errors="coerce")
    age = pd.to_numeric(age_days, errors="coerce")
    valid = (v >= 0) & age.notna() & (age >= 0)
    result = pd.Series(np.nan, index=v.index, dtype="float64")
    result.loc[valid] = v.loc[valid] / age.loc[valid].clip(lower=1 / 24)
    return result


def neutral_percentile_rank(values: pd.Series, *, min_group_size: int = 3) -> pd.Series:
    """Percentile ranks with a neutral result for undersized comparison sets."""
    numeric = pd.to_numeric(values, errors="coerce")
    valid_count = int(numeric.notna().sum())
    result = pd.Series(0.5, index=numeric.index, dtype="float64")
    if valid_count < min_group_size:
        return result
    ranked = numeric.rank(pct=True, method="average")
    result.loc[ranked.notna()] = ranked.loc[ranked.notna()].clip(0.0, 1.0)
    return result


def weighted_available(parts: Iterable[tuple[Optional[float], float]]) -> Optional[float]:
    """Weighted mean that renormalizes over available, finite components."""
    numerator = 0.0
    denominator = 0.0
    for value, weight in parts:
        if value is None or not math.isfinite(float(value)) or weight <= 0:
            continue
        numerator += float(value) * float(weight)
        denominator += float(weight)
    return numerator / denominator if denominator else None


def log_lift(value: float, baseline: float, *, cap: float = 8.0) -> Optional[float]:
    """Map a positive ratio to [0, 1] using a capped logarithmic transform."""
    if baseline <= 0 or value < 0:
        return None
    ratio = min(max(value / baseline, 0.0), cap)
    return math.log1p(ratio) / math.log1p(cap)


def shrunk_log_trend(
    recent_values: pd.Series,
    prior_values: pd.Series,
    *,
    alpha: float = 1.0,
    min_sample: int = MIN_TREND_SAMPLE,
    prior_strength: float = TREND_PRIOR_STRENGTH,
) -> tuple[Optional[float], str]:
    """Return a stable recent-vs-prior log lift and an evidence label.

    Sparse two-window comparisons abstain. A topic with enough recent evidence
    but no prior observations is labelled ``new`` instead of receiving a
    fabricated growth percentage.
    """
    recent = pd.to_numeric(recent_values, errors="coerce").dropna()
    prior = pd.to_numeric(prior_values, errors="coerce").dropna()
    if len(recent) < min_sample:
        return None, "insufficient"
    if len(prior) < min_sample:
        return None, "new"
    raw = math.log((float(recent.median()) + alpha) / (float(prior.median()) + alpha))
    reliability = min(len(recent), len(prior)) / (min(len(recent), len(prior)) + prior_strength)
    return raw * reliability, "measured"


def evidence_confidence(sample_size: int, *, minimum: int = MIN_BASELINE_SAMPLE) -> str:
    if sample_size < minimum:
        return "Low"
    if sample_size < minimum * 2:
        return "Medium"
    return "High"


def robust_consistency(values: pd.Series) -> Optional[float]:
    """Return a 0-100 robust consistency index based on median absolute deviation."""
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if len(numeric) < 3:
        return None
    median = float(numeric.median())
    if median <= 0:
        return None
    mad = float((numeric - median).abs().median())
    return max(0.0, min(100.0, 100.0 * (1.0 - min(mad / median, 1.0))))


__all__ = [
    "MIN_BASELINE_SAMPLE",
    "MIN_TREND_SAMPLE",
    "evidence_confidence",
    "lifetime_average_daily_views",
    "log_lift",
    "neutral_percentile_rank",
    "public_interaction_rate",
    "robust_consistency",
    "shrunk_log_trend",
    "weighted_available",
]
