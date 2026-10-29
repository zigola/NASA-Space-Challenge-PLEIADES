from __future__ import annotations

import pandas as pd

from src.ml_model import train_risk_model


if __name__ == "__main__":
    synthetic = pd.DataFrame(
        {
            "latitude": [35.1, 35.2, 35.3, 35.4],
            "longitude": [-5.1, -5.2, -5.0, -5.4],
            "timestamp": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
            "evidence_score": [0.2, 0.5, 0.8, 0.95],
            "count": [2, 4, 7, 9],
        }
    )
    model, metrics = train_risk_model(synthetic)
    print(model)
    print(metrics)
