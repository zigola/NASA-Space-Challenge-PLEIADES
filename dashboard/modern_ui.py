from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from config.i18n import LANGUAGES, get_text
from dashboard.alerts_view import render_alerts_panel
from dashboard.charts import render_analytics_panel
from dashboard.filters import render_csv_export_button, render_sidebar_filters
from dashboard.layout import apply_pleiades_theme, render_application_header
from dashboard.maps import render_map
from dashboard.metrics import render_kpis
from dashboard.replay_view import render_replay_view
from src.ingest import (
    DEFAULT_BBOX,
    get_reference_dataset,
    normalize_firms_dataset,
    read_firms_file,
)
from src.nasa_firms.client import FIRMSClient


NAVIGATION_PAGES = [
    ("overview", "🛰️ Overview"),
    ("live_map", "🗺️ Live Fire Map"),
    ("detections", "📋 Satellite Detections"),
    ("data_explorer", "📥 Data Explorer"),
    ("analytics", "📊 Analytics"),
    ("alerts", "🚨 Alerts & Sensors"),
    ("data_sources", "🌐 Data Sources"),
    ("settings", "⚙️ Settings"),
]


def render_sidebar_navigation() -> str:
    """Render the primary navigation menu in the left sidebar."""
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; padding: 6px 0; margin-bottom: 8px;">
            <div style="
                width: 30px; height: 30px; border-radius: 8px;
                background: linear-gradient(135deg, #0284C7, #FF7A45);
                display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
            ">🛰️</div>
            <div>
                <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: 0.06em; color: #F1F5F9;">PLEIADES</div>
                <div style="font-size: 0.7rem; color: #9FB0C5;">Wildfire Intelligence System</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page_labels = [label for _, label in NAVIGATION_PAGES]
    page_keys = [key for key, _ in NAVIGATION_PAGES]

    current_idx = 0
    if "current_nav_key" in st.session_state and st.session_state["current_nav_key"] in page_keys:
        current_idx = page_keys.index(st.session_state["current_nav_key"])

    selected_label = st.sidebar.radio(
        "Navigation",
        page_labels,
        index=current_idx,
        label_visibility="collapsed",
        key="primary_navigation_radio",
    )

    selected_key = page_keys[page_labels.index(selected_label)]
    st.session_state["current_nav_key"] = selected_key
    return selected_key


def render_overview_page(
    filtered_df: pd.DataFrame,
    all_df: pd.DataFrame,
    region_name: str,
    is_sample_data: bool,
) -> None:
    """Render Main Overview Dashboard (Section 5.C)."""
    # 1. Operational summary banner
    st.markdown(
        f"""
        <div class="pleiades-card" style="border-left: 4px solid #38BDF8; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h3 style="margin: 0; font-size: 1.15rem; color: #F1F5F9;">Operational Situation Report · {region_name}</h3>
                    <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px; line-height: 1.5;">
                        Monitoring thermal anomalies detected by satellite constellations (NASA Terra, Aqua, Suomi-NPP, NOAA-20, NOAA-21).
                        Data is validated against physical fire radiative thresholds and geospatial bounding coordinates.
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.75rem; color: #9FB0C5;">Dataset State:</span>
                    <span style="font-size: 0.8rem; font-weight: 700; color: {'#F59E0B' if is_sample_data else '#34D399'};">
                        {'Reference Testbed' if is_sample_data else 'Active Telemetry'}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Row of KPI Cards
    render_kpis(filtered_df, region_name=region_name, is_sample_data=is_sample_data)

    # 3. Interactive Fire Map
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; margin-bottom: 8px;">
            <div style="font-weight: 700; font-size: 1rem; color: #F1F5F9;">Geospatial Wildfire Hotspot Intelligence Map</div>
            <div style="font-size: 0.8rem; color: #9FB0C5;">Pan, zoom, or click markers to inspect telemetry</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_map(filtered_df, height=520, key="overview_map")

    # 4. Analytics Summary Row (Timeline & Sensor comparison)
    col1, col2 = st.columns([1.6, 1.4])
    with col1:
        st.markdown(
            """
            <div style="font-weight: 700; font-size: 0.95rem; color: #F1F5F9; margin-top: 20px; margin-bottom: 8px;">
                Temporal Distribution
            </div>
            """,
            unsafe_allow_html=True,
        )
        from dashboard.charts import plot_detections_timeline
        fig_time = plot_detections_timeline(filtered_df)
        if fig_time:
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No timeline data available for current selection.")

    with col2:
        st.markdown(
            """
            <div style="font-weight: 700; font-size: 0.95rem; color: #F1F5F9; margin-top: 20px; margin-bottom: 8px;">
                Instrument Breakdown
            </div>
            """,
            unsafe_allow_html=True,
        )
        from dashboard.charts import plot_instrument_comparison
        fig_comp = plot_instrument_comparison(filtered_df)
        if fig_comp:
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No sensor breakdown available.")

    # 5. Recent Detections Quick Table & Export
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; margin-bottom: 10px;">
            <div style="font-weight: 700; font-size: 0.95rem; color: #F1F5F9;">Recent Satellite Hotspot Observations</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not filtered_df.empty:
        table_cols = [c for c in ["satellite", "instrument", "latitude", "longitude", "confidence", "frp", "brightness", "acq_date", "acq_time", "daynight"] if c in filtered_df.columns]
        st.dataframe(filtered_df[table_cols].head(15), use_container_width=True)
        render_csv_export_button(filtered_df, filename=f"pleiades_{region_name.lower().replace(' ', '_')}_hotspots.csv")
    else:
        st.info("No observations match current filter criteria.")


def render_live_map_page(filtered_df: pd.DataFrame, region_name: str) -> None:
    """Render full-screen dedicated geospatial fire map."""
    st.markdown(
        """
        <div style="margin-bottom: 14px;">
            <h3 style="margin: 0; color: #F1F5F9; font-size: 1.25rem;">Live Fire Geospatial Console</h3>
            <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px;">
                High-resolution mapping with multi-satellite telemetry overlays, spatial clustering, and interactive hotspot interrogation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
    col1.metric("Visible Detections", f"{len(filtered_df):,}")
    high_conf = int((pd.to_numeric(filtered_df.get("confidence", 0), errors="coerce") >= 80).sum()) if not filtered_df.empty else 0
    col2.metric("High Confidence (≥80%)", f"{high_conf:,}")
    max_frp = float(pd.to_numeric(filtered_df.get("frp", 0), errors="coerce").max() or 0.0) if not filtered_df.empty else 0.0
    col3.metric("Peak FRP", f"{max_frp:.1f} MW")
    with col4:
        st.write("")
        render_csv_export_button(filtered_df, filename="pleiades_live_map_detections.csv")

    render_map(filtered_df, height=620, key="fullscreen_map")


def render_detections_page(filtered_df: pd.DataFrame) -> None:
    """Render Satellite Detections tabular inspector with search, sorting, and export."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #F1F5F9; font-size: 1.25rem;">Satellite Hotspot Telemetry Catalog</h3>
            <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px;">
                Inspect, query, filter, and export individual NASA FIRMS detection records with complete scientific attributes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        st.info("No detections available in the current filtered dataset.")
        return

    # Search query
    col_search, col_export = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("🔍 Search detections by satellite, instrument, date, or day/night", "")
    with col_export:
        st.write("")
        render_csv_export_button(filtered_df)

    display_df = filtered_df.copy()
    if search_query:
        query_str = search_query.strip().lower()
        mask = pd.Series(False, index=display_df.index)
        for col in ["satellite", "instrument", "acq_date", "daynight", "source_file"]:
            if col in display_df.columns:
                mask |= display_df[col].astype(str).str.lower().str.contains(query_str, na=False)
        display_df = display_df[mask]

    st.caption(f"Showing {len(display_df):,} matching detection records")
    st.dataframe(display_df, use_container_width=True, height=520)


def render_data_explorer_page(
    on_data_loaded_callback: Any = None,
) -> None:
    """Render file upload, schema normalization, and sample data loader (Section 7)."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #F1F5F9; font-size: 1.25rem;">Data Explorer & File Ingestion</h3>
            <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px;">
                Ingest NASA FIRMS CSV, JSON, or GeoJSON datasets. Validates geospatial coordinates, parses observation timestamps, and harmonizes schemas.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_upload, tab_samples = st.tabs(["📤 Upload Dataset (CSV, JSON, GeoJSON)", "📚 Preloaded Reference Datasets"])

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Choose a NASA FIRMS or geospatial wildfire file",
            type=["csv", "json", "geojson", "txt"],
            help="Supports standard FIRMS CSV exports, GeoJSON FeatureCollections, and structured JSON arrays.",
        )

        if uploaded_file is not None:
            try:
                parsed_df = read_firms_file(uploaded_file)
                st.session_state["custom_data"] = parsed_df
                st.session_state["data_source_mode"] = f"Uploaded File: {uploaded_file.name}"
                st.session_state["is_sample_data"] = False
                st.success(f"Successfully parsed and validated {len(parsed_df):,} fire records from {uploaded_file.name}!")

                col1, col2, col3 = st.columns(3)
                col1.metric("Rows Validated", len(parsed_df))
                col2.metric("Sensors Found", ", ".join(parsed_df["instrument"].unique()))
                col3.metric("Date Span", f"{parsed_df['acq_date'].min()} to {parsed_df['acq_date'].max()}")

                st.markdown("<h4 style='color: #F1F5F9; font-size: 0.95rem; margin-top: 1rem;'>Schema & Preview</h4>", unsafe_allow_html=True)
                st.dataframe(parsed_df.head(20), use_container_width=True)

                if st.button("Apply Dataset to Dashboard", type="primary"):
                    st.rerun()
            except Exception as exc:
                st.error(f"Failed to ingest file: {exc}")

    with tab_samples:
        st.write("Load one of the verified reference testbeds:")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(
                """
                <div class="pleiades-card">
                    <div style="font-weight: 700; color: #38BDF8; font-size: 1rem; margin-bottom: 6px;">
                        🔥 Morocco-Rif & Mediterranean Testbed (CSV)
                    </div>
                    <div style="color: #9FB0C5; font-size: 0.82rem; margin-bottom: 12px;">
                        Realistic multi-satellite dataset containing synchronized MODIS (Terra/Aqua) and VIIRS (Suomi-NPP/NOAA-20) wildfire detections.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Load Morocco-Rif CSV Sample", key="load_morocco_csv"):
                ref_df = get_reference_dataset()
                st.session_state["custom_data"] = ref_df
                st.session_state["data_source_mode"] = "Sample Reference Testbed"
                st.session_state["is_sample_data"] = True
                st.success(f"Loaded {len(ref_df)} reference observations!")
                st.rerun()

        with col_s2:
            st.markdown(
                """
                <div class="pleiades-card">
                    <div style="font-weight: 700; color: #38BDF8; font-size: 1rem; margin-bottom: 6px;">
                        🌍 GeoJSON Wildfire FeatureCollection
                    </div>
                    <div style="color: #9FB0C5; font-size: 0.82rem; margin-bottom: 12px;">
                        GeoJSON Point feature collection demonstrating format versatility and coordinate geometry extraction.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Load GeoJSON Sample", key="load_geojson_sample"):
                geojson_path = Path(__file__).resolve().parent.parent / "data" / "samples" / "sample_firms_wildfires.geojson"
                if geojson_path.exists():
                    geo_df = read_firms_file(geojson_path)
                    st.session_state["custom_data"] = geo_df
                    st.session_state["data_source_mode"] = "Sample GeoJSON Testbed"
                    st.session_state["is_sample_data"] = True
                    st.success(f"Loaded {len(geo_df)} GeoJSON features!")
                    st.rerun()


def render_data_sources_page(api_key: str | None) -> None:
    """Render Data Sources and NASA FIRMS API status (Section 8)."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #F1F5F9; font-size: 1.25rem;">NASA FIRMS Data Sources & Satellite Telemetry</h3>
            <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px;">
                Architecture, instrument resolution specifications, and API access management.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="pleiades-card">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem;">🛰️</span>
                    <span style="font-weight: 700; color: #EF4444; font-size: 1.05rem;">VIIRS (Visible Infrared Imaging Radiometer Suite)</span>
                </div>
                <div style="font-size: 0.82rem; color: #9FB0C5; line-height: 1.5;">
                    <p><b>Satellites:</b> Suomi-NPP, NOAA-20 (JPSS-1), NOAA-21 (JPSS-2)</p>
                    <p><b>Spatial Resolution:</b> 375 meters at nadir (I-bands: I4 thermal 3.74 μm, I5 thermal 11.45 μm)</p>
                    <p><b>Characteristics:</b> Exceptional sensitivity to smaller, flaming sub-pixel fires; higher perimeter fidelity; daytime and nighttime observations.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="pleiades-card">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem;">🛰️</span>
                    <span style="font-weight: 700; color: #F59E0B; font-size: 1.05rem;">MODIS (Moderate Resolution Imaging Spectroradiometer)</span>
                </div>
                <div style="font-size: 0.82rem; color: #9FB0C5; line-height: 1.5;">
                    <p><b>Satellites:</b> EOS Terra (10:30 AM/PM orbit) & Aqua (1:30 PM/AM orbit)</p>
                    <p><b>Spatial Resolution:</b> 1.0 km nominal resolution at nadir</p>
                    <p><b>Characteristics:</b> Multi-decadal baseline record (2000-present); robust Fire Radiative Power (FRP) calibration; long-term climatological trend benchmark.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<h4 style='color: #F1F5F9; font-size: 1rem; margin-top: 1.5rem;'>NASA FIRMS API Connection Status</h4>", unsafe_allow_html=True)
    is_key_present = bool(api_key or os.getenv("NASA_FIRMS_MAP_KEY"))

    status_pill = "🟢 Configured (MAP KEY Active)" if is_key_present else "🟡 Local / Offline Mode (No Key Set)"
    st.info(f"FIRMS API Connection: **{status_pill}**")

    st.markdown(
        """
        <div style="font-size: 0.82rem; color: #9FB0C5; margin-bottom: 12px;">
            To fetch live data directly from NASA FIRMS servers, obtain a free Map Key from
            <a href="https://firms.modaps.eosdis.nasa.gov/api/map_key/" target="_blank" style="color: #38BDF8;">NASA FIRMS Map Key Request</a>
            and set it in the environment variable <code>NASA_FIRMS_MAP_KEY</code>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    custom_key_input = st.text_input("Enter NASA FIRMS Map Key (for current session)", type="password", value=api_key or "")
    if custom_key_input:
        st.session_state["NASA_FIRMS_MAP_KEY"] = custom_key_input
        st.success("Session MAP KEY registered.")

    if st.button("Test Live FIRMS API Connection"):
        test_key = custom_key_input or api_key or os.getenv("NASA_FIRMS_MAP_KEY")
        if not test_key:
            st.warning("Please supply a valid NASA FIRMS Map Key above before initiating test.")
        else:
            with st.spinner("Connecting to NASA FIRMS modaps.eosdis.nasa.gov..."):
                try:
                    client = FIRMSClient(api_key=test_key)
                    # Query 1-day VIIRS over Morocco-Rif
                    live_df = client.fetch_area_csv(34.5, 36.5, -6.5, -2.0, collection="VIIRS_SNPP_NRT", days=1)
                    st.success(f"Connection verified! NASA FIRMS returned {len(live_df)} live fire hotspots.")
                    if not live_df.empty:
                        st.dataframe(live_df.head(10), use_container_width=True)
                except Exception as exc:
                    st.error(f"Live FIRMS request failed: {exc}")


def render_settings_page(lang: str) -> None:
    """Render Settings and Application Preferences."""
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #F1F5F9; font-size: 1.25rem;">Settings & Geospatial Parameters</h3>
            <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px;">
                Configure default geographic bounding boxes, language localization, and spatial thresholds.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h4 style='color: #F1F5F9; font-size: 1rem;'>System Configuration</h4>", unsafe_allow_html=True)
        st.json({
            "Application": "PLEIADES Wildfire Intelligence Platform",
            "Challenge": "NASA Space Apps Challenge",
            "Framework": "Streamlit with Leaflet / Folium & Plotly",
            "Local First Architecture": True,
            "Active Language": lang,
            "Environment Status": "Operational",
        })

    with col2:
        st.markdown("<h4 style='color: #F1F5F9; font-size: 1rem;'>Default Detection Thresholds</h4>", unsafe_allow_html=True)
        st.write("Confidence Classification Rules:")
        st.markdown("- **Critical:** Confidence ≥ 85% AND FRP ≥ 75 MW")
        st.markdown("- **High:** Confidence ≥ 75% OR FRP ≥ 45 MW")
        st.markdown("- **Moderate:** Confidence ≥ 50% OR FRP ≥ 20 MW")
        st.markdown("- **Low:** Confidence < 50%")


def render_modern_dashboard(all_data: pd.DataFrame, lang: str = "en") -> None:
    """Master presentation orchestrator adhering to all PLEIADES requirements."""
    apply_pleiades_theme()

    # Determine data source mode
    is_sample_data = st.session_state.get("is_sample_data", False)
    data_source_mode = st.session_state.get("data_source_mode", "Sample Reference Testbed" if is_sample_data else "Active Telemetry")
    api_key = st.session_state.get("NASA_FIRMS_MAP_KEY", os.getenv("NASA_FIRMS_MAP_KEY"))

    # Navigation in sidebar
    nav_page = render_sidebar_navigation()

    # Sidebar Filters
    filtered_df, filter_meta = render_sidebar_filters(all_data, current_region=st.session_state.get("selected_region", "Morocco-Rif"))
    region_name = filter_meta["region"]
    st.session_state["selected_region"] = region_name

    # Sidebar Live Fetch Action if API key available
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #38BDF8; margin-bottom: 8px;">
            Satellite Stream Sync
        </div>
        """,
        unsafe_allow_html=True,
    )

    if api_key:
        if st.sidebar.button("🛰️ Fetch Live NASA FIRMS Data", type="primary", use_container_width=True):
            with st.spinner("Fetching live satellite observations from NASA FIRMS..."):
                try:
                    client = FIRMSClient(api_key=api_key)
                    min_lat, min_lon, max_lat, max_lon = filter_meta["bbox"]
                    live_df = client.fetch_area_csv(
                        lat_min=min(min_lat, max_lat),
                        lat_max=max(min_lat, max_lat),
                        lon_min=min(min_lon, max_lon),
                        lon_max=max(min_lon, max_lon),
                        collection="VIIRS_SNPP_NRT",
                        days=1,
                    )
                    if not live_df.empty:
                        st.session_state["custom_data"] = live_df
                        st.session_state["data_source_mode"] = "NASA FIRMS API (Live)"
                        st.session_state["is_sample_data"] = False
                        st.session_state["last_refresh_time"] = pd.Timestamp.now().strftime("%H:%M:%S UTC")
                        st.sidebar.success(f"Received {len(live_df)} live observations!")
                        st.rerun()
                    else:
                        st.sidebar.warning("NASA FIRMS returned 0 hotspots for this bounding box in the last 24h.")
                except Exception as exc:
                    st.sidebar.error(f"Live request failed: {exc}")
    else:
        st.sidebar.caption("💡 Set NASA_FIRMS_MAP_KEY to stream live data.")

    # Replay engine quick link
    if st.sidebar.button("⏱️ Spatiotemporal Replay Engine", use_container_width=True):
        st.session_state["current_nav_key"] = "replay"
        st.rerun()

    # Calculate active alerts count
    alerts_count = int((pd.to_numeric(filtered_df.get("confidence", 0), errors="coerce") >= 80).sum()) if not filtered_df.empty else 0

    # Header Bar
    page_title_map = {
        "overview": "Overview Dashboard",
        "live_map": "Geospatial Map",
        "detections": "Satellite Telemetry",
        "data_explorer": "Data Explorer & Ingestion",
        "analytics": "Scientific Analytics",
        "alerts": "Threat Alerts & Sensors",
        "data_sources": "NASA FIRMS Sources",
        "settings": "Settings & Parameters",
        "replay": "Spatiotemporal Replay",
    }
    render_application_header(
        page_title=page_title_map.get(nav_page, "Dashboard"),
        data_source_mode=data_source_mode,
        last_refresh_time=st.session_state.get("last_refresh_time", "Recent"),
        alerts_count=alerts_count,
        lang=lang,
    )

    # Route views
    if nav_page == "overview":
        render_overview_page(filtered_df, all_data, region_name, is_sample_data)
    elif nav_page == "live_map":
        render_live_map_page(filtered_df, region_name)
    elif nav_page == "detections":
        render_detections_page(filtered_df)
    elif nav_page == "data_explorer":
        render_data_explorer_page()
    elif nav_page == "analytics":
        render_analytics_panel(filtered_df)
    elif nav_page == "alerts":
        render_alerts_panel(filtered_df)
    elif nav_page == "data_sources":
        render_data_sources_page(api_key)
    elif nav_page == "settings":
        render_settings_page(lang)
    elif nav_page == "replay":
        render_replay_view(filtered_df)
    else:
        render_overview_page(filtered_df, all_data, region_name, is_sample_data)
