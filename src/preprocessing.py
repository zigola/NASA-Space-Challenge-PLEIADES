from __future__ import annotations

import pandas as pd


def clean_fire_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize a raw fire dataset."""
    if df.empty:
        return df.copy()
    cleaned = df.copy()
    cleaned = cleaned.dropna(subset=["latitude", "longitude"]).copy()
    cleaned["latitude"] = pd.to_numeric(cleaned["latitude"], errors="coerce")
    cleaned["longitude"] = pd.to_numeric(cleaned["longitude"], errors="coerce")
    cleaned["confidence"] = pd.to_numeric(cleaned.get("confidence", 0), errors="coerce").fillna(0)
    cleaned["frp"] = pd.to_numeric(cleaned.get("frp", 0), errors="coerce").fillna(0)
    cleaned["timestamp"] = pd.to_datetime(cleaned.get("timestamp", cleaned.get("acq_date")), errors="coerce")
    cleaned = cleaned.dropna(subset=["timestamp"]).copy()
    return cleaned
