"""
Location Analytics, Multidimensional Visual Data & Clustering API Endpoints
"""

from typing import Optional, Dict, Any, List
from backend.fastapi_compat import APIRouter, HTTPException, Query
from backend.services.data_loader import TrafficDataLoader
from backend.analytics.correlation import generate_correlation_matrix
from backend.analytics.accidents import analyze_accident_safety_profile
from backend.analytics.clustering import extract_corridor_features, run_kmeans_clustering

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
loader = TrafficDataLoader.get_instance()


@router.get("/location/{road_id}")
def get_location_analytics(road_id: str):
    """Returns 24-hour analytical profile and multi-chart dataset for a selected corridor."""
    profile = loader.get_location_profile(road_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Road ID '{road_id}' not found")
    return profile


@router.get("/leaderboard")
def get_corridor_leaderboard(
    hour: int = Query(8, ge=0, le=23),
    zone: Optional[str] = None,
    congestion_level: Optional[str] = None
):
    """
    Returns corridors ranked dynamically by Congestion Index (CI) and Speed Deficit
    for the selected hour and active filter state.
    """
    records = loader.get_time_slice(hour)
    
    if zone:
        records = [r for r in records if r["zone"].lower() == zone.lower()]
    if congestion_level:
        records = [r for r in records if r["congestion_level"].lower() == congestion_level.lower()]

    sorted_records = sorted(records, key=lambda x: (x["congestion_index"], x["priority_score"]), reverse=True)
    return [
        {
            "rank": idx + 1,
            "road_id": r["road_id"],
            "road_name": r["road_name"],
            "zone": r["zone"],
            "congestion_index": r["congestion_index"],
            "congestion_level": r["congestion_level"],
            "average_speed": r["average_speed"],
            "speed_limit": r["speed_limit"],
            "speed_reduction_pct": round(r["speed_reduction"] * 100, 1),
            "vehicle_count": r["vehicle_count"],
            "road_capacity": r["road_capacity"],
            "utilization_pct": round(r["traffic_utilization"] * 100, 1),
            "accident_count": r["accident_count"],
            "priority_level": r["priority_level"],
            "priority_score": r["priority_score"]
        }
        for idx, r in enumerate(sorted_records)
    ]


@router.get("/correlation-matrix")
def get_correlation_matrix(zone: Optional[str] = None):
    """
    Computes dynamic Pearson correlation matrix across volume, speed, utilization, rainfall, and accidents.
    """
    records = loader.canonical_records
    if zone:
        records = [r for r in records if r["zone"].lower() == zone.lower()]
    return generate_correlation_matrix(records)


@router.get("/accidents-safety")
def get_accident_safety_breakdown(road_id: Optional[str] = None):
    """
    Returns incident breakdown by hour, severity (Minor vs Major), and weather condition.
    """
    return analyze_accident_safety_profile(loader.canonical_records, road_id)


@router.get("/clusters")
def get_behavioral_clusters(k: int = Query(3, ge=2, le=5)):
    """
    Executes K-Means unsupervised clustering on active corridor multi-dimensional feature vectors.
    """
    features = extract_corridor_features(loader.canonical_records)
    return run_kmeans_clustering(features, k=k)


@router.get("/scatter-volume-speed")
def get_volume_speed_scatter(road_id: Optional[str] = None):
    """
    Returns volume vs speed pairs for regression and fundamental flow analysis.
    """
    records = loader.canonical_records
    if road_id:
        records = [r for r in records if r["road_id"] == road_id]

    return [
        {
            "road_id": r["road_id"],
            "road_name": r["road_name"],
            "hour": r["hour"],
            "vehicle_count": r["vehicle_count"],
            "average_speed": r["average_speed"],
            "speed_limit": r["speed_limit"],
            "traffic_utilization": r["traffic_utilization"],
            "congestion_index": r["congestion_index"],
            "congestion_level": r["congestion_level"],
            "rainfall": r.get("rainfall", 0.0),
            "accident_count": r["accident_count"]
        }
        for r in records
    ]
