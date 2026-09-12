"""
Unit Tests for Machine Learning Training and Candidate Models
Chennai Traffic Intelligence Platform
Verifies candidate model construction, multi-horizon support, training, and artifact validity.
"""

import os
import joblib
import numpy as np
import pandas as pd
from ml.models import build_random_forest_model, build_gradient_boosting_model, MultiHorizonTrafficModel
from ml.baselines import calculate_metrics


def _get_dummy_dataset(n_samples: int = 150):
    np.random.seed(42)
    # Generate simple linear + non-linear synthetic relationship
    X = pd.DataFrame({
        "vehicle_count_lag_1": np.random.uniform(500, 4000, n_samples),
        "speed_lag_1": np.random.uniform(10, 60, n_samples),
        "congestion_lag_1": np.random.uniform(10, 90, n_samples),
        "hour_sin": np.random.uniform(-1, 1, n_samples),
        "hour_cos": np.random.uniform(-1, 1, n_samples),
        "is_peak_hour": np.random.choice([0, 1], n_samples),
        "road_capacity": [3600] * n_samples,
        "speed_limit": [50.0] * n_samples
    })
    # Target influenced by congestion_lag_1 and speed_lag_1
    y = np.clip(
        0.7 * X["congestion_lag_1"] - 0.3 * X["speed_lag_1"] + 0.005 * X["vehicle_count_lag_1"] + np.random.normal(0, 3, n_samples),
        0.0, 100.0
    ).values
    return X, y


def test_candidate_models_fit_and_predict():
    """Verifies both Random Forest and HistGradientBoosting fit cleanly and yield valid predictions."""
    X, y = _get_dummy_dataset()
    train_x, test_x = X.iloc[:100], X.iloc[100:]
    train_y, test_y = y[:100], y[100:]

    # Test Random Forest
    rf = build_random_forest_model({"n_estimators": 20, "max_depth": 6})
    rf.fit(train_x, train_y)
    rf_preds = rf.predict(test_x)
    assert len(rf_preds) == len(test_x)
    assert np.var(rf_preds) > 1.0, "Predictions should not be trivial/constant"
    rf_metrics = calculate_metrics(test_y, rf_preds)
    assert rf_metrics["mae"] < 25.0
    assert rf_metrics["r2"] > 0.40

    # Test Gradient Boosting
    gb = build_gradient_boosting_model({"max_iter": 30, "max_depth": 4})
    gb.fit(train_x, train_y)
    gb_preds = gb.predict(test_x)
    assert len(gb_preds) == len(test_x)
    assert np.var(gb_preds) > 1.0
    gb_metrics = calculate_metrics(test_y, gb_preds)
    assert gb_metrics["mae"] < 25.0
    assert gb_metrics["r2"] > 0.40


def test_non_trivial_prediction_sensitivity():
    """
    Asserts that changing traffic state from free-flow to congested
    produces substantially distinct predictions (non-constant model behavior).
    """
    X, y = _get_dummy_dataset()
    gb = build_gradient_boosting_model({"max_iter": 40})
    gb.fit(X, y)

    # State A: Free flow (low vol, high spd, low ci)
    state_free_flow = pd.DataFrame([{
        "vehicle_count_lag_1": 600.0,
        "speed_lag_1": 55.0,
        "congestion_lag_1": 15.0,
        "hour_sin": 0.0,
        "hour_cos": 1.0,
        "is_peak_hour": 0,
        "road_capacity": 3600,
        "speed_limit": 50.0
    }])

    # State B: Severe jam (high vol, low spd, high ci)
    state_severe_jam = pd.DataFrame([{
        "vehicle_count_lag_1": 4200.0,
        "speed_lag_1": 8.0,
        "congestion_lag_1": 85.0,
        "hour_sin": 0.5,
        "hour_cos": -0.8,
        "is_peak_hour": 1,
        "road_capacity": 3600,
        "speed_limit": 50.0
    }])

    pred_free = gb.predict(state_free_flow)[0]
    pred_jam = gb.predict(state_severe_jam)[0]

    assert pred_jam > pred_free + 20.0, f"Model failed sensitivity test: free={pred_free}, jam={pred_jam}"


def test_multi_horizon_model_wrapper():
    """Verifies multi-horizon manager trains and predicts across distinct horizons."""
    X, y = _get_dummy_dataset()
    multi = MultiHorizonTrafficModel("gradient_boosting")

    multi.fit_horizon("15min", X, y)
    multi.fit_horizon("30min", X, y * 1.05)

    p15 = multi.predict("15min", X.iloc[:5])
    p30 = multi.predict("30min", X.iloc[:5])

    assert len(p15) == 5
    assert len(p30) == 5
