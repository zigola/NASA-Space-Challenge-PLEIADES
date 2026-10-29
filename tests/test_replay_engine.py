import pandas as pd

from src.replay_engine import build_replay_index, generate_replay_window


def test_replay_engine_builds_window():
    records = pd.DataFrame(
        {
            "timestamp": pd.to_datetime([
                "2024-01-01 10:00:00",
                "2024-01-01 11:00:00",
                "2024-01-01 12:00:00",
            ]),
            "latitude": [35.1, 35.2, 35.3],
            "longitude": [-5.1, -5.2, -5.3],
            "evidence_score": [10, 20, 30],
        }
    )

    index = build_replay_index(records)
    window = generate_replay_window(index, start_idx=0, end_idx=2, speed=2.0)

    assert len(index) == 3
    assert len(window) == 3
    assert window[0]["timestamp"] == records.iloc[0]["timestamp"]
