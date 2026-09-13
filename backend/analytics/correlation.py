"""
Statistical Correlation Engine for Chennai Traffic Intelligence Platform
Computes Pearson correlation coefficients dynamically from active Canonical records.
Adheres to Master PRD: Does NOT claim causation from correlation.
"""

from typing import List, Dict, Any, Optional
import math


def compute_pearson_correlation(x_vals: List[float], y_vals: List[float]) -> Optional[float]:
    """
    Computes Pearson correlation coefficient between two numeric series.
    Returns None if variance is zero or length < 2.
    """
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return None

    n = len(x_vals)
    mean_x = sum(x_vals) / n
    mean_y = sum(y_vals) / n

    numerator = 0.0
    var_x = 0.0
    var_y = 0.0

    for x, y in zip(x_vals, y_vals):
        dx = x - mean_x
        dy = y - mean_y
        numerator += dx * dy
        var_x += dx * dx
        var_y += dy * dy

    denominator = math.sqrt(var_x * var_y)
    if denominator == 0.0:
        return 0.0

    r = numerator / denominator
    # Clamp to [-1.0, 1.0] to handle floating point imprecision
    return round(max(-1.0, min(1.0, r)), 3)


def generate_correlation_matrix(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates dynamic correlation matrix across 5 key canonical dimensions:
    1. vehicle_count (Volume)
    2. average_speed (Speed)
    3. traffic_utilization (Capacity Utilization V/C)
    4. rainfall (Precipitation Intensity)
    5. accident_count (Incident Frequency)
    """
    dimensions = [
        {"key": "vehicle_count", "label": "Vehicle Volume (v/h)"},
        {"key": "average_speed", "label": "Average Speed (km/h)"},
        {"key": "traffic_utilization", "label": "Capacity Utilization (V/C)"},
        {"key": "rainfall", "label": "Rainfall (mm/hr)"},
        {"key": "accident_count", "label": "Accident Count"}
    ]

    labels = [d["label"] for d in dimensions]
    matrix: List[List[Optional[float]]] = []
    explanations: Dict[str, str] = {}

    for i, row_dim in enumerate(dimensions):
        row: List[Optional[float]] = []
        for j, col_dim in enumerate(dimensions):
            if i == j:
                row.append(1.0)
                continue

            # Extract valid paired pairs (filter None)
            x_pairs: List[float] = []
            y_pairs: List[float] = []

            for r in records:
                x_val = r.get(row_dim["key"])
                y_val = r.get(col_dim["key"])
                if x_val is not None and y_val is not None:
                    try:
                        x_pairs.append(float(x_val))
                        y_pairs.append(float(y_val))
                    except (ValueError, TypeError):
                        continue

            corr = compute_pearson_correlation(x_pairs, y_pairs)
            row.append(corr)

            # Generate scientific interpretation without claiming causality
            pair_key = f"{row_dim['key']}_vs_{col_dim['key']}"
            if corr is not None:
                if corr <= -0.6:
                    strength = "Strong negative association"
                elif corr <= -0.3:
                    strength = "Moderate negative association"
                elif corr >= 0.6:
                    strength = "Strong positive association"
                elif corr >= 0.3:
                    strength = "Moderate positive association"
                else:
                    strength = "Weak or negligible linear association"
                explanations[pair_key] = f"{strength} (r = {corr}, N = {len(x_pairs)}). Note: Correlation indicates statistical co-occurrence, not direct physical causality."

        matrix.append(row)

    return {
        "dimensions": labels,
        "variables": labels,
        "dimension_keys": [d["key"] for d in dimensions],
        "correlation_matrix": matrix,
        "matrix": matrix,
        "sample_size": len(records),
        "explanations": explanations,
        "data_state": "DERIVED"
    }
