"""
Traffic State and Geospatial Map API Endpoints
"""

from typing import Optional, Dict, Any
from backend.fastapi_compat import APIRouter, Query
from backend.services.data_loader import TrafficDataLoader
from backend.models.schemas import CityOverviewSummary

router = APIRouter(prefix="/api/traffic", tags=["traffic"])
loader = TrafficDataLoader.get_instance()


@router.get("/overview", response_model=CityOverviewSummary)
def get_city_overview(hour: int = Query(8, ge=0, le=23)):
    """Returns high-level city-wide traffic indicators for the selected hour."""
    return loader.get_city_overview(hour)


@router.get("/geojson")
def get_chennai_geojson():
    """Returns the base Chennai road network FeatureCollection."""
    return loader.geo_network


@router.get("/map-layers")
def get_map_layers(
    hour: int = Query(8, ge=0, le=23),
    zone: Optional[str] = None,
    congestion_level: Optional[str] = None
):
    """
    Returns active GeoJSON features enriched with real-time/historical traffic conditions,
    congestion levels, and accident states for MapLibre rendering.
    """
    time_slice = loader.get_time_slice(hour)
    slice_map = {r["road_id"]: r for r in time_slice}

    enriched_features = []
    base_features = loader.geo_network.get("features", [])

    for feat in base_features:
        feat_copy = dict(feat)
        props = dict(feat.get("properties", {}))
        road_id = props.get("road_id")

        if road_id and road_id in slice_map:
            t_data = slice_map[road_id]

            # Apply query filters
            if zone and t_data["zone"].lower() != zone.lower():
                continue
            if congestion_level and t_data["congestion_level"].lower() != congestion_level.lower():
                continue

            props.update({
                "vehicle_count": t_data["vehicle_count"],
                "average_speed": t_data["average_speed"],
                "congestion_index": t_data["congestion_index"],
                "congestion_level": t_data["congestion_level"],
                "priority_score": t_data["priority_score"],
                "priority_level": t_data["priority_level"],
                "accident_count": t_data["accident_count"],
                "accident_severity": t_data["accident_severity"],
                "weather_condition": t_data["weather_condition"],
                "rainfall": t_data["rainfall"],
                "timestamp": t_data["timestamp"]
            })
            feat_copy["properties"] = props
            enriched_features.append(feat_copy)
        elif "junction_id" in props:
            # Junction nodes
            enriched_features.append(feat_copy)

    return {
        "type": "FeatureCollection",
        "timestamp": f"2026-08-30T{hour:02d}:00:00+05:30",
        "features": enriched_features
    }
