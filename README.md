# PLEIADES

## Wildfire monitoring with satellite and environmental data

PLEIADES is an experimental, open-development wildfire-awareness platform created for the NASA Space Apps Challenge 2026 in Béni Mellal, Morocco. It explores how satellite observations, simulated sensor data, geospatial processing, and transparent risk analysis can support earlier wildfire awareness.

> PLEIADES is a research and demonstration project. It is not a certified detection, forecasting, or emergency-response system.

## What the repository currently contains

The repository currently includes Python modules and tests for:

- Local ingestion of NASA FIRMS-compatible CSV data
- MODIS and VIIRS observation handling and harmonization experiments
- Geographic filtering, distance calculations, and spatial utilities
- Synthetic IoT sensor generation and replay workflows
- Experimental risk assessment and machine-learning components
- Streamlit dashboard views, charts, maps, and filters
- Sample GeoJSON data and documented configuration
- Automated tests covering ingestion, geospatial logic, harmonization, simulation, replay, and risk modules

The presence of a module does not imply operational validation. Check the source code, tests, and documentation before relying on a capability.

## Architecture

```text
app.py                 Streamlit entry point
config/                Regions, thresholds, settings, and translations
dashboard/             Dashboard views, maps, charts, and UI helpers
data/                  Samples and synthetic sensor data
docs/                  Installation, architecture, methodology, and data dictionary
scripts/               Ingestion, harmonization, simulation, training, and pipeline runners
src/                   Core processing, models, NASA FIRMS clients, spatial, and risk logic
tests/                 Automated tests
```

## Data sources and limitations

PLEIADES is designed to work with NASA FIRMS observations from MODIS and VIIRS. These products differ in resolution, timing, detection characteristics, confidence fields, and availability. Satellite observations may be delayed, incomplete, or affected by cloud cover and other conditions.

Synthetic sensor data are useful for development and demonstrations. They are not evidence of real-world sensor accuracy. Any operational use would require independent validation, field testing, reliable communications, and coordination with the relevant authorities.

## Installation

Python 3.10 or newer is recommended.

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the dashboard

```bash
streamlit run app.py
```

## Optional NASA FIRMS configuration

Copy `.env.example` to `.env` and set a valid key only when your selected FIRMS workflow requires one. Never commit `.env`, API keys, or other credentials.

```text
NASA_FIRMS_API_KEY=your_key_here
NASA_FIRMS_BASE_URL=https://firms.modaps.eosdis.nasa.gov/api
DEFAULT_REGION=Morocco-Rif
LOG_LEVEL=INFO
```

Official source: [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)

## Run tests

```bash
pytest -q
```

## Run selected pipeline stages

Use only the stages supported by the current implementation and local data:

```bash
python scripts/run_ingestion.py
python scripts/run_harmonization.py
python scripts/simulate_iot.py
python scripts/train_model.py
python scripts/run_pipeline.py
```

## Development status

### Implemented or represented in the current repository

- Local data ingestion and validation modules
- Satellite observation schemas and harmonization code
- Spatial utilities and dashboard components
- Synthetic IoT data and replay support
- Test suite and sample data

### Planned or requiring further validation

- Independent evaluation of risk-scoring methods
- Production-quality alert delivery and offline communication
- Hardware integration and field measurements
- Performance evaluation with representative datasets
- Deployment hardening and operational monitoring

## Responsible use and security

- Do not use PLEIADES as the sole basis for emergency decisions.
- Treat risk scores as experimental outputs, not confirmed incidents.
- Validate input data and model assumptions.
- Keep secrets outside version control.
- Review third-party data terms and usage limits.
- Report security issues privately using the process in [SECURITY.md](SECURITY.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request. Small improvements to tests, documentation, reproducibility, and data validation are especially welcome.

## License and project ownership

This repository currently does not declare an open-source license. Do not assume that the code, documentation, data, or team materials may be reused or redistributed until the project owners confirm the licensing terms. A license should be added after ownership and contributor permissions are confirmed.

## Acknowledgements

PLEIADES explores NASA FIRMS data and open-source Python tools. NASA is a data-source reference here, not an endorsement or affiliation with this project.
