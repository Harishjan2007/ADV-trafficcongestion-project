"""
Unit Tests for Phase 8 Dynamic Insight Engine
Validates deterministic observation generation from data without hardcoding.
"""

from backend.analytics.insights import generate_live_insights


def test_generate_live_insights_bottleneck_detection():
    sample_records = [
        {
            "road_id": "ROAD_GST_1",
            "road_name": "GST Road (Kathipara to Airport)",
            "zone": "South Zone",
            "hour": 8,
            "average_speed": 14.5,
            "speed_limit": 60.0,
            "vehicle_count": 4700,
            "traffic_utilization": 0.98,
            "congestion_index": 88.0,
            "congestion_level": "Severe",
            "accident_count": 1,
            "accident_severity": "Major",
            "rainfall": 6.5,
            "priority_level": "Critical"
        }
    ]

    insights = generate_live_insights(sample_records, hour=8)
    assert len(insights) >= 2

    # Check bottleneck alert
    bottleneck_insight = next((i for i in insights if i.category == "BOTTLENECK"), None)
    assert bottleneck_insight is not None
    assert "Peak Gridlock: GST Road" in bottleneck_insight.title
    assert "75.8% speed deficit" in bottleneck_insight.description
    assert bottleneck_insight.severity == "CRITICAL"

    # Check incident safety alert
    safety_insight = next((i for i in insights if i.category == "ACCIDENT_RISK"), None)
    assert safety_insight is not None
    assert "Active Road Incident" in safety_insight.title


def test_generate_live_insights_empty_handling():
    insights = generate_live_insights([], hour=12)
    assert len(insights) == 1
    assert "No Data Available" in insights[0].title
