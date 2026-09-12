"""
Unit Tests for Machine Learning Inference Engine and Explainability
Chennai Traffic Intelligence Platform
Tests MLEngine prediction formatting, dynamic feature attribution, and graceful error handling.
"""

import numpy as np
import pandas as pd
from ml.explain import ModelExplainer, FEATURE_DISPLAY_NAMES
from backend.services.ml_engine import MLEngine
from backend.services.ml_adapter import MLPredictionAdapter
from backend.models.schemas import MLPredictionPayload


def test_model_explainer_dynamic_instance_attribution():
    """Verifies that the explainer generates non-static, directionally sound feature drivers."""
    feature_names = ["vehicle_count_lag_1", "speed_lag_1", "rainfall", "congestion_lag_1"]
    explainer = ModelExplainer(
        feature_names=feature_names,
        feature_means={"vehicle_count_lag_1": 2000.0, "speed_lag_1": 35.0, "rainfall": 0.0, "congestion_lag_1": 45.0},
        feature_stds={"vehicle_count_lag_1": 800.0, "speed_lag_1": 10.0, "rainfall": 5.0, "congestion_lag_1": 15.0},
        importances=np.array([0.35, 0.30, 0.20, 0.15])
    )

    # Scenario A: High rain and low speed
    row_storm = pd.Series({
        "vehicle_count_lag_1": 2200.0,
        "speed_lag_1": 12.0,   # Way below normal (should indicate 'increases_congestion')
        "rainfall": 15.0,       # High rain (should indicate 'increases_congestion')
        "congestion_lag_1": 70.0
    })
    exps_storm = explainer.explain_instance(row_storm, top_k=3)

    assert len(exps_storm) == 3
    # Check normalization
    assert abs(sum(e["importance_score"] for e in exps_storm) - 1.0) < 0.05

    # Check directions
    speed_exp = next((e for e in exps_storm if "Speed" in e["feature_name"]), None)
    if speed_exp:
        assert speed_exp["direction"] == "increases_congestion"

    # Scenario B: High speed and dry (free flow)
    row_fast = pd.Series({
        "vehicle_count_lag_1": 800.0,
        "speed_lag_1": 52.0,   # Way above normal (should indicate 'decreases_congestion')
        "rainfall": 0.0,
        "congestion_lag_1": 18.0
    })
    exps_fast = explainer.explain_instance(row_fast, top_k=3)
    speed_exp_fast = next((e for e in exps_fast if "Speed" in e["feature_name"]), None)
    if speed_exp_fast:
        assert speed_exp_fast["direction"] == "decreases_congestion"


def test_ml_adapter_prediction_contract():
    """Verifies that the ML adapter returns properly formatted MLPredictionPayload instances."""
    adapter = MLPredictionAdapter.get_instance()
    pred = adapter.get_prediction("ROAD_ANNA_SALAI_1", horizon="30min", hour=9)

    assert isinstance(pred, MLPredictionPayload)
    assert pred.location_id == "ROAD_ANNA_SALAI_1"
    assert pred.prediction_horizon == "30min"
    assert 0.0 <= pred.predicted_congestion_index <= 100.0
    assert 0.0 <= pred.confidence <= 1.0
    assert pred.predicted_congestion_level in ["Low", "Moderate", "High", "Severe"]
    assert len(pred.top_contributing_features) >= 1
    assert pred.model_version is not None
    # Verify no hardcoded ST-GCN fake strings
    assert "ST-GCN" not in pred.model_version


def test_ml_adapter_all_corridors_predictions():
    """Verifies batch inference retrieval across all monitored corridors."""
    adapter = MLPredictionAdapter.get_instance()
    all_preds = adapter.get_all_predictions(horizon="30min", hour=8)

    assert len(all_preds) >= 12
    road_ids = [p.location_id for p in all_preds]
    assert "ROAD_ANNA_SALAI_1" in road_ids
    assert "ROAD_GST_1" in road_ids
    assert "ROAD_OMR_1" in road_ids


def test_ml_engine_status_reporting():
    """Verifies that MLEngine provides accurate health and provenance status."""
    engine = MLEngine.get_instance()
    status = engine.get_status()

    assert "model_available" in status
    assert "status" in status
    if status["model_available"]:
        assert "model_name" in status
        assert "training_date" in status
        assert "test_metrics" in status
    else:
        assert "error" in status or "instructions" in status
