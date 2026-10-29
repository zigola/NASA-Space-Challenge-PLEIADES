from __future__ import annotations

from datetime import datetime


def as_utc_iso(value: datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.isoformat()
