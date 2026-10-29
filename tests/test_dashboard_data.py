from __future__ import annotations

import io
from pathlib import Path
import pytest
import pandas as pd

from src.ingest import read_firms_file, get_reference_dataset, filter_bbox, DEFAULT_BBOX


def test_read_firms_file_csv_valid(tmp_path: Path):
    csv_file = tmp_path / "test_firms.csv"
    csv_file.write_text(
        "latitude,longitude,brightness,confidence,satellite,acq_date,acq_time,frp\n"
        "35.2,-5.4,340.5,95,N,2024-08-15,1342,65.2\n"
        "34.8,-4.9,320.0,75,T,2024-08-15,1130,28.0\n",
        encoding="utf-8",
    )
    df = read_firms_file(csv_file)
    assert len(df) == 2
    assert "instrument" in df.columns
    assert df.loc[df["satellite"] == "Suomi-NPP", "instrument"].iloc[0] == "VIIRS"
    assert df.loc[df["satellite"] == "Terra", "instrument"].iloc[0] == "MODIS"
    assert df["frp"].iloc[0] == 65.2
    assert df["is_valid"].all()


def test_read_firms_file_geojson_feature_collection(tmp_path: Path):
    geojson_file = tmp_path / "test_firms.geojson"
    geojson_file.write_text(
        """{
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-5.35, 35.24]},
                    "properties": {
                        "brightness": 344.2,
                        "satellite": "Suomi-NPP",
                        "confidence": 94,
                        "frp": 82.5
                    }
                }
            ]
        }""",
        encoding="utf-8",
    )
    df = read_firms_file(geojson_file)
    assert len(df) == 1
    assert df["latitude"].iloc[0] == 35.24
    assert df["longitude"].iloc[0] == -5.35
    assert df["instrument"].iloc[0] == "VIIRS"
    assert df["confidence"].iloc[0] == 94.0


def test_read_firms_file_json_array(tmp_path: Path):
    json_file = tmp_path / "test_firms.json"
    json_file.write_text(
        """[
            {"latitude": 35.1, "longitude": -5.1, "satellite": "A", "confidence": "high", "frp": 30.0}
        ]""",
        encoding="utf-8",
    )
    df = read_firms_file(json_file)
    assert len(df) == 1
    assert df["satellite"].iloc[0] == "Aqua"
    assert df["instrument"].iloc[0] == "MODIS"
    # Text confidence 'high' converted to 95.0
    assert df["confidence"].iloc[0] == 95.0


def test_read_firms_file_empty_raises(tmp_path: Path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        read_firms_file(empty_file)


def test_read_firms_file_missing_coords_raises(tmp_path: Path):
    bad_file = tmp_path / "bad.csv"
    bad_file.write_text("temperature,humidity\n25.0,60.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required FIRMS coordinates"):
        read_firms_file(bad_file)


def test_get_reference_dataset():
    ref_df = get_reference_dataset()
    assert not ref_df.empty
    assert len(ref_df) >= 5
    assert {"latitude", "longitude", "satellite", "instrument", "confidence", "frp"}.issubset(ref_df.columns)
    assert ref_df["instrument"].isin(["VIIRS", "MODIS"]).all()
