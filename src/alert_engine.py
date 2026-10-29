from __future__ import annotations

import pandas as pd


def build_alert_summary(alerts: pd.DataFrame) -> dict:
    if alerts.empty:
        return {"total": 0, "by_level": {}}
    return {
        "total": int(len(alerts)),
        "by_level": alerts["alert_level"].value_counts().to_dict() if "alert_level" in alerts.columns else {},
    }
