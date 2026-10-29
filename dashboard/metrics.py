from __future__ import annotations

import pandas as pd
import streamlit as st


def render_kpis(df: pd.DataFrame, region_name: str = "Active Region", is_sample_data: bool = False) -> None:
    """Render high-contrast, professional KPI cards adhering to PLEIADES design tokens."""
    if df.empty:
        total = 0
        high_conf = 0
        max_frp = 0.0
        avg_frp = 0.0
        viirs_count = 0
        modis_count = 0
        latest_time = "N/A"
    else:
        total = len(df)
        high_conf = int((pd.to_numeric(df.get("confidence", 0), errors="coerce") >= 80).sum())
        frp_clean = pd.to_numeric(df.get("frp", 0), errors="coerce").fillna(0.0)
        max_frp = float(frp_clean.max()) if not frp_clean.empty else 0.0
        avg_frp = float(frp_clean.mean()) if not frp_clean.empty else 0.0
        inst_series = df.get("instrument", pd.Series(["UNKNOWN"] * len(df))).astype(str).str.upper()
        viirs_count = int((inst_series == "VIIRS").sum())
        modis_count = int((inst_series == "MODIS").sum())

        if "timestamp" in df.columns and not df["timestamp"].dropna().empty:
            latest_time = str(df["timestamp"].dropna().max())[:16]
        elif "acq_date" in df.columns:
            latest_time = str(df["acq_date"].iloc[0])
        else:
            latest_time = "Recent"

    data_status_badge = "DEMO SAMPLE" if is_sample_data else "LIVE ACTIVE" if total > 0 else "NO DATA"
    data_status_color = "#F59E0B" if is_sample_data else "#34D399" if total > 0 else "#94A3B8"

    st.markdown(
        f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 20px;">
            <div style="background: linear-gradient(180deg, #122238 0%, #0D1929 100%); border: 1px solid #25374C; border-radius: 12px; padding: 14px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                <div style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; color: #9FB0C5; margin-bottom: 6px;">Total Hotspots</div>
                <div style="font-size: 1.85rem; font-weight: 700; color: #F1F5F9; line-height: 1.1;">{total:,}</div>
                <div style="font-size: 0.72rem; color: #38BDF8; margin-top: 6px; font-weight: 500;">FIRMS satellite observations</div>
            </div>
            <div style="background: linear-gradient(180deg, #122238 0%, #0D1929 100%); border: 1px solid #25374C; border-radius: 12px; padding: 14px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                <div style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; color: #9FB0C5; margin-bottom: 6px;">High Confidence</div>
                <div style="font-size: 1.85rem; font-weight: 700; color: #34D399; line-height: 1.1;">{high_conf:,}</div>
                <div style="font-size: 0.72rem; color: #9FB0C5; margin-top: 6px;">{(high_conf / max(total, 1) * 100):.1f}% with confidence ≥ 80%</div>
            </div>
            <div style="background: linear-gradient(180deg, #122238 0%, #0D1929 100%); border: 1px solid #25374C; border-radius: 12px; padding: 14px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                <div style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; color: #9FB0C5; margin-bottom: 6px;">Peak FRP (Power)</div>
                <div style="font-size: 1.85rem; font-weight: 700; color: #FF7A45; line-height: 1.1;">{max_frp:.1f} <span style="font-size: 1rem; font-weight: 400; color: #9FB0C5;">MW</span></div>
                <div style="font-size: 0.72rem; color: #9FB0C5; margin-top: 6px;">Mean intensity: {avg_frp:.1f} MW</div>
            </div>
            <div style="background: linear-gradient(180deg, #122238 0%, #0D1929 100%); border: 1px solid #25374C; border-radius: 12px; padding: 14px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                <div style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; color: #9FB0C5; margin-bottom: 6px;">Sensors (VIIRS / MODIS)</div>
                <div style="font-size: 1.85rem; font-weight: 700; color: #60A5FA; line-height: 1.1;">{viirs_count} <span style="font-size: 1.1rem; color: #9FB0C5;">/</span> {modis_count}</div>
                <div style="font-size: 0.72rem; color: #9FB0C5; margin-top: 6px;">375m VIIRS vs 1km MODIS</div>
            </div>
            <div style="background: linear-gradient(180deg, #122238 0%, #0D1929 100%); border: 1px solid #25374C; border-radius: 12px; padding: 14px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                <div style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; color: #9FB0C5; margin-bottom: 6px;">Region / Latest Update</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #F1F5F9; line-height: 1.3; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{region_name}</div>
                <div style="font-size: 0.72rem; color: #9FB0C5; margin-top: 4px;">Latest: {latest_time}</div>
                <div style="display: inline-block; margin-top: 6px; font-size: 0.68rem; font-weight: 700; color: {data_status_color}; background: {data_status_color}22; padding: 2px 6px; border-radius: 4px;">{data_status_badge}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(df: pd.DataFrame) -> None:
    """Backward-compatible entry point."""
    render_kpis(df)
