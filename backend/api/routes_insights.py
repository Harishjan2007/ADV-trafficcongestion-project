"""
Automated Insight and Decision Support API Endpoints: Multi-City Architecture
"""

from typing import List, Optional, Dict, Any
from backend.fastapi_compat import APIRouter, Query
from backend.services.data_loader import TrafficDataLoader
from backend.models.schemas import AutomatedInsight
from backend.analytics.insights import generate_live_insights, generate_city_comparison_insights

router = APIRouter(prefix="/api/insights", tags=["insights"])
loader = TrafficDataLoader.get_instance()


@router.get("/summary", response_model=List[AutomatedInsight])
def get_automated_insights(
    city: str = Query("chennai"),
    hour: int = Query(8, ge=0, le=23),
    zone: Optional[str] = None,
    congestion_level: Optional[str] = None
):
    """
    Generates deterministic data-driven observations strictly from active time-slice records and filters.
    """
    records = loader.get_time_slice(hour=hour, city=city)
    if zone:
        records = [r for r in records if r["zone"].lower() == zone.lower()]
    if congestion_level:
        records = [r for r in records if r["congestion_level"].lower() == congestion_level.lower()]

    return generate_live_insights(records, hour=hour, active_zone=zone, active_severity=congestion_level)


@router.get("/comparison", response_model=List[AutomatedInsight])
def get_comparison_insights(hour: int = Query(8, ge=0, le=23)):
    """
    Generates algorithmic cross-city comparative insights dynamically from active observations
    across Chennai, Vellore, and Coimbatore.
    """
    city_slice_map = {
        "chennai": loader.get_time_slice(hour=hour, city="chennai"),
        "vellore": loader.get_time_slice(hour=hour, city="vellore"),
        "coimbatore": loader.get_time_slice(hour=hour, city="coimbatore")
    }
    return generate_city_comparison_insights(city_slice_map, hour=hour)
