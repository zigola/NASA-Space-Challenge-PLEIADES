from __future__ import annotations


def classify_risk(score: float) -> str:
    """Map a numeric risk score to LOW, MODERATE, HIGH, or CRITICAL."""
    if score >= 0.9:
        return "CRITICAL"
    if score >= 0.7:
        return "HIGH"
    if score >= 0.4:
        return "MODERATE"
    return "LOW"
