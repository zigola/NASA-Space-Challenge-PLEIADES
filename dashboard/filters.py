from __future__ import annotations

from typing import Any, Tuple
import pandas as pd
import streamlit as st

REGION_PRESETS: dict[str, Tuple[float, float, float, float]] = {
    "Morocco-Rif": (34.5, -6.5, 36.5, -2.0),
    "Morocco-Atlas": (30.0, -10.0, 34.5, -4.0),
    "North Africa": (20.0, -18.0, 38.0, 15.0),
    "Mediterranean Basin": (30.0, -10.0, 46.0, 36.0),
    "Global Extent": (-90.0, -180.0, 90.0, 180.0),
}


def render_sidebar_filters(
    df: pd.DataFrame,
    current_region: str = "Morocco-Rif",
    key_prefix: str = "filter",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Render working filters in the sidebar and return the filtered DataFrame + metadata."""
    st.sidebar.markdown(
        """
        <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #38BDF8; margin-top: 10px; margin-bottom: 8px;">
            Telemetry & Sensor Filters
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Geographic Region
    region_options = list(REGION_PRESETS.keys())
    default_region_idx = region_options.index(current_region) if current_region in region_options else 0
    selected_region = st.sidebar.selectbox(
        "Geographic Domain",
        region_options,
        index=default_region_idx,
        key=f"{key_prefix}_region",
    )
    selected_bbox = REGION_PRESETS[selected_region]

    # 2. Satellite / Instrument
    available_instruments = ["VIIRS", "MODIS"]
    selected_instruments = st.sidebar.multiselect(
        "Instruments",
        available_instruments,
        default=available_instruments,
        key=f"{key_prefix}_instruments",
    )

    # 3. Confidence Threshold
    min_confidence = st.sidebar.slider(
        "Minimum Confidence (%)",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help="Filter satellite detections by minimum detection confidence algorithm score.",
        key=f"{key_prefix}_min_conf",
    )

    # 4. Minimum FRP (Fire Radiative Power)
    max_possible_frp = 300
    if not df.empty and "frp" in df.columns:
        max_frp_val = float(pd.to_numeric(df["frp"], errors="coerce").max() or 300)
        max_possible_frp = max(50, int(max_frp_val))

    min_frp = st.sidebar.slider(
        "Min Fire Radiative Power (MW)",
        min_value=0,
        max_value=min(max_possible_frp, 500),
        value=0,
        step=5,
        help="Filter hotspots by radiative power emitted by the active fire.",
        key=f"{key_prefix}_min_frp",
    )

    # 5. Day / Night
    daynight_filter = st.sidebar.selectbox(
        "Solar Observation Period",
        ["All Observations", "Daytime Only", "Nighttime Only"],
        index=0,
        key=f"{key_prefix}_daynight",
    )

    # Apply filters
    filtered_df = df.copy() if not df.empty else pd.DataFrame()

    if not filtered_df.empty:
        # Instrument filter
        if selected_instruments:
            inst_series = filtered_df.get("instrument", pd.Series(["UNKNOWN"] * len(filtered_df))).astype(str).str.upper()
            filtered_df = filtered_df[inst_series.isin({i.upper() for i in selected_instruments})].copy()
        else:
            filtered_df = filtered_df.iloc[0:0]

        # Confidence filter
        if min_confidence > 0 and "confidence" in filtered_df.columns:
            conf_numeric = pd.to_numeric(filtered_df["confidence"], errors="coerce").fillna(0)
            filtered_df = filtered_df[conf_numeric >= min_confidence].copy()

        # FRP filter
        if min_frp > 0 and "frp" in filtered_df.columns:
            frp_numeric = pd.to_numeric(filtered_df["frp"], errors="coerce").fillna(0)
            filtered_df = filtered_df[frp_numeric >= min_frp].copy()

        # Day/Night filter
        if daynight_filter == "Daytime Only" and "daynight" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["daynight"].astype(str).str.upper() == "D"].copy()
        elif daynight_filter == "Nighttime Only" and "daynight" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["daynight"].astype(str).str.upper() == "N"].copy()

        # Bounding box filter if not global
        if selected_region != "Global Extent" and "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
            min_lat, min_lon, max_lat, max_lon = selected_bbox
            in_lat = filtered_df["latitude"].between(min(min_lat, max_lat), max(min_lat, max_lat))
            in_lon = filtered_df["longitude"].between(min(min_lon, max_lon), max(min_lon, max_lon))
            filtered_df = filtered_df[in_lat & in_lon].copy()

    # Reset button
    if st.sidebar.button("Reset All Filters", key=f"{key_prefix}_reset_btn", use_container_width=True):
        st.session_state[f"{key_prefix}_min_conf"] = 0
        st.session_state[f"{key_prefix}_min_frp"] = 0
        st.session_state[f"{key_prefix}_daynight"] = "All Observations"
        st.session_state[f"{key_prefix}_instruments"] = available_instruments
        st.rerun()

    filter_meta = {
        "region": selected_region,
        "bbox": selected_bbox,
        "instruments": selected_instruments,
        "min_confidence": min_confidence,
        "min_frp": min_frp,
        "daynight": daynight_filter,
    }

    return filtered_df, filter_meta


def render_csv_export_button(df: pd.DataFrame, filename: str = "pleiades_filtered_firms_hotspots.csv") -> None:
    """Render a functional download button for exporting filtered geospatial records."""
    if df.empty:
        st.button("Export Filtered CSV (0 records)", disabled=True)
        return

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"⬇️ Export Filtered Hotspots ({len(df):,} rows)",
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        help="Download currently filtered satellite detections as standard CSV.",
        use_container_width=False,
    )
