"""
Unit Tests for Machine Learning Feature Engineering and Target Construction
Tests cyclical transforms, backward lags, rolling stats, neighbor adjacency, and targets.
"""

import pandas as pd
import numpy as np
from ml.preprocessing import TrafficPreprocessor
from ml.features import FeatureEngineer, FEATURE_COLUMNS
from ml.targets import TargetBuilder
from ml.generate_benchmark_data import generate_multiday_benchmark


def _get_cleaned_test_df():
    # Use 3 days of benchmark data for feature testing
    bench = generate_multiday_benchmark(num_days=3, seed=42)
    preprocessor = TrafficPreprocessor()
    return preprocessor.fit_transform(bench["records"])


def test_preprocessing_integrity():
    """Verifies domain-aware cleaning, deduplication, and sanity checking."""
    records = [
        # Normal record
        {"road_id": "R1", "timestamp": "2026-08-30T08:00:00+05:30", "vehicle_count": 1000, "average_speed": 40.0},
        # Duplicate record with slightly updated speed
        {"road_id": "R1", "timestamp": "2026-08-30T08:00:00+05:30", "vehicle_count": 1000, "average_speed": 42.0},
        # Record with negative vehicle count (should be rejected)
        {"road_id": "R1", "timestamp": "2026-08-30T09:00:00+05:30", "vehicle_count": -50, "average_speed": 40.0},
        # Record with missing speed (should be imputed)
        {"road_id": "R1", "timestamp": "2026-08-30T10:00:00+05:30", "vehicle_count": 1200, "average_speed": None},
    ]
    preprocessor = TrafficPreprocessor()
    df_clean = preprocessor.fit_transform(records)

    assert len(df_clean) == 2  # Deduplicated and negative dropped
    assert df_clean.iloc[0]["average_speed"] == 42.0  # Kept last duplicate
    assert not df_clean["average_speed"].isnull().any()  # Imputed


def test_feature_engineering_columns_and_bounds():
    """Verifies all required feature columns are populated and within physical bounds."""
    df_clean = _get_cleaned_test_df()
    engineer = FeatureEngineer()
    df_features = engineer.build_features(df_clean)

    # Check all feature columns are present
    for col in FEATURE_COLUMNS:
        assert col in df_features.columns, f"Missing engineered feature: {col}"
        assert not df_features[col].isnull().any(), f"NaN detected in feature: {col}"

    # Verify cyclical feature bounds
    assert df_features["hour_sin"].between(-1.0, 1.0).all()
    assert df_features["hour_cos"].between(-1.0, 1.0).all()
    assert df_features["day_of_week_sin"].between(-1.0, 1.0).all()
    assert df_features["day_of_week_cos"].between(-1.0, 1.0).all()

    # Verify lags are properly lagged (not constant)
    assert not (df_features["vehicle_count_lag_1"] == df_features["vehicle_count_lag_2"]).all()


def test_target_construction():
    """Verifies target building attaches lead values and correct categorical levels."""
    df_clean = _get_cleaned_test_df()
    engineer = FeatureEngineer()
    df_features = engineer.build_features(df_clean)

    target_builder = TargetBuilder(primary_lead_steps=1)
    df_targets = target_builder.attach_targets(df_features)

    assert "target_congestion_index" in df_targets.columns
    assert "target_congestion_level" in df_targets.columns
    assert "target_speed" in df_targets.columns
    assert "target_vehicle_count" in df_targets.columns

    # Verify levels match documented standards
    valid_levels = {"Low", "Moderate", "High", "Severe"}
    assert set(df_targets["target_congestion_level"].unique()).issubset(valid_levels)
