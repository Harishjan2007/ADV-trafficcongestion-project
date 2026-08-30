"""
Automated Insight and Decision Support API Endpoints
"""

from typing import List, Optional
from backend.fastapi_compat import APIRouter, Query
from backend.services.data_loader import TrafficDataLoader
from backend.models.schemas import AutomatedInsight
from backend.analytics.insights import generate_live_insights

router = APIRouter(prefix="/api/insights", tags=["insights"])
loader = TrafficDataLoader.get_instance()


@router.get("/summary", response_model=List[AutomatedInsight])
def get_automated_insights(
    hour: int = Query(8, ge=0, le=23),
    zone: Optional[str] = None,
    congestion_level: Optional[str] = None
):
    """
    Generates deterministic data-driven observations strictly from active time-slice records and filters.
    """
    records = loader.get_time_slice(hour)
    if zone:
        records = [r for r in records if r["zone"].lower() == zone.lower()]
    if congestion_level:
        records = [r for r in records if r["congestion_level"].lower() == congestion_level.lower()]

    return generate_live_insights(records, hour=hour, active_zone=zone, active_severity=congestion_level)
