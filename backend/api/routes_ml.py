"""
Decoupled Machine Learning Prediction Ingestion and Retrieval API: Multi-City Architecture
Adheres strictly to docs/ml-integration.md and ml-contract/schema_prediction.json
Supports Chennai, Vellore, and Coimbatore.
"""

from typing import List, Optional, Dict, Any
from backend.fastapi_compat import APIRouter, HTTPException, Query
from backend.models.schemas import MLPredictionPayload
from backend.services.ml_adapter import MLPredictionAdapter
from backend.services.ml_engine import MLEngine

router = APIRouter(prefix="/api/ml", tags=["ml"])
adapter = MLPredictionAdapter.get_instance()


def _clean_param(val: Any, default: Any) -> Any:
    if val is None or val is ...:
        return default
    if hasattr(val, "default"):
        return val.default if val.default is not ... else default
    return val


@router.get("/status")
def get_ml_status(city: str = Query("chennai")) -> Dict[str, Any]:
    """Returns genuine ML model health, version, training date, and validation metrics for the requested city."""
    target_city = str(_clean_param(city, "chennai")).lower().strip()
    engine = MLEngine.get_instance(city_id=target_city)
    return engine.get_status()


@router.get("/predictions", response_model=List[MLPredictionPayload])
def get_all_predictions(
    city: str = Query("chennai"),
    horizon: str = Query("30min"),
    hour: int = Query(8, ge=0, le=23)
):
    """Returns genuine ML predictions across all corridors for the requested city and forecast horizon."""
    target_city = str(_clean_param(city, "chennai")).lower().strip()
    target_horizon = str(_clean_param(horizon, "30min")).strip()
    target_hour = int(_clean_param(hour, 8))
    return adapter.get_all_predictions(horizon=target_horizon, hour=target_hour, city=target_city)


@router.get("/predict/{location_id}", response_model=MLPredictionPayload)
def get_prediction_for_location(
    location_id: str,
    city: str = Query("chennai"),
    horizon: str = Query("30min"),
    hour: int = Query(8, ge=0, le=23)
):
    """Returns genuine predictive forecast, calibrated confidence, and feature explanations for a corridor in any city."""
    target_city = str(_clean_param(city, "chennai")).lower().strip()
    target_horizon = str(_clean_param(horizon, "30min")).strip()
    target_hour = int(_clean_param(hour, 8))
    return adapter.get_prediction(location_id, horizon=target_horizon, hour=target_hour, city=target_city)


@router.post("/ingest")
def ingest_prediction_payload(payload: MLPredictionPayload, city: Optional[str] = None):
    """Endpoint for external ML pipelines to POST fresh inference batches."""
    target_city = payload.city_id or city or "chennai"
    adapter.ingest_prediction(payload, city=target_city)
    return {
        "status": "success",
        "message": f"Prediction recorded for {payload.location_id} [{payload.prediction_horizon}] in {target_city.capitalize()}"
    }


@router.get("/comparison")
def get_ml_comparison(hour: int = Query(8, ge=0, le=23)) -> Dict[str, Any]:
    """Returns multi-city ML forecast comparisons across +15m, +30m, +45m, +60m."""
    target_hour = int(_clean_param(hour, 8))
    return adapter.get_comparison_predictions(hour=target_hour)
