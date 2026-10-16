import os
from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.services.analytics_metrics import lifetime_average_daily_views, public_interaction_rate

from dashboard.components.visualizations import (
    apply_dashboard_chart_theme,
    compact_axis_ticks,
    format_compact_number,
    kpi_row,
    plotly_bar_chart,
    section_header,
    show_plotly_chart,
    styled_dataframe,
)


BASE_DATA_DIR = os.path.join("data", "youtube api data")
CATEGORY_FILES = {
    "Research / Science": "research_science_channels_videos.csv",
    "Tech": "tech_channels_videos.csv",
    "Gaming": "gaming_channels_videos.csv",
    "Entertainment": "entertainment_channels_videos.csv",
}
ALL_LABEL = "All Categories"


def _coerce_publish_date_range(
    selection: object,
    *,
    data_min: date,
    data_max: date,
) -> tuple[date, date]:
    """Normalize ``st.date_input`` range output to an inclusive (start, end) pair.

    Range mode can return ``()``, ``(start,)``, ``(start, end)``, a bare ``date``, or a ``list``.
    Empty selection falls back to the dataset span so charts match the widget default.
    """
    if selection is None:
        return data_min, data_max
    if isinstance(selection, datetime):
        d = selection.date()
        return d, d
    if isinstance(selection, date):
        return selection, selection
    if isinstance(selection, (tuple, list)):
        dates: list[date] = []
        for item in selection:
            if item is None:
                continue
            if isinstance(item, datetime):
                dates.append(item.date())
            elif isinstance(item, date):
                dates.append(item)
        if len(dates) >= 2:
            a, b = dates[0], dates[1]
            if a > b:
                a, b = b, a
            return a, b
        if len(dates) == 1:
            d0 = dates[0]
            return d0, d0
        return data_min, data_max
    return data_min, data_max


def _filter_rows_by_publish_calendar_range(
    frame: pd.DataFrame, start: date, end: date
) -> pd.DataFrame:
    """Keep rows whose publish instant falls on a UTC calendar day in [*start*, *end*]."""
    ts = frame["video_publishedAt"]
    valid = ts.notna()
    ts_ok = ts[valid]
    if ts_ok.empty:
        return frame.iloc[0:0]
    if ts_ok.dt.tz is None:
        ts_ok = ts_ok.dt.tz_localize("UTC")
    else:
        ts_ok = ts_ok.dt.tz_convert("UTC")
    pub_day = ts_ok.dt.date
    m = valid.copy()
    m.loc[valid] = (pub_day >= start) & (pub_day <= end)
    return frame.loc[m]


def _dataset_path_for_label(label: str) -> str:
    filename = CATEGORY_FILES.get(label) or CATEGORY_FILES.get("Research / Science")
    return os.path.join(BASE_DATA_DIR, filename)


def _available_categories() -> list[str]:
    labels: list[str] = []
    for label, filename in CATEGORY_FILES.items():
        path = os.path.join(BASE_DATA_DIR, filename)
        if os.path.exists(path):
            labels.append(label)
    if labels:
        return [ALL_LABEL] + labels
    return list(CATEGORY_FILES.keys())


