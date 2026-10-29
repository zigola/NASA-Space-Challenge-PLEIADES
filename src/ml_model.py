from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


def build_risk_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Create a basic daily risk classification dataset from fire detections."""
    if df.empty:
        return df.copy()

    features = df.copy()
    features["day_of_year"] = pd.to_datetime(features["timestamp"], errors="coerce").dt.day_of_year
    features["month"] = pd.to_datetime(features["timestamp"], errors="coerce").dt.month
    features["risk_label"] = "LOW"
    features.loc[features.get("evidence_score", 0) >= 0.7, "risk_label"] = "HIGH"
    features.loc[features.get("evidence_score", 0) >= 0.9, "risk_label"] = "CRITICAL"
    features.loc[features.get("count", 0) >= 5, "risk_label"] = "MODERATE"
    features["risk_label"] = features["risk_label"].str.upper()
    return features


def _normalize_report_keys(report):
    if isinstance(report, dict):
        normalized = {}
        for key, value in report.items():
            if isinstance(key, str):
                normalized_key = key.strip().replace(" ", "_")
                normalized[normalized_key] = _normalize_report_keys(value)
            else:
                normalized[key] = _normalize_report_keys(value)
        return normalized
    return report


def train_risk_model(df: pd.DataFrame):
    """Train a small decision-tree model for risk classification and return model plus metrics."""
    prepared = build_risk_dataset(df)
    if prepared.empty:
        raise ValueError("No data available to train the risk model.")

    model_columns = ["latitude", "longitude", "day_of_year", "month", "evidence_score", "count"]
    feature_frame = prepared[model_columns].fillna(0)
    target = prepared["risk_label"]

    X_train, X_test, y_train, y_test = train_test_split(feature_frame, target, test_size=0.25, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    report = classification_report(y_test, preds, output_dict=True)
    return model, {"classification_report": _normalize_report_keys(report), "n_samples": len(prepared)}


if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "latitude": [35.1, 35.2, 35.3, 35.4],
            "longitude": [-5.1, -5.2, -5.0, -5.4],
            "timestamp": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
            "evidence_score": [0.2, 0.6, 0.8, 0.95],
            "count": [2, 4, 7, 9],
        }
    )
    model, metrics = train_risk_model(sample)
    print(model.predict([[35.2, -5.1, 20, 1, 0.75, 7]]))
    print(metrics)
