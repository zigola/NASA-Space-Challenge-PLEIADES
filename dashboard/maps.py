from __future__ import annotations

import folium
from folium.plugins import Fullscreen, MarkerCluster
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


def render_map_legend() -> None:
    """Render an aesthetic geospatial legend adhering to the PLEIADES design system."""
    st.markdown(
        """
        <div style="
            background: rgba(18, 34, 56, 0.85);
            border: 1px solid #25374C;
            border-radius: 10px;
            padding: 10px 16px;
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            font-size: 0.82rem;
            color: #9FB0C5;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #EF4444; border: 2px solid #FCA5A5; box-shadow: 0 0 8px rgba(239, 68, 68, 0.8);"></span>
                <span style="color: #F1F5F9; font-weight: 600;">VIIRS</span>
                <span>(375m resolution · Suomi-NPP / NOAA-20 / NOAA-21)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #F59E0B; border: 2px solid #FDE68A; box-shadow: 0 0 8px rgba(245, 158, 11, 0.8);"></span>
                <span style="color: #F1F5F9; font-weight: 600;">MODIS</span>
                <span>(1km resolution · Terra / Aqua)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 14px; height: 14px; border-radius: 50%; border: 2px dashed #FF7A45;"></span>
                <span>Marker Radius ∝ FRP (Megawatts)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="color: #38BDF8; font-weight: 600;">Confidence:</span>
                <span style="color: #34D399;">High (≥80%)</span> ·
                <span style="color: #FBBF24;">Med (50-79%)</span> ·
                <span style="color: #94A3B8;">Low (&lt;50%)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_folium_map(
    df: pd.DataFrame,
    cluster_markers: bool = True,
    basemap: str = "CartoDB dark_matter",
) -> folium.Map:
    """Construct an interactive Folium map populated with FIRMS hotspot observations."""
    if df.empty or "latitude" not in df.columns or "longitude" not in df.columns:
        # Default center on Mediterranean/Morocco
        center_lat, center_lon = 35.0, -5.0
        zoom_start = 6
    else:
        valid_geo = df.dropna(subset=["latitude", "longitude"])
        if valid_geo.empty:
            center_lat, center_lon = 35.0, -5.0
            zoom_start = 6
        else:
            center_lat = float(valid_geo["latitude"].mean())
            center_lon = float(valid_geo["longitude"].mean())
            zoom_start = 7

    # Create the base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="Dark Matter (Default)",
        control_scale=True,
        prefer_canvas=True,
    )

    # Add alternative basemaps with attributions
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
        name="Esri Satellite Imagery",
    ).add_to(m)

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap",
    ).add_to(m)

    Fullscreen(position="topright", force_separate_button=True).add_to(m)

    if df.empty:
        folium.LayerControl(position="topright").add_to(m)
        return m

    valid_df = df.dropna(subset=["latitude", "longitude"]).copy()
    if valid_df.empty:
        folium.LayerControl(position="topright").add_to(m)
        return m

    # Feature groups for toggleable layers
    viirs_layer = folium.FeatureGroup(name="VIIRS Observations", show=True)
    modis_layer = folium.FeatureGroup(name="MODIS Observations", show=True)

    if cluster_markers:
        viirs_cluster = MarkerCluster(name="VIIRS Clusters").add_to(viirs_layer)
        modis_cluster = MarkerCluster(name="MODIS Clusters").add_to(modis_layer)
    else:
        viirs_cluster = viirs_layer
        modis_cluster = modis_layer

    bounds_points = []

    for _, row in valid_df.iterrows():
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        bounds_points.append([lat, lon])

        instrument = str(row.get("instrument", "UNKNOWN")).upper()
        satellite = str(row.get("satellite", "UNKNOWN"))
        confidence = float(row.get("confidence", 50.0))
        frp = float(row.get("frp", 0.0))
        brightness = float(row.get("brightness", row.get("bright_t31", 300.0)))
        acq_date = str(row.get("acq_date", "N/A"))
        acq_time = str(row.get("acq_time", "N/A")).replace(".0", "").zfill(4)
        if len(acq_time) == 4:
            acq_time_fmt = f"{acq_time[:2]}:{acq_time[2:]} UTC"
        else:
            acq_time_fmt = acq_time

        daynight = str(row.get("daynight", "D")).upper()
        daynight_str = "Day" if daynight == "D" else "Night" if daynight == "N" else daynight
        scan = str(row.get("scan", "N/A"))
        track = str(row.get("track", "N/A"))

        # Determine styling by instrument and confidence
        is_viirs = "VIIRS" in instrument or satellite in {"Suomi-NPP", "NOAA-20", "NOAA-21", "N", "1", "2"}
        if is_viirs:
            color = "#EF4444"
            fill_color = "#DC2626"
            badge_bg = "rgba(239, 68, 68, 0.25)"
            badge_text = "#FCA5A5"
            resolution = "375m"
        else:
            color = "#F59E0B"
            fill_color = "#D97706"
            badge_bg = "rgba(245, 158, 11, 0.25)"
            badge_text = "#FDE68A"
            resolution = "1.0km"

        # Radius based on FRP
        if frp > 100:
            radius = 12
        elif frp > 50:
            radius = 9
        elif frp > 20:
            radius = 7
        else:
            radius = 5

        # Confidence color code
        if confidence >= 80:
            conf_color = "#34D399"
            conf_label = "High"
        elif confidence >= 50:
            conf_color = "#FBBF24"
            conf_label = "Moderate"
        else:
            conf_color = "#94A3B8"
            conf_label = "Low"

        # Professional scientific popup card
        popup_html = f"""
        <div style="
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            min-width: 260px;
            max-width: 300px;
            background: #0C1824;
            color: #F1F5F9;
            padding: 12px 14px;
            border-radius: 10px;
            border: 1px solid #25374C;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #25374C; padding-bottom: 6px;">
                <span style="font-weight: 700; font-size: 13px; color: #38BDF8; display: flex; align-items: center; gap: 4px;">
                    🔥 {instrument} Detection
                </span>
                <span style="font-size: 11px; font-weight: 600; background: {badge_bg}; color: {badge_text}; padding: 2px 7px; border-radius: 4px; border: 1px solid {color}44;">
                    {satellite} ({resolution})
                </span>
            </div>
            <table style="width: 100%; font-size: 11.5px; border-collapse: collapse; line-height: 1.5;">
                <tr>
                    <td style="color: #9FB0C5; padding: 2px 0;">Coordinates:</td>
                    <td style="text-align: right; font-weight: 600; font-family: monospace; color: #F1F5F9;">{lat:.4f}°N, {lon:.4f}°E</td>
                </tr>
                <tr>
                    <td style="color: #9FB0C5; padding: 2px 0;">Acquisition:</td>
                    <td style="text-align: right; color: #F1F5F9;">{acq_date} {acq_time_fmt}</td>
                </tr>
                <tr>
                    <td style="color: #9FB0C5; padding: 2px 0;">Confidence:</td>
                    <td style="text-align: right; font-weight: 700; color: {conf_color};">
                        {confidence:.0f}% <span style="font-size: 10px; font-weight: 400;">({conf_label})</span>
                    </td>
                </tr>
                <tr>
                    <td style="color: #9FB0C5; padding: 2px 0;">Radiative Power (FRP):</td>
                    <td style="text-align: right; font-weight: 700; color: #FF7A45;">{frp:.1f} MW</td>
                </tr>
                <tr>
                    <td style="color: #9FB0C5; padding: 2px 0;">Brightness Temp:</td>
                    <td style="text-align: right; color: #F1F5F9;">{brightness:.1f} K</td>
                </tr>
                <tr>
                    <td style="color: #9FB0C5; padding: 2px 0;">Observation:</td>
                    <td style="text-align: right; color: #F1F5F9;">{daynight_str} (Scan {scan} × {track} km)</td>
                </tr>
            </table>
        </div>
        """

        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            weight=2,
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.85,
            tooltip=f"{instrument} Hotspot: {lat:.3f}°N, {lon:.3f}°E | FRP: {frp:.1f} MW | Conf: {confidence:.0f}%",
            popup=folium.Popup(popup_html, max_width=320),
        )

        if is_viirs:
            marker.add_to(viirs_cluster)
        else:
            marker.add_to(modis_cluster)

    viirs_layer.add_to(m)
    modis_layer.add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    if bounds_points and len(bounds_points) > 1:
        lats = [p[0] for p in bounds_points]
        lons = [p[1] for p in bounds_points]
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=[20, 20])

    return m


def render_map(
    df: pd.DataFrame,
    height: int = 560,
    cluster_markers: bool = True,
    key: str = "polaris_fire_map",
) -> None:
    """Streamlit entry point for rendering the real interactive geospatial map."""
    if df.empty:
        st.markdown(
            """
            <div style="
                background: #122238;
                border: 1px dashed #25374C;
                border-radius: 12px;
                padding: 3rem 2rem;
                text-align: center;
                color: #9FB0C5;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛰️</div>
                <div style="font-weight: 600; font-size: 1.1rem; color: #F1F5F9; margin-bottom: 0.25rem;">
                    No Fire Hotspots in Current Selection
                </div>
                <div>Adjust your satellite filters, expand the observation date range, or select a different bounding box.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    col_ctrl1, col_ctrl2 = st.columns([3, 1])
    with col_ctrl1:
        st.caption(f"Visualizing {len(df):,} satellite hotspot observations · Click any marker for telemetry popup")
    with col_ctrl2:
        clustering = st.checkbox("Cluster markers", value=cluster_markers, key=f"{key}_clustering_cb")

    try:
        fmap = create_folium_map(df, cluster_markers=clustering)
        st_folium(fmap, width="100%", height=height, returned_objects=[])
        render_map_legend()
    except Exception as exc:
        st.warning(f"Interactive Folium rendering encountered an issue: {exc}. Displaying tabular fallback.")
        st.dataframe(df[["latitude", "longitude", "satellite", "instrument", "confidence", "frp"]].head(25), use_container_width=True)
