# YouTube Creator Insights UX audit

This audit treats every chart and interface element as a decision aid. A view passes only when a user can answer three questions without reading implementation details:

1. What am I looking at?
2. What evidence supports it?
3. What should I do next—or avoid concluding?

## Product-wide rules

- Use sentence case for controls and chart titles; reserve uppercase for short navigation eyebrows.
- Use medians for skewed video-performance data and show the sample size wherever a small cohort could mislead.
- Never connect independent publication cohorts with a line.
- Never combine unrelated units on an unlabeled or decorative scale.
- Use lifetime average daily views only as an age-normalized historical rate, never as current velocity.
- Call `(likes + comments) / views` **public interaction rate**, not total engagement.
- Put model, artifact, and provider details behind progressive disclosure unless the user must act on them.
- Tables use plain-language column names and no decorative magnitude bars that imply comparability across unrelated measures.
- Charts do not capture scroll-wheel input; controls remain available on hover.

## Channel Analysis

- Replaced the misleading monthly connected line with adaptive publication-cohort bars.
  - Up to 36 months: monthly cohorts with month labels.
  - Longer spans: yearly cohorts with year labels.
  - Metric: median lifetime average daily views.
  - Hover: exact cohort, median rate, and video count.
- Moved the channel concentration chart to full width and clarified that it describes sample weighting, not channel quality.
- Added median reference lines to reach-versus-interaction scatter plots.
- Replaced subjective low/medium/high interaction grades with neutral numeric ranges.
- Rebuilt the formula explanation as a compact definition, valid-row rule, and limitation block.
- Moved the detailed channel table behind an expander to preserve scanability.

## Channel Insights

- Converted stored 0–1 rates to clearly labeled percentages in tables.
- Expanded theme charts to full width and stated the minimum-evidence logic.
- Removed the dual-axis publish-hour chart; performance and sample size are now communicated without mixing units.
- Split history measures with different units into separate charts.
- Reframed BERTopic as an optional semantic-theme beta and moved model/artifact details behind expanders.
- Replaced implementation-oriented labels with user-facing theme and snapshot language.

## Creator Studio

- Replaced the eight-option segmented control with one labeled workflow selector and a contextual description.
- Removed the redundant Outlier Finder shortcut from the channel workspace because it already has a dedicated navigation destination.
- Separated thumbnail creation/export from transcript, audio, and video export.
- Removed fabricated thumbnail brief defaults; fields now begin empty with useful examples as placeholders.
- Configured API keys are no longer copied into a visible password field.

## Channel workspace analytics

- Replaced average views with median views in the overview.
- Split monthly upload volume and age-normalized reach into two charts with explicit month labels.
- Removed the competitor radar because it mixed counts, views, and rates on one radial scale.
- Publishing recommendations now require a minimum evidence threshold and use median age-normalized reach.
- Timing heatmaps pair performance with a separate sample-size heatmap.

## Outlier Finder

- Replaced transformed log values on the channel-size axis with real subscriber counts on a log-scaled axis.
- Simplified age, length, and title-structure charts so color does not encode an unrelated second metric.
- Increased chart width by reducing the three-column chart row to two columns and a separate evidence-quality panel.
- Replaced causal-sounding “winning” language with descriptive result-set language.
- Standardized form labels, sort options, and actions to sentence case.

## Media Export and Thumbnail Lab

- Kept single-video thumbnail export in Thumbnail Lab.
- Removed the duplicate single-video thumbnail download control from Media Export.
- Retained batch and playlist thumbnail operations because they solve a distinct bulk-export job.
- Updated Streamlit width APIs to remove production deprecation noise.

