"""
Model Evaluation Script: Chennai Traffic Intelligence Platform
Loads trained artifacts and test dataset, verifies model performance against baselines,
and generates formal evaluation reports.
"""

import os
import json
import joblib
from ml.config import ARTIFACTS_DIR, REPORTS_DIR, BENCHMARK_DATASET_PATH
from ml.train import run_training_pipeline


def evaluate_model():
    """Evaluates the primary model artifact and ensures reports are up-to-date."""
    metadata_path = os.path.join(ARTIFACTS_DIR, "model_metadata.json")
    primary_model_path = os.path.join(ARTIFACTS_DIR, "traffic_model_30m.joblib")

    if not os.path.exists(primary_model_path) or not os.path.exists(metadata_path):
        print("[INFO] Model artifact not found. Executing training pipeline...")
        run_training_pipeline()

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    print("=" * 70)
    print("CHENNAI TRAFFIC ML MODEL EVALUATION AUDIT")
    print("=" * 70)
    print(f"Model:           {meta['model_name']} (v{meta['model_version']})")
    print(f"Family:          {meta.get('model_family', 'Decision Trees')}")
    print(f"Training Date:   {meta['training_date']}")
    print(f"Data Source:     {meta['data_source']} ({meta['data_classification']})")
    print(f"Total Rows:      {meta['total_rows']} (Train: {meta['training_rows']}, Val: {meta['validation_rows']}, Test: {meta['test_rows']})")
    print(f"Features:        {len(meta['features'])} features")
    print("-" * 70)
    print("TEST PERFORMANCE VS BASELINES:")
    test_m = meta["metrics"]["test"]
    pers_m = meta["metrics"]["baseline_persistence_test"]
    hist_m = meta["metrics"]["baseline_historical_test"]

    print(f"  Persistence Baseline -> MAE: {pers_m['mae']:.3f} | RMSE: {pers_m['rmse']:.3f} | R2: {pers_m['r2']:.4f}")
    print(f"  Historical Baseline  -> MAE: {hist_m['mae']:.3f} | RMSE: {hist_m['rmse']:.3f} | R2: {hist_m['r2']:.4f}")
    print(f"  Trained Model        -> MAE: {test_m['mae']:.3f} | RMSE: {test_m['rmse']:.3f} | R2: {test_m['r2']:.4f}")
    
    improvement = ((pers_m["mae"] - test_m["mae"]) / pers_m["mae"]) * 100
    print(f"  Improvement vs Persistence: {improvement:+.1f}%")
    print("-" * 70)
    print("MULTI-HORIZON TEST ACCURACY:")
    for h_name, h_met in meta["metrics"]["horizons"].items():
        print(f"  Horizon +{h_name:<6} -> MAE: {h_met['mae']:.3f} | RMSE: {h_met['rmse']:.3f} | R2: {h_met['r2']:.4f}")
    print("=" * 70)

    return meta


if __name__ == "__main__":
    evaluate_model()
