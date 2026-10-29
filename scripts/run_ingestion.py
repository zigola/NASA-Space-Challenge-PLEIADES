from __future__ import annotations

from pathlib import Path

from src.ingest import normalize_firms_dataset


if __name__ == "__main__":
    csv_files = list(Path("data/raw").glob("**/*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files were found in data/raw.")
    result = normalize_firms_dataset(csv_files, output_dir="data/processed/satellite")
    print(f"Normalized {len(result)} data points.")
