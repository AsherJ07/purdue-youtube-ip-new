import math
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


# Creator Insights palette aligned to YouTube red + accessible comparison accents.
# The first two colors carry the product identity; later colors are reserved for
# multi-series charts where distinct hues are necessary for comprehension.
YT_COLORWAY: List[str] = [
    "#E60012",
    "#0071E3",
    "#7A3FF2",
    "#C05A00",
    "#00876A",
    "#B4236A",
    "#455A64",
]

YT_RED = "#E60012"
YT_BLUE = "#0071E3"
CHART_INK = "#17171A"
CHART_MUTED = "#6E6E73"
CHART_GRID = "rgba(23,23,26,0.075)"
CHART_BORDER = "rgba(23,23,26,0.10)"

PLOTLY_INTERACTIVE_CONFIG: Dict[str, Any] = {
    "scrollZoom": False,
    "displayModeBar": "hover",
    "displaylogo": False,
    "responsive": True,
    "doubleClick": "reset",
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

# Transparent analytics canvas. The glass surface belongs to the Streamlit
# chart container, not the Plotly SVG, so the app background remains visible
# and charts feel native to the product instead of pasted from a notebook.
PLOTLY_DASHBOARD_TEMPLATE: Dict[str, Any] = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": CHART_INK,
            "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            "size": 12,
        },
        "xaxis": {
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "ticks": "",
            "title": {"font": {"color": CHART_MUTED, "size": 12}},
            "tickfont": {"color": CHART_MUTED, "size": 11},
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": CHART_GRID,
            "gridwidth": 1,
            "zeroline": False,
            "showline": False,
            "ticks": "",
            "title": {"font": {"color": CHART_MUTED, "size": 12}},
            "tickfont": {"color": CHART_MUTED, "size": 11},
        },
        "colorway": YT_COLORWAY,
        "hoverlabel": {
            "bgcolor": "rgba(255,255,255,0.97)",
            "font": {"color": CHART_INK, "size": 12},
            "bordercolor": CHART_BORDER,
            "namelength": -1,
        },
        "hovermode": "closest",
    }
}

# Back-compat alias
PLOTLY_LIGHT_TEMPLATE = PLOTLY_DASHBOARD_TEMPLATE


def _friendly_label(raw: str) -> str:
    """Convert snake_case / terse names into plain-English labels."""
    text = str(raw or "").strip()
    if not text:
        return ""
    aliases = {
        "publish_month": "Publish Month",
        "publish_day": "Publish Day",
        "publish_hour": "Publish Hour (UTC)",
        "video_publishedAt": "Publish Date",
        "views_per_day": "Lifetime Avg. Daily Views",
        "median_daily_views": "Median Lifetime Avg. Daily Views",
        "median_views_per_day": "Median Lifetime Avg. Daily Views",
        "engagement_rate": "Public Interaction Rate",
        "engagement_pct": "Public Interaction Rate (%)",
        "public_interaction_pct": "Public Interaction Rate (%)",
        "typical_public_interaction_pct": "Typical Public Interaction (%)",
        "median_lifetime_daily_views": "Median Lifetime Avg. Daily Views",
        "outlier_score": "Outlier Score",
        "channel_title": "Channel",
        "video_title": "Video Title",
        "video_id": "YouTube Video ID",
        "topic_label": "Theme",
        "primary_topic": "Primary Theme",
        "video_count": "Videos",
        "recent_video_count": "Recent Videos",
        "previous_video_count": "Earlier Videos",
        "trend_status": "Momentum",
        "trend_score": "Momentum Score",
        "median_public_interaction_rate": "Typical Public Interaction",
        "interaction_coverage": "Videos With Interaction Data",
        "duration_bucket": "Video Length",
        "title_pattern": "Title Structure",
        "performance_score": "Performance Score",
        "why_it_worked": "Why It Stood Out",
        "why_it_lagged": "Why It Lagged",
        "snapshot_at": "Snapshot Date",
        "recent_outlier_count": "Recent Outliers",
        "avg_views": "Average Views",
        "total_views": "Total Views",
        "videos": "Videos",
        "keyword": "Keyword",
        "momentum_delta": "Momentum Change",
        "competitor_count": "Competitor Count",
        "log10_subscribers": "Channel Size (log10 subscribers + 1)",
    }
    if text in aliases:
        return aliases[text]
    if text.endswith("_pct"):
        text = text[:-4] + " percent"
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text.title()


