# Machine Learning Subsystem Limitations & Data Boundaries
## Chennai Traffic Intelligence Platform

---

## 1. Scientific Provenance & Benchmark Scope

1. **Development & Benchmark Data Scope**:
   - The multi-day training dataset (`data/synthetic/chennai_traffic_multiday_benchmark.json`) is a calibrated simulation reflecting known physical attributes of 14 arterial corridors in Chennai (OpenStreetMap geometry, design capacities, posted speed limits, diurnal commute patterns, and monsoon rainfall distributions).
   - In accordance with the Project Honesty Policy, this data is formally watermarked as `SIMULATED BENCHMARK DATASET FOR DEVELOPMENT & MODEL VALIDATION`.
   - **Never represent simulation benchmarks as empirical physical sensor recordings.**

2. **Single-Day Fixture Rejection**:
   - The single-day 24-hour fixture (`data/synthetic/chennai_traffic_fixture.json`, 288 records) is scientifically insufficient for machine learning training.
   - The Data Sufficiency Gate (`ml/data_audit.py`) deliberately halts execution if training is attempted on this fixture.

---

## 2. Model Operational Boundaries

1. **Prediction Horizons**:
   - Trained models are optimized for short-term operational forecasting: **+15, +30, +45, and +60 minutes**.
   - Forecasting beyond 60 minutes carries rapidly expanding uncertainty due to unmodeled stochastic events (unannounced road closures, VIP motorcades, local flash flooding, localized accidents).

2. **Spatial Topology Assumptions**:
   - Spatial spillover features (`neighbor_congestion_lag_1`) model first-order network adjacency based on major arterial junctions (e.g. Kathipara, Gemini Flyover, Koyambedu CMBT).
   - Secondary side streets and minor collector roads are not monitored in the current network scope.

3. **Extreme Weather & Severe Anomalies**:
   - Rainfall impacts are calibrated up to 25–35 mm/hr (moderate to heavy monsoon spells).
   - Catastrophic cyclonic inundation causing complete road submersion represents an out-of-distribution regime where physical traffic flow breaks down completely; under such conditions, model confidence scores degrade appropriately.

---

## 3. Transition to Physical Empirical Data

When physical IoT sensor feeds (induction loops, automated number plate recognition cameras, TomTom/Google Traffic APIs) are connected:
1. The Data Classification in `model_metadata.json` will update from `SIMULATED` to `REAL`.
2. The Data Sufficiency Gate will verify empirical sensor coverage before retraining.
3. Feature engineering and model architecture remain fully reusable without modification.
