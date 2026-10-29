from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.spatial.distance import haversine_km


@dataclass
class FireCluster:
    cluster_id: int
    latitude: float
    longitude: float
    timestamp: pd.Timestamp
    evidence_score: float
    count: int


def spatial_temporal_merge(df: pd.DataFrame, max_distance_km: float = 2.5, max_time_hours: float = 12.0) -> pd.DataFrame:
    """Group nearby observations into harmonized fire events using a simple spatiotemporal clustering rule."""
    if df.empty:
        return pd.DataFrame(columns=["latitude", "longitude", "timestamp", "evidence_score", "count", "sources"])

    data = df[["latitude", "longitude", "timestamp"]].dropna().copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data = data.dropna(subset=["timestamp"]).copy()
    if data.empty:
        return pd.DataFrame(columns=["latitude", "longitude", "timestamp", "evidence_score", "count", "sources"])

    visited = set()
    clusters = []
    for idx in range(len(data)):
        if idx in visited:
            continue
        group = [idx]
        visited.add(idx)
        for other in range(len(data)):
            if other in visited or other == idx:
                continue
            point_a = data.iloc[idx]
            point_b = data.iloc[other]
            dist = haversine_km(point_a["latitude"], point_a["longitude"], point_b["latitude"], point_b["longitude"])
            dt = abs((point_b["timestamp"] - point_a["timestamp"]).total_seconds() / 3600.0)
            if dist <= max_distance_km and dt <= max_time_hours:
                group.append(other)
                visited.add(other)
        group_df = data.iloc[group].copy()
        sources = df.iloc[group].get("satellite", pd.Series(["UNKNOWN"] * len(group))).tolist() if len(group) > 0 else []
        evidence = 1.2 * float(df.iloc[group]["frp"].sum()) if "frp" in df.columns else float(len(group))
        evidence += 0.5 * float(df.iloc[group].get("confidence", 0).sum()) if "confidence" in df.columns else 0.0
        evidence += 3.0 * len(group)
        clusters.append(
            {
                "latitude": float(group_df["latitude"].mean()),
                "longitude": float(group_df["longitude"].mean()),
                "timestamp": group_df["timestamp"].median(),
                "evidence_score": float(evidence),
                "count": int(len(group_df)),
                "sources": sorted(set(sources)),
            }
        )

    result = pd.DataFrame(clusters)
    if result.empty:
        return pd.DataFrame(columns=["latitude", "longitude", "timestamp", "evidence_score", "count", "sources"])
    return result.sort_values("timestamp").reset_index(drop=True)


if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "latitude": [35.1, 35.11, 40.0],
            "longitude": [-5.1, -5.11, 10.0],
            "timestamp": pd.to_datetime(["2024-01-01 10:00:00", "2024-01-01 10:30:00", "2024-01-01 12:00:00"]),
            "frp": [25, 30, 50],
            "confidence": [80, 85, 60],
            "satellite": ["VIIRS", "MODIS", "VIIRS"],
        }
    )
    print(spatial_temporal_merge(sample, max_distance_km=3.0, max_time_hours=2.0))
