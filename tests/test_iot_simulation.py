import pandas as pd

from src.iot_simulation import IoTStation, simulate_lora_alerts


def test_simulate_lora_alerts_matches_nearby_sensors():
    fires = pd.DataFrame(
        {
            "latitude": [35.14],
            "longitude": [-5.12],
            "timestamp": [pd.Timestamp("2024-01-01 12:00:00")],
            "evidence_score": [90],
            "is_simulated": [True],
        }
    )
    sensors = [
        IoTStation("S1", 35.13, -5.11, 10.0, status="available"),
        IoTStation("S2", 35.70, -5.70, 10.0, status="offline"),
    ]

    result = simulate_lora_alerts(fires, sensors)

    assert len(result) == 1
    assert result.iloc[0]["station_id"] == "S1"
    assert result.iloc[0]["is_simulated"] is True
