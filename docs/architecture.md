# Architecture Overview

PLEIADES implements a modular offline-first wildfire detection platform. The system is organized around ingestion, preprocessing, harmonization, IoT simulation, risk assessment, and a Streamlit dashboard.

## Layers

- Data acquisition: local FIRMS CSV ingestion and optional future API integration.
- Processing: validation, cleaning, and geospatial filtering.
- Harmonization: spatiotemporal grouping of MODIS and VIIRS detections.
- Sensor simulation: LoRa-style offline alert generation.
- ML risk: experimental supervised classification with RandomForest.
- Presentation: Streamlit dashboard and replay view.

## Design goals

- Minimal dependencies
- Local-first processing
- Synthetic-data fallback for absent real data
- Clear separation between configuration and logic
