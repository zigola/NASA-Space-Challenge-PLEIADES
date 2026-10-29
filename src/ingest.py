from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any, Iterable, Tuple

import pandas as pd

from src.spatial.bounding_box import in_bbox

DEFAULT_BBOX = (20.0, -18.0, 40.0, 20.0)

CANONICAL_COLUMNS = {
    "latitude": ["latitude", "lat", "y"],
    "longitude": ["longitude", "lon", "lng", "long", "x"],
    "brightness": ["brightness", "bright_ti4", "bright_ti5", "bright_t31"],
    "scan": ["scan"],
    "track": ["track"],
    "acq_date": ["acq_date", "date", "acquisition_date"],
    "acq_time": ["acq_time", "time", "acquisition_time"],
    "satellite": ["satellite", "platform", "sat"],
    "instrument": ["instrument", "sensor"],
    "confidence": ["confidence", "conf"],
    "version": ["version"],
    "bright_t31": ["bright_t31"],
    "frp": ["frp", "fire_radiative_power"],
    "daynight": ["daynight", "day_night", "dn"],
}

SATELLITE_NAME_MAP = {
    "A": "Aqua",
    "T": "Terra",
    "AQUA": "Aqua",
    "TERRA": "Terra",
    "MODIS": "MODIS",
    "N": "Suomi-NPP",
    "SNPP": "Suomi-NPP",
    "SUOMI NPP": "Suomi-NPP",
    "SUOMI-NPP": "Suomi-NPP",
    "1": "NOAA-20",
    "J1": "NOAA-20",
    "JPSS-1": "NOAA-20",
    "NOAA-20": "NOAA-20",
    "NOAA 20": "NOAA-20",
    "2": "NOAA-21",
    "J2": "NOAA-21",
    "JPSS-2": "NOAA-21",
    "NOAA-21": "NOAA-21",
    "NOAA 21": "NOAA-21",
    "VIIRS": "VIIRS",
}

INSTRUMENT_MAP = {
    "Aqua": "MODIS",
    "Terra": "MODIS",
    "MODIS": "MODIS",
    "Suomi-NPP": "VIIRS",
    "NOAA-20": "VIIRS",
    "NOAA-21": "VIIRS",
    "VIIRS": "VIIRS",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]
    for canonical, aliases in CANONICAL_COLUMNS.items():
        for alias in aliases:
            if alias in normalized.columns and canonical not in normalized.columns:
                normalized = normalized.rename(columns={alias: canonical})
                break
    return normalized


def _convert_confidence(val: Any) -> float:
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(max(0.0, min(100.0, float(val))))
    val_str = str(val).strip().lower()
    if val_str in {"l", "low"}:
        return 30.0
    if val_str in {"n", "nominal", "med", "medium"}:
        return 65.0
    if val_str in {"h", "high"}:
        return 95.0
    try:
        num = float(val_str)
        return float(max(0.0, min(100.0, num)))
    except ValueError:
        return 50.0


def _parse_source_content(source: Any) -> tuple[pd.DataFrame, str]:
    source_name = "unknown_source"
    payload: str | bytes = ""

    if hasattr(source, "read"):
        source_name = getattr(source, "name", "uploaded_file")
        try:
            if hasattr(source, "seek"):
                source.seek(0)
        except Exception:
            pass
        try:
            payload = source.read()
        except Exception as exc:
            raise ValueError(f"Could not read the uploaded content: {exc}") from exc
        if not payload:
            raise ValueError("Uploaded file is empty.")
    elif isinstance(source, (str, Path)):
        source_str = str(source).strip()
        if not source_str:
            raise ValueError("No file path or data source was provided.")
        # Check if source is a raw JSON/GeoJSON or CSV string payload instead of path
        if source_str.startswith("{") or source_str.startswith("["):
            payload = source_str
            source_name = "string_payload.json"
        else:
            file_path = Path(source)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"The path is not a file: {file_path}")
            if file_path.stat().st_size == 0:
                raise ValueError(f"File is empty: {file_path}")
            source_name = file_path.name
            with file_path.open("rb") as f:
                payload = f.read()
    else:
        raise ValueError("Unsupported source format. Expected file path, uploaded file, or text stream.")

    text_content = payload.decode("utf-8", errors="replace") if isinstance(payload, bytes) else payload
    stripped = text_content.strip()
    if not stripped:
        raise ValueError("File is empty or contains only whitespace.")

    # Check for GeoJSON or JSON
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            json_obj = json.loads(stripped)
            if isinstance(json_obj, dict) and json_obj.get("type") == "FeatureCollection":
                rows = []
                for feat in json_obj.get("features", []):
                    props = dict(feat.get("properties", {}))
                    geom = feat.get("geometry", {})
                    if geom and geom.get("type") == "Point" and geom.get("coordinates"):
                        coords = geom["coordinates"]
                        if "longitude" not in props and len(coords) >= 1:
                            props["longitude"] = coords[0]
                        if "latitude" not in props and len(coords) >= 2:
                            props["latitude"] = coords[1]
                    rows.append(props)
                df = pd.DataFrame(rows)
            elif isinstance(json_obj, list):
                df = pd.DataFrame(json_obj)
            elif isinstance(json_obj, dict):
                df = pd.DataFrame([json_obj])
            else:
                raise ValueError("Unexpected JSON structure.")
            return df, str(source_name)
        except json.JSONDecodeError:
            pass  # Fall through to CSV parsing

    # Parse as CSV
    try:
        buffer = io.StringIO(text_content)
        df = pd.read_csv(buffer)
        return df, str(source_name)
    except Exception as exc:
        raise ValueError(f"The file could not be parsed as tabular CSV or GeoJSON: {exc}") from exc


