from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.harmonization import spatial_temporal_merge


if __name__ == "__main__":
    data_path = Path("data/processed/satellite/normalized_firms.csv")
    if not data_path.exists():
        raise FileNotFoundError(f"Missing ingestion output: {data_path}")
    df = pd.read_csv(data_path)
    harmonized = spatial_temporal_merge(df)
    out = Path("data/processed/harmonized")
    out.mkdir(parents=True, exist_ok=True)
    harmonized.to_csv(out / "master_fires_harmonized.csv", index=False)
    print(f"Saved {len(harmonized)} harmonized events.")
