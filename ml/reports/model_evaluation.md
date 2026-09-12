# Machine Learning Model Evaluation Report

**Model Name:** `GradientBoostingRegressor (HistGradientBoosting)`  
**Model Version:** `1.0.0`  
**Training Date:** `2026-09-12 20:07:17`  
**Target:** `congestion_index` (+30 min lead)  
**Data Classification:** `SIMULATED BENCHMARK` (Scientific honesty notice: synthetic development data)

---

## 1. Dataset & Split Summary

- **Total Chronological Rows:** 4648
- **Training Set (70%):** 3253 rows
- **Validation Set (15%):** 697 rows
- **Test Set (15%):** 698 rows
- **Corridors Evaluated:** 14 Chennai arterial corridors
- **Features Used:** 27 engineered features (Strict zero future leakage)

---

## 2. Model Comparison on Validation Set

| Candidate Model | Val MAE | Val RMSE | Val $R^2$ | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Persistence Baseline** | 16.644 | 22.925 | 0.0765 | Benchmark |
| **Historical Average Baseline** | 2.974 | 4.434 | 0.9655 | Benchmark |
| **Random Forest Regressor** | 2.125 | 3.472 | 0.9788 | Candidate A |
| **Gradient Boosting (HistGBDT)** | **2.071** | **3.361** | **0.9801** | **SELECTED** |

---

## 3. Final Evaluation on Held-Out Test Set

| Evaluation Model | Test MAE | Test RMSE | Test $R^2$ | Improvement vs Persistence |
| :--- | :--- | :--- | :--- | :--- |
| **Persistence Benchmark** | 5.526 | 7.817 | 0.0678 | Baseline (0.0%) |
| **Historical Average Benchmark** | 4.061 | 5.215 | 0.5851 | +26.5% |
| **Selected ML Model (GradientBoostingRegressor (HistGradientBoosting))** | **2.510** | **4.031** | **0.7521** | **+54.6%** |

---

## 4. Multi-Horizon Forecasting Accuracy

| Forecast Horizon | Test MAE | Test RMSE | Test $R^2$ |
| :--- | :--- | :--- | :--- |
| **+15 minutes** | 2.510 | 4.031 | 0.7521 |
| **+30 minutes (Primary)** | 2.510 | 4.031 | 0.7521 |
| **+45 minutes** | 3.695 | 5.927 | 0.4618 |
| **+60 minutes** | 3.695 | 5.927 | 0.4618 |

---

## 5. Artifact Verification

- Model artifact: `C:\Users\haris\OneDrive\Desktop\advmainproject\backend\models\artifacts\traffic_model_30m.joblib`
- Metadata: `C:\Users\haris\OneDrive\Desktop\advmainproject\backend\models\artifacts\model_metadata.json`
- Schema: `C:\Users\haris\OneDrive\Desktop\advmainproject\backend\models\artifacts\feature_schema.json`
- Residual standard deviation (Empirical Uncertainty): `3.885` CI points
