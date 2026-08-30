"""
Unit Tests for Data Normalization & Canonical Metric Engine
Validates formulas in docs/data-contract.md
"""

from backend.services.normalizer import calculate_derived_metrics, normalize_raw_record


def test_calculate_derived_metrics_free_flow():
    # Free flow scenario: Low volume, high speed
    res = calculate_derived_metrics(
        vehicle_count=500,
        average_speed=48.0,
        road_capacity=4000,
        speed_limit=50.0,
        accident_count=0,
        is_peak_hour=False
    )
    assert res["congestion_level"] == "Low"
    assert res["congestion_index"] < 30.0
    assert res["priority_level"] == "Low"
    assert res["traffic_utilization"] == 0.125


def test_calculate_derived_metrics_severe_congestion():
    # Severe bottleneck scenario: High volume, low speed + 1 incident
    res = calculate_derived_metrics(
        vehicle_count=3900,
        average_speed=12.0,
        road_capacity=4000,
        speed_limit=50.0,
        accident_count=1,
        is_peak_hour=True
    )
    assert res["congestion_level"] == "Severe"
    assert res["congestion_index"] >= 75.0
    assert res["priority_level"] == "Critical"
    assert res["speed_reduction"] == 0.76


def test_normalize_raw_record_defensive_fallbacks():
    # Ingestion record with missing optional weather & accident fields
    raw = {
        "road_id": "ROAD_TEST_1",
        "road_name": "Anna Salai Segment Test",
        "hour": 9,
        "vehicle_count": 2800,
        "average_speed": 22.0
    }
    canonical = normalize_raw_record(raw)
    assert canonical["record_id"] == "REC_ROAD_TEST_1_0900"
    assert canonical["peak_hour_flag"] is True
    assert canonical["weather_condition"] is None
    assert canonical["accident_count"] == 0
    assert canonical["speed_limit"] == 50.0
    assert "congestion_index" in canonical
