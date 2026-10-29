from __future__ import annotations

import pandas as pd


def validate_fire_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply basic validation for latitude, longitude, and timestamp columns."""
    if df.empty:
        return df.copy()
    validated = df.copy()
    validated["latitude"] = pd.to_numeric(validated.get("latitude", 0), errors="coerce")
    validated["longitude"] = pd.to_numeric(validated.get("longitude", 0), errors="coerce")
    validated["timestamp"] = pd.to_datetime(validated.get("timestamp", pd.NaT), errors="coerce")
    validated = validated.loc[
        validated["latitude"].between(-90, 90)
        & validated["longitude"].between(-180, 180)
        & validated["timestamp"].notna()
    ].copy()
    return validated
