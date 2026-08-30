"""
Data Loader and In-Memory Repository for Chennai Traffic Intelligence Platform
Serves canonical records, spatial features, and time slices with high performance.
"""

import json
import os
from typing import Dict, List, Any, Optional
from backend.services.normalizer import normalize_raw_record, calculate_derived_metrics


class TrafficDataLoader:
    _instance = None

    def __init__(self):
        self.geo_network: Dict[str, Any] = {}
        self.raw_fixture: Dict[str, Any] = {}
        self.canonical_records: List[Dict[str, Any]] = []
        self.corridor_lookup: Dict[str, Dict[str, Any]] = {}
        self.junction_lookup: Dict[str, Dict[str, Any]] = {}
        self._load_datasets()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_datasets(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        geo_path = os.path.join(base_dir, "data", "geo", "chennai_network.geojson")
        fixture_path = os.path.join(base_dir, "data", "synthetic", "chennai_traffic_fixture.json")

        # 1. Load GeoJSON
        if os.path.exists(geo_path):
            with open(geo_path, "r", encoding="utf-8") as f:
                self.geo_network = json.load(f)
                for feat in self.geo_network.get("features", []):
                    props = feat.get("properties", {})
                    if "road_id" in props:
                        self.corridor_lookup[props["road_id"]] = {
                            "geometry": feat.get("geometry"),
                            "properties": props
                        }
                    elif "junction_id" in props:
                        self.junction_lookup[props["junction_id"]] = {
                            "geometry": feat.get("geometry"),
                            "properties": props
                        }

        # 2. Load and normalize fixture records across hours 0-23
        if os.path.exists(fixture_path):
            with open(fixture_path, "r", encoding="utf-8") as f:
                self.raw_fixture = json.load(f)

            corridors = self.raw_fixture.get("corridors", [])
            for c in corridors:
                road_id = c.get("road_id")
                geo_info = self.corridor_lookup.get(road_id, {})
                coords = geo_info.get("geometry", {}).get("coordinates", [[80.2707, 13.0827]])
                mid_point = coords[len(coords) // 2] if coords else [80.2707, 13.0827]

                hourly_profiles = c.get("hourly_profiles", {})
                for hour in range(24):
                    hour_str = str(hour)
                    prof = hourly_profiles.get(hour_str)
                    if not prof:
                        # Interpolate baseline diurnal curve
                        is_peak = (8 <= hour <= 11) or (17 <= hour <= 20)
                        factor = 0.95 if is_peak else 0.45
                        vol = int(c.get("road_capacity", 3600) * factor)
                        spd = 18.0 if is_peak else 42.0
                        prof = {
                            "vehicle_count": vol,
                            "average_speed": spd,
                            "weather": "Clear",
                            "rain": 0.0,
                            "accidents": 0
                        }

                    raw_item = {
                        "record_id": f"REC_{road_id}_{hour:02d}00",
                        "timestamp": f"2026-08-30T{hour:02d}:00:00+05:30",
                        "latitude": mid_point[1],
                        "longitude": mid_point[0],
                        "road_id": road_id,
                        "road_name": c.get("road_name"),
                        "zone": c.get("zone", "Central Zone"),
                        "road_type": c.get("road_type", "Arterial"),
                        "vehicle_count": prof.get("vehicle_count", 2000),
                        "average_speed": prof.get("average_speed", 30.0),
                        "road_capacity": c.get("road_capacity", 3600),
                        "speed_limit": c.get("speed_limit", 50.0),
                        "lane_count": c.get("lane_count", 3),
                        "accident_count": prof.get("accidents", 0),
                        "accident_severity": prof.get("accident_severity"),
                        "weather_condition": prof.get("weather", "Clear"),
                        "rainfall": prof.get("rain", 0.0),
                        "hour": hour,
                        "date": "2026-08-30",
                        "day_of_week": "Monday"
                    }

                    canonical = normalize_raw_record(raw_item)
                    self.canonical_records.append(canonical)

    def get_time_slice(self, hour: int = 8) -> List[Dict[str, Any]]:
        """Returns all canonical corridor records active at the specified hour."""
        return [r for r in self.canonical_records if r["hour"] == hour]

    def get_city_overview(self, hour: int = 8) -> Dict[str, Any]:
        """Aggregates city-wide high-level metrics for the top header & KPI cards."""
        slice_records = self.get_time_slice(hour)
        if not slice_records:
            return {
                "timestamp": f"2026-08-30T{hour:02d}:00:00+05:30",
                "total_monitored_roads": 0,
                "average_city_speed": 0.0,
                "average_congestion_index": 0.0,
                "severe_congestion_count": 0,
                "high_priority_count": 0,
                "total_active_accidents": 0,
                "monitored_vehicle_volume": 0,
                "data_state": "SIMULATED"
            }

        total_vol = sum(r["vehicle_count"] for r in slice_records)
        avg_spd = round(sum(r["average_speed"] for r in slice_records) / len(slice_records), 1)
        avg_ci = round(sum(r["congestion_index"] for r in slice_records) / len(slice_records), 1)
        severe_count = sum(1 for r in slice_records if r["congestion_level"] == "Severe")
        high_priority = sum(1 for r in slice_records if r["priority_level"] in ["High", "Critical"])
        total_accidents = sum(r["accident_count"] for r in slice_records)

        return {
            "timestamp": f"2026-08-30T{hour:02d}:00:00+05:30",
            "total_monitored_roads": len(slice_records),
            "average_city_speed": avg_spd,
            "average_congestion_index": avg_ci,
            "severe_congestion_count": severe_count,
            "high_priority_count": high_priority,
            "total_active_accidents": total_accidents,
            "monitored_vehicle_volume": total_vol,
            "data_state": "SIMULATED"
        }

    def get_location_profile(self, road_id: str) -> Optional[Dict[str, Any]]:
        """Returns 24-hour analytical profile for a single selected corridor."""
        records = [r for r in self.canonical_records if r["road_id"] == road_id]
        if not records:
            return None

        geo = self.corridor_lookup.get(road_id, {})
        records_sorted = sorted(records, key=lambda x: x["hour"])

        return {
            "road_id": road_id,
            "road_name": records[0]["road_name"],
            "zone": records[0]["zone"],
            "road_type": records[0]["road_type"],
            "speed_limit": records[0]["speed_limit"],
            "road_capacity": records[0]["road_capacity"],
            "lane_count": records[0]["lane_count"],
            "geometry": geo.get("geometry"),
            "hourly_series": records_sorted,
            "total_24h_accidents": sum(r["accident_count"] for r in records),
            "peak_congestion_hour": max(records, key=lambda x: x["congestion_index"])["hour"]
        }
