from __future__ import annotations

from typing import Iterable, Tuple


BBox = Tuple[float, float, float, float]


def create_bbox(min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> BBox:
    return (float(min_lat), float(min_lon), float(max_lat), float(max_lon))


def _matches_bbox(lat: float, lon: float, bbox: BBox) -> bool:
    min_a, min_b, max_a, max_b = bbox
    return min_a <= lat <= max_a and min_b <= lon <= max_b


def in_bbox(lat: float, lon: float, bbox: BBox) -> bool:
    primary = bbox
    if _matches_bbox(lat, lon, primary):
        return True

    alt = (bbox[1], bbox[0], bbox[3], bbox[2])
    if _matches_bbox(lat, lon, alt):
        return True

    return False


def filter_by_bbox(rows: Iterable[dict], bbox: BBox) -> list[dict]:
    return [row for row in rows if in_bbox(float(row["latitude"]), float(row["longitude"]), bbox)]
