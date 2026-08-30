"""
Unit Tests for Coordinated Multi-Filters
Validates simultaneous filtering across zone, severity, and temporal windows.
"""

from backend.services.data_loader import TrafficDataLoader


def test_time_slice_filtering():
    loader = TrafficDataLoader.get_instance()
    slice_8 = loader.get_time_slice(8)
    assert len(slice_8) > 0
    assert all(r["hour"] == 8 for r in slice_8)

    slice_18 = loader.get_time_slice(18)
    assert len(slice_18) > 0
    assert all(r["hour"] == 18 for r in slice_18)


def test_zone_and_severity_coordination():
    loader = TrafficDataLoader.get_instance()
    slice_8 = loader.get_time_slice(8)

    # Filter by South Zone
    south_corridors = [r for r in slice_8 if r["zone"].lower() == "south zone"]
    assert len(south_corridors) > 0
    assert all(r["zone"] == "South Zone" for r in south_corridors)

    # Filter by Severe Congestion
    severe_corridors = [r for r in slice_8 if r["congestion_level"] == "Severe"]
    assert all(r["congestion_index"] >= 75.0 for r in severe_corridors)
