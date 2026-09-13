"""
Location Analytics, Multidimensional Visual Data & Multi-City Comparative API Endpoints
"""

from typing import Optional, Dict, Any, List
from backend.fastapi_compat import APIRouter, HTTPException, Query
from backend.services.data_loader import TrafficDataLoader
from backend.analytics.correlation import generate_correlation_matrix
from backend.analytics.accidents import analyze_accident_safety_profile
from backend.analytics.clustering import extract_corridor_features, run_kmeans_clustering
from backend.services.ml_engine import MLEngine

router = APIRouter(prefix="/api", tags=["analytics"])
loader = TrafficDataLoader.get_instance()


@router.get("/analytics/location/{road_id}")
def get_location_analytics(road_id: str, city: Optional[str] = Query(None)):
    """Returns 24-hour analytical profile and multi-chart dataset for a selected corridor across any city."""
    profile = loader.get_location_profile(road_id, city=city)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Road ID '{road_id}' not found")
    return profile


@router.get("/analytics/leaderboard")
def get_corridor_leaderboard(
    hour: int = Query(8, ge=0, le=23),
    city: str = Query("chennai"),
    zone: Optional[str] = None,
    congestion_level: Optional[str] = None
):
    """
    Returns corridors ranked dynamically by Congestion Index (CI) and Speed Deficit
    for the selected city, hour, and active filter state.
    """
    records = loader.get_time_slice(hour=hour, city=city)
    
    if zone:
        records = [r for r in records if r["zone"].lower() == zone.lower()]
    if congestion_level:
        records = [r for r in records if r["congestion_level"].lower() == congestion_level.lower()]

    sorted_records = sorted(records, key=lambda x: (x["congestion_index"], x["priority_score"]), reverse=True)
    return [
        {
            "rank": idx + 1,
            "city_id": r.get("city_id", city),
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


@router.get("/analytics/correlation-matrix")
def get_correlation_matrix(city: str = Query("chennai"), zone: Optional[str] = None):
    """
    Computes dynamic Pearson correlation matrix across volume, speed, utilization, rainfall, and accidents.
    """
    records = loader.get_canonical_records(city=city)
    if zone:
        records = [r for r in records if r["zone"].lower() == zone.lower()]
    return generate_correlation_matrix(records)


@router.get("/analytics/accidents-safety")
@router.get("/accidents")
def get_accident_safety_breakdown(city: str = Query("chennai"), road_id: Optional[str] = None):
    """
    Returns incident breakdown by hour, severity (Minor vs Major), and weather condition for the city.
    """
    records = loader.get_canonical_records(city=city)
    return analyze_accident_safety_profile(records, road_id)


@router.get("/analytics/clusters")
@router.get("/clusters")
def get_behavioral_clusters(city: str = Query("chennai"), k: int = Query(3, ge=2, le=5)):
    """
    Executes K-Means unsupervised clustering on active corridor multi-dimensional feature vectors.
    """
    records = loader.get_canonical_records(city=city)
    features = extract_corridor_features(records)
    return run_kmeans_clustering(features, k=k)


@router.get("/analytics/scatter-volume-speed")
def get_volume_speed_scatter(city: str = Query("chennai"), road_id: Optional[str] = None):
    """
    Returns volume vs speed pairs for regression and fundamental flow analysis for the selected city.
    """
    records = loader.get_canonical_records(city=city)
    if road_id:
        records = [r for r in records if r["road_id"] == road_id]

    return [
        {
            "city_id": r.get("city_id", city),
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


@router.get("/analytics")
def get_city_analytics_summary(city: str = Query("chennai")):
    """Returns general analytics bundle for requested city."""
    records = loader.get_canonical_records(city=city)
    return {
        "city_id": city,
        "record_count": len(records),
        "correlation": generate_correlation_matrix(records),
        "safety": analyze_accident_safety_profile(records),
        "clusters": run_kmeans_clustering(extract_corridor_features(records), k=3)
    }


@router.get("/analytics/comparison")
def get_city_comparison_analytics(hour: int = Query(8, ge=0, le=23)) -> Dict[str, Any]:
    """
    Computes complete comparative analytics package across Chennai, Vellore, and Coimbatore:
    - Average congestion comparison
    - Hourly congestion comparison
    - Congestion distribution by city
    - Accident comparisons
    - Average speed & deficit comparisons
    - Traffic volume comparisons
    - Cross-city cluster distributions
    - Model performance benchmark metrics
    """
    overview = loader.get_comparison_overview(hour=hour)
    cities = ["chennai", "vellore", "coimbatore"]

    # 1. Congestion distribution by city (box plot data)
    box_data = {}
    speed_data = {}
    volume_data = {}
    for c in cities:
        recs = loader.get_canonical_records(city=c)
        box_data[c] = [r["congestion_index"] for r in recs]
        speed_data[c] = {
            "average_speed": round(sum(r["average_speed"] for r in recs) / len(recs), 1) if recs else 0.0,
            "average_limit": round(sum(r["speed_limit"] for r in recs) / len(recs), 1) if recs else 50.0,
            "speed_deficit_pct": round(sum(r["speed_reduction"] for r in recs) / len(recs) * 100, 1) if recs else 0.0
        }
        volume_data[c] = {
            "total_volume": sum(r["vehicle_count"] for r in recs),
            "average_utilization_pct": round(sum(r["traffic_utilization"] for r in recs) / len(recs) * 100, 1) if recs else 0.0
        }

    # 2. Cross-City Cluster Distribution
    cluster_dist = {}
    for c in cities:
        recs = loader.get_canonical_records(city=c)
        feats = extract_corridor_features(recs)
        clust_res = run_kmeans_clustering(feats, k=3)
        c_counts = {0: 0, 1: 0, 2: 0}
        for item in clust_res.get("clusters", []):
            cid = item.get("cluster_id", 0)
            c_counts[cid] = c_counts.get(cid, 0) + 1
        cluster_dist[c] = c_counts

    # 3. Model Performance Comparison
    ml_metrics = {}
    for c in cities:
        engine = MLEngine.get_instance(city_id=c)
        status = engine.get_status()
        ml_metrics[c] = {
            "model_name": status.get("model_name"),
            "test_metrics": status.get("test_metrics", {}),
            "baseline_persistence": status.get("baseline_persistence", {}),
            "baseline_historical": status.get("baseline_historical", {})
        }

    # 4. Cross-City Heatmap Matrix (City x Hour)
    heatmap_matrix = []
    for c in cities:
        heatmap_matrix.append(overview["hourly_congestion"][c])

    return {
        "hour": hour,
        "city_overviews": overview["cities"],
        "hourly_congestion": overview["hourly_congestion"],
        "hourly_speed": overview["hourly_speed"],
        "hourly_volume": overview["hourly_volume"],
        "congestion_distribution": box_data,
        "speed_comparison": speed_data,
        "volume_comparison": volume_data,
        "accidents_comparison": overview["accidents"],
        "cluster_distribution": cluster_dist,
        "ml_performance": ml_metrics,
        "cross_city_heatmap": {
            "cities": ["Chennai", "Vellore", "Coimbatore"],
            "hours": list(range(24)),
            "matrix": heatmap_matrix
        },
        "provenance": "DERIVED (CALCULATED FROM ACTIVE BENCHMARK RECORDS)"
    }
