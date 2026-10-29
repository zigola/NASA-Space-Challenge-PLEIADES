from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.yaml"


def _coerce_scalar(value: str):
    value = value.strip()
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("\"") for item in value[1:-1].split(",") if item.strip()]
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value.strip("\"")


def _parse_simple_yaml(path: str | Path) -> dict:
    data: dict = {}
    stack: list[tuple[int, dict]] = [(-1, data)]
    pending_key = None

    with Path(path).open("r", encoding="utf-8") as handle:
        lines = [line.rstrip() for line in handle if line.strip() and not line.lstrip().startswith("#")]

    for raw_line in lines:
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        text = raw_line.strip()
        if text.startswith("-"):
            if pending_key is None:
                continue
            if not isinstance(stack[-1][1].get(pending_key), list):
                stack[-1][1][pending_key] = []
            stack[-1][1][pending_key].append(_coerce_scalar(text[1:].strip()))
            continue
        if ":" not in text:
            continue
        key, remainder = text.split(":", 1)
        key = key.strip()
        remainder = remainder.strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if remainder == "":
            new_dict: dict = {}
            current[key] = new_dict
            stack.append((indent, new_dict))
            pending_key = key
        else:
            current[key] = _coerce_scalar(remainder)
            pending_key = key

    return data


@dataclass
class AppSettings:
    default_region: str = "Morocco-Rif"
    bbox: dict = field(default_factory=lambda: {"min_lat": 30.0, "min_lon": -10.0, "max_lat": 37.0, "max_lon": 0.0})
    input_dirs: dict = field(default_factory=lambda: {"modis": "data/raw/modis", "viirs": "data/raw/viirs", "environmental": "data/raw/environmental"})
    output_dirs: dict = field(default_factory=lambda: {"satellite": "data/processed/satellite", "harmonized": "data/processed/harmonized", "environmental": "data/processed/environmental", "iot": "data/iot", "models": "models/trained", "metadata": "models/metadata"})
    harmonization: dict = field(default_factory=lambda: {"max_distance_km": 2.5, "max_time_hours": 12, "evidence_formula": "frp * 1.2 + confidence * 0.5 + count * 3", "false_positive_rules": []})
    thresholds: dict = field(default_factory=lambda: {"risk": {"low": 0.0, "moderate": 0.4, "high": 0.7, "critical": 0.9}, "iot": {"match_distance_km": 12.0, "match_time_hours": 6.0}})
    replay: dict = field(default_factory=lambda: {"default_speed": 2.0, "max_days": 30})
    logging: dict = field(default_factory=lambda: {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"})

    @classmethod
    def from_yaml(cls, config_path: str | Path | None = None) -> "AppSettings":
        path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
        if path.exists():
            data = _parse_simple_yaml(path)
            return cls(**data)
        return cls()


def load_settings() -> AppSettings:
    settings = AppSettings.from_yaml()
    settings.default_region = os.getenv("DEFAULT_REGION", settings.default_region)
    return settings
