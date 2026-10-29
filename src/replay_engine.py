from __future__ import annotations

import pandas as pd


def build_replay_index(records: pd.DataFrame) -> pd.DataFrame:
    if records.empty:
        return records.copy()
    replay = records.copy()
    replay["timestamp"] = pd.to_datetime(replay["timestamp"], errors="coerce")
    return replay.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)


def generate_replay_window(index: pd.DataFrame, start_idx: int = 0, end_idx: int | None = None, speed: float = 1.0) -> list[dict]:
    if index.empty:
        return []

    if end_idx is None:
        end = len(index)
    else:
        end = min(max(end_idx, start_idx), len(index) - 1)
        end += 1

    window = index.iloc[start_idx:end].copy()
    window["playback_speed"] = speed
    records = window.to_dict(orient="records")
    return records