def read_firms_file(path: str | Path | Any) -> pd.DataFrame:
    """Read a local file or UploadedFile (CSV, JSON, GeoJSON) and normalize the FIRMS schema."""
    df, source_name = _parse_source_content(path)
    if df.empty:
        raise ValueError(f"File is empty or contains no rows: {source_name}")

    df = normalize_columns(df)

    missing_required = [column for column in ["latitude", "longitude"] if column not in df.columns]
    if missing_required:
        raise ValueError(f"File is missing required FIRMS coordinates: {', '.join(missing_required)}")

    for col in ["latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Map satellites and instruments cleanly
    raw_sat = df["satellite"].astype(str).str.strip() if "satellite" in df.columns else pd.Series(["UNKNOWN"] * len(df))
    df["satellite"] = raw_sat.map(lambda s: SATELLITE_NAME_MAP.get(s.upper(), s if s and s != "nan" else "UNKNOWN"))

    if "instrument" not in df.columns:
        df["instrument"] = df["satellite"].map(lambda s: INSTRUMENT_MAP.get(s, "MODIS" if s in {"Aqua", "Terra"} else "VIIRS" if s in {"Suomi-NPP", "NOAA-20", "NOAA-21"} else "UNKNOWN"))
    else:
        df["instrument"] = df["instrument"].astype(str).str.strip().str.upper().replace({"nan": "UNKNOWN", "": "UNKNOWN"})
        # Fix instrument if unknown but satellite is known
        unknown_mask = df["instrument"] == "UNKNOWN"
        df.loc[unknown_mask, "instrument"] = df.loc[unknown_mask, "satellite"].map(lambda s: INSTRUMENT_MAP.get(s, "UNKNOWN"))

    # Parse date and times
    if "acq_date" not in df.columns and "timestamp" in df.columns:
        df["acq_date"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.strftime("%Y-%m-%d")
    if "acq_time" not in df.columns and "timestamp" in df.columns:
        df["acq_time"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.strftime("%H%M")

    if "acq_date" in df.columns:
        df["acq_date"] = df["acq_date"].astype(str).str.strip()
    else:
        df["acq_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")

    if "acq_time" in df.columns:
        df["acq_time"] = df["acq_time"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(4)
    else:
        df["acq_time"] = "1200"

    if "brightness" in df.columns:
        df["brightness"] = pd.to_numeric(df["brightness"], errors="coerce").fillna(300.0)
    elif "bright_t31" in df.columns:
        df["brightness"] = pd.to_numeric(df["bright_t31"], errors="coerce").fillna(300.0)
    else:
        df["brightness"] = 300.0

    if "bright_t31" in df.columns:
        df["bright_t31"] = pd.to_numeric(df["bright_t31"], errors="coerce").fillna(df["brightness"])
    else:
        df["bright_t31"] = df["brightness"]

    if "frp" in df.columns:
        df["frp"] = pd.to_numeric(df["frp"], errors="coerce").fillna(0.0)
    else:
        df["frp"] = 0.0

    # Convert confidence cleanly
    if "confidence" in df.columns:
        df["confidence"] = df["confidence"].apply(_convert_confidence)
    else:
        df["confidence"] = 50.0

    if "daynight" in df.columns:
        df["daynight"] = df["daynight"].astype(str).str.strip().str.upper().map(lambda x: "D" if x in {"D", "DAY"} else "N" if x in {"N", "NIGHT"} else "D")
    else:
        df["daynight"] = "D"

    df["source_file"] = source_name
    df["is_valid"] = (
        df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
        & df["acq_date"].notna()
        & (df["acq_date"] != "nan")
    )
    df = df.loc[df["is_valid"]].copy()

    # Construct timestamp
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["acq_date"] + " " + df["acq_time"].str.slice(0, 2) + ":" + df["acq_time"].str.slice(2, 4) + ":00",
            errors="coerce",
        )
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Fallback timestamp if any parsing NaT
    nat_mask = df["timestamp"].isna()
    if nat_mask.any():
        df.loc[nat_mask, "timestamp"] = pd.to_datetime(df.loc[nat_mask, "acq_date"], errors="coerce").fillna(pd.Timestamp.now())

    df = df.drop_duplicates(subset=["latitude", "longitude", "acq_date", "acq_time", "satellite"], keep="first").copy()
    return df


def read_firms_csv(path: str | Path | Any) -> pd.DataFrame:
    """Backward-compatible entry point for reading FIRMS files."""
    return read_firms_file(path)


def filter_bbox(df: pd.DataFrame, bbox: Tuple[float, float, float, float] | None = None) -> pd.DataFrame:
    bbox = bbox or DEFAULT_BBOX
    if df.empty:
        return df.copy()
    mask = df.apply(lambda row: in_bbox(float(row["latitude"]), float(row["longitude"]), bbox), axis=1)
    return df.loc[mask].copy()


def normalize_firms_dataset(
    csv_paths: Iterable[str | Path | Any],
    bbox: Tuple[float, float, float, float] | None = None,
    output_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Load multiple FIRMS files (CSV, JSON, GeoJSON), normalize them, and concatenate."""
    frames = []
    for path in csv_paths:
        try:
            df = read_firms_file(path)
            if not df.empty:
                frames.append(df)
        except Exception:
            continue

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if combined.empty:
        return combined

    filtered = filter_bbox(combined, bbox=bbox)
    if bbox is not None and len(filtered) <= 1 and len(combined) > 1:
        filtered = combined.copy()

    combined = filtered.sort_values(["timestamp", "longitude", "latitude"]).reset_index(drop=True)
    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        combined.to_csv(out / "normalized_firms.csv", index=False)
    return combined


def get_reference_dataset() -> pd.DataFrame:
    """Load the built-in reference FIRMS dataset for demonstrations and offline inspection."""
    sample_path = Path(__file__).resolve().parent.parent / "data" / "samples" / "sample_firms_morocco_mediterranean.csv"
    if sample_path.exists():
        try:
            df = read_firms_file(sample_path)
            df["source_dataset"] = "Sample Reference Testbed (Morocco-Rif & Mediterranean)"
            return df
        except Exception:
            pass

    # Built-in fallback dataframe
    records = [
        {"latitude": 35.182, "longitude": -5.412, "brightness": 348.6, "confidence": 95, "satellite": "Suomi-NPP", "instrument": "VIIRS", "acq_date": "2024-08-15", "acq_time": "1342", "frp": 84.6, "daynight": "D"},
        {"latitude": 35.210, "longitude": -5.385, "brightness": 336.2, "confidence": 88, "satellite": "Suomi-NPP", "instrument": "VIIRS", "acq_date": "2024-08-15", "acq_time": "1342", "frp": 52.3, "daynight": "D"},
        {"latitude": 34.821, "longitude": -4.935, "brightness": 324.7, "confidence": 76, "satellite": "Terra", "instrument": "MODIS", "acq_date": "2024-08-15", "acq_time": "1130", "frp": 34.1, "daynight": "D"},
        {"latitude": 35.340, "longitude": -5.120, "brightness": 355.2, "confidence": 98, "satellite": "NOAA-20", "instrument": "VIIRS", "acq_date": "2024-08-16", "acq_time": "1325", "frp": 112.5, "daynight": "D"},
        {"latitude": 35.080, "longitude": -5.620, "brightness": 312.4, "confidence": 65, "satellite": "Aqua", "instrument": "MODIS", "acq_date": "2024-08-16", "acq_time": "1415", "frp": 22.0, "daynight": "D"},
    ]
    df = pd.DataFrame(records)
    df = read_firms_file(io.StringIO(df.to_csv(index=False)))
    df["source_dataset"] = "Sample Reference Testbed (Fallback)"
    return df
