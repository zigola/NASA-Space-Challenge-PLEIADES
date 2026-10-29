from src.spatial.bounding_box import create_bbox, in_bbox
from src.spatial.distance import haversine_km


def test_bbox_helpers_and_distance():
    bbox = create_bbox(35.0, -6.0, 35.5, -5.0)
    assert in_bbox(35.2, -5.2, bbox) is True
    assert haversine_km(35.0, -5.0, 35.0, -5.1) > 0
