from pathlib import Path

import pandas as pd

from src.ingest import normalize_firms_dataset


def test_normalize_firms_dataset_filters_and_deduplicates(tmp_path):
    csv_path = tmp_path / "firms.csv"
    df = pd.DataFrame(
        [
            {
                "latitude": 35.1,
                "longitude": -5.1,
                "bright_t31": 330,
                "scan": 1,
                "track": 1,
                "acq_date": "2024-01-01",
                "acq_time": "1230",
                "satellite": "N",
                "instrument": "VIIRS",
                "confidence": 90,
                "version": "2.0",
                "frp": 25,
                "daynight": "D",
            },
            {
                "latitude": 35.1,
                "longitude": -5.1,
                "bright_t31": 330,
                "scan": 1,
                "track": 1,
                "acq_date": "2024-01-01",
                "acq_time": "1230",
                "satellite": "N",
                "instrument": "VIIRS",
                "confidence": 90,
                "version": "2.0",
                "frp": 25,
                "daynight": "D",
            },
            {
                "latitude": 12.0,
                "longitude": -8.0,
                "bright_t31": 300,
                "scan": 1,
                "track": 1,
                "acq_date": "2024-01-02",
                "acq_time": "0100",
                "satellite": "A",
                "instrument": "MODIS",
                "confidence": 50,
                "version": "1.0",
                "frp": 15,
                "daynight": "N",
            },
        ]
    )
    df.to_csv(csv_path, index=False)

    result = normalize_firms_dataset([csv_path], bbox=(-10.0, 30.0, 0.0, 40.0))

    assert len(result) == 2
    assert {"latitude", "longitude"}.issubset(result.columns)
    assert result["instrument"].notna().all()
