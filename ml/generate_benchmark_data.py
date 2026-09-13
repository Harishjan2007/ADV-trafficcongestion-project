"""
Benchmark Dataset Generator: Multi-City Urban Arterial Networks (Chennai, Vellore, Coimbatore)
Generates 14-day calibrated synthetic traffic datasets and 24-hour diurnal fixtures
strictly for development, automated testing, ML pipeline validation, and comparative analytics.
Clearly watermarked and metadata-tagged as SIMULATED BENCHMARK DATA.
"""

import os
import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ml.config import (
    DATA_DIR,
    BENCHMARK_DATASET_PATH,
    GEO_NETWORK_PATH,
    get_geo_network_path,
    get_benchmark_path,
    get_fixture_path,
    get_congestion_level
)

CITY_METADATA = {
    "chennai": {
        "city_name": "Chennai",
        "state": "Tamil Nadu",
        "default_seed": 42,
        "peak_morning": (8, 11),
        "peak_evening": (17, 20),
        "weather_type": "Coastal Tropical / Monsoon",
        "rain_schedule": {
            4: [(7, 10, 4.2, "Light Rain"), (17, 20, 8.5, "Moderate Rain")],
            5: [(8, 13, 16.5, "Heavy Rain"), (16, 21, 12.0, "Moderate Rain")],
            11: [(6, 11, 7.8, "Moderate Rain"), (17, 22, 18.0, "Heavy Rain")]
        },
        "incident_events": {
            (2, 9, "ROAD_GST_1"): (2, "Major"),
            (4, 18, "ROAD_ANNA_SALAI_1"): (1, "Minor"),
            (5, 8, "ROAD_100FT_1"): (1, "Major"),
            (8, 19, "ROAD_OMR_1"): (1, "Minor"),
            (11, 18, "ROAD_GST_1"): (2, "Major")
        }
    },
    "vellore": {
        "city_name": "Vellore",
        "state": "Tamil Nadu",
        "default_seed": 101,
        "peak_morning": (8, 10),
        "peak_evening": (16, 19),
        "weather_type": "Inland Semi-Arid",
        "rain_schedule": {
            3: [(15, 18, 5.0, "Moderate Rain")],
            9: [(17, 20, 9.5, "Moderate Rain")]
        },
        "incident_events": {
            (3, 9, "ROAD_VEL_NH48_1"): (1, "Major"),
            (6, 17, "ROAD_VEL_KATPADI_1"): (1, "Minor"),
            (10, 18, "ROAD_VEL_RANIPET_1"): (1, "Minor"),
            (12, 8, "ROAD_VEL_ARNI_1"): (1, "Major")
        }
    },
    "coimbatore": {
        "city_name": "Coimbatore",
        "state": "Tamil Nadu",
        "default_seed": 202,
        "peak_morning": (8, 11),
        "peak_evening": (17, 21),
        "weather_type": "Western Ghats Foothills / Moderate",
        "rain_schedule": {
            2: [(16, 19, 6.0, "Light Rain")],
            6: [(7, 11, 11.5, "Moderate Rain"), (17, 20, 14.0, "Heavy Rain")],
            12: [(18, 22, 8.5, "Moderate Rain")]
        },
        "incident_events": {
            (1, 18, "ROAD_CBE_AVINASHI_1"): (1, "Minor"),
            (4, 9, "ROAD_CBE_SATHY_1"): (1, "Major"),
            (7, 19, "ROAD_CBE_TRICHY_2"): (1, "Minor"),
            (11, 18, "ROAD_CBE_METTUPALAYAM_1"): (2, "Major")
        }
    }
}


