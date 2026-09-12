"""
Target Variable Construction & Categorical Mapping
Chennai Traffic Intelligence Platform
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
from ml.config import get_congestion_level, PRIMARY_TARGET


class TargetBuilder:
    """
    Constructs forward-looking supervised regression targets and discrete congestion labels.
    Never uses target timestamp information in feature inputs.
    """

    def __init__(self, primary_lead_steps: int = 1):
        # 1 step = next time slice (+30m to +60m depending on sampling frequency)
        self.primary_lead_steps = primary_lead_steps

    def attach_targets(self, df: pd.DataFrame, lead_steps: int = None) -> pd.DataFrame:
        """
        Attaches forward target values: target_congestion_index, target_speed, target_volume.
        Drops trailing rows per corridor that do not have forward target ground truth.
        """
        lead = lead_steps if lead_steps is not None else self.primary_lead_steps
        data = df.copy()
        data = data.sort_values(["road_id", "timestamp"]).reset_index(drop=True)

        grouped = data.groupby("road_id")

        # Forward target shift(-lead)
        data["target_congestion_index"] = grouped["congestion_index"].shift(-lead)
        data["target_speed"] = grouped["average_speed"].shift(-lead)
        data["target_vehicle_count"] = grouped["vehicle_count"].shift(-lead)

        # Drop records where forward target is unavailable (end of series)
        valid_data = data.dropna(subset=["target_congestion_index"]).copy()

        # Categorical label for target
        valid_data["target_congestion_level"] = valid_data["target_congestion_index"].apply(get_congestion_level)

        return valid_data

    @staticmethod
    def map_level_to_int(level: str) -> int:
        mapping = {"Low": 0, "Moderate": 1, "High": 2, "Severe": 3}
        return mapping.get(level, 0)

    @staticmethod
    def map_int_to_level(val: int) -> str:
        reverse = {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"}
        return reverse.get(val, "Low")
