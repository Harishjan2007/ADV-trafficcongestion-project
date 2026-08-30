"""
Accident and Safety Analytics Engine
Analyzes incident frequencies by hour, weather condition, and severity.
Adheres to Master PRD: Explicitly handles zero/unavailable records without fabricating incidents.
"""

from typing import List, Dict, Any, Optional


def analyze_accident_safety_profile(records: List[Dict[str, Any]], road_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes accident distributions across 24 hours, weather conditions, and severities
    for a specific corridor or across all corridors.
    """
    filtered = [r for r in records if (not road_id or r["road_id"] == road_id)]

    hourly_accidents: List[int] = [0] * 24
    hourly_minor: List[int] = [0] * 24
    hourly_major: List[int] = [0] * 24
    weather_breakdown: Dict[str, int] = {}
    severity_breakdown: Dict[str, int] = {"Minor": 0, "Major": 0, "Fatal": 0, "None": 0}

    total_accidents = 0

    for r in filtered:
        hour = r["hour"]
        acc = r.get("accident_count", 0)
        sev = r.get("accident_severity") or "None"
        weather = r.get("weather_condition") or "Weather Unavailable"

        if acc > 0:
            total_accidents += acc
            hourly_accidents[hour] += acc
            if sev == "Major":
                hourly_major[hour] += acc
            else:
                hourly_minor[hour] += acc

            severity_breakdown[sev] = severity_breakdown.get(sev, 0) + acc
            weather_breakdown[weather] = weather_breakdown.get(weather, 0) + acc

    # Compute peak incident window
    max_acc = max(hourly_accidents) if hourly_accidents else 0
    peak_hours = [h for h, count in enumerate(hourly_accidents) if count == max_acc and max_acc > 0]

    return {
        "road_id": road_id or "ALL_CORRIDORS",
        "total_recorded_accidents": total_accidents,
        "hourly_total": hourly_accidents,
        "hourly_minor": hourly_minor,
        "hourly_major": hourly_major,
        "severity_breakdown": severity_breakdown,
        "weather_breakdown": weather_breakdown,
        "peak_incident_hours": peak_hours,
        "has_accidents": total_accidents > 0,
        "data_state": "OBSERVED"
    }
