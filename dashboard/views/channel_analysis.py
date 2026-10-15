import os
from datetime import date, datetime

import pandas as pd
import streamlit as st

from src.services.analytics_metrics import lifetime_average_daily_views, public_interaction_rate

from dashboard.components.visualizations import (
    kpi_row,
    plotly_bar_chart,
    plotly_line_chart,
    plotly_scatter,
    section_header,
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
    df["publish_month"] = df["video_publishedAt"].dt.to_period("M").astype(str)
    df["publish_day"] = df["video_publishedAt"].dt.day_name()
    return df


def _render_engagement_formula_block() -> None:
    st.markdown("#### How public interaction is calculated")
    st.caption(
        "Public interaction rate = (public likes + public comments) / views. "
        "Rows with zero views or unavailable interaction counts are excluded—not imputed. "
        "This is not total engagement because public data omits watch time, shares, and saves."
    )

    formula_matrix = pd.DataFrame(
        [
            {"Metric": "Likes", "Meaning": "Total likes on the video"},
            {"Metric": "Comments", "Meaning": "Total comments on the video"},
            {"Metric": "Views", "Meaning": "Total views on the video"},
            {
                "Metric": "Public Interaction Rate (%)",
                "Meaning": "((Likes + Comments) / Views) * 100",
            },
        ]
    )
    with st.expander("Open formula matrix", expanded=False):
        st.table(formula_matrix)


def render() -> None:
    section_header(
        "Channel Analysis",
        subtitle="Compare a clearly defined sample, understand what is typical, and identify hypotheses worth testing.",
        icon="📊",
    )

    categories = _available_categories()
    selected_category = st.selectbox("Category", categories, index=0)

    st.caption(f"Showing the committed {selected_category} research sample.")

    df = _load_data_for_label(selected_category)
    if df.empty:
        st.warning(
            "No data available for the selected category. Check that the CSV files exist."
        )
        return

    channels = sorted(df["channel_title"].dropna().unique().tolist())
    selected_channels = st.multiselect(
        "Channels to compare", channels, default=channels[:8]
    )

    ts_min = df["video_publishedAt"].min()
    ts_max = df["video_publishedAt"].max()
    min_date = ts_min.date() if pd.notna(ts_min) else date.today()
    max_date = ts_max.date() if pd.notna(ts_max) else date.today()
    # Do not set max_value to the latest video date: choosing any window past that (e.g. next month)
    # would fail Streamlit validation and snap the widget back to the full range, so charts ignore the
    # user's range. min_value stays the dataset floor; upper bound defaults to last default +10y in Streamlit.
    date_range = st.date_input(
        "Publication window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=None,
        key=f"channel_analysis_pub_range:{selected_category}",
        help="UTC publish date of each video. Narrow ranges with no uploads in this dataset will empty the charts until you widen the window.",
    )
    st.caption(
        "Filter uses each video's **UTC** calendar day. Switching dataset category resets this range to that file's span."
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
            "value": f"{filtered['channel_id'].nunique():,}",
            "icon": "📺",
            "color": "#FDFDFD",
        },
        {
            "label": "Total Views",
            "value": f"{int(filtered['views'].fillna(0).sum()):,}",
            "icon": "👁️",
            "color": "#FF0000",
        },
        {
            "label": "Median Views / Video",
            "value": f"{int(filtered['views'].median()):,}",
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
    with st.container(border=True):
        st.markdown("#### What this comparison says")
        st.markdown(
            f"- **Typical reach:** the median video has **{int(filtered['views'].median()):,} views**, which is more representative than the average when a few videos dominate.\n"
            f"- **Audience concentration:** **{leader_name}** accounts for **{leader_share:.1f}%** of views in the selected sample.\n"
            f"- **Interaction evidence:** the typical public interaction rate is **{filtered['engagement_rate'].median() * 100:.2f}%**, supported by **{valid_interactions:,} of {len(filtered):,} videos**."
        )
        st.caption("These are descriptive signals from the selected public-data sample, not causal performance claims.")

    left, right = st.columns(2)

    with left:
        section_header("Where Reach Is Concentrated", icon="🏆")
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
            title="Total Views in the Selected Sample",
            horizontal=True,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Use this chart to see whether the comparison is balanced or dominated by one large channel.")
        channel_table = channel_summary.rename(
            columns={
                "channel_title": "Channel",
                "videos": "Videos Analyzed",
                "total_views": "Total Views",
                "median_views": "Median Views per Video",
                "valid_interaction_rows": "Videos with Interaction Data",
                "typical_public_interaction_pct": "Typical Public Interaction (%)",
            }
        )
        styled_dataframe(channel_table, title="Channel comparison", precision=2)

    with right:
        section_header("How Upload Cohorts Compare", icon="📆")
        trend = (
            filtered.groupby("publish_month", dropna=False)
            .agg(videos=("video_id", "count"), median_lifetime_views=("views", "median"))
            .reset_index()
            .sort_values("publish_month")
        )
        fig = plotly_line_chart(
            trend,
            x="publish_month",
            y_cols=["median_lifetime_views"],
            title="Median Lifetime Views by Publication Month",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Each point is the current median lifetime view count for videos published that month. It compares cohorts; it is not a view-growth timeline.")

    section_header("Videos With the Most Reach", subtitle="Review individual winners after understanding the channel-level baseline.", icon="⭐")
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
        title="Highest-viewed videos in this sample",
        precision=2,
    )
    _render_engagement_formula_block()

    section_header("Observed Patterns by Publish Day", subtitle="Compare medians and sample sizes before treating a weekday as a useful test.", icon="🗓️")
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
            title="Median Lifetime Daily Views by Publish Day",
        )
        st.plotly_chart(fig_views, use_container_width=True)
        st.caption("Higher bars mean stronger typical age-normalized reach for videos published on that weekday.")
    with col_day2:
        fig_eng = plotly_bar_chart(
            day_perf,
            x="publish_day",
            y="typical_public_interaction_pct",
            title="Typical Public Interaction by Publish Day",
        )
        fig_eng.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig_eng, use_container_width=True)
        st.caption("This measures public likes and comments per view—not watch time, shares, saves, or causality.")

    day_table = day_perf.rename(
        columns={
            "publish_day": "Publish Day",
            "median_lifetime_daily_views": "Median Lifetime Avg. Daily Views",
            "sample_size": "Sample Size",
            "typical_public_interaction_pct": "Typical Public Interaction (%)",
        }
    )
    styled_dataframe(day_table, title="Weekday evidence and sample size", precision=2)

    section_header("Reach vs Public Interaction", subtitle="Look for videos that combine scale with active public response.", icon="📉")
    scatter_df = filtered.copy()
    fig_scatter = plotly_scatter(
        scatter_df,
        x="views",
        y="public_interaction_pct",
        size=None,
        color="channel_title",
        title="Video Reach vs Public Interaction",
    )
    fig_scatter.update_traces(marker={"size": 9, "opacity": 0.65})
    fig_scatter.update_xaxes(type="log", title="Views (log scale)")
    fig_scatter.update_yaxes(title="Public Interaction Rate (%)", ticksuffix="%")
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("The horizontal axis uses a log scale so small and very large videos remain visible together. Upper-right observations combine higher reach and interaction.")

    section_header("How Public Interaction Is Distributed", icon="📊")
    bins = []
    for val in filtered["engagement_rate"]:
        if pd.isna(val):
            continue
        pct = val * 100
        if pct < 2:
            bins.append("Low (<2%)")
        elif pct < 8:
            bins.append("Medium (2–8%)")
        else:
            bins.append("High (8%+)")
    if bins:
        counts = pd.Series(bins, name="bucket").value_counts().reset_index()
        counts.columns = ["bucket", "count"]
        dist_df = counts
        dist_df["share_pct"] = dist_df["count"] / dist_df["count"].sum() * 100
        fig_donut = plotly_bar_chart(
            dist_df,
            x="bucket",
            y="share_pct",
            title="Share of Videos by Public Interaction Band",
            horizontal=True,
        )
        fig_donut.update_xaxes(title="Share of Videos (%)", ticksuffix="%")
        st.plotly_chart(fig_donut, use_container_width=True)
        st.caption("Bands are descriptive orientation points, not universal quality thresholds.")
