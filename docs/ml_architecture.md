# Machine Learning System Architecture
## Chennai Traffic Intelligence Platform

---

## 1. Architectural Overview

The Chennai Traffic Intelligence ML Subsystem is an autoregressive, multi-horizon traffic forecasting platform designed to predict congestion severity across Chennai's monitored arterial road network (+15, +30, +45, +60 minutes into the future).

The architecture is built on six foundational principles:
1. **Scientific Honesty & Data Provenance**: Explicit distinction between `OBSERVED`, `DERIVED`, `PREDICTED`, and `SIMULATED` data.
2. **Data Sufficiency Gate**: Automated validation preventing model training on unrepresentative or insufficient data sets.
3. **Strict Zero Future Data Leakage**: Enforced chronological ordering, lagging, and rolling windows with `closed='left'` (shifted by 1).
4. **Mandatory Baseline Hurdles**: Persistence and Historical Average benchmarks as performance hurdles.
5. **Multi-Horizon Specialized Forecasters**: Dedicated GBDT models trained per lead time (+15m, +30m, +45m, +60m).
6. **Dynamic Instance-Level Explainability**: Normalized directional feature contribution scoring replacing static mock weights.

---

## 2. End-to-End Pipeline Diagram

```
                              RAW DATA INGESTION
                     (data/synthetic/ or Live Feeds)
                                    │
                                    ▼
                          DATA SUFFICIENCY GATE
                            (ml/data_audit.py)
                 Checks: >=7 days, >=1,000 rows, 0 duplicates
                                    │
                                    ▼
                         PREPROCESSING & CLEANING
                          (ml/preprocessing.py)
             Deduplication, Range Validation, Continuity Imputation
                                    │
                                    ▼
                           FEATURE ENGINEERING
                            (ml/features.py)
            Temporal Cyclical (sin/cos), Lags (1,2,3), Rolling Stats (3h),
                   Spatial Adjacency, Weather & Incidents
                                    │
                                    ▼
                           TARGET CONSTRUCTION
                            (ml/targets.py)
             Lead Shifting (-h), Categorical Threshold Mapping
                                    │
                                    ▼
                          CHRONOLOGICAL SPLIT
                   Train (70%) / Val (15%) / Test (15%)
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
   Persistence Baseline    Random Forest Candidate  HistGradientBoosting
     (y_{t+h} = y_t)       (sklearn RandomForest)    (Candidate Selected)
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                                    ▼
                             MODEL SELECTION
                       (Lowest Validation MAE)
                                    │
                                    ▼
                          EXPLAINABILITY FIT
                           (ml/explain.py)
                  Learns Feature Means, Stds, Weights
                                    │
                                    ▼
                         ARTIFACT SERIALIZATION
                   (backend/models/artifacts/*.joblib)
                                    │
                                    ▼
                         PRODUCTION INFERENCE
                    (backend/services/ml_engine.py)
                                    │
                                    ▼
                            FASTAPI ENDPOINTS
                       (backend/api/routes_ml.py)
                                    │
                                    ▼
                          FRONTEND DASHBOARD
                   (MapLibre WebGL + Plotly Charts)
```

---

## 3. Component Details

### 3.1 Data Sufficiency Gate (`ml/data_audit.py`)
Enforces mathematical minimums before any training run:
- $\ge 7$ unique calendar days
- $\ge 1,000$ valid observation records
- $\ge 50$ observations per corridor
- $\le 10\%$ missing rate on key numerical sensors
- 0 unhandled duplicate `(road_id, timestamp)` tuples
- Produces structured reports: `ml/reports/data_audit.json` and `ml/reports/data_audit.md`.

### 3.2 Preprocessing Engine (`ml/preprocessing.py`)
- Rejects physical impossibilities: negative vehicle volumes, negative speeds, impossible rain accumulations.
- Enforces road physical ceilings: vehicle count capped at $1.8 \times \text{Capacity}$, speeds capped at $1.3 \times \text{Speed Limit}$.
- Forward-fills and backward-fills time-series gaps within each corridor before falling back to global medians.

### 3.3 Feature Engineering (`ml/features.py`)
Computes 26 strictly backward-looking features:
- **Cyclical Temporal**: $\sin(2\pi \cdot \text{hour}/24)$, $\cos(2\pi \cdot \text{hour}/24)$, $\sin(2\pi \cdot \text{dow}/7)$, $\cos(2\pi \cdot \text{dow}/7)$.
- **Temporal Indicators**: `is_weekend`, `is_peak_hour` (08:00–11:00 & 17:00–20:00 weekdays).
- **Static Physical**: `road_capacity`, `speed_limit`, `lane_count`.
- **Corridor Lags**: `vehicle_count_lag_1`, `vehicle_count_lag_2`, `vehicle_count_lag_3`, `speed_lag_1`, `speed_lag_2`, `speed_lag_3`, `congestion_lag_1`, `congestion_lag_2`.
- **Rolling Context**: 3-hour rolling mean of speed, volume, and congestion index calculated strictly on `shift(1)`.
- **Spatial Topology**: `neighbor_congestion_lag_1` querying the mean congestion of physically adjacent corridors at $T-1$.
- **Weather & Incidents**: `rainfall`, `temperature`, `is_raining`, `accident_lag_1`.

### 3.4 Target Definition (`ml/targets.py`)
- Continuous primary target: `target_congestion_index` at $T + h$.
- Derived categorical severity levels adhering to Chennai standard:
  - `Low`: $[0.0, 30.0)$
  - `Moderate`: $[30.0, 55.0)$
  - `High`: $[55.0, 75.0)$
  - `Severe`: $[75.0, 100.0]$

### 3.5 Model Zoo (`ml/models.py` & `ml/train.py`)
- **Baseline 1 (Persistence)**: $\hat{y}_{t+h} = y_t$.
- **Baseline 2 (Historical Average)**: Grouped by `(road_id, hour, is_weekend)`.
- **Candidate 1 (Random Forest)**: 100 estimators, max depth 12.
- **Candidate 2 (HistGradientBoosting)**: High-performance GBDT with native histogram binning, learning rate 0.08, max depth 8, early stopping.
- **Multi-Horizon Suite**: Dedicated models trained for +15m, +30m, +45m, and +60m lead times.

### 3.6 Explainability Engine (`ml/explain.py`)
- Computes instance-level feature attributions by weighting global model feature importances with standardized deviation ($z$-score) from training baselines.
- Directional classification:
  - `increases_congestion` (elevated volume, rainfall, incidents, peak hours)
  - `decreases_congestion` (elevated corridor speed, weekend status, high capacity)
- Normalizes top 3 drivers per prediction to sum to 1.0.

### 3.7 Serving Engine (`backend/services/ml_engine.py`)
- Singleton service loading joblib artifacts and metadata into memory.
- Provides fallback handling if artifacts are absent.
- Serves `/api/ml/status`, `/api/ml/predictions`, and `/api/ml/predict/{location_id}`.
