# Methodology

The platform uses a lightweight offline processing pipeline. FIRMS detections are cleaned, filtered geographically, and grouped by proximity and time. Evidence scores combine fire radiative power and detection confidence. A synthetic LoRa network then validates detections spatially and temporally. The ML workflow is meant as an experimental risk indicator rather than real operational forecasting.

## Scientific assumptions

- Nearby detections separated by short time intervals likely originate from the same event.
- Sensor validation is synthetic and must not be interpreted as measured field truth.
- Risk categories are heuristic thresholds unless a robust labelled dataset becomes available.
