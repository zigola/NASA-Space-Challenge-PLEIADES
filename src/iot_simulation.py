from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from src.spatial.distance import haversine_km


@dataclass
class IoTStation:
    id: str
    latitude: float
    longitude: float
    coverage_km: float = 10.0
    status: str = "available"
    temperature_c: float = 25.0
    smoke_ppm: float = 0.0
    humidity_pct: float = 50.0
    is_simulated: bool = True


def simulate_lora_alerts(fire_events: pd.DataFrame, stations: Iterable[IoTStation]) -> pd.DataFrame:
    """Validate fire events against nearby IoT stations and generate synthetic alerts."""
    stations = list(stations)
    if fire_events.empty or not stations:
        return pd.DataFrame(columns=["fire_latitude", "fire_longitude", "station_id", "distance_km", "alert_level", "timestamp", "is_simulated"])

    rows = []
    for _, event in fire_events.iterrows():
        for station in stations:
            if station.status != "available":
                continue
            dist = haversine_km(float(event["latitude"]), float(event["longitude"]), station.latitude, station.longitude)
            if dist <= station.coverage_km:
                alert = "LOW"
                if float(event.get("evidence_score", 0)) >= 80:
                    alert = "HIGH"
                elif float(event.get("evidence_score", 0)) >= 30:
                    alert = "MEDIUM"
                rows.append(
                    {
                        "fire_latitude": float(event["latitude"]),
                        "fire_longitude": float(event["longitude"]),
                        "station_id": station.id,
                        "distance_km": dist,
                        "alert_level": alert,
                        "timestamp": event.get("timestamp", pd.Timestamp.now("UTC")),
                        "is_simulated": bool(True),
                    }
                )
    result = pd.DataFrame(rows)
    if not result.empty:
        result["is_simulated"] = result["is_simulated"].map(bool).astype(object)
    return result


if __name__ == "__main__":
    fires = pd.DataFrame(
        {
            "latitude": [35.15],
            "longitude": [-5.1],
            "timestamp": [pd.Timestamp("2024-01-01")],
            "evidence_score": [90],
            "is_simulated": [True],
        }
    )
    stations = [
        IoTStation("S1", 35.12, -5.08, coverage_km=12, status="available"),
        IoTStation("S2", 35.50, -5.60, coverage_km=8, status="offline"),
    ]
    print(simulate_lora_alerts(fires, stations))