def load_corridor_specs(city_id: str = "chennai") -> List[Dict[str, Any]]:
    """Loads corridor properties from GeoJSON for a specific city."""
    geo_path = get_geo_network_path(city_id)
    if not os.path.exists(geo_path):
        raise FileNotFoundError(f"GeoJSON not found for city '{city_id}' at {geo_path}")

    with open(geo_path, "r", encoding="utf-8") as f:
        geo_data = json.load(f)

    specs = []
    for feat in geo_data.get("features", []):
        props = feat.get("properties", {})
        if "road_id" in props:
            coords = feat.get("geometry", {}).get("coordinates", [[80.25, 13.05]])
            mid_idx = len(coords) // 2
            specs.append({
                "road_id": props["road_id"],
                "road_name": props["road_name"],
                "zone": props["zone"],
                "road_type": props["road_type"],
                "speed_limit": float(props.get("speed_limit", 50.0)),
                "road_capacity": int(props.get("road_capacity", 3600)),
                "lane_count": int(props.get("lane_count", 3)),
                "lat": coords[mid_idx][1],
                "lng": coords[mid_idx][0]
            })
    return specs


def generate_multiday_benchmark(city_id: str = "chennai", num_days: int = 14, seed: Optional[int] = None, city: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates 14 days of realistic, diurnal, weather-responsive corridor traffic data for any supported city.
    Ensures zero future leakage in structure and consistent schemas.
    """
    target_c = city or city_id
    city_key = str(target_c).lower().strip()
    c_meta = CITY_METADATA.get(city_key, CITY_METADATA["chennai"])
    actual_seed = seed if seed is not None else c_meta["default_seed"]
    random.seed(actual_seed)

    corridor_specs = load_corridor_specs(city_key)
    start_date = datetime(2026, 8, 17, 0, 0)  # Monday
    records = []

    rain_schedule = c_meta["rain_schedule"]
    incident_events = c_meta["incident_events"]
    m_peak_start, m_peak_end = c_meta["peak_morning"]
    e_peak_start, e_peak_end = c_meta["peak_evening"]

    for day_idx in range(num_days):
        current_day = start_date + timedelta(days=day_idx)
        date_str = current_day.strftime("%Y-%m-%d")
        day_of_week_num = current_day.weekday()
        is_weekend = (day_of_week_num >= 5)
        day_name = current_day.strftime("%A")

        for hour in range(24):
            is_morning_peak = (m_peak_start <= hour <= m_peak_end)
            is_evening_peak = (e_peak_start <= hour <= e_peak_end)
            is_peak_hour = (is_morning_peak or is_evening_peak) and not is_weekend

            # Weather lookup
            rain_mm = 0.0
            weather_cond = "Clear"
            if day_idx in rain_schedule:
                for r_start, r_end, r_amount, r_cond in rain_schedule[day_idx]:
                    if r_start <= hour <= r_end:
                        rain_mm = round(r_amount * (0.8 + 0.4 * math.sin((hour - r_start) * math.pi / max(1, r_end - r_start))), 1)
                        weather_cond = r_cond
                        break

            # Diurnal temperature cycle
            base_temp = 30.0 if city_key == "chennai" else (32.0 if city_key == "vellore" else 26.0)
            temp_c = round(base_temp + 5.5 * math.sin((hour - 8) * math.pi / 12) - (rain_mm * 0.4), 1)
            visibility_km = round(max(1.5, 10.0 - (rain_mm * 0.6)), 1)

            for c in corridor_specs:
                cap = c["road_capacity"]
                limit = c["speed_limit"]
                rid = c["road_id"]

                # Base volume factor calibrated by city characteristics
                if is_weekend:
                    vol_factor = 0.35 + 0.30 * math.sin(max(0, hour - 7) * math.pi / 14)
                elif is_morning_peak:
                    vol_factor = 0.88 + 0.08 * random.uniform(-0.5, 0.5)
                elif is_evening_peak:
                    vol_factor = 0.92 + 0.08 * random.uniform(-0.5, 0.5)
                elif 12 <= hour <= 16:
                    vol_factor = 0.58 + 0.05 * random.uniform(-0.5, 0.5)
                elif 0 <= hour <= 5:
                    vol_factor = 0.12 + 0.04 * random.uniform(-0.5, 0.5)
                else:
                    vol_factor = 0.48 + 0.06 * random.uniform(-0.5, 0.5)

                # City-specific arterial adjustments
                if city_key == "chennai":
                    if rid in ["ROAD_GST_1", "ROAD_ANNA_SALAI_1", "ROAD_OMR_1"]:
                        vol_factor *= 1.05
                elif city_key == "vellore":
                    # Concentrated Green Circle bottleneck
                    if rid in ["ROAD_VEL_NH48_1", "ROAD_VEL_KATPADI_1"]:
                        vol_factor *= 1.08
                    else:
                        vol_factor *= 0.92
                elif city_key == "coimbatore":
                    # Avinashi Road and Sathy Road handle heavy commuters
                    if rid in ["ROAD_CBE_AVINASHI_1", "ROAD_CBE_AVINASHI_2", "ROAD_CBE_SATHY_1"]:
                        vol_factor *= 1.06
                    else:
                        vol_factor *= 0.95

                vol = int(cap * vol_factor)
                util = vol / cap

                # Greenshields speed degradation model
                rain_penalty = min(0.35, (rain_mm / 25.0) * 0.4)
                if util < 0.60:
                    spd_factor = 0.85 - (util * 0.25)
                elif util < 0.85:
                    spd_factor = 0.65 - ((util - 0.60) * 0.8)
                else:
                    spd_factor = 0.35 - ((util - 0.85) * 0.6)

                spd_factor = max(0.15, spd_factor - rain_penalty)
                avg_spd = round(limit * spd_factor * (1.0 + 0.04 * random.uniform(-1, 1)), 1)
                avg_spd = max(5.0, min(limit, avg_spd))

                # Accident occurrences
                acc_count, acc_sev = 0, None
                if (day_idx, hour, rid) in incident_events:
                    acc_count, acc_sev = incident_events[(day_idx, hour, rid)]
                    avg_spd = max(5.0, round(avg_spd * 0.55, 1))

                # Congestion index (Canonical Formula)
                speed_deficit = max(0.0, (limit - avg_spd) / limit)
                util_score = min(1.0, util / 1.2)
                ci = round((0.45 * util_score * 100.0) + (0.55 * speed_deficit * 100.0), 1)
                ci = max(0.0, min(100.0, ci))
                level = get_congestion_level(ci)

                timestamp_iso = f"{date_str}T{hour:02d}:00:00+05:30"
                rec_id = f"REC_{city_key.upper()}_{rid}_{current_day.strftime('%Y%m%d')}_{hour:02d}"

                records.append({
                    "record_id": rec_id,
                    "city_id": city_key,
                    "city_name": c_meta["city_name"],
                    "timestamp": timestamp_iso,
                    "date": date_str,
                    "hour": hour,
                    "day_of_week": day_name,
                    "is_weekend": is_weekend,
                    "is_peak_hour": is_peak_hour,
                    "road_id": rid,
                    "road_name": c["road_name"],
                    "zone": c["zone"],
                    "road_type": c["road_type"],
                    "latitude": c["lat"],
                    "longitude": c["lng"],
                    "vehicle_count": vol,
                    "average_speed": avg_spd,
                    "road_capacity": cap,
                    "speed_limit": limit,
                    "lane_count": c["lane_count"],
                    "traffic_utilization": round(util, 3),
                    "speed_reduction": round(speed_deficit, 3),
                    "congestion_index": ci,
                    "congestion_level": level,
                    "weather_condition": weather_cond,
                    "rainfall": rain_mm,
                    "temperature": temp_c,
                    "visibility": visibility_km,
                    "accident_count": acc_count,
                    "accident_severity": acc_sev
                })

    dataset = {
        "metadata": {
            "dataset_name": f"{c_meta['city_name']} Urban Calibrated Multi-Day Development Benchmark",
            "city_id": city_key,
            "city_name": c_meta["city_name"],
            "version": "1.0.0",
            "is_simulated": True,
            "data_classification": "SIMULATED",
            "watermark": "SIMULATED BENCHMARK DATA - STRICTLY FOR MULTI-CITY DEVELOPMENT AND EVALUATION",
            "temporal_scope": f"{records[0]['date']} to {records[-1]['date']} ({num_days} Days)",
            "sampling_frequency": "1 hour (60 minutes)",
            "corridor_count": len(corridor_specs),
            "record_count": len(records),
            "random_seed": actual_seed,
            "date_range": {
                "start": records[0]["timestamp"],
                "end": records[-1]["timestamp"]
            },
            "created_at": "2026-09-13T08:00:00+05:30"
        },
        "records": records
    }
    return dataset


def generate_single_day_fixture(city_id: str = "chennai", seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Generates single-day 24-hour baseline fixture for a specific city.
    """
    city_key = city_id.lower().strip()
    c_meta = CITY_METADATA.get(city_key, CITY_METADATA["chennai"])
    corridor_specs = load_corridor_specs(city_key)
    multi_data = generate_multiday_benchmark(city_id=city_key, num_days=1, seed=seed)
    
    # Organize into corridor hourly profile format for fast in-memory loading
    corridors_output = []
    records_by_road = {}
    for r in multi_data["records"]:
        records_by_road.setdefault(r["road_id"], []).append(r)

    for spec in corridor_specs:
        rid = spec["road_id"]
        road_recs = records_by_road.get(rid, [])
        hourly_profiles = {}
        for r in road_recs:
            h_str = str(r["hour"])
            hourly_profiles[h_str] = {
                "vehicle_count": r["vehicle_count"],
                "average_speed": r["average_speed"],
                "weather": r["weather_condition"],
                "rain": r["rainfall"],
                "accidents": r["accident_count"],
                "accident_severity": r["accident_severity"]
            }

        corridors_output.append({
            "road_id": rid,
            "road_name": spec["road_name"],
            "zone": spec["zone"],
            "road_type": spec["road_type"],
            "speed_limit": spec["speed_limit"],
            "road_capacity": spec["road_capacity"],
            "lane_count": spec["lane_count"],
            "base_volume": int(spec["road_capacity"] * 0.75),
            "hourly_profiles": hourly_profiles
        })

    fixture = {
        "metadata": {
            "dataset_name": f"{c_meta['city_name']} Urban Traffic Multi-Corridor Calibrated Fixture",
            "city_id": city_key,
            "city_name": c_meta["city_name"],
            "version": "1.0.0",
            "is_simulated": True,
            "data_classification": "SIMULATED",
            "watermark": "SIMULATED BENCHMARK DATA - NOT OFFICIAL POLICE RECORDS",
            "temporal_scope": "2026-08-30 (24-Hour Cycle)",
            "corridor_count": len(corridor_specs)
        },
        "corridors": corridors_output
    }
    return fixture


def save_all_city_datasets():
    """Generates and saves benchmark and fixture datasets for all supported cities."""
    for city in ["chennai", "vellore", "coimbatore"]:
        bench_path = get_benchmark_path(city)
        fixt_path = get_fixture_path(city)

        # 1. Multi-day benchmark
        print(f"Generating 14-day benchmark for {city.upper()}...")
        bench_data = generate_multiday_benchmark(city_id=city, num_days=14)
        with open(bench_path, "w", encoding="utf-8") as f:
            json.dump(bench_data, f, indent=2)
        print(f"  Saved {len(bench_data['records'])} records to: {bench_path}")

        # 2. Single-day fixture
        print(f"Generating 24h fixture for {city.upper()}...")
        fixt_data = generate_single_day_fixture(city_id=city)
        with open(fixt_path, "w", encoding="utf-8") as f:
            json.dump(fixt_data, f, indent=2)
        print(f"  Saved {len(fixt_data['corridors'])} corridors to: {fixt_path}")


if __name__ == "__main__":
    save_all_city_datasets()
