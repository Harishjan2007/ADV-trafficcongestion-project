# ML Implementation Master Plan: Chennai Traffic Intelligence Platform

Replace the existing mocked traffic prediction fixtures and client-side arithmetic with a genuine, reproducible, scientifically honest, and fully tested Machine Learning pipeline.

---

## 1. Executive Summary & Problem Diagnosis

The current Chennai Traffic Intelligence repository provides high-quality visualization, MapLibre rendering, corridor clustering, and FastAPI routing, but its machine-learning prediction capabilities are entirely mocked:
1. **Mock Fixtures**: Predictions in `backend/services/ml_adapter.py` are hardcoded fixtures labeled with fictitious names like `"ST-GCN-Chennai-v2.1"`.
2. **Frontend Arithmetic**: The client interface in `index.html` computes predicted congestion indices using client-side multipliers (`pred_ci = Math.min(100.0, Math.round(ci * (isPeak ? 1.08 : 0.95)))`).
3. **Fabricated Uncertainty & SHAP**: Confidence bands are hardcoded as `CI ± 6`, and feature importances are static numbers `[0.42, 0.31, 0.18]`.
4. **Data Scarcity**: The only existing dataset is a 288-record single-day fixture (`data/synthetic/chennai_traffic_fixture.json`).

This plan defines the end-to-end engineering architecture to eliminate all mock logic, enforce a rigorous Data Sufficiency Gate, train real machine-learning models (Random Forest and Gradient Boosting) using chronological validation, generate verifiable model artifacts, serve them via FastAPI, integrate them into the frontend without client-side formula arithmetic, and validate the system with comprehensive automated tests.

---

## 2. Scientific Honesty & Data Provenance Policy

As mandated by Sections 1, 2, 6, 8, and 61 of the Master Plan:
- **Never claim a model is trained if it is not.**
- **Never display fabricated predictions as real predictions.**
- **Never label a model "ST-GCN" or "Deep Learning" unless that architecture is actually trained and executing inference.**
- **Strict Data Classification**:
  - `OBSERVED`: Chennai road geometry, lane count, speed limits from OpenStreetMap/GIS.
  - `REAL`: Recorded empirical traffic observations (when physical sensor feeds are connected).
  - `DERIVED`: Congestion indices, speed reduction ratios, V/C ratios.
  - `PREDICTED`: Real machine-learning forecasts produced by model inference.
  - `SIMULATED`: Benchmark/testing data for development and validation.

### Data Readiness Gate & Multi-Day Benchmark
- **Data Sufficiency Gate (`ml/data_audit.py`)**: When evaluated against the existing 1-day fixture, the audit will explicitly return `is_ready: False` with status `NOT READY` (insufficient time horizon and sample count). The training pipeline will halt with a clear error.
- **Calibrated Multi-Day Benchmark Dataset**: To enable genuine, reproducible ML model training without fabricating real-world claims, we will create `data/synthetic/chennai_traffic_multiday_benchmark.json` (14 days of time-aligned observations across 13 corridors = 4,368 records). It will be clearly watermarked as `SIMULATED BENCHMARK DATASET FOR DEVELOPMENT & MODEL VALIDATION`, and `model_metadata.json` will report `synthetic_data_used: true`.

---

## 3. End-to-End System Architecture

```
                                    DATA
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          ↓                          ↓                          ↓
    Traffic Volume              Road Network                 Weather
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     ↓
                            DATA SUFFICIENCY GATE
                             (ml/data_audit.py)
                                     ↓
                            DATA PREPROCESSING
                           (ml/preprocessing.py)
                                     ↓
                            FEATURE ENGINEERING
                             (ml/features.py)
                     (Strict backward lags, rolling stats)
                                     ↓
                            TARGET CONSTRUCTION
                              (ml/targets.py)
                            (+30m Congestion Index)
                                     ↓
                           CHRONOLOGICAL SPLIT
                      Train (70%) / Val (15%) / Test (15%)
                                     ↓
          ┌──────────────────────────┼──────────────────────────┐
          ↓                          ↓                          ↓
      Baselines                Random Forest            Gradient Boosting
  (Persistence, Avg)                 │                          │
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     ↓
                              MODEL SELECTION
                             (Lowest Val MAE)
                                     ↓
                             EXPLAINABILITY & CI
                        (Feature contributions & CI)
                                     ↓
                               MODEL ARTIFACTS
                     (backend/models/artifacts/*.joblib)
                                     ↓
                             INFERENCE ENGINE
                       (backend/services/ml_engine.py)
                                     ↓
                               FASTAPI SERVER
                        (backend/api/routes_ml.py)
                                     ↓
                               FRONTEND UI
                           (MapLibre + Plotly)
```

