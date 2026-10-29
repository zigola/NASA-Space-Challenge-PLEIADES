from __future__ import annotations

from pathlib import Path

from src.nasa_firms.client import FIRMSClient


class MODISClient(FIRMSClient):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        super().__init__(api_key=api_key, base_url=base_url)

    def list_local_files(self, directory: str | Path):
        return super().list_local_files(directory)
