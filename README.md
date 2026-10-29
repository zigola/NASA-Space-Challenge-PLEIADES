# PLEIADES — Intelligent Wildfire Monitoring and Early Warning

**NASA Space Apps Challenge 2026 | Béni Mellal, Morocco**

PLEIADES is a modular wildfire monitoring and risk-assessment platform designed to improve wildfire awareness by combining satellite observations, environmental sensor data, data processing, and risk analysis.

The project explores the integration of NASA FIRMS fire observations from MODIS and VIIRS with simulated or real ground-based sensor measurements. It also provides a foundation for data visualization, experimental machine-learning risk scoring, and early-warning workflows.

## The Problem

Wildfires threaten forests, biodiversity, communities, and infrastructure. Early awareness and reliable communication can be challenging in remote areas or locations with limited internet connectivity.

PLEIADES explores an integrated approach to wildfire monitoring that combines satellite observations, environmental measurements, and accessible monitoring tools.

## Our Mission

The project aims to:

- Process satellite hotspot observations from MODIS and VIIRS.
- Combine available observations into a consistent data structure.
- Explore environmental monitoring using temperature, humidity, smoke, flame, and other suitable sensors.
- Assess potential fire-related risks using transparent data-processing methods.
- Explore communication options for areas with limited connectivity.
- Present relevant observations through a monitoring dashboard.
- Support informed decisions without replacing official emergency services.

## Main Capabilities

The software architecture is designed to support:

- Local ingestion of NASA FIRMS CSV files.
- Geographic filtering of wildfire observations.
- A normalized wildfire observation schema.
- Spatiotemporal clustering of nearby detections.
- Synthetic IoT and LoRa-like sensor simulation.
- Experimental Random Forest risk scoring when suitable data are available.
- A Streamlit dashboard and replay interface.
- Automated processing pipelines and automated tests.

The availability of each capability depends on its implementation and validation status.

## How It Works

### 1. Satellite Monitoring

PLEIADES uses data from NASA's Fire Information for Resource Management System (FIRMS) to explore satellite-derived fire and thermal anomaly observations.

MODIS and VIIRS provide complementary observations. Their spatial resolution, detection characteristics, observation times, and data availability must be considered when comparing or combining their results.

### 2. Environmental Sensing

The proposed hardware architecture may include sensors for:

- Temperature.
- Humidity.
- Smoke.
- Flame.
- Selected gases, depending on sensor availability.

Sensor measurements can be simulated during software development and replaced with real measurements when compatible hardware becomes available.

### 3. Data Integration and Analysis

The software processes available observations, validates relevant fields, applies geographic filters, and explores relationships between satellite detections and environmental measurements.

Potential analysis variables include latitude, longitude, observation time, satellite instrument, confidence, brightness, and fire radiative power when provided by the selected data product.

### 4. Risk Assessment

The project explores experimental risk-scoring methods, including machine learning where suitable training data are available.

Synthetic data are intended for development and demonstration. They do not establish real-world predictive accuracy.

### 5. Monitoring and Alerts

The proposed system may integrate a dashboard with communication options such as Wi-Fi, cellular networks, or LoRa-based local communication.

Possible notification channels depend on the hardware, network coverage, and services actually implemented and tested.

## Free and Open-Source Policy

PLEIADES is designed to use free, open-source, and locally executable tools wherever practical.

- Python is the primary programming language.
- Core ingestion and analysis run locally.
- NASA FIRMS access is optional and configured through a local environment variable.
- The basic workflow does not require a paid cloud service or paid API.
- Compatible CSV files and synthetic datasets can be used without a live internet connection.
- Optional online services must comply with their respective terms and usage limits.

## Technologies and Data Sources

- **Python:** Data processing and application logic.
- **Streamlit:** Interactive monitoring dashboard.
- **Pandas:** Data manipulation and analysis.
- **Scikit-learn:** Experimental machine-learning workflows.
- **NASA FIRMS:** Satellite-derived fire and thermal anomaly observations.
- **MODIS and VIIRS:** Complementary satellite observation sources.
- **IoT sensors:** Potential ground-based environmental measurements.
- **LoRa, Wi-Fi, and cellular networks:** Communication technologies under consideration.
- **Pytest:** Automated software testing.

The final technology stack depends on implementation, testing, and hardware availability.

## Project Architecture

The current software architecture is organized around the following components:

- `app.py` — Streamlit application entry point.
- `config/` — Configuration, regions, and thresholds.
- `src/` — Data processing, harmonization, simulation, machine learning, and risk logic.
- `dashboard/` — Dashboard components.
- `data/` — Raw, processed, and synthetic datasets.
- `models/` — Model files and metadata.
- `scripts/` — Processing pipeline and stage runners.
- `tests/` — Automated tests.
- `docs/` — Installation, methodology, and demonstration documentation.

Actual files and available features may vary as development progresses.

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks environment activation, use the Python executable inside the virtual environment directly or follow the relevant Windows environment configuration guidance.

## Run the Dashboard

```powershell
streamlit run app.py
```

## Optional NASA FIRMS Configuration

Obtain an appropriate NASA FIRMS map key through the official service if your intended data product and workflow require it.

Set the key in the current PowerShell session:

```powershell
$env:NASA_FIRMS_MAP_KEY = "your_real_key_here"
streamlit run app.py
```

Never commit API keys, passwords, or other credentials to Git. Keep local secrets outside version control.

Official data source: https://firms.modaps.eosdis.nasa.gov/

## Run Pipeline Stages

If the corresponding scripts are present in the project:

```powershell
python scripts/run_ingestion.py
python scripts/run_harmonization.py
python scripts/simulate_iot.py
python scripts/train_model.py
python scripts/run_pipeline.py
```

Run only the stages supported by the current codebase.

## Run Tests

```powershell
pytest -q
```

## Development Roadmap

- [ ] Validate the project structure and installation workflow.
- [ ] Implement and test local FIRMS CSV ingestion.
- [ ] Validate the normalized observation schema.
- [ ] Develop and evaluate MODIS–VIIRS harmonization.
- [ ] Implement geographic filtering and spatiotemporal clustering.
- [ ] Develop the sensor simulation workflow.
- [ ] Evaluate machine-learning methods using appropriate data.
- [ ] Improve the monitoring dashboard.
- [ ] Prototype hardware and communication components.
- [ ] Test alert delivery and offline communication where supported.
- [ ] Document system limitations and validation results.

Progress should be updated as features are implemented and tested.

## Security and Reliability

- Do not commit API keys or other secrets.
- Keep local environment files excluded from version control.
- Validate input files before processing.
- Treat synthetic data as demonstration data, not evidence of operational accuracy.
- Account for the latency, resolution, and limitations of satellite observations.
- Test any operational alerting workflow before relying on it.

## Limitations and Disclaimer

PLEIADES is a developing research and demonstration project. It is not a certified wildfire detection or forecasting system.

Satellite observations can be delayed or incomplete, and environmental sensors can produce inaccurate readings. Experimental risk scores must not be interpreted as confirmed fire incidents.

Operational deployment would require extensive testing, independent validation, reliable communications, and coordination with the relevant authorities.

## Team and Contributions

PLEIADES is being developed for the NASA Space Apps Challenge 2026 in Béni Mellal, Morocco.

Technical feedback, contributions, and ideas are welcome. Open an issue to discuss a proposed improvement before submitting substantial changes.

---

**PLEIADES — Connecting satellite intelligence and environmental sensing for wildfire awareness.**