---

## 4. Proposed Implementation Steps & File Changes

### Component 1: ML Pipeline Module (`ml/`)

| File | Status | Description |
| :--- | :--- | :--- |
| `ml/__init__.py` | **[NEW]** | Package initialization and version metadata (`1.0.0`). |
| `ml/config.py` | **[NEW]** | Configuration settings (horizons `[15, 30, 45, 60]`, primary horizon `30`, split ratios, random seeds, paths). |
| `ml/data_audit.py` | **[NEW]** | Audits row counts, unique roads, date range, frequency, missing values, duplicates. Enforces Data Sufficiency Gate; outputs `ml/reports/data_audit.json` and `ml/reports/data_audit.md`. |
| `ml/preprocessing.py` | **[NEW]** | Implements domain-aware missing value imputation (forward fill within corridor, then hour medians), outlier detection, and negative value rejection. |
| `ml/features.py` | **[NEW]** | Generates cyclical time features, strict time lags (`lag_1`, `lag_2`, `lag_3`), rolling historical statistics (`mean_30m`, `std_30m` with `closed='left'` to prevent future leakage), spatial adjacency features, and weather features. |
| `ml/targets.py` | **[NEW]** | Constructs $+30$ min target (`congestion_index_lead_30m`) and maps continuous predictions to documented categories (`Low`, `Moderate`, `High`, `Severe`). |
| `ml/baselines.py` | **[NEW]** | Implements Baseline 1 (Persistence: $\hat{y}_{t+h} = y_t$) and Baseline 2 (Historical road-hour-weekend average). Calculates baseline MAE, RMSE, R². |
| `ml/models.py` | **[NEW]** | Wraps `RandomForestRegressor` and `HistGradientBoostingRegressor` (scikit-learn's native, high-performance GBDT equivalent to LightGBM). Supports multi-horizon training. |
| `ml/train.py` | **[NEW]** | End-to-end training pipeline. Audits data, splits chronologically, trains baselines and candidate models, selects best model, evaluates on test set, and exports artifacts. |
| `ml/evaluate.py` | **[NEW]** | Generates detailed evaluation metrics and outputs `ml/reports/model_evaluation.json` and `ml/reports/model_evaluation.md`. |
| `ml/explain.py` | **[NEW]** | Computes real feature importances and directional contributions per prediction instance. |

---

### Component 2: Multi-Day Benchmark Dataset (`data/synthetic/`)

| File | Status | Description |
| :--- | :--- | :--- |
| `data/synthetic/chennai_traffic_multiday_benchmark.json` | **[NEW]** | 14-day calibrated benchmark dataset (4,368 time-aligned records across 13 corridors). Features realistic diurnal waves, weekend patterns, and monsoon weather events. Explicitly watermarked as simulated benchmark data. |

---

### Component 3: Backend Services & API Integration

| File | Status | Description |
| :--- | :--- | :--- |
| `backend/services/ml_engine.py` | **[NEW]** | Production inference engine. Loads model artifacts, validates inputs, generates predictions, computes empirical prediction intervals and feature explanations. Fails cleanly if artifacts are missing. |
| `backend/services/ml_adapter.py` | **[MODIFY]** | Removes hardcoded fixture dictionaries and fake "ST-GCN" labels. Delegates directly to `MLEngine` with an explicit development offline fallback. |
| `backend/api/routes_ml.py` | **[MODIFY]** | Adds `GET /api/ml/status` returning model version, test MAE, and training date. Connects `GET /api/ml/predictions` and `GET /api/ml/predict/{location_id}` to genuine `MLEngine` inference. |

---

### Component 4: Frontend De-Mocking & API Integration

| File | Status | Description |
| :--- | :--- | :--- |
| `index.html` & `frontend/public/index.html` | **[MODIFY]** | 1. Remove client-side prediction formulas (`ci * multiplier`).<br>2. Remove fake `CI ± 6` and static SHAP `[0.42, 0.31, 0.18]`.<br>3. Remove all "ST-GCN-Chennai-v2.1" and "95% Conf" text.<br>4. Fetch predictions asynchronously from `/api/ml/predictions` and `/api/ml/predict/{id}`.<br>5. Display real model name, version, and dynamic feature explanations.<br>6. Display clear `OBSERVED` vs `PREDICTED` vs `SIMULATED` state badges. |

---

### Component 5: Test Suite & Leakage Prevention

| File | Status | Description |
| :--- | :--- | :--- |
| `tests/test_ml_data_audit.py` | **[NEW]** | Verifies audit correctly rejects 1-day fixture and approves multi-day benchmark data. |
| `tests/test_ml_features.py` | **[NEW]** | Verifies lag, cyclical, and rolling feature generation. |
| `tests/test_ml_data_leakage.py` | **[NEW]** | **Mandatory scientific validity test**: Asserts features at timestamp $T$ contain no future data from $T+1, T+2, \dots$. |
| `tests/test_ml_baselines.py` | **[NEW]** | Verifies persistence and historical average baseline calculations. |
| `tests/test_ml_training.py` | **[NEW]** | Verifies candidate model training, metric computation, artifact saving, reloading, and non-trivial prediction output. |
| `tests/test_ml_inference.py` | **[NEW]** | Verifies `MLEngine` schema validation, prediction generation, error handling, and health status. |
| `tests/test_ml_contract.py` | **[MODIFY]** | Updates existing contract test to validate against genuine ML engine outputs. |
| `tests/run_all_tests.py` | **[MODIFY]** | Integrates all new ML tests into the master test runner. |

---

### Component 6: Colab Notebook & Documentation

| File | Status | Description |
| :--- | :--- | :--- |
| `notebooks/chennai_traffic_ml_training.ipynb` | **[NEW]** | Full 18-section Google Colab-compatible notebook executing the identical ML pipeline. |
| `docs/ml_architecture.md` | **[NEW]** | Comprehensive architecture documentation covering data flow, feature engineering, training, and inference. |
| `docs/ml_data_dictionary.md` | **[NEW]** | Complete dictionary of all raw, derived, and engineered features. |
| `docs/ml_training_report.md` | **[NEW]** | Scientific report documenting dataset size, date range, baseline vs model metrics, and hyperparameter selections. |
| `docs/ml_limitations.md` | **[NEW]** | Honest disclosure of simulation data boundaries, sensor coverage assumptions, and prediction horizons. |
| `docs/ml-integration.md` | **[MODIFY]** | Replaces ST-GCN references with actual Gradient Boosting architecture. |
| `docs/walkthrough.md` | **[MODIFY]** | Updates walkthrough to document the completed genuine ML pipeline. |

---

## 5. Verification Plan

1. **Automated Test Execution**:
   - Run `tests/run_all_tests.py` verifying all unit, feature, leakage, baseline, training, inference, and contract tests pass with 0 failures.
2. **Data Leakage Verification**:
   - `tests/test_ml_data_leakage.py` strictly checks timestamps and shifts to prove no future leakage.
3. **Baseline Comparison Verification**:
   - Compare trained models against Persistence and Historical Average baselines, verifying that ML model improves upon baseline MAE.
4. **Non-Trivial Prediction Test**:
   - Verify that varying inputs (free-flow vs peak-hour congestion) produce distinct, non-constant predictions.
5. **API & Frontend Verification**:
   - Verify `GET /api/ml/status` returns `model_available: true` and active model metrics.
   - Verify `GET /api/ml/predictions` returns valid prediction payloads.
   - Verify `index.html` displays real model predictions, prediction intervals, and dynamic feature contributions.