def _compact_number(value: float) -> str:
    """Format large values into compact user-friendly units (K/M/B/T)."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    sign = "-" if num < 0 else ""
    n = abs(num)
    if n >= 1_000_000_000_000:
        return f"{sign}{n / 1_000_000_000_000:.1f}T"
    if n >= 1_000_000_000:
        return f"{sign}{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{sign}{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{sign}{n / 1_000:.1f}K"
    if n.is_integer():
        return f"{int(num)}"
    return f"{num:.2f}"


def _needs_compact_units(series: pd.Series) -> bool:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.dropna().empty:
        return False
    return bool(numeric.abs().max() >= 10_000)


def apply_dashboard_chart_theme(fig: go.Figure) -> go.Figure:
    """Apply the shared glass-native analytics system to a Plotly figure."""
    fig.update_layout(**PLOTLY_DASHBOARD_TEMPLATE["layout"])
    fig.update_layout(
        title=dict(
            x=0.02,
            xanchor="left",
            y=0.965,
            yanchor="top",
            font=dict(
                size=17,
                family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
                color=CHART_INK,
            ),
        ),
        legend=dict(
            orientation="h",
            x=0.99,
            xanchor="right",
            y=0.985,
            yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(color="#55555B", size=11),
            title=dict(font=dict(color=CHART_MUTED, size=11)),
            itemsizing="constant",
        ),
        margin=dict(l=22, r=20, t=76, b=56),
        autosize=True,
        bargap=0.24,
        barcornerradius=7,
        separators=".,",
        transition=dict(duration=180, easing="cubic-in-out"),
    )
    fig.update_xaxes(
        automargin=True,
        title_standoff=12,
        tickfont=dict(color=CHART_MUTED, size=11),
        title_font=dict(color=CHART_MUTED, size=12),
        fixedrange=True,
    )
    fig.update_yaxes(
        automargin=True,
        title_standoff=12,
        tickfont=dict(color=CHART_MUTED, size=11),
        title_font=dict(color=CHART_MUTED, size=12),
        fixedrange=True,
    )
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
    # Secondary axes (e.g. dual-axis) — same dark ink as primary
    for axis in ("xaxis2", "yaxis2", "xaxis3", "yaxis3"):
        if getattr(fig.layout, axis, None) is not None:
            fig.update_layout(
                **{
                    axis: dict(
                        title=dict(font=dict(color=CHART_MUTED, size=12)),
                        tickfont=dict(color=CHART_MUTED, size=11),
                        gridcolor=CHART_GRID,
                        zeroline=False,
                        showline=False,
                        fixedrange=True,
                    )
                }
            )
    if getattr(fig.layout, "polar", None) is not None:
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    gridcolor=CHART_GRID,
                    linecolor=CHART_BORDER,
                    tickfont=dict(color=CHART_MUTED, size=11),
                ),
                angularaxis=dict(
                    linecolor=CHART_BORDER,
                    tickfont=dict(color=CHART_MUTED, size=11),
                ),
            )
        )
    # Plotly table traces: force steel-glass fills (avoid default dark themes)
    for trace in fig.data:
        if getattr(trace, "type", "") == "table":
            trace.header.update(
                fill=dict(color="rgba(238, 241, 247, 0.96)"),
                line=dict(color="rgba(0,0,0,0.12)"),
                font=dict(color="#1d1d1f", size=12),
                align="left",
            )
            trace.cells.update(
                fill=dict(color="rgba(255,255,255,0.92)"),
                line=dict(color="rgba(0,0,0,0.08)"),
                font=dict(color="#1d1d1f", size=12),
                align="left",
            )
    return fig


def show_plotly_chart(fig: go.Figure, *, config: Optional[Dict[str, Any]] = None) -> None:
    """Render a responsive chart without hijacking normal page scrolling."""
    merged = dict(PLOTLY_INTERACTIVE_CONFIG)
    if config:
        merged.update(config)
    st.plotly_chart(fig, width="stretch", config=merged)


def graph_insight_expander(chart_title: str, body_md: str, *, for_instructions: bool = False) -> None:
    """Collapsed help text: chart interpretation (`for_instructions=False`) or step-by-step (`True`)."""
    if for_instructions:
        label = f"Instructions — {chart_title}"
    else:
        label = f"How to read this chart — {chart_title}"
    with st.expander(label, expanded=False):
        st.markdown(body_md)


def format_compact_number(value: Any, *, decimals: int = 1) -> str:
    """Format large display metrics compactly while preserving useful precision."""
    if value is None or pd.isna(value):
        return "—"
    number = float(value)
    magnitude = abs(number)
    for threshold, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if magnitude >= threshold:
            rendered = f"{number / threshold:.{decimals}f}".rstrip("0").rstrip(".")
            return f"{rendered}{suffix}"
    return f"{int(round(number)):,}"


def styled_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
) -> str:
    """Return HTML for a single glassmorphism metric card.

    Leading whitespace is avoided so Markdown does not treat the block
    as an indented code block.
    """
    color_style = f"color:{color};" if color else ""
    delta_class = ""
    if delta:
        if delta.strip().startswith(("+", "▲")):
            delta_class = "positive"
        elif delta.strip().startswith(("-", "▼")):
            delta_class = "negative"
    delta_html = (
        f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ""
    )
    html = (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value" style="{color_style}">'
        f'{value}'
        f'</div>'
        f'{delta_html}'
        f'</div>'
    )
    return html


def kpi_row(metrics: List[Dict[str, Any]]) -> None:
    """Render a row of KPI metric cards.

    Each metric dict: {label, value, delta?, icon?, color?}
    """
    cards_html = "".join(
        styled_metric_card(
            m.get("label", ""),
            str(m.get("value", "")),
            delta=m.get("delta"),
            icon=m.get("icon"),
            color=m.get("color"),
        )
        for m in metrics
    )
    st.markdown(f'<div class="metric-row">{cards_html}</div>', unsafe_allow_html=True)


def section_header(title: str, subtitle: Optional[str] = None, icon: Optional[str] = None) -> None:
    """Render a styled text-only section header with optional subtitle."""
    st.markdown(
        f'<div class="yt-section-header"><span>{title}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="yt-section-underline"></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            "<p style='color:#6e6e73;font-size:13px;line-height:1.55;font-weight:500;'>" + subtitle + "</p>",
            unsafe_allow_html=True,
        )


def animated_counter(value: float, label: str) -> None:
    """Render a simple animated counter using CSS animation."""
    st.markdown(
        f"""
        <div class="fade-in" style="margin-bottom:0.6rem;">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="font-size:32px;">{value:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_line_chart(
    df: pd.DataFrame,
    x: str,
    y_cols: Sequence[str],
    title: str,
    secondary_y: Optional[Iterable[str]] = None,
) -> go.Figure:
    """Create a multi-line Plotly chart with optional secondary y-axis."""
    x_label = _friendly_label(x)
    line_palette = YT_COLORWAY
    secondary_y = set(secondary_y or [])
    if secondary_y:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for i, col in enumerate(y_cols):
            use_secondary = col in secondary_y
            color = line_palette[i % len(line_palette)]
            fig.add_trace(
                go.Scatter(
                    x=df[x],
                    y=df[col],
                    name=_friendly_label(col),
                    mode="lines+markers",
                    line={"shape": "linear", "color": color, "width": 2.8},
                    marker={"size": 7, "color": "#FFFFFF", "line": {"color": color, "width": 2.2}},
                    hovertemplate=f"{x_label}: %{{x}}<br>{_friendly_label(col)}: %{{y:~s}}<extra></extra>",
                ),
                secondary_y=use_secondary,
            )
        fig.update_xaxes(title_text=x_label)
        fig.update_yaxes(title_text=_friendly_label(y_cols[0]), secondary_y=False)
        if len(y_cols) > 1:
            fig.update_yaxes(title_text=_friendly_label(y_cols[-1]), secondary_y=True)
        primary_cols = [c for c in y_cols if c not in secondary_y]
        secondary_cols = [c for c in y_cols if c in secondary_y]
        if any(_needs_compact_units(df[c]) for c in primary_cols if c in df.columns):
            fig.update_yaxes(tickformat="~s", secondary_y=False)
        if any(_needs_compact_units(df[c]) for c in secondary_cols if c in df.columns):
            fig.update_yaxes(tickformat="~s", secondary_y=True)
    else:
        fig = go.Figure()
        for i, col in enumerate(y_cols):
            color = line_palette[i % len(line_palette)]
            fig.add_trace(
                go.Scatter(
                    x=df[x],
                    y=df[col],
                    name=_friendly_label(col),
                    mode="lines+markers",
                    line={"shape": "linear", "color": color, "width": 2.8},
                    marker={"size": 7, "color": "#FFFFFF", "line": {"color": color, "width": 2.2}},
                    fill="tozeroy" if len(y_cols) == 1 else None,
                    fillcolor="rgba(230,0,18,0.08)" if len(y_cols) == 1 else None,
                    hovertemplate=f"{x_label}: %{{x}}<br>{_friendly_label(col)}: %{{y:~s}}<extra></extra>",
                )
            )
        fig.update_xaxes(title_text=x_label)
        fig.update_yaxes(title_text=", ".join(_friendly_label(c) for c in y_cols))
        if any(_needs_compact_units(df[c]) for c in y_cols if c in df.columns):
            fig.update_yaxes(tickformat="~s")

    fig.update_layout(title=title, height=420)
    apply_dashboard_chart_theme(fig)
    return fig


def plotly_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    horizontal: bool = False,
) -> go.Figure:
    """Create a readable bar chart with direct labels and restrained emphasis."""
    bar_line = dict(color="rgba(255,255,255,0.72)", width=0.8)
    x_label = _friendly_label(x)
    y_label = _friendly_label(y)
    numeric_values = pd.to_numeric(df[y], errors="coerce").fillna(0)
    is_percentage = y.lower().endswith(("_pct", "_percent", "_percentage"))
    if is_percentage:
        compact_values = [
            f"{float(value):.2f}".rstrip("0").rstrip(".") + "%"
            for value in numeric_values.tolist()
        ]
    else:
        compact_values = [_compact_number(v) for v in numeric_values.tolist()]
    if numeric_values.empty:
        bar_colors: List[str] = []
    elif bool((numeric_values < 0).any()):
        # Direction is also written in the value labels; color is supplemental.
        bar_colors = [YT_BLUE if value >= 0 else YT_RED for value in numeric_values]
    else:
        bar_colors = ["rgba(230,0,18,0.74)"] * len(numeric_values)
        max_position = int(np.argmax(numeric_values.to_numpy()))
        bar_colors[max_position] = YT_BLUE
    if horizontal:
        fig = go.Figure(
            go.Bar(
                x=df[y],
                y=df[x],
                orientation="h",
                marker=dict(color=bar_colors, line=bar_line),
                text=compact_values,
                customdata=compact_values,
                texttemplate="%{text}",
                textposition="outside",
                textfont=dict(size=11, color=CHART_INK),
                cliponaxis=False,
                hovertemplate=f"{x_label}: %{{y}}<br>{y_label}: %{{customdata}}<extra></extra>",
            )
        )
        fig.update_xaxes(title_text=y_label)
        fig.update_yaxes(title_text=None, showgrid=False)
        fig.update_xaxes(showgrid=True, gridcolor=CHART_GRID, rangemode="tozero")
        if _needs_compact_units(numeric_values):
            fig.update_xaxes(tickformat="~s")
    else:
        fig = go.Figure(
            go.Bar(
                x=df[x],
                y=df[y],
                marker=dict(color=bar_colors, line=bar_line),
                text=compact_values,
                customdata=compact_values,
                texttemplate="%{text}",
                textposition="outside",
                textfont=dict(size=11, color=CHART_INK),
                cliponaxis=False,
                hovertemplate=f"{x_label}: %{{x}}<br>{y_label}: %{{customdata}}<extra></extra>",
            )
        )
        fig.update_xaxes(title_text=x_label)
        fig.update_yaxes(title_text=y_label, rangemode="tozero")
        if _needs_compact_units(numeric_values):
            fig.update_yaxes(tickformat="~s")
    fig.update_layout(title=title, showlegend=False)
    apply_dashboard_chart_theme(fig)
    return fig


