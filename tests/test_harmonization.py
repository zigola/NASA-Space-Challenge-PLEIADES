import pandas as pd

from src.harmonization import spatial_temporal_merge


def test_spatial_temporal_merge_groups_nearby_events():
    df = pd.DataFrame(
        {
            "latitude": [35.10, 35.11, 40.0],
            "longitude": [-5.10, -5.11, 10.0],
            "timestamp": pd.to_datetime([
                "2024-01-01 10:00:00",
                "2024-01-01 10:30:00",
                "2024-01-01 12:00:00",
            ]),
            "frp": [25, 30, 50],
            "satellite": ["VIIRS", "MODIS", "VIIRS"],
        }
    )

    result = spatial_temporal_merge(df, max_distance_km=3.0, max_time_hours=2)

    assert len(result) == 2
    assert result["evidence_score"].ge(0).all()
    assert result["count"].ge(1).all()
