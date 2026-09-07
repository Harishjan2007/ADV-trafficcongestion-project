"""
Geographic & Behavioral Corridor Clustering Engine
Performs unsupervised K-Means clustering directly on extracted corridor feature vectors.
Adheres strictly to Master PRD: Does NOT hard-code road memberships; assigns clusters via algorithmic convergence.
"""

from typing import List, Dict, Any, Tuple
import math
import random


def extract_corridor_features(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Extracts 5 multi-dimensional behavioral features for each unique corridor:
    1. peak_ci: Maximum Congestion Index during peak hours (8-10, 17-20)
    2. offpeak_ci: Average Congestion Index during off-peak hours
    3. speed_variance: Coefficient of variation of vehicular speed
    4. rain_sensitivity: Difference in mean CI under rainfall vs dry conditions
    5. total_accidents: 24-hour cumulative incident count
    """
    by_road: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        road_id = r["road_id"]
        if road_id not in by_road:
            by_road[road_id] = []
        by_road[road_id].append(r)

    features: Dict[str, Dict[str, Any]] = {}

    for road_id, r_list in by_road.items():
        road_name = r_list[0]["road_name"]
        zone = r_list[0]["zone"]

        # Feature 1: Peak CI
        peak_records = [r for r in r_list if (8 <= r["hour"] <= 10) or (17 <= r["hour"] <= 20)]
        peak_ci = max((r["congestion_index"] for r in peak_records), default=30.0)

        # Feature 2: Off-Peak CI
        offpeak_records = [r for r in r_list if not ((8 <= r["hour"] <= 10) or (17 <= r["hour"] <= 20))]
        offpeak_ci = sum(r["congestion_index"] for r in offpeak_records) / max(1, len(offpeak_records))

        # Feature 3: Speed Variation (Standard Deviation / Mean)
        speeds = [r["average_speed"] for r in r_list]
        mean_speed = sum(speeds) / max(1, len(speeds))
        var_speed = sum((s - mean_speed) ** 2 for s in speeds) / max(1, len(speeds))
        std_speed = math.sqrt(var_speed)
        speed_variance = (std_speed / mean_speed) if mean_speed > 0 else 0.0

        # Feature 4: Rain Sensitivity
        rainy = [r["congestion_index"] for r in r_list if (r.get("rainfall") or 0.0) > 0.0]
        dry = [r["congestion_index"] for r in r_list if (r.get("rainfall") or 0.0) == 0.0]
        mean_rain_ci = sum(rainy) / max(1, len(rainy)) if rainy else offpeak_ci
        mean_dry_ci = sum(dry) / max(1, len(dry)) if dry else offpeak_ci
        rain_sensitivity = max(0.0, mean_rain_ci - mean_dry_ci)

        # Feature 5: Total Accidents
        total_accidents = sum(r.get("accident_count", 0) for r in r_list)

        features[road_id] = {
            "road_id": road_id,
            "road_name": road_name,
            "zone": zone,
            "raw_vector": [peak_ci, offpeak_ci, speed_variance * 100.0, rain_sensitivity, total_accidents * 20.0],
            "metrics": {
                "peak_ci": round(peak_ci, 1),
                "offpeak_ci": round(offpeak_ci, 1),
                "speed_variance": round(speed_variance, 3),
                "rain_sensitivity": round(rain_sensitivity, 1),
                "total_accidents": total_accidents
            }
        }

    return features


def run_kmeans_clustering(
    features_dict: Dict[str, Dict[str, Any]],
    k: int = 3,
    max_iters: int = 50,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Executes K-Means algorithm on min-max normalized feature vectors.
    Computes dynamic cluster assignments, centroids, and profile labels based on centroid traits.
    """
    random.seed(seed)
    road_ids = list(features_dict.keys())
    if len(road_ids) < k:
        k = max(1, len(road_ids))

    raw_vectors = [features_dict[rid]["raw_vector"] for rid in road_ids]
    dim_count = len(raw_vectors[0])

    # Min-Max Normalization of features to [0.0, 1.0] for fair Euclidean distance
    mins = [min(v[i] for v in raw_vectors) for i in range(dim_count)]
    maxs = [max(v[i] for v in raw_vectors) for i in range(dim_count)]
    ranges = [max(1e-5, maxs[i] - mins[i]) for i in range(dim_count)]

    norm_vectors = [
        [(v[i] - mins[i]) / ranges[i] for i in range(dim_count)]
        for v in raw_vectors
    ]

    # Initialize centroids deterministically using spread
    step = len(norm_vectors) // k
    centroids = [norm_vectors[min(i * step, len(norm_vectors) - 1)] for i in range(k)]

    assignments = [0] * len(norm_vectors)

    for _ in range(max_iters):
        # 1. Assignment step
        changed = False
        for i, vec in enumerate(norm_vectors):
            dists = [
                math.sqrt(sum((vec[d] - c[d]) ** 2 for d in range(dim_count)))
                for c in centroids
            ]
            best_c = dists.index(min(dists))
            if assignments[i] != best_c:
                assignments[i] = best_c
                changed = True

        if not changed:
            break

        # 2. Update step
        for c_idx in range(k):
            assigned_pts = [norm_vectors[i] for i, a in enumerate(assignments) if a == c_idx] if hasattr(raw_vectors, 'count') else [norm_vectors[i] for i, a in enumerate(assignments) if a == c_idx]
            if assigned_pts:
                centroids[c_idx] = [
                    sum(pt[d] for pt in assigned_pts) / len(assigned_pts)
                    for d in range(dim_count)
                ]

    # Build cluster descriptions dynamically from centroid characteristics
    cluster_colors = ["#ec4899", "#06b6d4", "#f59e0b", "#8b5cf6"]
    cluster_profiles: List[Dict[str, Any]] = []

    for c_idx in range(k):
        member_ids = [road_ids[i] for i, a in enumerate(assignments) if a == c_idx]
        if not member_ids:
            continue

        # Compute centroid average metrics across raw dimensions
        member_feats = [features_dict[rid]["metrics"] for rid in member_ids]
        avg_peak = sum(m["peak_ci"] for m in member_feats) / len(member_feats)
        avg_offpeak = sum(m["offpeak_ci"] for m in member_feats) / len(member_feats)
        avg_acc = sum(m["total_accidents"] for m in member_feats) / len(member_feats)
        avg_rain = sum(m["rain_sensitivity"] for m in member_feats) / len(member_feats)

        # Determine dynamic profile label
        if avg_peak >= 75.0 or avg_acc >= 1.5:
            label = "High-Peak / Bottleneck Corridors"
            desc = "Heavy peak-hour gridlock with significant speed deficits and elevated incident frequency."
        elif avg_rain >= 4.0:
            label = "Monsoon & Rain Vulnerable Arterials"
            desc = "Moderate base congestion that spikes sharply during precipitation events."
        else:
            label = "Steady Flow Arterials"
            desc = "Lower speed variation and consistent free-flow capacity utilization."

        cluster_profiles.append({
            "cluster_id": c_idx,
            "cluster_label": label,
            "cluster_description": desc,
            "color": cluster_colors[c_idx % len(cluster_colors)],
            "member_count": len(member_ids),
            "member_roads": [features_dict[rid]["road_name"] for rid in member_ids],
            "member_road_ids": member_ids,
            "centroid_metrics": {
                "avg_peak_ci": round(avg_peak, 1),
                "avg_offpeak_ci": round(avg_offpeak, 1),
                "avg_accidents_24h": round(avg_acc, 1),
                "avg_rain_sensitivity": round(avg_rain, 1)
            },
            "radar_normalized": [
                round(centroids[c_idx][0] * 100, 1),
                round(centroids[c_idx][1] * 100, 1),
                round(centroids[c_idx][2] * 100, 1),
                round(centroids[c_idx][3] * 100, 1),
                round(centroids[c_idx][4] * 100, 1)
            ]
        })

    road_cluster_map = {
        road_ids[i]: {
            "cluster_id": assignments[i],
            "cluster_label": next((cp["cluster_label"] for cp in cluster_profiles if cp["cluster_id"] == assignments[i]), "Unassigned"),
            "color": cluster_colors[assignments[i] % len(cluster_colors)]
        }
        for i in range(len(road_ids))
    }

    return {
        "cluster_count": len(cluster_profiles),
        "cluster_profiles": cluster_profiles,
        "road_cluster_assignments": road_cluster_map,
        "radar_dimensions": ["Peak Congestion", "Off-Peak Volume", "Speed Variance", "Rain Sensitivity", "Incident Rate"],
        "data_state": "DERIVED"
    }
