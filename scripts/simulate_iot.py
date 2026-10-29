from __future__ import annotations

import pandas as pd

from src.iot_simulation import IoTStation, simulate_lora_alerts


if __name__ == "__main__":
    events = pd.DataFrame(
        {
            "latitude": [35.2],
            "longitude": [-5.1],
            "timestamp": [pd.Timestamp("2024-01-01 12:00:00")],
            "evidence_score": [90],
            "is_simulated": [True],
        }
    )
    sensors = [
        IoTStation("RIF-A", 35.21, -5.11, 12.0, status="available"),
        IoTStation("RIF-B", 35.7, -5.7, 8.0, status="offline"),
    ]
    alerts = simulate_lora_alerts(events, sensors)
    alerts.to_csv("data/iot/simulated_alerts.csv", index=False)
    print(f"Saved {len(alerts)} simulated alerts.")
