"""
Decoupled Machine Learning Prediction Ingestion and Retrieval API
Adheres strictly to docs/ml-integration.md and ml-contract/schema_prediction.json
"""

from typing import List, Optional, Dict, Any
from backend.fastapi_compat import APIRouter, HTTPException, Query
from backend.models.schemas import MLPredictionPayload
from backend.services.ml_adapter import MLPredictionAdapter
from backend.services.ml_engine import MLEngine

router = APIRouter(prefix="/api/ml", tags=["ml"])
adapter = MLPredictionAdapter.get_instance()
engine = MLEngine.get_instance()


@router.get("/status")
def get_ml_status() -> Dict[str, Any]:
    """Returns genuine ML model health, version, training date, and validation metrics."""
    return engine.get_status()


@router.get("/predictions", response_model=List[MLPredictionPayload])
def get_all_predictions(
    horizon: str = Query("30min"),
    hour: int = Query(8, ge=0, le=23)
):
    """Returns genuine ML predictions across all Chennai corridors for requested forecast horizon."""
    return adapter.get_all_predictions(horizon=horizon, hour=hour)


@router.get("/predict/{location_id}", response_model=MLPredictionPayload)
def get_prediction_for_location(
    location_id: str,
    horizon: str = Query("30min"),
    hour: int = Query(8, ge=0, le=23)
):
    """Returns genuine predictive forecast, calibrated confidence, and feature explanations for a corridor."""
    return adapter.get_prediction(location_id, horizon=horizon, hour=hour)


@router.post("/ingest")
def ingest_prediction_payload(payload: MLPredictionPayload):
    """Endpoint for external ML pipelines to POST fresh inference batches."""
    adapter.ingest_prediction(payload)
    return {
        "status": "success",
        "message": f"Prediction recorded for {payload.location_id} [{payload.prediction_horizon}]"
    }
