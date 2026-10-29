from __future__ import annotations

import pandas as pd
import folium

from dashboard.maps import create_folium_map
from src.ingest import get_reference_dataset


def test_create_folium_map_with_data():
    df = get_reference_dataset()
    m = create_folium_map(df, cluster_markers=True)
    assert isinstance(m, folium.Map)
    # Check that children include layer controls and feature groups
    child_names = [child.__class__.__name__ for child in m._children.values()]
    assert "FeatureGroup" in child_names
    assert "LayerControl" in child_names


def test_create_folium_map_empty():
    empty_df = pd.DataFrame(columns=["latitude", "longitude", "instrument"])
    m = create_folium_map(empty_df)
    assert isinstance(m, folium.Map)


def test_create_folium_map_unclustered():
    df = get_reference_dataset().head(5)
    m = create_folium_map(df, cluster_markers=False)
    assert isinstance(m, folium.Map)
