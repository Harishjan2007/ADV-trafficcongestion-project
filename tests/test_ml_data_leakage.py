"""
Mandatory Scientific Validity Test: Zero Future Data Leakage
Chennai Traffic Intelligence Platform
Verifies mathematically that feature matrices at timestamp T contain strictly backward-looking
observations and zero leakage from T, T+1, T+2, ...
"""

import pandas as pd
import numpy as np
from ml.preprocessing import TrafficPreprocessor
from ml.features import FeatureEngineer
from ml.generate_benchmark_data import generate_multiday_benchmark


def test_zero_future_leakage_temporal_alignment():
    """
    Asserts that lag_1, lag_2, lag_3 correspond exactly to historical observations
    at T-1, T-2, T-3 and never equal or leak T, T+1.
    """
    bench = generate_multiday_benchmark(num_days=3, seed=42)
    preprocessor = TrafficPreprocessor()
    df_clean = preprocessor.fit_transform(bench["records"])

    engineer = FeatureEngineer()
    df_features = engineer.build_features(df_clean)

    # For a specific corridor, verify each row against past rows
    road_id = "ROAD_ANNA_SALAI_1"
    corridor_raw = df_clean[df_clean["road_id"] == road_id].sort_values("timestamp").reset_index(drop=True)
    corridor_feat = df_features[df_features["road_id"] == road_id].sort_values("timestamp").reset_index(drop=True)

    # Check alignment across all valid rows
    for i in range(len(corridor_feat)):
        ts = corridor_feat.iloc[i]["timestamp"]
        # Find index in raw
        raw_idx = corridor_raw[corridor_raw["timestamp"] == ts].index[0]
        assert raw_idx >= 3, "Cold start rows should have been dropped by feature engineer"

        # Lag 1 at timestamp T MUST equal raw value at T-1
        expected_vol_lag1 = corridor_raw.iloc[raw_idx - 1]["vehicle_count"]
        actual_vol_lag1 = corridor_feat.iloc[i]["vehicle_count_lag_1"]
        assert actual_vol_lag1 == expected_vol_lag1, f"Leakage/misalignment at row {i}: expected {expected_vol_lag1}, got {actual_vol_lag1}"

        # Lag 2 at timestamp T MUST equal raw value at T-2
        expected_vol_lag2 = corridor_raw.iloc[raw_idx - 2]["vehicle_count"]
        actual_vol_lag2 = corridor_feat.iloc[i]["vehicle_count_lag_2"]
        assert actual_vol_lag2 == expected_vol_lag2, f"Lag 2 misalignment at row {i}"

        # Speed Lag 1 MUST equal raw speed at T-1
        expected_spd_lag1 = corridor_raw.iloc[raw_idx - 1]["average_speed"]
        actual_spd_lag1 = corridor_feat.iloc[i]["speed_lag_1"]
        assert actual_spd_lag1 == expected_spd_lag1, f"Speed Lag 1 misalignment at row {i}"


def test_zero_future_leakage_perturbation_test():
    """
    Strict perturbation test:
    Inject an artificial 10x traffic spike at future timestamp T+1.
    Verify that engineered features at timestamp T remain completely identical.
    """
    bench = generate_multiday_benchmark(num_days=3, seed=42)
    preprocessor = TrafficPreprocessor()
    df_clean_original = preprocessor.fit_transform(bench["records"])

    engineer = FeatureEngineer()
    df_feat_original = engineer.build_features(df_clean_original)

    # Select target timestamp T and future timestamp T+1
    road_id = "ROAD_GST_1"
    road_rows = df_clean_original[df_clean_original["road_id"] == road_id].sort_values("timestamp").reset_index(drop=True)
    t_idx = 10
    ts_t = road_rows.iloc[t_idx]["timestamp"]
    ts_future = road_rows.iloc[t_idx + 1]["timestamp"]

    # Create perturbed copy of clean data: modify future observation at T+1
    df_clean_perturbed = df_clean_original.copy()
    mask_future = (df_clean_perturbed["road_id"] == road_id) & (df_clean_perturbed["timestamp"] == ts_future)
    df_clean_perturbed.loc[mask_future, "vehicle_count"] = 99999
    df_clean_perturbed.loc[mask_future, "average_speed"] = 1.0
    df_clean_perturbed.loc[mask_future, "congestion_index"] = 99.9

    df_feat_perturbed = engineer.build_features(df_clean_perturbed)

    # Extract features at timestamp T for both
    feat_t_orig = df_feat_original[(df_feat_original["road_id"] == road_id) & (df_feat_original["timestamp"] == ts_t)].iloc[0]
    feat_t_pert = df_feat_perturbed[(df_feat_perturbed["road_id"] == road_id) & (df_feat_perturbed["timestamp"] == ts_t)].iloc[0]

    # Check lag features at T are untouched
    assert feat_t_orig["vehicle_count_lag_1"] == feat_t_pert["vehicle_count_lag_1"], "Future perturbation leaked into vehicle_count_lag_1!"
    assert feat_t_orig["speed_lag_1"] == feat_t_pert["speed_lag_1"], "Future perturbation leaked into speed_lag_1!"
    assert feat_t_orig["rolling_speed_mean_3h"] == feat_t_pert["rolling_speed_mean_3h"], "Future perturbation leaked into rolling_speed_mean_3h!"
    assert feat_t_orig["rolling_vol_mean_3h"] == feat_t_pert["rolling_vol_mean_3h"], "Future perturbation leaked into rolling_vol_mean_3h!"


def test_rolling_statistics_exclude_current_time():
    """
    Asserts that rolling 3-hour mean at timestamp T does not include the observation at T.
    Perturbing observation at T must NOT change rolling_speed_mean_3h at T.
    """
    bench = generate_multiday_benchmark(num_days=3, seed=42)
    preprocessor = TrafficPreprocessor()
    df_clean_original = preprocessor.fit_transform(bench["records"])

    engineer = FeatureEngineer()
    df_feat_original = engineer.build_features(df_clean_original)

    road_id = "ROAD_OMR_1"
    road_rows = df_clean_original[df_clean_original["road_id"] == road_id].sort_values("timestamp").reset_index(drop=True)
    t_idx = 8
    ts_t = road_rows.iloc[t_idx]["timestamp"]

    # Perturb observation at T
    df_clean_perturbed = df_clean_original.copy()
    mask_curr = (df_clean_perturbed["road_id"] == road_id) & (df_clean_perturbed["timestamp"] == ts_t)
    df_clean_perturbed.loc[mask_curr, "average_speed"] = 2.0  # Massive speed drop at T

    df_feat_perturbed = engineer.build_features(df_clean_perturbed)

    feat_t_orig = df_feat_original[(df_feat_original["road_id"] == road_id) & (df_feat_original["timestamp"] == ts_t)].iloc[0]
    feat_t_pert = df_feat_perturbed[(df_feat_perturbed["road_id"] == road_id) & (df_feat_perturbed["timestamp"] == ts_t)].iloc[0]

    # The rolling mean at T must be based only on T-1, T-2, T-3, so it MUST NOT change
    assert feat_t_orig["rolling_speed_mean_3h"] == feat_t_pert["rolling_speed_mean_3h"], (
        "Current observation leaked into rolling_speed_mean_3h at timestamp T!"
    )
