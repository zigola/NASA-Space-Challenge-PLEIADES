from src.risk_assessment import classify_risk


def test_classify_risk_thresholds():
    assert classify_risk(0.2) == "LOW"
    assert classify_risk(0.4) == "MODERATE"
    assert classify_risk(0.7) == "HIGH"
    assert classify_risk(0.95) == "CRITICAL"
