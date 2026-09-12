"""
Traffic Forecasting Baseline Benchmarks: Chennai Traffic Intelligence
Implements Persistence and Historical Average baselines as mandatory performance hurdles.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes MAE, RMSE, and R-squared."""
    errors = y_true - y_pred
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    ss_res = np.sum(errors ** 2)
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    return {
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 4)
    }


class PersistenceBaseline:
    """
    Persistence Benchmark:
    Assumes traffic at T + horizon will equal current traffic at T.
    y_pred(t+h) = y(t)
    """

    def __init__(self, current_col: str = "congestion_index"):
        self.current_col = current_col

    def fit(self, X: pd.DataFrame, y: np.ndarray = None):
        # Persistence has no parameters to fit
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.current_col not in X.columns:
            # Fallback to lag_1 if current_col not present in feature matrix
            if "congestion_lag_1" in X.columns:
                return X["congestion_lag_1"].values
            raise KeyError(f"Neither {self.current_col} nor congestion_lag_1 found in inputs.")
        return X[self.current_col].values


class HistoricalAverageBaseline:
    """
    Historical Profile Benchmark:
    Predicts using the historical mean congestion for the identical road, hour, and weekend state.
    Fitted strictly on training data.
    """

    def __init__(self):
        self.profile_lookup: Dict[tuple, float] = {}
        self.global_mean: float = 50.0

    def fit(self, X: pd.DataFrame, y: pd.Series):
        df = X.copy()
        df["_target"] = y.values
        self.global_mean = float(y.mean())

        # Group by road_id, hour, is_weekend
        grouped = df.groupby(["road_id", "hour", "is_weekend"])["_target"].mean()
        self.profile_lookup = grouped.to_dict()
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = []
        for _, row in X.iterrows():
            key = (row.get("road_id"), row.get("hour"), row.get("is_weekend"))
            val = self.profile_lookup.get(key, self.global_mean)
            preds.append(val)
        return np.array(preds)
