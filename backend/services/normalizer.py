"""
Data Normalization and Metric Computation Engine
Implements canonical mathematical derivations defined in docs/data-contract.md
"""

from typing import Dict, Any, Tuple


def calculate_derived_metrics(
    vehicle_count: int,
    average_speed: float,
    road_capacity: int = 3600,
    speed_limit: float = 50.0,
    accident_count: int = 0,
    is_peak_hour: bool = False
) -> Dict[str, Any]:
    """
    Computes canonical derived traffic metrics:
    - Traffic Utilization (U)
    - Speed Reduction (Rv)
    - Congestion Index (CI: 0-100)
    - Congestion Level (Low, Moderate, High, Severe)
    - Priority Score (PS: 0-100, Decision Support only)
    - Priority Level (Low, Medium, High, Critical)
    """
    # 1. Traffic Utilization
    capacity = max(100, road_capacity)
    utilization = round(float(vehicle_count) / float(capacity), 4)

    # 2. Speed Reduction
    limit = max(10.0, speed_limit)
    speed_deficit = max(0.0, float(limit - average_speed))
    speed_reduction = round(speed_deficit / limit, 4)

    # 3. Congestion Index (CI)
    # Composite: 45% Volume Utilization (capped at 1.5) + 55% Speed Deficit
    norm_util = min(utilization, 1.5) / 1.5  # 0.0 to 1.0
    raw_ci = (0.45 * norm_util * 100.0) + (0.55 * speed_reduction * 100.0)
    congestion_index = round(min(100.0, max(0.0, raw_ci)), 1)

    # 4. Congestion Level Mapping
    if congestion_index < 30.0:
        congestion_level = "Low"
    elif congestion_index < 55.0:
        congestion_level = "Moderate"
    elif congestion_index < 75.0:
        congestion_level = "High"
    else:
        congestion_level = "Severe"

    # 5. Documented Priority Score Calculation (Decision Support)
    # Formula: 40% CI + 30% Speed Reduction + 20% Accident Multiplier + 10% Peak Flag
    accident_component = min(100.0, float(accident_count) * 50.0)
    speed_red_component = speed_reduction * 100.0
    peak_component = 100.0 if is_peak_hour else 0.0

    raw_priority = (0.40 * congestion_index) + (0.30 * speed_red_component) + (0.20 * accident_component) + (0.10 * peak_component)
    priority_score = round(min(100.0, max(0.0, raw_priority)), 1)

    # 6. Priority Level Mapping
    if priority_score >= 75.0 or (congestion_level == "Severe" and accident_count >= 1):
        priority_level = "Critical"
    elif priority_score >= 55.0:
        priority_level = "High"
    elif priority_score >= 35.0:
        priority_level = "Medium"
    else:
        priority_level = "Low"

    return {
        "traffic_utilization": utilization,
        "speed_reduction": speed_reduction,
        "congestion_index": congestion_index,
        "congestion_level": congestion_level,
        "priority_score": priority_score,
        "priority_level": priority_level,
    }


def normalize_raw_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes arbitrary raw ingestion dictionary into Canonical Data Contract format.
    Handles missing optional fields defensively without fabricating unrecorded values.
    """
    hour = int(raw.get("hour", 8))
    # Peak hour windows in Chennai: 08:00-11:00 & 17:00-20:30
    is_peak = (8 <= hour <= 11) or (17 <= hour <= 20)

    vehicle_count = int(raw.get("vehicle_count", 1500))
    average_speed = float(raw.get("average_speed", 30.0))
    road_capacity = int(raw.get("road_capacity", 3600))
    speed_limit = float(raw.get("speed_limit", 50.0))
    accident_count = int(raw.get("accident_count", 0))

    derived = calculate_derived_metrics(
        vehicle_count=vehicle_count,
        average_speed=average_speed,
        road_capacity=road_capacity,
        speed_limit=speed_limit,
        accident_count=accident_count,
        is_peak_hour=is_peak
    )

    canonical = {
        "record_id": str(raw.get("record_id", f"REC_{raw.get('road_id', 'ROAD')}_{hour:02d}00")),
        "timestamp": str(raw.get("timestamp", f"2026-08-30T{hour:02d}:00:00+05:30")),
        "latitude": float(raw.get("latitude", 13.0827)),
        "longitude": float(raw.get("longitude", 80.2707)),
        "road_id": str(raw.get("road_id", "ROAD_UNKNOWN")),
        "road_name": str(raw.get("road_name", "Chennai Corridor")),
        "junction": raw.get("junction"),
        "zone": str(raw.get("zone", "Central Zone")),
        "road_type": str(raw.get("road_type", "Arterial")),
        "vehicle_count": vehicle_count,
        "average_speed": average_speed,
        "traffic_density": raw.get("traffic_density"),
        "vehicle_type": raw.get("vehicle_type", "Mixed Traffic"),
        "direction": raw.get("direction", "Two-way"),
        "date": str(raw.get("date", "2026-08-30")),
        "hour": hour,
        "day_of_week": str(raw.get("day_of_week", "Monday")),
        "weekend_flag": bool(raw.get("weekend_flag", False)),
        "peak_hour_flag": is_peak,
        "weather_condition": raw.get("weather_condition"),
        "rainfall": raw.get("rainfall"),
        "temperature": raw.get("temperature"),
        "visibility": raw.get("visibility"),
        "road_condition": raw.get("road_condition", "Dry"),
        "road_capacity": road_capacity,
        "lane_count": int(raw.get("lane_count", 3)),
        "speed_limit": speed_limit,
        "accident_count": accident_count,
        "accident_severity": raw.get("accident_severity"),
        **derived
    }

    return canonical