def _load_data_for_label(label: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    if label == ALL_LABEL:
        for filename in CATEGORY_FILES.values():
            path = os.path.join(BASE_DATA_DIR, filename)
            if os.path.exists(path):
                frames.append(pd.read_csv(path))
        if not frames:
            return pd.DataFrame()
        df = pd.concat(frames, ignore_index=True)
    else:
        dataset_path = _dataset_path_for_label(label)
        if not os.path.exists(dataset_path):
            return pd.DataFrame()
        df = pd.read_csv(dataset_path)

    for col in ["views", "likes", "comments"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["video_publishedAt"] = pd.to_datetime(
        df["video_publishedAt"], errors="coerce", utc=True
    )
    df["engagement_rate"] = public_interaction_rate(df["views"], df["likes"], df["comments"])
    df["public_interaction_pct"] = df["engagement_rate"] * 100
    now = pd.Timestamp.now(tz="UTC")
    df["age_days"] = (now - df["video_publishedAt"]).dt.total_seconds() / 86400
    df["views_per_day"] = lifetime_average_daily_views(df["views"], df["age_days"])
    df["publish_month"] = (
        df["video_publishedAt"].dt.tz_localize(None).dt.to_period("M").astype(str)
    )
    df["publish_day"] = df["video_publishedAt"].dt.day_name()
    return df


def _render_engagement_formula_block() -> None:
    with st.expander("How public interaction is calculated", expanded=False):
        st.markdown("**(Public likes + public comments) ÷ public views × 100**")
        definition, coverage, limitation = st.columns(3)
        with definition:
            st.markdown("**What it answers**")
            st.write("How often a public view is accompanied by a visible like or comment.")
        with coverage:
            st.markdown("**Rows included**")
            st.write("Only videos with views above zero and available like and comment counts.")
        with limitation:
            st.markdown("**What it omits**")
            st.write("Watch time, shares, saves, impressions, and private engagement signals.")

        formula_matrix = pd.DataFrame(
            [
                {"Metric": "Likes", "Meaning": "Total likes on the video"},
                {"Metric": "Comments", "Meaning": "Total comments on the video"},
                {"Metric": "Views", "Meaning": "Total views on the video"},
            ]
        )
        st.table(formula_matrix)


def _publication_cohort_summary(frame: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Aggregate publication cohorts at a readable grain for the selected span."""
    valid = frame.dropna(subset=["video_publishedAt", "views_per_day"]).copy()
    if valid.empty:
        return pd.DataFrame(), "year"

    span_days = (valid["video_publishedAt"].max() - valid["video_publishedAt"].min()).days
    if span_days <= 36 * 31:
        valid["cohort"] = (
            valid["video_publishedAt"].dt.tz_convert(None).dt.to_period("M").astype(str)
        )
        grain = "month"
    else:
        valid["cohort"] = valid["video_publishedAt"].dt.year.astype(str)
        grain = "year"

    summary = (
        valid.groupby("cohort", dropna=False)
        .agg(
            videos=("video_id", "count"),
            median_daily_views=("views_per_day", "median"),
        )
        .reset_index()
        .sort_values("cohort")
    )
    return summary, grain


def _publication_cohort_chart(summary: pd.DataFrame, grain: str) -> go.Figure:
    label = "Publication month" if grain == "month" else "Publication year"
    title = f"Typical daily reach by {grain} published"
    fig = go.Figure(
        go.Bar(
            x=summary["cohort"],
            y=summary["median_daily_views"],
            customdata=summary[["videos"]],
            marker={"color": "#FF0033", "line": {"color": "rgba(255,255,255,.75)", "width": 1}},
            hovertemplate=(
                f"{label}: %{{x}}<br>"
                "Median lifetime average daily views: %{y:,.0f}<br>"
                "Videos in cohort: %{customdata[0]:,}<extra></extra>"
            ),
        )
    )
    fig.update_layout(title=title, height=420, showlegend=False, bargap=0.18)
    fig.update_xaxes(title=label, type="category", tickangle=-35 if grain == "month" else 0)
    fig.update_yaxes(
        title="Median lifetime average daily views",
        rangemode="tozero",
        **compact_axis_ticks(summary["median_daily_views"]),
    )
    apply_dashboard_chart_theme(fig)
    return fig


def _reach_interaction_chart(frame: pd.DataFrame) -> tuple[go.Figure, dict[str, object]]:
    """Show reach/interaction without allowing a dense dataset to collapse into a dot cloud."""
    valid = frame[["views", "public_interaction_pct"]].copy()
    valid["views"] = pd.to_numeric(valid["views"], errors="coerce")
    valid["public_interaction_pct"] = pd.to_numeric(
        valid["public_interaction_pct"], errors="coerce"
    )
    valid = valid.replace([np.inf, -np.inf], np.nan).dropna()
    valid = valid[(valid["views"] > 0) & (valid["public_interaction_pct"] >= 0)]

    if valid.empty:
        fig = go.Figure()
        fig.update_layout(title="Where videos cluster by reach and interaction", height=460)
        apply_dashboard_chart_theme(fig)
        return fig, {"mode": "empty", "videos": 0, "overflow": 0, "y_cap": None}

    median_views = float(valid["views"].median())
    median_interaction = float(valid["public_interaction_pct"].median())

    # Individual dots remain legible for a small filtered selection. Larger selections use
    # aggregation so overlapping points communicate concentration instead of hiding it.
    if len(valid) < 250:
        fig = go.Figure(
            go.Scatter(
                x=valid["views"],
                y=valid["public_interaction_pct"],
                mode="markers",
                marker={
                    "size": 8,
                    "opacity": 0.68,
                    "color": "#FF0033",
                    "line": {"color": "rgba(255,255,255,.8)", "width": 0.7},
                },
                hovertemplate="Views: %{x:,.0f}<br>Public interaction: %{y:.2f}%<extra></extra>",
            )
        )
        fig.update_xaxes(
            type="log",
            title="Views (log scale)",
            **compact_axis_ticks(valid["views"], logarithmic=True),
        )
        fig.update_yaxes(title="Public interaction", ticksuffix="%", rangemode="tozero")
        mode = "scatter"
        overflow = 0
        y_cap = None
    else:
        x_log = np.log10(valid["views"].to_numpy(dtype=float))
        interaction = valid["public_interaction_pct"].to_numpy(dtype=float)
        q99 = float(np.nanpercentile(interaction, 99))
        y_cap = min(100.0, max(5.0, q99))
        overflow = int(np.sum(interaction > y_cap))
        y_binned = np.minimum(interaction, y_cap)

        x_min, x_max = float(x_log.min()), float(x_log.max())
        if np.isclose(x_min, x_max):
            x_min -= 0.25
            x_max += 0.25
        y_max = max(y_cap, 1.0)
        x_edges = np.linspace(x_min, x_max, 33)
        y_edges = np.linspace(0.0, y_max, 25)
        counts, _, _ = np.histogram2d(x_log, y_binned, bins=[x_edges, y_edges])
        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2
        visible_counts = np.where(counts.T > 0, counts.T, np.nan)

        fig = go.Figure(
            go.Heatmap(
                x=x_centers,
                y=y_centers,
                z=visible_counts,
                customdata=counts.T,
                colorscale=[
                    [0.0, "rgba(220,231,246,0.55)"],
                    [0.28, "#AFCDF2"],
                    [0.58, "#4D8BD8"],
                    [0.82, "#7D3C86"],
                    [1.0, "#FF0033"],
                ],
                colorbar={"title": {"text": "Videos"}, "thickness": 12, "len": 0.72},
                hovertemplate=(
                    "Reach: %{x:.1f} log₁₀ views<br>"
                    "Public interaction: %{y:.1f}%<br>"
                    "Videos in area: %{customdata:,.0f}<extra></extra>"
                ),
                hoverongaps=False,
            )
        )
        tick_start = int(np.floor(x_min))
        tick_end = int(np.ceil(x_max))
        tick_values = list(range(tick_start, tick_end + 1))
        fig.update_xaxes(
            title="Views (log scale)",
            tickmode="array",
            tickvals=tick_values,
            ticktext=[format_compact_number(10**value) for value in tick_values],
        )
        fig.update_yaxes(title="Public interaction", ticksuffix="%", rangemode="tozero")
        median_views = float(np.log10(median_views))
        mode = "density"

    fig.add_vline(x=median_views, line_dash="dot", line_color="#6E6E73")
    fig.add_hline(y=median_interaction, line_dash="dot", line_color="#6E6E73")
    fig.add_annotation(
        x=median_views,
        y=1,
        xref="x",
        yref="paper",
        text=f"Median reach · {format_compact_number(float(valid['views'].median()))}",
        showarrow=False,
        yshift=10,
        font={"size": 10, "color": "#6E6E73"},
        bgcolor="rgba(255,255,255,0.88)",
        borderpad=3,
    )
    fig.add_annotation(
        x=1,
        y=median_interaction,
        xref="paper",
        yref="y",
        text=f"Typical · {median_interaction:.2f}%",
        showarrow=False,
        xanchor="right",
        xshift=-6,
        font={"size": 10, "color": "#6E6E73"},
        bgcolor="rgba(255,255,255,0.88)",
        borderpad=3,
    )
    fig.update_layout(
        title="Where videos cluster by reach and interaction",
        height=500,
        showlegend=False,
    )
    apply_dashboard_chart_theme(fig)
    return fig, {
        "mode": mode,
        "videos": len(valid),
        "overflow": overflow,
        "y_cap": y_cap,
    }


def render() -> None:
    categories = _available_categories()
    with st.container(border=True):
        st.markdown('<div class="filter-panel-heading">Filter comparison</div>', unsafe_allow_html=True)
        filter_columns = st.columns([1.05, 1.9, 1.25], gap="medium")
        with filter_columns[0]:
            selected_category = st.selectbox("Category", categories, index=0)

        df = _load_data_for_label(selected_category)
        if df.empty:
            st.warning(
                "No data available for the selected category. Check that the CSV files exist."
            )
            return

        channels = sorted(df["channel_title"].dropna().unique().tolist())
        with filter_columns[1]:
            selected_channels = st.multiselect(
                "Channels",
                channels,
                default=[],
                placeholder="All channels",
                help="Leave empty to include every channel in this category.",
            )

        ts_min = df["video_publishedAt"].min()
        ts_max = df["video_publishedAt"].max()
        min_date = ts_min.date() if pd.notna(ts_min) else date.today()
        max_date = ts_max.date() if pd.notna(ts_max) else date.today()
        # Keep the upper bound open so a future-facing range does not reset the widget.
        with filter_columns[2]:
            date_range = st.date_input(
                "Publication window",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=None,
                key=f"channel_analysis_pub_range:{selected_category}",
                help="UTC publication dates included in this comparison.",
            )
    filtered = df.copy()
    if selected_channels:
        filtered = filtered[filtered["channel_title"].isin(selected_channels)]

    start_date, end_date = _coerce_publish_date_range(
        date_range, data_min=min_date, data_max=max_date
    )
    filtered = _filter_rows_by_publish_calendar_range(filtered, start_date, end_date)

    if filtered.empty:
        st.warning("No data after filters. Broaden your channel/date filters.")
        return

    # KPI row
    metrics = [
        {
            "label": "Videos",
            "value": f"{len(filtered):,}",
            "icon": "🎬",
            "color": "#FF0000",
        },
        {
            "label": "Channels",
            "value": f"{filtered['channel_title'].nunique():,}",
            "icon": "📺",
        },
        {
            "label": "Total Views",
            "value": format_compact_number(filtered["views"].fillna(0).sum()),
            "icon": "👁️",
            "color": "#FF0000",
        },
        {
            "label": "Median Views / Video",
            "value": format_compact_number(filtered["views"].median()),
            "icon": "📈",
        },
        {
            "label": "Typical Public Interaction",
            "value": f"{filtered['engagement_rate'].median() * 100:.2f}%",
            "icon": "💡",
        },
    ]
    kpi_row(metrics)

    valid_interactions = int(filtered["engagement_rate"].notna().sum())
    top_channel_views = filtered.groupby("channel_title")["views"].sum().sort_values(ascending=False)
    leader_name = str(top_channel_views.index[0]) if not top_channel_views.empty else "Unavailable"
    leader_share = (
        float(top_channel_views.iloc[0] / top_channel_views.sum() * 100)
        if not top_channel_views.empty and float(top_channel_views.sum()) > 0
        else 0.0
    )
    with st.expander("Key takeaways from this comparison", expanded=False):
        st.markdown(
            f"- **Typical reach:** the median video has **{int(filtered['views'].median()):,} views**, which is more representative than the average when a few videos dominate.\n"
            f"- **View concentration:** **{leader_name}** accounts for **{leader_share:.1f}%** of views in the selected sample.\n"
            f"- **Interaction evidence:** the typical public interaction rate is **{filtered['engagement_rate'].median() * 100:.2f}%**, supported by **{valid_interactions:,} of {len(filtered):,} videos**."
        )
        st.caption("These describe the selected public-data sample; they do not establish causality.")

    section_header("View concentration", icon="🏆")
    channel_summary = (
        filtered.groupby("channel_title", dropna=False)
        .agg(
            videos=("video_id", "count"),
            total_views=("views", "sum"),
            median_views=("views", "median"),
            typical_engagement_rate=("engagement_rate", "median"),
            valid_interaction_rows=("engagement_rate", "count"),
        )
        .sort_values("total_views", ascending=False)
        .head(15)
        .reset_index()
    )
    channel_summary["typical_public_interaction_pct"] = channel_summary.pop("typical_engagement_rate") * 100
    fig = plotly_bar_chart(
        channel_summary.sort_values("total_views"),
        x="channel_title",
        y="total_views",
        title="Total views represented in this comparison",
        horizontal=True,
    )
    fig.update_layout(height=max(360, 42 * len(channel_summary) + 120))
    show_plotly_chart(fig)
    channel_table = channel_summary.rename(
        columns={
            "channel_title": "Channel",
            "videos": "Videos analyzed",
            "total_views": "Total views",
            "median_views": "Median views per video",
            "valid_interaction_rows": "Videos with interaction data",
            "typical_public_interaction_pct": "Typical public interaction (%)",
        }
    )
    with st.expander("View channel-level details", expanded=False):
        styled_dataframe(channel_table, precision=2)

    section_header("Performance by publication period", icon="📆")
    cohort_summary, cohort_grain = _publication_cohort_summary(filtered)
    if cohort_summary.empty:
        st.info("There is not enough dated performance data to compare publication cohorts.")
    else:
        show_plotly_chart(_publication_cohort_chart(cohort_summary, cohort_grain))

    section_header("Highest-reach videos", icon="⭐")
    top_videos = filtered[
        [
            "channel_title",
            "video_title",
            "views",
            "likes",
            "comments",
            "public_interaction_pct",
            "video_publishedAt",
        ]
    ].sort_values("views", ascending=False)
    top_videos_table = top_videos.head(50).rename(
        columns={
            "channel_title": "Channel",
            "video_title": "Video",
            "views": "Views",
            "likes": "Public Likes",
            "comments": "Public Comments",
            "public_interaction_pct": "Public Interaction (%)",
            "video_publishedAt": "Published (UTC)",
        }
    )
    styled_dataframe(
        top_videos_table,
        precision=2,
    )
    _render_engagement_formula_block()

    section_header("Performance by publish day", icon="🗓️")
    day_perf = (
        filtered.groupby("publish_day", dropna=False)
        .agg(
            median_lifetime_daily_views=("views_per_day", "median"),
            typical_engagement_rate=("engagement_rate", "median"),
            sample_size=("video_id", "count"),
        )
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )
        .dropna(how="all")
        .reset_index()
    )
    day_perf["typical_public_interaction_pct"] = day_perf.pop("typical_engagement_rate") * 100

    col_day1, col_day2 = st.columns(2)
    with col_day1:
        fig_views = plotly_bar_chart(
            day_perf,
            x="publish_day",
            y="median_lifetime_daily_views",
            title="Typical age-normalized reach by publish day",
        )
        show_plotly_chart(fig_views)
    with col_day2:
        fig_eng = plotly_bar_chart(
            day_perf,
            x="publish_day",
            y="typical_public_interaction_pct",
            title="Typical public interaction by publish day",
        )
        fig_eng.update_yaxes(ticksuffix="%")
        show_plotly_chart(fig_eng)

    day_table = day_perf.rename(
        columns={
            "publish_day": "Publish Day",
            "median_lifetime_daily_views": "Median Lifetime Avg. Daily Views",
            "sample_size": "Sample Size",
            "typical_public_interaction_pct": "Typical Public Interaction (%)",
        }
    )
    with st.expander("View weekday sample sizes", expanded=False):
        styled_dataframe(day_table, precision=2)

    section_header("Reach vs public interaction", icon="📉")
    fig_reach, reach_meta = _reach_interaction_chart(filtered)
    show_plotly_chart(fig_reach)
    if reach_meta["mode"] == "density":
        density_note = "Color shows how many videos occupy each reach-and-interaction area."
        if reach_meta["overflow"]:
            density_note += (
                f" {reach_meta['overflow']:,} extreme values above "
                f"{reach_meta['y_cap']:.1f}% are grouped into the top band."
            )
        st.caption(density_note)

    section_header("Public interaction distribution", icon="📊")
    bins = []
    for val in filtered["engagement_rate"]:
        if pd.isna(val):
            continue
        pct = val * 100
        if pct < 1:
            bins.append("Under 1%")
        elif pct < 2:
            bins.append("1–2%")
        elif pct < 4:
            bins.append("2–4%")
        elif pct < 8:
            bins.append("4–8%")
        else:
            bins.append("8% or more")
    if bins:
        bucket_order = ["Under 1%", "1–2%", "2–4%", "4–8%", "8% or more"]
        counts = pd.Series(bins, name="bucket").value_counts().reindex(bucket_order, fill_value=0).reset_index()
        counts.columns = ["bucket", "count"]
        dist_df = counts
        dist_df["share_pct"] = dist_df["count"] / dist_df["count"].sum() * 100
        fig_donut = plotly_bar_chart(
            dist_df,
            x="bucket",
            y="share_pct",
            title="Videos by public interaction range",
            horizontal=False,
        )
        fig_donut.update_xaxes(title="Public interaction rate")
        fig_donut.update_yaxes(title="Share of videos", ticksuffix="%")
        show_plotly_chart(fig_donut)
