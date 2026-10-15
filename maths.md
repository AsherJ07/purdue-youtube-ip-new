# YouTube Creator Insights Metrics and Decision Logic

This document is the source of truth for every metric shown in YouTube Creator Insights. Rates are stored as decimal fractions in code (`0.05`) and displayed as percentages (`5.00%`). Missing or invalid observations remain unavailable; they are never converted to zero merely to make a formula run.

## Measurement boundaries

YouTube Creator Insights uses public YouTube data. It can observe views, public likes, public comments, publication time, duration, text metadata, and—when public—current subscriber count. It cannot observe watch time, retention, shares, saves, satisfaction, private interactions, historical subscriber count, or the time series of views.

The product therefore reports associations in the observed sample. It does not claim causal effects, current view velocity, total engagement, or guaranteed future performance.

## 1. Public interaction rate

For video \(i\):

\[
I_i = \frac{L_i + C_i}{V_i}
\]

where \(L_i\) is public likes, \(C_i\) is public comments, and \(V_i\) is public views.

A row is valid only when views are positive and all three counts are observed and non-negative. If views are zero, or likes/comments are unavailable, the result is missing. In particular, the denominator is never replaced with one.

Group summaries use the median of valid rates because a small number of anomalous records can heavily distort the arithmetic mean. The interface also reports interaction coverage:

\[
\text{coverage} = \frac{\text{rows with valid } I_i}{\text{all rows}}
\]

Why the name matters: this is a **public interaction rate**, not complete engagement. Public data omits watch time, shares, saves, and other meaningful behaviors.

## 2. Lifetime-average daily views

\[
D_i = \frac{V_i}{\max(A_i, 1/24)}
\]

where \(A_i\) is the video's observed age in days. A one-hour floor prevents a newly published video from receiving an unbounded value. Missing publication dates produce a missing result.

This is a lifetime average, not current momentum. A video's views are usually not distributed uniformly through its life. Comparisons therefore use medians and, where possible, publication-age cohorts.

## 3. Percentile ranks

Within a valid comparison group, a value receives its average percentile rank. Ties receive the same average rank. Groups with fewer than three valid observations receive the neutral value 0.50 because a one- or two-item sample does not support an extreme rank.

Missing metrics do not receive an artificially low value. Weighted calculations renormalize over the components that are actually available.

## 4. Channel video performance score

Within one channel snapshot:

\[
P_i = 100(0.70R_{D,i} + 0.30R_{I,i})
\]

where \(R_D\) is the percentile rank of lifetime-average daily views and \(R_I\) is the percentile rank of public interaction rate.

Recency is deliberately excluded: age is already represented in the daily-view metric, and adding recency again would double-count it. Videos are called top-quartile observations only when their score is at or above the snapshot's empirical 75th percentile. Snapshots with fewer than four videos do not declare an outlier.

This is a within-channel descriptive score; values should not be compared across unrelated channel snapshots.

## 5. Topic trend

For a topic with at least three recent and three prior observations:

\[
T = w \log\left(\frac{\widetilde{D}_{recent}+\alpha}{\widetilde{D}_{prior}+\alpha}\right)
\]

where \(\widetilde{D}\) is median lifetime-average daily views, \(\alpha=1\) is a smoothing constant, and

\[
w = \frac{\min(n_{recent}, n_{prior})}{\min(n_{recent}, n_{prior}) + 3}
\]

shrinks small samples toward no change.

Topics with fewer than three recent videos are marked `insufficient`. Topics with enough recent evidence but fewer than three prior observations are marked `new`; they do not receive a made-up growth rate. A positive measured value means recent performance is higher after shrinkage, while a negative value means it is lower.

## 6. Topic and format recommendations

A theme is recommendation-eligible only when it has at least three videos and is not `Misc` or `Unassigned`.

- **Double down** ranks eligible themes by median lifetime-average daily views.
- **Repackage** identifies the eligible theme with the lowest median.
- **Test next** requires a measured topic trend, at least three recent videos, and at least three prior videos.

Confidence is `Medium` for 3–9 supporting videos and `High` for 10 or more. Recommendations include sample size and the supporting statistic. They are framed as controlled experiments, not forecasts.

## 7. Outlier Finder score

The research score uses independent signals:

1. **Channel-relative reach**: a capped log transform of lifetime-average daily views divided by the channel's median. A channel baseline requires at least 10 videos.
2. **Peer reach**: lifetime-average daily-view percentile within a size-and-age peer group, falling back to an age group and then the whole scanned cohort when groups are too small.
3. **Public interaction**: public-interaction-rate percentile in the peer group.
4. **Evidence reliability**: a bounded function of channel-baseline sample size.

Channel-relative and peer reach are first combined:

\[
R = \operatorname{weightedAvailable}(0.55B, 0.45Q)
\]

The final score is:

\[
O = 100\operatorname{weightedAvailable}(0.65R, 0.25E, 0.10K)
\]

where \(B\) is channel-relative reach, \(Q\) peer reach percentile, \(E\) public-interaction percentile, and \(K\) evidence reliability. `weightedAvailable` removes unavailable components and divides by the remaining weights.

Freshness is shown separately and is not a quality multiplier. Subscriber-normalized reach remains diagnostic only because current subscriber count is not a valid historical denominator. A missing subscriber count is not replaced by an arbitrary constant.

The peer population is the returned search sample, not the entire niche, so scores are not calibrated across separate searches.

## 8. Publishing-day and format summaries

Day, hour, duration, and title-pattern summaries use median lifetime-average daily views and display sample size. These are observational associations. The product never calls a day or format causally “best.” Recommendation-facing format groups require at least three observations.

## 9. Upload cadence and consistency

Typical upload cadence is the median number of days between consecutive valid publication timestamps.

The retired all-in-one workspace also computes a robust consistency index for backward compatibility:

\[
C = 100\left(1 - \min\left(\frac{MAD(x)}{\operatorname{median}(x)},1\right)\right)
\]

where \(x\) is the series of upload gaps and `MAD` is median absolute deviation. At least three observations and a positive median are required.

## 10. BERTopic assignment confidence

Inference uses the same normalized title, description, and tag representation for every runtime request. An assignment is converted to `Unassigned` when:

- BERTopic returns topic `-1`;
- input has fewer than five tokens; or
- an available assignment probability is below 0.35.

The system preserves `Unassigned` instead of forcing every document into a topic. Only non-placeholder topics with repeated support can feed recommendations. The deployed model should be evaluated separately for assignment precision, topic coherence/diversity, stability across seeds, abstention rate, and human label usefulness.

## 11. Display and rounding

- Stored rate: decimal fraction.
- Displayed rate: multiply by 100 and append `%`.
- Aggregates: median unless explicitly documented otherwise.
- Counts: integers.
- Scores: 0–100, normally one decimal place.
- Missing evidence: `N/A`, never zero.

Implementation: [`src/services/analytics_metrics.py`](src/services/analytics_metrics.py). Formula tests: [`tests/unit/test_analytics_metrics.py`](tests/unit/test_analytics_metrics.py).
