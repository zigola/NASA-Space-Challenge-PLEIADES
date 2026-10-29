from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from src.iot_simulation import IoTStation, simulate_lora_alerts


def load_sensor_stations() -> list[IoTStation]:
    sensor_path = Path(__file__).resolve().parent.parent / "data" / "iot" / "sensors.json"
    if sensor_path.exists():
        try:
            with sensor_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return [
                IoTStation(
                    id=s.get("id", "UNKNOWN"),
                    latitude=float(s.get("latitude", 0.0)),
                    longitude=float(s.get("longitude", 0.0)),
                    coverage_km=float(s.get("coverage_km", 10.0)),
                    status=s.get("status", "available"),
                )
                for s in data
            ]
        except Exception:
            pass

    return [
        IoTStation(id="RIF-A-CHEFCHAOUEN", latitude=35.18, longitude=-5.26, coverage_km=15.0, status="available"),
        IoTStation(id="RIF-B-TETOUAN", latitude=35.57, longitude=-5.37, coverage_km=12.0, status="available"),
        IoTStation(id="ATLAS-C-IFRANE", latitude=33.52, longitude=-5.11, coverage_km=20.0, status="available"),
    ]


def render_alerts_panel(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 style="margin: 0; color: #F1F5F9; font-size: 1.25rem;">Wildfire Threat Alerts & Ground Sensor Telemetry</h3>
            <div style="color: #9FB0C5; font-size: 0.85rem; margin-top: 4px;">
                Automated risk classification and cross-correlation between NASA FIRMS satellite hotspots and IoT early-warning field stations.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("No active satellite fire detections to evaluate for ground alerts.")
        return

    # Derive high-priority alerts
    alerts_df = df.copy()
    conf_series = pd.to_numeric(alerts_df.get("confidence", 50), errors="coerce").fillna(50)
    frp_series = pd.to_numeric(alerts_df.get("frp", 0), errors="coerce").fillna(0)

    # Calculate alert level
    def _calculate_severity(row: pd.Series) -> str:
        conf = float(row.get("confidence", 50))
        frp = float(row.get("frp", 0))
        if conf >= 85 and frp >= 75:
            return "CRITICAL"
        if conf >= 75 or frp >= 45:
            return "HIGH"
        if conf >= 50 or frp >= 20:
            return "MODERATE"
        return "LOW"

    alerts_df["severity"] = alerts_df.apply(_calculate_severity, axis=1)

    crit_count = (alerts_df["severity"] == "CRITICAL").sum()
    high_count = (alerts_df["severity"] == "HIGH").sum()
    mod_count = (alerts_df["severity"] == "MODERATE").sum()
    low_count = (alerts_df["severity"] == "LOW").sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Critical Threat (Tier 1)", f"{crit_count:,}")
    col2.metric("High Alert (Tier 2)", f"{high_count:,}")
    col3.metric("Moderate Watch", f"{mod_count:,}")
    col4.metric("Low Confidence", f"{low_count:,}")

    # Top critical fire incidents table
    st.markdown("<h4 style='color: #F1F5F9; margin-top: 1.2rem; font-size: 1rem;'>Active Fire Threat Matrix</h4>", unsafe_allow_html=True)
    display_cols = [c for c in ["severity", "satellite", "instrument", "latitude", "longitude", "confidence", "frp", "acq_date", "acq_time", "daynight"] if c in alerts_df.columns]
    sorted_alerts = alerts_df.sort_values(by=["frp", "confidence"], ascending=[False, False])[display_cols].reset_index(drop=True)
    st.dataframe(sorted_alerts.head(30), use_container_width=True)

    # IoT Sensors section
    st.markdown("---")
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <h4 style="margin: 0; color: #F1F5F9; font-size: 1rem;">📡 LoRa Ground Sensor Network Corroboration</h4>
                <div style="color: #9FB0C5; font-size: 0.8rem;">Field telemetry stations listening for RF smoke, temperature, and atmospheric ionization spikes within radar perimeter.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stations = load_sensor_stations()
    station_rows = []
    for s in stations:
        station_rows.append({
            "Station ID": s.id,
            "Coordinates": f"{s.latitude:.3f}°N, {s.longitude:.3f}°E",
            "Radar Perimeter": f"{s.coverage_km} km",
            "Hardware Status": s.status.upper(),
        })
    st.table(pd.DataFrame(station_rows))

    if st.button("Trigger LoRa Field Proximity Analysis", type="primary"):
        with st.spinner("Calculating spatial distance matrices and LoRa alerts..."):
            sensor_alerts = simulate_lora_alerts(alerts_df, stations=stations)
            if sensor_alerts.empty:
                st.info("No fire hotspots currently fall within the immediate perimeter of registered ground stations.")
            else:
                st.success(f"Matched {len(sensor_alerts)} satellite detections within ground station coverage perimeters!")
                st.dataframe(sensor_alerts, use_container_width=True)


def render_alerts(alerts: pd.DataFrame) -> None:
    """Backward-compatible entry point."""
    render_alerts_panel(alerts)
