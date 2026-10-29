from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

CHART_THEME = {
    "paper_bgcolor": "rgba(18, 34, 56, 0.9)",
    "plot_bgcolor": "rgba(13, 25, 41, 0.8)",
    "font_color": "#F1F5F9",
    "grid_color": "#25374C",
    "accent_cyan": "#38BDF8",
    "accent_blue": "#60A5FA",
    "fire_orange": "#FF7A45",
    "fire_red": "#EF4444",
    "amber": "#F59E0B",
    "emerald": "#34D399",
}


def _apply_dark_layout(fig: go.Figure, title: str, x_title: str | None = None, y_title: str | None = None) -> go.Figure:
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "font": {"size": 14, "color": CHART_THEME["font_color"]},
            "x": 0.02,
            "y": 0.95,
        },
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font={"color": CHART_THEME["font_color"], "family": "Inter, -apple-system, sans-serif"},
        margin=dict(l=40, r=20, t=45, b=40),
        xaxis=dict(
            title=x_title,
            gridcolor=CHART_THEME["grid_color"],
            zerolinecolor=CHART_THEME["grid_color"],
            color="#9FB0C5",
        ),
        yaxis=dict(
            title=y_title,
            gridcolor=CHART_THEME["grid_color"],
            zerolinecolor=CHART_THEME["grid_color"],
            color="#9FB0C5",
        ),
        legend=dict(
            bgcolor="rgba(18, 34, 56, 0.6)",
            bordercolor=CHART_THEME["grid_color"],
            font=dict(color="#F1F5F9", size=11),
        ),
    )
    return fig


def plot_detections_timeline(df: pd.DataFrame) -> go.Figure | None:
    if df.empty or "timestamp" not in df.columns:
        return None

    timeline_df = df.copy()
    timeline_df["date"] = pd.to_datetime(timeline_df["timestamp"], errors="coerce").dt.date
    daily = timeline_df.groupby(["date", "instrument"]).size().reset_index(name="count")

    if daily.empty:
        return None

    color_map = {
        "VIIRS": CHART_THEME["fire_red"],
        "MODIS": CHART_THEME["amber"],
        "UNKNOWN": CHART_THEME["accent_cyan"],
    }

    fig = px.bar(
        daily,
        x="date",
        y="count",
        color="instrument",
        color_discrete_map=color_map,
        barmode="stack",
    )
    return _apply_dark_layout(fig, "Hotspot Detections Over Time", "Observation Date", "Detections Count")


def plot_instrument_comparison(df: pd.DataFrame) -> go.Figure | None:
    if df.empty or "instrument" not in df.columns:
        return None

    counts = df["instrument"].value_counts().reset_index()
    counts.columns = ["instrument", "count"]

    colors = [CHART_THEME["fire_red"] if inst == "VIIRS" else CHART_THEME["amber"] for inst in counts["instrument"]]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts["instrument"],
                values=counts["count"],
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="#122238", width=2)),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
            )
        ]
    )
    return _apply_dark_layout(fig, "Sensor Distribution: MODIS vs VIIRS")


def plot_confidence_distribution(df: pd.DataFrame) -> go.Figure | None:
    if df.empty or "confidence" not in df.columns:
        return None

    conf_series = pd.to_numeric(df["confidence"], errors="coerce").dropna()
    if conf_series.empty:
        return None

    fig = go.Figure(
        data=[
            go.Histogram(
                x=conf_series,
                nbinsx=20,
                marker=dict(
                    color=CHART_THEME["accent_cyan"],
                    line=dict(color="#122238", width=1),
                ),
            )
        ]
    )
    return _apply_dark_layout(fig, "Detection Confidence Distribution", "Confidence (%)", "Observations")


def plot_frp_distribution(df: pd.DataFrame) -> go.Figure | None:
    if df.empty or "frp" not in df.columns:
        return None

    frp_clean = pd.to_numeric(df["frp"], errors="coerce").dropna()
    if frp_clean.empty:
        return None

    fig = go.Figure(
        data=[
            go.Box(
                y=frp_clean,
                x=df.get("instrument", "All"),
                marker_color=CHART_THEME["fire_orange"],
                boxpoints="outliers",
                jitter=0.3,
                pointpos=-1.8,
            )
        ]
    )
    return _apply_dark_layout(fig, "Fire Radiative Power (FRP) by Instrument", "Instrument", "FRP (MW)")


def plot_daynight_distribution(df: pd.DataFrame) -> go.Figure | None:
    if df.empty or "daynight" not in df.columns:
        return None

    dn_counts = df["daynight"].map({"D": "Daytime", "N": "Nighttime"}).value_counts().reset_index()
    dn_counts.columns = ["period", "count"]

    fig = px.bar(
        dn_counts,
        x="period",
        y="count",
        color="period",
        color_discrete_map={"Daytime": CHART_THEME["amber"], "Nighttime": CHART_THEME["accent_blue"]},
    )
    return _apply_dark_layout(fig, "Diurnal Cycle: Day vs Night Detections", "Observation Time", "Detections")


def render_analytics_panel(df: pd.DataFrame) -> None:
    """Render the full analytics dashboard panel with responsive multi-column layouts."""
    if df.empty:
        st.markdown(
            """
            <div style="background: #122238; border: 1px dashed #25374C; border-radius: 12px; padding: 2.5rem; text-align: center; color: #9FB0C5;">
                <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-weight: 600; font-size: 1.05rem; color: #F1F5F9;">No Analytics Data Available</div>
                <div>Load or upload NASA FIRMS observations to generate spatiotemporal fire metrics.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Row 1: Timeline & Sensor breakdown
    col1, col2 = st.columns([1.8, 1.2])
    with col1:
        fig_time = plot_detections_timeline(df)
        if fig_time:
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Temporal data insufficient for timeline rendering.")

    with col2:
        fig_inst = plot_instrument_comparison(df)
        if fig_inst:
            st.plotly_chart(fig_inst, use_container_width=True)
        else:
            st.info("Instrument data unavailable for comparison.")

    # Row 2: Confidence & FRP & Diurnal
    col3, col4, col5 = st.columns(3)
    with col3:
        fig_conf = plot_confidence_distribution(df)
        if fig_conf:
            st.plotly_chart(fig_conf, use_container_width=True)
        else:
            st.info("Confidence data unavailable.")

    with col4:
        fig_frp = plot_frp_distribution(df)
        if fig_frp:
            st.plotly_chart(fig_frp, use_container_width=True)
        else:
            st.info("FRP data unavailable.")

    with col5:
        fig_dn = plot_daynight_distribution(df)
        if fig_dn:
            st.plotly_chart(fig_dn, use_container_width=True)
        else:
            st.info("Day/Night data unavailable.")


def render_charts(df: pd.DataFrame) -> None:
    """Backward-compatible entry point."""
    render_analytics_panel(df)
