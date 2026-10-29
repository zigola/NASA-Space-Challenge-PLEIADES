from __future__ import annotations

REGIONS = {
    "Morocco-Rif": {
        "bbox": {"min_lat": 34.5, "min_lon": -6.0, "max_lat": 36.5, "max_lon": -2.0},
        "country": "Morocco",
        "region": "Rif",
    },
    "Morocco-Atlas": {
        "bbox": {"min_lat": 30.0, "min_lon": -10.0, "max_lat": 34.5, "max_lon": -4.0},
        "country": "Morocco",
        "region": "Atlas",
    },
    "Global": {
        "bbox": {"min_lat": -90.0, "min_lon": -180.0, "max_lat": 90.0, "max_lon": 180.0},
        "country": "Global",
        "region": "World",
    },
}
