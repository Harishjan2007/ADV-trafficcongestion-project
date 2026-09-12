"""
Feature Engineering Pipeline: Chennai Traffic Intelligence
Builds strictly backward-looking temporal, cyclical, lag, rolling, spatial, and weather features.
Enforces zero future-data leakage.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any


FEATURE_COLUMNS = [
    # Cyclical Time
    "hour_sin", "hour_cos", "day_of_week_sin", "day_of_week_cos",
    # Temporal Flags
    "is_weekend", "is_peak_hour", "hour",
    # Corridor Static Context
    "road_capacity", "speed_limit", "lane_count",
    # Backward Traffic Lags
    "vehicle_count_lag_1", "vehicle_count_lag_2", "vehicle_count_lag_3",
    "speed_lag_1", "speed_lag_2", "speed_lag_3",
    "congestion_lag_1", "congestion_lag_2",
    # Rolling Historical Statistics (shift(1) to avoid current-time/future leakage)
    "rolling_speed_mean_3h", "rolling_vol_mean_3h", "rolling_ci_mean_3h", "rolling_ci_std_3h",
    # Spatial Network Neighbor Congestion Lag
    "neighbor_congestion_lag_1",
    # Contextual Weather & Incidents
    "rainfall", "temperature", "is_raining", "accident_lag_1"
]


class FeatureEngineer:
    """
    Transforms preprocessed time series into feature matrices for supervised forecasting.
    Guarantees no future leakage by applying strict chronological group shifts.
    """

    def __init__(self, neighbor_map: Dict[str, List[str]] = None):
        # Default spatial adjacency based on Chennai network topology
        self.neighbor_map = neighbor_map or {
            "ROAD_ANNA_SALAI_1": ["ROAD_ANNA_SALAI_2", "ROAD_PH_1", "ROAD_MARINA_1"],
            "ROAD_ANNA_SALAI_2": ["ROAD_ANNA_SALAI_1", "ROAD_GST_1", "ROAD_SP_ROAD_1"],
            "ROAD_GST_1": ["ROAD_ANNA_SALAI_2", "ROAD_GST_2", "ROAD_100FT_1", "ROAD_MOUNT_POON_1"],
            "ROAD_GST_2": ["ROAD_GST_1", "ROAD_ECR_1"],
            "ROAD_OMR_1": ["ROAD_SP_ROAD_1", "ROAD_OMR_2", "ROAD_ECR_1"],
            "ROAD_OMR_2": ["ROAD_OMR_1", "ROAD_ECR_1"],
            "ROAD_PH_1": ["ROAD_ANNA_SALAI_1", "ROAD_PH_2", "ROAD_100FT_1"],
            "ROAD_PH_2": ["ROAD_PH_1", "ROAD_ARCOT_1"],
            "ROAD_100FT_1": ["ROAD_PH_1", "ROAD_ARCOT_1", "ROAD_GST_1"],
            "ROAD_ECR_1": ["ROAD_OMR_1", "ROAD_OMR_2", "ROAD_GST_2"],
            "ROAD_MOUNT_POON_1": ["ROAD_GST_1", "ROAD_ARCOT_1"],
            "ROAD_ARCOT_1": ["ROAD_100FT_1", "ROAD_MOUNT_POON_1", "ROAD_PH_2"],
            "ROAD_SP_ROAD_1": ["ROAD_ANNA_SALAI_2", "ROAD_OMR_1"],
            "ROAD_MARINA_1": ["ROAD_ANNA_SALAI_1", "ROAD_SP_ROAD_1"]
        }

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates full feature set from cleaned records dataframe.
        Input dataframe must have: ['road_id', 'timestamp', 'vehicle_count', 'average_speed', 'congestion_index']
        """
        data = df.copy()
        data = data.sort_values(["road_id", "timestamp"]).reset_index(drop=True)

        # 1. Temporal & Cyclical Features
        ts = pd.to_datetime(data["timestamp"])
        hour = ts.dt.hour
        day_of_week = ts.dt.dayofweek

        data["hour"] = hour
        data["minute"] = ts.dt.minute
        data["day_of_week"] = day_of_week
        data["is_weekend"] = day_of_week.isin([5, 6]).astype(int)

        # Peak hours: 8-11 and 17-20 on weekdays
        is_morning = (hour >= 8) & (hour <= 11)
        is_evening = (hour >= 17) & (hour <= 20)
        data["is_peak_hour"] = ((is_morning | is_evening) & (data["is_weekend"] == 0)).astype(int)

        # Cyclical transformations
        data["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
        data["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)
        data["day_of_week_sin"] = np.sin(2 * np.pi * day_of_week / 7.0)
        data["day_of_week_cos"] = np.cos(2 * np.pi * day_of_week / 7.0)

        # 2. Historical Lag Features (Per Road)
        # Strictly shift(k) where k >= 1
        grouped = data.groupby("road_id")

        data["vehicle_count_lag_1"] = grouped["vehicle_count"].shift(1)
        data["vehicle_count_lag_2"] = grouped["vehicle_count"].shift(2)
        data["vehicle_count_lag_3"] = grouped["vehicle_count"].shift(3)

        data["speed_lag_1"] = grouped["average_speed"].shift(1)
        data["speed_lag_2"] = grouped["average_speed"].shift(2)
        data["speed_lag_3"] = grouped["average_speed"].shift(3)

        data["congestion_lag_1"] = grouped["congestion_index"].shift(1)
        data["congestion_lag_2"] = grouped["congestion_index"].shift(2)

        if "accident_count" in data.columns:
            data["accident_lag_1"] = grouped["accident_count"].shift(1).fillna(0)
        else:
            data["accident_lag_1"] = 0

        # 3. Rolling Statistics (Shifted by 1 so the current window is excluded)
        # rolling on shift(1) ensures that observation at T is NOT used to predict T
        data["rolling_speed_mean_3h"] = grouped["average_speed"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
        data["rolling_vol_mean_3h"] = grouped["vehicle_count"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
        data["rolling_ci_mean_3h"] = grouped["congestion_index"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
        data["rolling_ci_std_3h"] = grouped["congestion_index"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).std()).fillna(0.0)

        # 4. Spatial Neighbor Congestion (Average congestion of adjacent corridors at T-1)
        ci_lag1_lookup = data.set_index(["timestamp", "road_id"])["congestion_lag_1"].to_dict()

        def compute_neighbor_ci(row):
            rid = row["road_id"]
            ts_val = row["timestamp"]
            neighbors = self.neighbor_map.get(rid, [])
            vals = [ci_lag1_lookup.get((ts_val, n)) for n in neighbors if (ts_val, n) in ci_lag1_lookup]
            valid_vals = [v for v in vals if v is not None and not np.isnan(v)]
            return np.mean(valid_vals) if valid_vals else row["congestion_lag_1"]

        data["neighbor_congestion_lag_1"] = data.apply(compute_neighbor_ci, axis=1)

        # 5. Weather Context
        if "rainfall" not in data.columns:
            data["rainfall"] = 0.0
        if "temperature" not in data.columns:
            data["temperature"] = 30.0

        data["is_raining"] = (data["rainfall"] > 0.0).astype(int)

        # 6. Static Physical Corridor Attributes
        if "road_capacity" not in data.columns:
            data["road_capacity"] = 3600
        if "speed_limit" not in data.columns:
            data["speed_limit"] = 50.0
        if "lane_count" not in data.columns:
            data["lane_count"] = 3

        # Drop initial rows where lag_3 is NaN (cold start rows)
        clean_features = data.dropna(subset=["vehicle_count_lag_3", "speed_lag_3", "congestion_lag_2"]).copy()

        return clean_features
