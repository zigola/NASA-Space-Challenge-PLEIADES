import pandas as pd

from src.ml_model import build_risk_dataset, train_risk_model


def test_train_risk_model_handles_synthetic_data():
    df = pd.DataFrame(
        {
            "latitude": [35.1, 35.2, 35.3, 35.4],
            "longitude": [-5.1, -5.2, -5.0, -5.4],
            "timestamp": pd.to_datetime([
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
            ]),
            "evidence_score": [45, 90, 160, 200],
            "count": [2, 4, 7, 9],
        }
    )

    prepared = build_risk_dataset(df)
    model, metrics = train_risk_model(df)

    assert "risk_label" in prepared.columns
    assert model is not None
    assert "macro_avg" in metrics["classification_report"]
