"""
Benchmark Dataset Generator: Chennai Urban Arterial Network
Generates a multi-week (14-day) calibrated synthetic traffic dataset
strictly for development, automated testing, and ML pipeline validation.
Clearly watermarked and metadata-tagged as SIMULATED DEVELOPMENT BENCHMARK.
"""

import os
import json
import math
import random
from datetime import datetime, timedelta
from ml.config import DATA_DIR, BENCHMARK_DATASET_PATH, GEO_NETWORK_PATH, get_congestion_level

def generate_multiday_benchmark(num_days: int = 14, seed: int = 42) -> dict:
    """
    Generates 14 days of realistic, diurnal, weather-responsive corridor traffic data.
    Corridors are calibrated according to the physical properties defined in chennai_network.geojson.
    """
    random.seed(seed)
    
    # Load GeoJSON to extract authentic road properties
    with open(GEO_NETWORK_PATH, "r", encoding="utf-8") as f:
        geo_data = json.load(f)

    corridor_specs = []
    for feat in geo_data.get("features", []):
        props = feat.get("properties", {})
        if "road_id" in props:
            coords = feat.get("geometry", {}).get("coordinates", [[80.25, 13.05]])
            mid_idx = len(coords) // 2
            corridor_specs.append({
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

    start_date = datetime(2026, 8, 17, 0, 0)  # Monday
    records = []

    # Monsoon days: Days 4 (Thursday), 5 (Friday), 11 (Friday) have rain spells
    rain_schedule = {
        4: [(7, 10, 4.2, "Light Rain"), (17, 20, 8.5, "Moderate Rain")],
        5: [(8, 13, 16.5, "Heavy Rain"), (16, 21, 12.0, "Moderate Rain")],
        11: [(6, 11, 7.8, "Moderate Rain"), (17, 22, 18.0, "Heavy Rain")]
    }

    # Incident chokepoints on specific corridors
    incident_events = {
        (2, 9, "ROAD_GST_1"): (2, "Major"),
        (4, 18, "ROAD_ANNA_SALAI_1"): (1, "Minor"),
        (5, 8, "ROAD_100FT_1"): (1, "Major"),
        (8, 19, "ROAD_OMR_1"): (1, "Minor"),
        (11, 18, "ROAD_GST_1"): (2, "Major")
    }

    for day_idx in range(num_days):
        current_day = start_date + timedelta(days=day_idx)
        date_str = current_day.strftime("%Y-%m-%d")
        day_of_week_num = current_day.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = (day_of_week_num >= 5)
        day_name = current_day.strftime("%A")

        for hour in range(24):
            is_morning_peak = (8 <= hour <= 11)
            is_evening_peak = (17 <= hour <= 20)
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
            temp_c = round(28.0 + 6.0 * math.sin((hour - 8) * math.pi / 12) - (rain_mm * 0.4), 1)
            visibility_km = round(max(1.5, 10.0 - (rain_mm * 0.6)), 1)

            for c in corridor_specs:
                cap = c["road_capacity"]
                limit = c["speed_limit"]
                rid = c["road_id"]

                # Base volume factor
                if is_weekend:
                    vol_factor = 0.35 + 0.30 * math.sin(max(0, hour - 7) * math.pi / 14)
                elif is_morning_peak:
                    vol_factor = 0.88 + 0.08 * random.uniform(-0.5, 0.5)
                elif is_evening_peak:
                    vol_factor = 0.92 + 0.08 * random.uniform(-0.5, 0.5)
                elif 12 <= hour <= 16:
                    vol_factor = 0.60 + 0.05 * random.uniform(-0.5, 0.5)
                elif 0 <= hour <= 5:
                    vol_factor = 0.12 + 0.04 * random.uniform(-0.5, 0.5)
                else:
                    vol_factor = 0.48 + 0.06 * random.uniform(-0.5, 0.5)

                # High capacity arterials handle more volume
                if rid in ["ROAD_GST_1", "ROAD_ANNA_SALAI_1", "ROAD_OMR_1"]:
                    vol_factor *= 1.05

                vol = int(cap * vol_factor)
                util = vol / cap

                # Speed model with Greenshields breakdown & rain friction
                rain_penalty = min(0.35, (rain_mm / 25.0) * 0.4)
                if util < 0.60:
                    spd_factor = 0.85 - (util * 0.25)
                elif util < 0.85:
                    spd_factor = 0.65 - ((util - 0.60) * 0.8)
                else: # Forced breakdown
                    spd_factor = 0.35 - ((util - 0.85) * 0.6)

                spd_factor = max(0.15, spd_factor - rain_penalty)
                avg_spd = round(limit * spd_factor * (1.0 + 0.04 * random.uniform(-1, 1)), 1)
                avg_spd = max(5.0, min(limit, avg_spd))

                # Accident occurrences
                acc_count, acc_sev = 0, None
                if (day_idx, hour, rid) in incident_events:
                    acc_count, acc_sev = incident_events[(day_idx, hour, rid)]
                    avg_spd = max(5.0, round(avg_spd * 0.55, 1))

                # Calculate congestion index (Canonical Formula)
                speed_deficit = max(0.0, (limit - avg_spd) / limit)
                util_score = min(1.0, util / 1.2)
                ci = round((0.45 * util_score * 100.0) + (0.55 * speed_deficit * 100.0), 1)
                ci = max(0.0, min(100.0, ci))
                level = get_congestion_level(ci)

                timestamp_iso = f"{date_str}T{hour:02d}:00:00+05:30"
                rec_id = f"REC_{rid}_{current_day.strftime('%Y%m%d')}_{hour:02d}"

                records.append({
                    "record_id": rec_id,
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
            "dataset_name": "Chennai Urban Arterial Calibrated Multi-Day Development Benchmark",
            "version": "1.0.0",
            "is_simulated": True,
            "data_classification": "SIMULATED",
            "watermark": "SIMULATED DEVELOPMENT BENCHMARK - STRICTLY FOR PIPELINE VALIDATION AND TESTING",
            "temporal_scope": f"{records[0]['date']} to {records[-1]['date']} ({num_days} Days)",
            "sampling_frequency": "1 hour (60 minutes)",
            "corridor_count": len(corridor_specs),
            "record_count": len(records),
            "date_range": {
                "start": records[0]["timestamp"],
                "end": records[-1]["timestamp"]
            },
            "created_at": "2026-09-12T19:15:00+05:30"
        },
        "records": records
    }

    return dataset

def save_benchmark_dataset():
    data = generate_multiday_benchmark(num_days=14)
    with open(BENCHMARK_DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data['records'])} records across {data['metadata']['corridor_count']} corridors.")
    print(f"Saved to: {BENCHMARK_DATASET_PATH}")
    return data

if __name__ == "__main__":
    save_benchmark_dataset()