def plotly_donut_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str,
) -> go.Figure:
    """Create a donut chart with center label."""
    fig = px.pie(
        df,
        names=names,
        values=values,
        hole=0.55,
        color_discrete_sequence=YT_COLORWAY,
        labels={names: _friendly_label(names), values: _friendly_label(values)},
    )
    fig.update_traces(
        textposition="outside",
        texttemplate="%{label}<br>%{percent}",
        textfont=dict(size=12, color=CHART_INK),
        marker=dict(line=dict(color="rgba(255,255,255,0.95)", width=1.2)),
        hovertemplate=f"{_friendly_label(names)}: %{{label}}<br>{_friendly_label(values)}: %{{value:~s}}<extra></extra>",
    )
    fig.update_layout(title=title, showlegend=True)
    apply_dashboard_chart_theme(fig)
    return fig


def plotly_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str,
) -> go.Figure:
    """Create a heatmap from tall-form data with x, y, z columns."""
    pivot = df.pivot(index=y, columns=x, values=z)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[
                [0.0, "rgba(230,0,18,0.06)"],
                [0.45, "rgba(230,0,18,0.42)"],
                [1.0, YT_RED],
            ],
            hoverongaps=False,
            colorbar=dict(
                title=_friendly_label(z),
                thickness=10,
                outlinewidth=0,
                tickfont=dict(color=CHART_MUTED),
                title_font=dict(color=CHART_MUTED, size=11),
            ),
        )
    )
    fig.update_layout(title=title)
    fig.update_xaxes(title_text=_friendly_label(x))
    fig.update_yaxes(title_text=_friendly_label(y))
    apply_dashboard_chart_theme(fig)
    return fig


