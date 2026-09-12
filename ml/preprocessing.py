"""
Data Preprocessing and Validation Pipeline: Chennai Traffic Intelligence
Applies domain-aware data validation, missing value imputation, duplicate resolution,
and canonical road-time indexing.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List


class TrafficPreprocessor:
    """
    Cleans raw traffic records, validates physical feasibility constraints,
    resolves duplicates, and imputes missing fields using time-series continuity.
    """

    def __init__(self):
        self.validation_stats: Dict[str, Any] = {}

    def fit_transform(self, raw_records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converts raw list of dicts to a validated, chronologically sorted DataFrame."""
        df = pd.DataFrame(raw_records)
        if df.empty:
            raise ValueError("Input records list is empty.")

        # 1. Validate mandatory fields
        required_cols = ["road_id", "timestamp", "vehicle_count", "average_speed"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise KeyError(f"Missing mandatory columns: {missing_cols}")

        initial_count = len(df)

        # 2. Timestamp Parsing & Sorting
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(["road_id", "timestamp"]).reset_index(drop=True)

        # 3. Deduplication on (road_id, timestamp)
        before_dedup = len(df)
        df = df.drop_duplicates(subset=["road_id", "timestamp"], keep="last")
        dedup_dropped = before_dedup - len(df)

        # Environmental defaults if not present
        if "rainfall" not in df.columns:
            df["rainfall"] = 0.0
        else:
            df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce").fillna(0.0)

        # 4. Reject Physically Impossible Values
        # Negative counts or speeds, or invalid speeds/precipitation
        invalid_mask = (
            (df["vehicle_count"] < 0) |
            (df["average_speed"] < 0) |
            (df["rainfall"] < 0)
        )
        invalid_dropped = int(invalid_mask.sum())
        df = df[~invalid_mask].copy()

        # Cap physical extremes based on road capacity and speed limits
        if "road_capacity" in df.columns:
            # Vehicle count cannot exceed 1.8x design capacity even in severe jam
            df["vehicle_count"] = df.apply(
                lambda r: min(r["vehicle_count"], r["road_capacity"] * 1.8) if pd.notnull(r.get("road_capacity")) else r["vehicle_count"],
                axis=1
            )

        if "speed_limit" in df.columns:
            # Average speed cannot exceed 1.3x speed limit on monitored urban corridors
            df["average_speed"] = df.apply(
                lambda r: min(r["average_speed"], r["speed_limit"] * 1.3) if pd.notnull(r.get("speed_limit")) else r["average_speed"],
                axis=1
            )

        # 5. Missing Value Imputation
        # Group by road_id and forward-fill / backward-fill time series
        numeric_cols = ["vehicle_count", "average_speed", "congestion_index", "rainfall", "temperature"]
        for col in numeric_cols:
            if col in df.columns:
                # Forward fill within road_id
                df[col] = df.groupby("road_id")[col].transform(lambda s: s.ffill().bfill())
                # Fallback to global median (or 0.0 for rainfall) if an entire road had missing values
                if df[col].isnull().any():
                    fallback = 0.0 if col == "rainfall" else df[col].median()
                    df[col] = df[col].fillna(fallback)

        # Categoricals
        if "weather_condition" in df.columns:
            df["weather_condition"] = df["weather_condition"].fillna("Clear")
        if "accident_count" in df.columns:
            df["accident_count"] = df["accident_count"].fillna(0).astype(int)

        # 6. Canonical Congestion Index Calculation (if missing or needs verification)
        if "congestion_index" not in df.columns or df["congestion_index"].isnull().all():
            limit = df["speed_limit"] if "speed_limit" in df.columns else 50.0
            cap = df["road_capacity"] if "road_capacity" in df.columns else 3600.0
            speed_deficit = np.maximum(0.0, (limit - df["average_speed"]) / limit)
            util = np.minimum(1.0, (df["vehicle_count"] / cap) / 1.2)
            df["congestion_index"] = np.round((0.45 * util * 100.0) + (0.55 * speed_deficit * 100.0), 1)
            df["congestion_index"] = df["congestion_index"].clip(0.0, 100.0)

        self.validation_stats = {
            "initial_rows": initial_count,
            "final_rows": len(df),
            "duplicates_removed": dedup_dropped,
            "invalid_rows_removed": invalid_dropped,
            "unique_corridors": df["road_id"].nunique(),
            "time_range_start": str(df["timestamp"].min()),
            "time_range_end": str(df["timestamp"].max())
        }

        return df
