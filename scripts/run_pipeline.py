from __future__ import annotations

from pathlib import Path

from src.ingest import normalize_firms_dataset
from src.harmonization import spatial_temporal_merge
from src.iot_simulation import IoTStation, simulate_lora_alerts
from src.ml_model import train_risk_model


if __name__ == "__main__":
    csv_files = list(Path("data/raw").glob("**/*.csv"))
    if not csv_files:
        print("No raw FIRMS CSV files found; pipeline is running in synthetic demonstration mode.")
        synthetic = [
            {"latitude": 35.1, "longitude": -5.1, "timestamp": "2024-01-01 00:00:00", "evidence_score": 0.8, "satellite": "VIIRS", "confidence": 80, "frp": 30},
            {"latitude": 35.15, "longitude": -5.12, "timestamp": "2024-01-01 00:30:00", "evidence_score": 0.9, "satellite": "MODIS", "confidence": 85, "frp": 35},
        ]
        import pandas as pd
        pd.DataFrame(synthetic).to_csv("data/processed/satellite/demo_fires.csv", index=False)
        df = pd.read_csv("data/processed/satellite/demo_fires.csv")
    else:
        df = normalize_firms_dataset(csv_files)
    harmonized = spatial_temporal_merge(df)
    sensors = [IoTStation("RIF-A", 35.12, -5.11, 12.0, status="available")]
    alerts = simulate_lora_alerts(harmonized, sensors)
    try:
        train_risk_model(harmonized)
        print("Pipeline stages completed with model training enabled.")
    except ValueError:
        print("Pipeline completed in empty-data mode; model training skipped due to insufficient labelled data.")
    print(f"Harmonized events: {len(harmonized)}; alerts: {len(alerts)}")