def plotly_radar_chart(
    categories: Sequence[str],
    series: Dict[str, Sequence[float]],
    title: str,
) -> go.Figure:
    """Create a radar / spider chart for competitor comparison."""
    fig = go.Figure()
    for name, values in series.items():
        vals = list(values)
        if vals and vals[0] != vals[-1]:
            vals.append(vals[0])
        cats = list(categories)
        if cats and cats[0] != cats[-1]:
            cats.append(cats[0])
        fig.add_trace(go.Scatterpolar(r=vals, theta=cats, fill="toself", name=name))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title=title)
    apply_dashboard_chart_theme(fig)
    return fig


def plotly_gauge_chart(
    value: float,
    title: str,
    max_val: float = 100,
) -> go.Figure:
    """Create a circular gauge for scoring."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            gauge={
                "axis": {"range": [0, max_val]},
                "bar": {"color": "#FF0000"},
                "steps": [
                    {"range": [0, max_val * 0.5], "color": "rgba(0,0,0,0.06)"},
                    {"range": [max_val * 0.5, max_val * 0.8], "color": "rgba(0,119,237,0.12)"},
                    {"range": [max_val * 0.8, max_val], "color": "rgba(255,0,0,0.18)"},
                ],
            },
            title={"text": title},
        )
    )
    apply_dashboard_chart_theme(fig)
    return fig


def plotly_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    size: Optional[str],
    color: Optional[str],
    title: str,
    *,
    log_x: bool = False,
    enhanced_markers: bool = False,
) -> go.Figure:
    """Create a scatter plot with optional log-scaled X and clearer markers."""
    hover_cols = [c for c in ("channel_title", "video_title") if c in df.columns]
    color_kw: Dict[str, Any] = {}
    color_cardinality = int(df[color].nunique(dropna=True)) if color and color in df.columns else 0
    # A legend with dozens (or hundreds) of recycled colors is not a legend—it
    # is noise. Preserve the category in hover details and use one product color
    # when the categorical dimension exceeds a scannable legend.
    use_categorical_color = bool(color and color in df.columns and color_cardinality <= 8)
    if use_categorical_color:
        color_kw["color"] = color
        color_kw["color_discrete_sequence"] = YT_COLORWAY
    fig = px.scatter(
        df,
        x=x,
        y=y,
        render_mode="svg",
        size=size if size in df.columns else None,
        hover_data=hover_cols if hover_cols else None,
        labels={
            x: _friendly_label(x),
            y: _friendly_label(y),
            size: _friendly_label(size) if size else "",
            color: _friendly_label(color) if color else "",
        },
        **color_kw,
    )
    fig.update_layout(title=title)
    apply_dashboard_chart_theme(fig)
    fig.update_layout(showlegend=use_categorical_color)
    if log_x:
        fig.update_xaxes(type="log", title=f"{_friendly_label(x)} (log scale)")
    else:
        fig.update_xaxes(title=_friendly_label(x))
    fig.update_yaxes(title=_friendly_label(y))
    fig.update_xaxes(showgrid=True, gridcolor=CHART_GRID)
    fig.update_yaxes(showgrid=True, gridcolor=CHART_GRID)
    if x in df.columns and _needs_compact_units(df[x]):
        fig.update_xaxes(tickformat="~s")
    if y in df.columns and _needs_compact_units(df[y]):
        fig.update_yaxes(tickformat="~s")
    marker_style: Dict[str, Any] = {
        "opacity": 0.72,
        "line": {"width": 1.1, "color": "rgba(255,255,255,0.82)"},
    }
    if not use_categorical_color:
        marker_style["color"] = YT_RED
    if enhanced_markers:
        marker_style["size"] = 14
        marker_style["opacity"] = 0.88
    fig.update_traces(marker=marker_style)
    return fig


def plotly_treemap(
    df: pd.DataFrame,
    path: Sequence[str],
    values: str,
    title: str,
) -> go.Figure:
    """Create a treemap for keyword intelligence."""
    fig = px.treemap(
        df,
        path=path,
        values=values,
        color=values,
        color_continuous_scale=["#FDEBED", "#F45B69", YT_RED],
        labels={values: _friendly_label(values)},
    )
    fig.update_layout(title=title)
    fig.update_traces(
        textfont=dict(size=12, color=CHART_INK),
        texttemplate="%{label}<br>%{value:~s}",
    )
    apply_dashboard_chart_theme(fig)
    return fig


def plotly_funnel_chart(
    stages: Sequence[str],
    values: Sequence[float],
    title: str,
) -> go.Figure:
    """Create a funnel chart for content pipeline stages."""
    fig = go.Figure(
        go.Funnel(
            y=list(stages),
            x=list(values),
            textinfo="text+percent initial",
            text=[_compact_number(v) for v in values],
            textfont=dict(size=13, color="#1d1d1f"),
            hovertemplate="Stage: %{y}<br>Value: %{x:~s}<extra></extra>",
        )
    )
    fig.update_layout(title=title)
    fig.update_xaxes(title_text="Value")
    fig.update_yaxes(title_text="Stage")
    apply_dashboard_chart_theme(fig)
    return fig


def styled_dataframe(
    df: pd.DataFrame,
    title: Optional[str] = None,
    precision: int = 1,
    image_columns: Optional[Sequence[str]] = None,
) -> None:
    """Render a readable dataframe with plain-language column labels.

    Args:
        df: DataFrame to render.
        title: Optional title shown above the table.
        precision: Decimal precision for numeric columns.
        image_columns: Optional list of columns that should display images if URLs.
    """
    if df.empty:
        st.info("No rows to display.")
        return

    if title:
        st.markdown(f"**{title}**", unsafe_allow_html=True)

    display_df = df.rename(columns={column: _friendly_label(str(column)) for column in df.columns})
    styler = (
        display_df.style.format(precision=precision, thousands=",")
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background", "linear-gradient(180deg, rgba(238,241,247,0.98), rgba(226,230,238,0.95))"),
                        ("color", "#1d1d1f"),
                        ("font-weight", "700"),
                        ("border", "1px solid rgba(0,0,0,0.12)"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("background", "rgba(255,255,255,0.9)"),
                        ("color", "#1d1d1f"),
                        ("border", "1px solid rgba(0,0,0,0.08)"),
                    ],
                },
            ]
        )
        .set_properties(
            **{
                "background-color": "rgba(255,255,255,0.9)",
                "color": "#1d1d1f",
                "border-color": "rgba(0,0,0,0.08)",
            }
        )
    )
    # Use Streamlit's native image column config when requested
    column_config: Dict[str, Any] = {}
    if image_columns:
        for col in image_columns:
            if col in df.columns:
                friendly_col = _friendly_label(str(col))
                column_config[friendly_col] = st.column_config.ImageColumn(friendly_col)

    try:
        st.dataframe(
            styler,
            width="stretch",
            hide_index=True,
            column_config=column_config or None,
        )
    except Exception:
        # Styled DataFrames use Arrow; a broken/missing pyarrow install (common on Windows) still shows data.
        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True,
            column_config=column_config or None,
        )


def styled_keyword_chips(keywords: Sequence[str]) -> None:
    """Render a set of keywords as styled chips."""
    chips = "".join(f'<span class="keyword-chip">{kw}</span>' for kw in keywords)
    st.markdown(chips, unsafe_allow_html=True)
