import html as html_module
import os

import pandas as pd
import streamlit as st

from dashboard.components.visualizations import (
    graph_insight_expander,
    kpi_row,
    plotly_bar_chart,
    plotly_donut_chart,
    plotly_line_chart,
    plotly_scatter,
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
    df["engagement_rate"] = (
        (df["likes"].fillna(0) + df["comments"].fillna(0))
        / df["views"].clip(lower=1)
    )
    df["publish_month"] = df["video_publishedAt"].dt.to_period("M").astype(str)
    df["publish_day"] = df["video_publishedAt"].dt.day_name()
    return df


def _executive_summary_bullets(filtered: pd.DataFrame, category_label: str) -> str:
    n_vid = len(filtered)
    n_ch = int(filtered["channel_id"].nunique())
    total_v = int(filtered["views"].fillna(0).sum())
    med_eng = float(filtered["engagement_rate"].median()) * 100 if n_vid else 0.0
    by_ch = (
        filtered.groupby("channel_title", dropna=False)["views"]
        .sum()
        .sort_values(ascending=False)
    )
    top_name = str(by_ch.index[0]) if len(by_ch) else "N/A"
    top_share = float(by_ch.iloc[0] / max(total_v, 1) * 100) if len(by_ch) and total_v else 0.0
    best_day = "N/A"
    if "publish_day" in filtered.columns and not filtered.empty:
        day_means = filtered.groupby("publish_day")["views"].mean()
        if not day_means.empty:
            best_day = str(day_means.idxmax())

    items = [
        f"<strong>Dataset:</strong> {html_module.escape(category_label)} — {n_vid:,} videos across {n_ch:,} channels after your filters.",
        f"<strong>Reach:</strong> {total_v:,} total views; leading channel is <em>{html_module.escape(top_name)}</em> (~{top_share:.1f}% of views in this slice).",
        f"<strong>Typical engagement:</strong> median {med_eng:.2f}% (likes + comments per view — see the blue callout for the exact formula).",
        f"<strong>Publishing hint:</strong> highest average views on <strong>{html_module.escape(best_day)}</strong> in this filtered set (correlation only — topic and seasonality matter).",
    ]
    lis = "".join(f"<li style='margin-bottom:0.35rem;'>{s}</li>" for s in items)
    return f'<ul class="strategy-summary-list">{lis}</ul>'


def _recommendations_block(filtered: pd.DataFrame) -> str:
    med_eng = float(filtered["engagement_rate"].median()) * 100
    avg_v = float(filtered["views"].fillna(0).mean())
    top_mean = float(
        filtered.groupby("channel_title")["views"]
        .mean()
        .sort_values(ascending=False)
        .head(1)
        .iloc[0]
    ) if not filtered.empty else 0.0
    tips: list[str] = []
    if med_eng < 2.0:
        tips.append(
            "Median engagement is below 2% — prioritize stronger CTAs, community prompts, and titles that match search intent."
        )
    elif med_eng > 6.0:
        tips.append(
            "Engagement is healthy — double down on formats that already earn comments and likes, and test sequels on top topics."
        )
    if top_mean > avg_v * 1.4 and avg_v > 0:
        tips.append(
            "A small set of channels drives outsized views per video — study their thumbnails and pacing, then adapt (not copy) for your niche."
        )
    if not tips:
        tips.append(
            "Performance is mixed — use the scatter plot (log-scale views) to find high-engagement outliers, then review their titles side by side."
        )
    tips.append("Use the date and channel filters to isolate one vertical before making publishing decisions.")
    lis = "".join(f"<li style='margin-bottom:0.4rem;'>{html_module.escape(t)}</li>" for t in tips)
    return (
        '<div class="yt-callout-recommend">'
        "<h4>Recommendations</h4>"
        f"<ul>{lis}</ul>"
        "</div>"
    )


def render() -> None:
    section_header("Dataset & filters", icon="📊")

    categories = _available_categories()
    selected_category = st.selectbox("Dataset category", categories, index=0)

    st.caption(f"Analytics for `{selected_category}` YouTube channels and videos.")

    df = _load_data_for_label(selected_category)
    if df.empty:
        st.warning(
            "No data available for the selected category. Check that the CSV files exist."
        )
        return

    channels = sorted(df["channel_title"].dropna().unique().tolist())
    selected_channels = st.multiselect(
        "Filter channels", channels, default=channels[:8]
    )

    min_date = df["video_publishedAt"].min().date()
    max_date = df["video_publishedAt"].max().date()
    date_range = st.date_input(
        "Published date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    filtered = df.copy()
    if selected_channels:
        filtered = filtered[filtered["channel_title"].isin(selected_channels)]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered["video_publishedAt"].dt.date >= start_date)
            & (filtered["video_publishedAt"].dt.date <= end_date)
        ]

    if filtered.empty:
        st.warning("No data after filters. Broaden your channel/date filters.")
        return

    st.markdown(
        '<div class="yt-summary-panel">'
        "<h3>At a glance</h3>"
        + _executive_summary_bullets(filtered, selected_category)
        + "</div>",
        unsafe_allow_html=True,
    )

    eng_col, rec_col = st.columns(2)
    with eng_col:
        st.markdown(
            (
                '<div class="yt-callout-info">'
                "<strong>How engagement rate is calculated</strong><br><br>"
                "For each video we use public counts only:<br>"
                "<code style='background:#FFF;padding:2px 6px;border-radius:4px;'>"
                "engagement_rate = (likes + comments) / max(views, 1)"
                "</code><br><br>"
                "This is a <em>ratio</em>, not YouTube Studio CTR or watch time. "
                "It lets you compare videos fairly when raw like/comment totals differ."
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    with rec_col:
        st.markdown(_recommendations_block(filtered), unsafe_allow_html=True)

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
            "color": "#065FD4",
        },
        {
            "label": "Total Views",
            "value": f"{int(filtered['views'].fillna(0).sum()):,}",
            "icon": "👁️",
        },
        {
            "label": "Avg Views / Video",
            "value": f"{int(filtered['views'].fillna(0).mean()):,}",
            "icon": "📈",
        },
        {
            "label": "Median Engagement",
            "value": f"{filtered['engagement_rate'].median() * 100:.2f} %",
            "icon": "💡",
        },
    ]
    kpi_row(metrics)

    left, right = st.columns(2)

    with left:
        section_header("Top Channels by Views", icon="🏆")
        channel_summary = (
            filtered.groupby("channel_title", dropna=False)
            .agg(
                videos=("video_id", "count"),
                total_views=("views", "sum"),
                avg_views=("views", "mean"),
                engagement=("engagement_rate", "median"),
            )
            .sort_values("total_views", ascending=False)
            .head(15)
            .reset_index()
        )
        bar_df = channel_summary.sort_values("total_views", ascending=True)
        fig = plotly_bar_chart(
            bar_df,
            x="channel_title",
            y="total_views",
            title="Top 15 Channels by Total Views",
            horizontal=True,
        )
        fig.update_layout(yaxis=dict(tickfont=dict(size=11)), height=max(400, 28 * len(bar_df)))
        show_plotly_chart(fig)
        graph_insight_expander(
            "Top channels (horizontal bars)",
            "**Bars** show total views in your filtered window. **Longer bars = more cumulative reach.** "
            "Compare against the table below for upload count and median engagement per channel.",
        )
        styled_dataframe(channel_summary, title="Channel Summary")

    with right:
        section_header("Monthly Upload Trend", icon="📆")
        trend = (
            filtered.groupby("publish_month", dropna=False)
            .agg(videos=("video_id", "count"), views=("views", "sum"))
            .reset_index()
            .sort_values("publish_month")
        )
        fig = plotly_line_chart(
            trend,
            x="publish_month",
            y_cols=["videos", "views"],
            title="Videos & Views Over Time",
            secondary_y=["views"],
        )
        fig.update_layout(
            hovermode="x unified",
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=1.01,
                bgcolor="rgba(255,255,255,0.97)",
                bordercolor="rgba(0,0,0,0.16)",
                borderwidth=1,
                font=dict(size=13, color="#111216"),
            ),
            margin=dict(l=72, r=110, t=74, b=70),
        )
        fig.update_xaxes(
            title_text="Publish Month",
            tickformat="%Y",
            hoverformat="%b %Y",
            showline=True,
            linewidth=1.2,
            linecolor="rgba(0,0,0,0.28)",
            gridcolor="rgba(0,0,0,0.08)",
            tickfont=dict(size=12, color="#1d1d1f"),
            title_font=dict(size=15, color="#111216"),
        )
        fig.update_yaxes(
            title_text="Videos",
            secondary_y=False,
            tickfont=dict(size=12, color="#111216"),
            title_font=dict(size=15, color="#111216"),
            gridcolor="rgba(0,0,0,0.11)",
            rangemode="tozero",
        )
        fig.update_yaxes(
            title_text="Views",
            secondary_y=True,
            tickformat="~s",
            tickfont=dict(size=12, color="#111216"),
            title_font=dict(size=15, color="#111216"),
            showgrid=False,
            rangemode="tozero",
        )
        fig.update_traces(
            selector=dict(name="Videos"),
            mode="lines",
            line=dict(color="#FF0033", width=2.6),
            hovertemplate="Month: %{x|%b %Y}<br>Videos: %{y:~s}<extra></extra>",
        )
        fig.update_traces(
            selector=dict(name="Views"),
            mode="lines",
            line=dict(color="#00A6FF", width=2.6),
            hovertemplate="Month: %{x|%b %Y}<br>Views: %{y:~s}<extra></extra>",
        )
        show_plotly_chart(fig)
        graph_insight_expander(
            "Uploads & views over time",
            "**First line (left axis):** count of videos published each month. **Second line (right axis):** total views that month. "
            "Rising uploads with flat views can mean packaging or topic fatigue; falling uploads with steady views can mean catalog strength.",
        )

    section_header("Best Performing Videos", icon="⭐")
    top_videos = filtered[
        [
            "channel_title",
            "video_title",
            "views",
            "likes",
            "comments",
            "engagement_rate",
            "video_publishedAt",
        ]
    ].sort_values("views", ascending=False)
    styled_dataframe(
        top_videos.head(50),
        title="Top Videos by Views",
        precision=2,
    )

    section_header("Publishing Day Performance", icon="🗓️")
    day_perf = (
        filtered.groupby("publish_day", dropna=False)
        .agg(
            videos=("video_id", "count"),
            avg_views=("views", "mean"),
            median_engagement=("engagement_rate", "median"),
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
    day_perf["median_engagement_pct"] = day_perf["median_engagement"].fillna(0) * 100

    col_day1, col_day2 = st.columns(2)
    with col_day1:
        fig_views = plotly_bar_chart(
            day_perf,
            x="publish_day",
            y="avg_views",
            title="Average Views by Day",
        )
        show_plotly_chart(fig_views)
        graph_insight_expander(
            "Average views by weekday",
            "Each bar is the **mean** views for videos published on that weekday. "
            "Sample sizes differ — sparse days can look noisy. Treat as a hypothesis for scheduling tests.",
        )
    with col_day2:
        fig_eng = plotly_bar_chart(
            day_perf,
            x="publish_day",
            y="median_engagement_pct",
            title="Median Engagement Rate by Day",
        )
        if not day_perf["median_engagement_pct"].dropna().empty:
            eng_min = float(day_perf["median_engagement_pct"].min())
            eng_max = float(day_perf["median_engagement_pct"].max())
            spread = max(eng_max - eng_min, 0.01)
            pad = max(spread * 0.3, 0.08)
            low = max(0.0, eng_min - pad)
            high = eng_max + pad
            fig_eng.update_yaxes(range=[low, high], ticksuffix="%", tickformat=".2f")
        fig_eng.update_traces(texttemplate="%{y:.2f}%", hovertemplate="Publish Day: %{x}<br>Median Engagement: %{y:.2f}%<extra></extra>")
        show_plotly_chart(fig_eng)
        graph_insight_expander(
            "Engagement by weekday",
            "Shows **median** engagement rate (likes + comments per view) by publish day. "
            "Use with the views chart: a day can have high engagement but fewer uploads.",
        )

    section_header("Views vs Engagement", icon="📉")
    st.caption(
        "Tip: use the **toolbar** (top-right of the chart) to zoom and pan. **Scroll** zooms when the cursor is over the plot. **Double-click** resets the view."
    )
    scatter_df = filtered.copy()
    fig_scatter = plotly_scatter(
        scatter_df,
        x="views",
        y="engagement_rate",
        size=None,
        color="channel_title",
        title="Views vs Engagement Rate (log-scale views)",
        log_x=True,
        enhanced_markers=True,
    )
    fig_scatter.update_layout(
        height=520,
        legend=dict(
            title="Channel",
            title_font=dict(size=12, color="#1d1d1f"),
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=11, color="#1d1d1f"),
            bgcolor="rgba(255,255,255,0.98)",
            bordercolor="rgba(0,0,0,0.12)",
            borderwidth=1,
        ),
        margin=dict(l=96, r=190, t=72, b=92),
    )
    fig_scatter.update_xaxes(
        title_text="Views (log scale)",
        title_font=dict(size=15, color="#1d1d1f"),
        tickfont=dict(size=12, color="#424245"),
        title_standoff=16,
        automargin=True,
    )
    fig_scatter.update_yaxes(
        title_text="Engagement Rate (%)",
        title_font=dict(size=15, color="#1d1d1f"),
        tickfont=dict(size=12, color="#424245"),
        tickformat=".0%",
        title_standoff=16,
        automargin=True,
    )
    show_plotly_chart(fig_scatter)
    graph_insight_expander(
        "Views vs engagement scatter",
        "- **X-axis (log scale):** view count — logarithmic spacing spreads mega-hits and small videos so both are visible.\n"
        "- **Y-axis:** engagement rate (0–1 on the chart = 0–100%).\n"
        "- **Color:** channel — each hue is a different creator in your filter.\n"
        "- **Upper-left region:** fewer views but relatively strong engagement — niche or early breakout candidates.\n"
        "- **Lower-right:** high views but lower engagement — broad reach, lighter interaction per view.",
    )

    section_header("Engagement Distribution", icon="🥧")
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
        fig_donut = plotly_donut_chart(
            dist_df,
            names="bucket",
            values="count",
            title="Engagement Rate Buckets",
        )
        show_plotly_chart(fig_donut)
        graph_insight_expander(
            "Engagement buckets (donut)",
            "Videos are grouped by engagement **percentage**: Low (&lt;2%), Medium (2–8%), High (8%+). "
            "The donut shows **share of videos** in each band, not share of views.",
        )
