"""
Decoupled Machine Learning Prediction Ingestion and Retrieval API
Adheres strictly to docs/ml-integration.md and ml-contract/schema_prediction.json
"""

from typing import List, Optional
from backend.fastapi_compat import APIRouter, HTTPException, Query
from backend.models.schemas import MLPredictionPayload
from backend.services.ml_adapter import MLPredictionAdapter

router = APIRouter(prefix="/api/ml", tags=["ml"])
adapter = MLPredictionAdapter.get_instance()


@router.get("/predictions", response_model=List[MLPredictionPayload])
def get_all_predictions(horizon: str = Query("30min", regex="^(15min|30min|45min|60min)$")):
    """Returns all available ML predictions for the requested forecast horizon."""
    return adapter.get_all_predictions(horizon=horizon)


@router.get("/predict/{location_id}", response_model=MLPredictionPayload)
def get_prediction_for_location(
    location_id: str,
    horizon: str = Query("30min", regex="^(15min|30min|45min|60min)$")
):
    """Returns predictive forecast, confidence, and feature explanations for a single corridor."""
    return adapter.get_prediction(location_id, horizon=horizon)


@router.post("/ingest")
def ingest_prediction_payload(payload: MLPredictionPayload):
    """Endpoint for the external ML pipeline to POST fresh inference batches."""
    adapter.ingest_prediction(payload)
    return {"status": "success", "message": f"Prediction recorded for {payload.location_id} [{payload.prediction_horizon}]"}
