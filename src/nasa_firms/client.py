from __future__ import annotations

import io
import os
from pathlib import Path

import pandas as pd
import requests

from src.ingest import read_firms_csv


class FIRMSClient:
    """Helper client for NASA FIRMS CSV ingestion and optional API access."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("NASA_FIRMS_MAP_KEY")
        self.base_url = (base_url or "https://firms.modaps.eosdis.nasa.gov").rstrip("/")

    def read_csv(self, path: str | Path) -> pd.DataFrame:
        return pd.read_csv(path)

    def list_local_files(self, directory: str | Path) -> list[Path]:
        directory = Path(directory)
        if not directory.exists():
            return []
        return sorted(directory.glob("*.csv"))

    def fetch_area_csv(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        collection: str = "VIIRS_SNPP_NRT",
        days: int = 1,
        timeout: int = 30,
    ) -> pd.DataFrame:
        if not self.api_key:
            raise ValueError("NASA_FIRMS_MAP_KEY is not set. Configure the environment variable before calling the NASA FIRMS API.")
        if not 1 <= days <= 30:
            raise ValueError("The FIRMS API days parameter must be between 1 and 30.")

        url = (
            f"{self.base_url}/api/area/csv/{self.api_key}/{collection}/{days}/{lat_min}/{lon_min}/{lat_max}/{lon_max}"
        )
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ValueError(f"NASA FIRMS API request failed: {exc}") from exc

        content = response.text.strip()
        if not content or "error" in content.lower() or "not authorized" in content.lower():
            raise ValueError("NASA FIRMS API returned no data or rejected the supplied map key.")

        try:
            return read_firms_csv(io.StringIO(content))
        except ValueError as exc:
            raise ValueError(f"NASA FIRMS API response was not valid FIRMS CSV data: {exc}") from exc
