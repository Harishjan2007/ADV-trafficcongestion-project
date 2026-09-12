"""
Unit Tests for Traffic Forecasting Benchmark Baselines
Tests Persistence Baseline and Historical Average Baseline performance and metrics computation.
"""

import numpy as np
import pandas as pd
from ml.baselines import PersistenceBaseline, HistoricalAverageBaseline, calculate_metrics


def test_calculate_metrics_exact_values():
    """Verifies standard regression metrics calculation."""
    y_true = np.array([10.0, 20.0, 30.0, 40.0])
    y_pred = np.array([12.0, 19.0, 32.0, 37.0])  # errors: +2, -1, +2, -3

    # MAE = (|2| + |1| + |2| + |3|) / 4 = 8 / 4 = 2.0
    # RMSE = sqrt((4 + 1 + 4 + 9) / 4) = sqrt(18 / 4) = sqrt(4.5) ≈ 2.121
    m = calculate_metrics(y_true, y_pred)
    assert m["mae"] == 2.0
    assert abs(m["rmse"] - 2.121) < 0.01
    assert m["r2"] > 0.90


def test_persistence_baseline_logic():
    """Verifies that persistence baseline predicts current state into the future."""
    df = pd.DataFrame({
        "congestion_index": [35.0, 55.0, 80.0],
        "congestion_lag_1": [30.0, 50.0, 75.0]
    })
    pers = PersistenceBaseline(current_col="congestion_index")
    preds = pers.predict(df)
    assert list(preds) == [35.0, 55.0, 80.0]

    # Test fallback to lag_1
    df_no_curr = pd.DataFrame({
        "congestion_lag_1": [30.0, 50.0, 75.0]
    })
    pers2 = PersistenceBaseline(current_col="congestion_index")
    preds2 = pers2.predict(df_no_curr)
    assert list(preds2) == [30.0, 50.0, 75.0]


def test_historical_average_baseline_grouping():
    """Verifies fitting and lookup by (road_id, hour, is_weekend)."""
    train_df = pd.DataFrame({
        "road_id": ["R1", "R1", "R1", "R2"],
        "hour": [9, 9, 10, 9],
        "is_weekend": [0, 0, 0, 0]
    })
    y_train = pd.Series([60.0, 70.0, 40.0, 50.0])

    hist = HistoricalAverageBaseline()
    hist.fit(train_df, y_train)

    # R1 at hour 9 should average (60 + 70) / 2 = 65.0
    test_df = pd.DataFrame({
        "road_id": ["R1", "R1", "R2", "UNKNOWN"],
        "hour": [9, 10, 9, 9],
        "is_weekend": [0, 0, 0, 0]
    })
    preds = hist.predict(test_df)

    assert preds[0] == 65.0
    assert preds[1] == 40.0
    assert preds[2] == 50.0
    assert preds[3] == hist.global_mean  # Fallback for unknown road
