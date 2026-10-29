from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FireObservation:
    """Canonical internal detection model for NASA FIRMS observations."""
    latitude: float
    longitude: float
    timestamp: str
    acquisition_date: str = ""
    acquisition_time: str = ""
    satellite: str = "UNKNOWN"
    instrument: str = "UNKNOWN"
    confidence: float = 0.0
    frp: float | None = None
    brightness: float | None = None
    brightness_temperature: float | None = None
    scan: float | None = None
    track: float | None = None
    daynight: str = "D"
    source_dataset: str = ""
    source_version: str = ""
    is_valid: bool = True
    source_metadata: dict[str, Any] = field(default_factory=dict)
