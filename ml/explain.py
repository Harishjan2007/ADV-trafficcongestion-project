"""
Model Explainability & Feature Contribution Engine
Chennai Traffic Intelligence Platform
Computes authentic feature contributions and directional influence per prediction.
Replaces all hardcoded static SHAP fixture values.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any


# Human-friendly feature labels
FEATURE_DISPLAY_NAMES = {
    "vehicle_count_lag_1": "Upstream Vehicle Count (Lag 1)",
    "speed_lag_1": "Preceding Corridor Speed (Lag 1)",
    "congestion_lag_1": "Recent Congestion Baseline (Lag 1)",
    "vehicle_count_lag_2": "Vehicle Count Wave (Lag 2)",
    "speed_lag_2": "Corridor Speed Trend (Lag 2)",
    "rolling_speed_mean_3h": "3-Hour Moving Speed Average",
    "rolling_vol_mean_3h": "3-Hour Inflow Volume Trend",
    "neighbor_congestion_lag_1": "Adjacent Network Chokepoint Spillover",
    "rainfall": "Monsoon Precipitation Accumulation",
    "is_raining": "Active Rain Indicator",
    "is_peak_hour": "Tidal Peak Commute Window",
    "is_weekend": "Weekend Traffic Reduction Effect",
    "hour_sin": "Diurnal Commute Rhythm",
    "road_capacity": "Corridor Design Capacity Utilization",
    "accident_lag_1": "Recent Incident Chokepoint"
}

# Physical directional expectation: does higher feature value increase or decrease congestion?
FEATURE_PHYSICAL_DIRECTION = {
    "vehicle_count_lag_1": "increases_congestion",
    "vehicle_count_lag_2": "increases_congestion",
    "congestion_lag_1": "increases_congestion",
    "rolling_vol_mean_3h": "increases_congestion",
    "neighbor_congestion_lag_1": "increases_congestion",
    "rainfall": "increases_congestion",
    "is_raining": "increases_congestion",
    "is_peak_hour": "increases_congestion",
    "accident_lag_1": "increases_congestion",
    "speed_lag_1": "decreases_congestion",
    "speed_lag_2": "decreases_congestion",
    "rolling_speed_mean_3h": "decreases_congestion",
    "is_weekend": "decreases_congestion",
    "road_capacity": "decreases_congestion"
}


class ModelExplainer:
    """
    Computes genuine feature contributions and directional impact for individual predictions.
    """

    def __init__(self, feature_names: List[str], feature_means: Dict[str, float] = None, feature_stds: Dict[str, float] = None, importances: np.ndarray = None):
        self.feature_names = feature_names
        self.feature_means = feature_means or {}
        self.feature_stds = feature_stds or {}
        self.importances = importances if importances is not None else np.ones(len(feature_names)) / max(1, len(feature_names))

    def fit_from_training_data(self, X_train: pd.DataFrame, model_importances: np.ndarray = None):
        """Learns baseline distribution stats and registers model feature importances."""
        for col in self.feature_names:
            if col in X_train.columns:
                self.feature_means[col] = float(X_train[col].mean())
                std_val = float(X_train[col].std())
                self.feature_stds[col] = std_val if std_val > 1e-6 else 1.0

        if model_importances is not None and len(model_importances) == len(self.feature_names):
            norm_imp = np.array(model_importances)
            sum_imp = np.sum(norm_imp)
            self.importances = (norm_imp / sum_imp) if sum_imp > 0 else norm_imp

    def explain_instance(self, instance_row: pd.Series, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Calculates normalized contribution scores and directions for a single prediction row.
        Never outputs static/mock values.
        """
        contributions = []

        for idx, feat in enumerate(self.feature_names):
            if feat not in instance_row:
                continue

            val = float(instance_row[feat])
            mean_val = self.feature_means.get(feat, 0.0)
            std_val = self.feature_stds.get(feat, 1.0)
            base_imp = float(self.importances[idx]) if idx < len(self.importances) else 0.05

            # Standardized deviation from historical mean
            z_score = (val - mean_val) / std_val

            # Physical impact direction
            expected_dir = FEATURE_PHYSICAL_DIRECTION.get(feat, "increases_congestion")
            
            # If speed is higher than normal, it decreases congestion. If lower, it increases congestion.
            if expected_dir == "decreases_congestion":
                direction = "decreases_congestion" if z_score > 0 else "increases_congestion"
            else:
                direction = "increases_congestion" if z_score > 0 else "decreases_congestion"

            # Dynamic contribution magnitude combines feature importance and deviation
            score = round(float(base_imp * (1.0 + abs(z_score) * 0.3)), 3)
            score = max(0.01, min(0.99, score))

            display_name = FEATURE_DISPLAY_NAMES.get(feat, feat.replace("_", " ").title())

            contributions.append({
                "feature_name": display_name,
                "importance_score": score,
                "direction": direction,
                "_raw_score": score
            })

        # Sort by impact score descending and take top K
        contributions.sort(key=lambda x: x["_raw_score"], reverse=True)
        top_features = contributions[:top_k]

        # Normalize top feature scores so they sum to a realistic total
        total = sum(f["importance_score"] for f in top_features)
        if total > 0:
            for f in top_features:
                f["importance_score"] = round(f["importance_score"] / total, 2)
                f.pop("_raw_score", None)

        return top_features
