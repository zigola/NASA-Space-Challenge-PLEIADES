# PLEIADES

PLEIADES is a modular wildfire monitoring and risk-assessment platform designed for the NASA Space Apps Challenge. The application integrates local NASA FIRMS observations, spatiotemporal harmonization between MODIS and VIIRS, synthetic IoT sensor data, experimental machine-learning risk scoring, and a Streamlit dashboard.

## Free and open-source policy

This project is designed to run with free, open-source, and locally executable tools wherever practical:

- Python is the primary language.
- The dependency set is limited to free and widely used packages.
- Core ingestion and analysis run locally without a paid API or subscription.
- NASA FIRMS API access is optional and environment-driven only.
- No paid cloud services, paid map tiers, or billable authentication providers are required for the basic project workflow.
- The project must continue to function when optional online services are unavailable.

The app does not require a paid subscription for its core workflow. A live NASA FIRMS request is only attempted when the user has configured a local environment variable and the service is available under its own terms.

## Main capabilities

- Offline FIRMS CSV ingestion and geographic filtering
- Normalized wildfire observation schema
- Spatiotemporal clustering of nearby detections
- Synthetic LoRa-like sensor simulation
- RandomForest-based risk scoring in synthetic or labelled data scenarios
- Streamlit dashboard and replay interface

## Project architecture

- `app.py` — Streamlit entry point
- `config/` — settings, regions, thresholds
- `src/` — data processing, harmonization, simulation, ML, risk logic
- `dashboard/` — dashboard submodules
- `data/` — raw, processed, and synthetic datasets
- `models/` — trained models and metadata
- `scripts/` — pipeline and stage runners
- `tests/` — pytest coverage
- `docs/` — installation, methodology, and demo documentation

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the dashboard

```bash
streamlit run app.py
```

## NASA FIRMS API setup (optional)

To enable the optional NASA FIRMS API fetch feature, set the environment variable before running the app:

```powershell
$env:NASA_FIRMS_MAP_KEY = "your_real_key_here"
streamlit run app.py
```

Do not commit this key to source control. Keep it in a local environment or a .env file that is excluded from Git.

## Local-first architecture

The application is intentionally designed to work without a paid backend:

- Upload a compatible FIRMS CSV locally.
- Validate column names, latitude, longitude, and timestamps.
- Filter by geographic bounding box and source.
- Run charting and summary analysis locally.
- Use NASA FIRMS API access only when explicitly configured.

## Run pipeline stages

```bash
python scripts/run_ingestion.py
python scripts/run_harmonization.py
python scripts/simulate_iot.py
python scripts/train_model.py
python scripts/run_pipeline.py
```

## Security and dependency notes

- No plaintext secrets are committed to the repository.
- API credentials must remain in local environment variables or a local `.env` file excluded from Git.
- No paid APIs, subscriptions, or cloud services are required for the local-first workflow.
- Optional online integrations must respect external service terms and rate limits.

## Test suite

```bash
pytest -q
```

## Notes

The platform is intentionally offline-first and uses synthetic data when real FIRMS access or labelled wildfire labels are unavailable. It is intended for demonstration, reproducible analysis, and project validation rather than operational forecasting.
