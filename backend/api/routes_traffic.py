"""
Traffic State, Multi-City Registry and Geospatial Map API Endpoints
"""

from typing import Optional, Dict, Any, List
from backend.fastapi_compat import APIRouter, Query, HTTPException
from backend.services.data_loader import TrafficDataLoader
from backend.models.schemas import CityOverviewSummary

router = APIRouter(prefix="/api", tags=["traffic"])
loader = TrafficDataLoader.get_instance()


@router.get("/cities")
def get_cities() -> List[Dict[str, Any]]:
    """Returns the list of all supported cities in the platform."""
    return loader.get_city_registry()


@router.get("/cities/{city_id}")
def get_city_by_id(city_id: str) -> Dict[str, Any]:
    """Returns geographical and corridor metadata for a specific city."""
    meta = loader.get_city_metadata(city_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found. Supported: chennai, vellore, coimbatore")
    return meta


@router.get("/traffic")
def get_city_traffic(city: str = Query("chennai")) -> List[Dict[str, Any]]:
    """Returns canonical traffic data records for the selected city."""
    return loader.get_canonical_records(city=city)


@router.get("/roads")
def get_city_roads(city: str = Query("chennai")) -> List[Dict[str, Any]]:
    """Returns the list of monitored road corridors for the selected city."""
    corridor_lookup = loader.get_corridor_lookup(city=city)
    return [
        {
            "road_id": rid,
            "road_name": data.get("properties", {}).get("road_name", rid),
            "zone": data.get("properties", {}).get("zone"),
            "road_type": data.get("properties", {}).get("road_type"),
            "speed_limit": data.get("properties", {}).get("speed_limit"),
            "road_capacity": data.get("properties", {}).get("road_capacity"),
            "lane_count": data.get("properties", {}).get("lane_count")
        }
        for rid, data in corridor_lookup.items()
    ]


@router.get("/traffic/overview", response_model=CityOverviewSummary)
def get_city_overview(
    hour: int = Query(8, ge=0, le=23),
    city: str = Query("chennai")
):
    """Returns high-level city-wide traffic indicators for the selected hour and city."""
    return loader.get_city_overview(hour=hour, city=city)


@router.get("/traffic/geojson")
def get_geojson(city: str = Query("chennai")):
    """Returns the base road network FeatureCollection for requested city."""
    return loader.get_geo_network(city=city)


@router.get("/traffic/map-layers")
def get_map_layers(
    hour: int = Query(8, ge=0, le=23),
    city: str = Query("chennai"),
    zone: Optional[str] = None,
    congestion_level: Optional[str] = None
):
    """
    Returns active GeoJSON features enriched with real-time/historical traffic conditions,
    congestion levels, and accident states for MapLibre rendering in the selected city.
    """
    time_slice = loader.get_time_slice(hour=hour, city=city)
    slice_map = {r["road_id"]: r for r in time_slice}

    enriched_features = []
    base_features = loader.get_geo_network(city=city).get("features", [])

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
                "city_id": t_data.get("city_id", city),
                "city_name": t_data.get("city_name", city.capitalize()),
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
        "city_id": city,
        "timestamp": f"2026-08-30T{hour:02d}:00:00+05:30",
        "features": enriched_features
    }
