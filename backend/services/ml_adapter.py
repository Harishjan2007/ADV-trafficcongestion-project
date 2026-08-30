"""
Decoupled Machine Learning Ingestion Adapter & Forecasting Service
Adheres strictly to docs/ml-integration.md and ml-contract/schema_prediction.json
"""

from typing import Dict, Any, List, Optional
from backend.models.schemas import MLPredictionPayload, FeatureContribution


class MLPredictionAdapter:
    """
    Manages ingestion, caching, and serving of decoupled ML model predictions.
    Supports multi-horizon forecasting (+15m, +30m, +45m, +60m) with confidence intervals.
    """
    _instance: Optional["MLPredictionAdapter"] = None

    def __init__(self):
        self._predictions: Dict[str, Dict[str, MLPredictionPayload]] = {}
        self._initialize_fixtures()

    @classmethod
    def get_instance(cls) -> "MLPredictionAdapter":
        if cls._instance is None:
            cls._instance = MLPredictionAdapter()
        return cls._instance

    def _initialize_fixtures(self):
        """Populates calibrated sample predictions for Chennai corridors across horizons."""
        horizons = ["15min", "30min", "45min", "60min"]
        
        sample_configs = [
            {
                "road_id": "ROAD_ANNA_SALAI_1",
                "base_ci": 88.4,
                "base_speed": 10.5,
                "base_vol": 4250,
                "conf": 0.91,
                "level": "Severe",
                "features": [
                    FeatureContribution(feature_name="Rainfall Accumulation (mm)", importance_score=0.42, direction="increases_congestion"),
                    FeatureContribution(feature_name="Upstream Inflow (Chennai Central)", importance_score=0.31, direction="increases_congestion"),
                    FeatureContribution(feature_name="Morning Peak Wave Lag", importance_score=0.18, direction="increases_congestion")
                ]
            },
            {
                "road_id": "ROAD_GST_1",
                "base_ci": 92.1,
                "base_speed": 11.2,
                "base_vol": 4900,
                "conf": 0.94,
                "level": "Severe",
                "features": [
                    FeatureContribution(feature_name="Kathipara Grade Separator Chokepoint", importance_score=0.49, direction="increases_congestion"),
                    FeatureContribution(feature_name="Active Collision Incident", importance_score=0.36, direction="increases_congestion")
                ]
            },
            {
                "road_id": "ROAD_OMR_1",
                "base_ci": 74.0,
                "base_speed": 17.5,
                "base_vol": 4150,
                "conf": 0.88,
                "level": "High",
                "features": [
                    FeatureContribution(feature_name="IT Park Shift Inflow", importance_score=0.52, direction="increases_congestion"),
                    FeatureContribution(feature_name="Tidal Commute Volume", importance_score=0.28, direction="increases_congestion")
                ]
            },
            {
                "road_id": "ROAD_ECR_1",
                "base_ci": 28.5,
                "base_speed": 46.0,
                "base_vol": 1200,
                "conf": 0.95,
                "level": "Low",
                "features": [
                    FeatureContribution(feature_name="Free-Flow Coastal Arterial Alignment", importance_score=0.65, direction="decreases_congestion")
                ]
            }
        ]

        for cfg in sample_configs:
            rid = cfg["road_id"]
            self._predictions[rid] = {}
            for h_idx, horizon in enumerate(horizons):
                ci_delta = (h_idx - 1) * 2.5
                ci = round(min(100.0, max(0.0, cfg["base_ci"] + ci_delta)), 1)
                spd = round(max(5.0, cfg["base_speed"] - (ci_delta * 0.4)), 1)
                vol = int(cfg["base_vol"] + (ci_delta * 30))
                conf = round(max(0.65, cfg["conf"] - (h_idx * 0.04)), 2)

                self._predictions[rid][horizon] = MLPredictionPayload(
                    location_id=rid,
                    prediction_timestamp="2026-08-30T09:00:00+05:30",
                    prediction_horizon=horizon,
                    predicted_congestion_level=cfg["level"],
                    predicted_congestion_index=ci,
                    predicted_vehicle_count=vol,
                    predicted_speed=spd,
                    confidence=conf,
                    model_version="ST-GCN-Chennai-v2.1",
                    top_contributing_features=cfg["features"]
                )

    def get_prediction(self, road_id: str, horizon: str = "30min") -> MLPredictionPayload:
        """Retrieves prediction for a single road and horizon with fallback."""
        if road_id in self._predictions and horizon in self._predictions[road_id]:
            return self._predictions[road_id][horizon]

        # Defensive fallback prediction
        return MLPredictionPayload(
            location_id=road_id,
            prediction_timestamp="2026-08-30T09:00:00+05:30",
            prediction_horizon=horizon,
            predicted_congestion_level="Moderate",
            predicted_congestion_index=45.0,
            predicted_vehicle_count=2100,
            predicted_speed=34.0,
            confidence=0.78,
            model_version="Baseline-Autoregression-v1",
            top_contributing_features=[
                FeatureContribution(feature_name="Historical Baseline Trend", importance_score=0.85, direction="increases_congestion")
            ]
        )

    def get_all_predictions(self, horizon: str = "30min") -> List[MLPredictionPayload]:
        """Returns all predictions for the requested horizon."""
        results = []
        for rid, h_dict in self._predictions.items():
            if horizon in h_dict:
                results.append(h_dict[horizon])
        return results

    def ingest_prediction(self, payload: MLPredictionPayload):
        """Ingests a prediction payload conforming to JSON Schema Draft-07."""
        if payload.location_id not in self._predictions:
            self._predictions[payload.location_id] = {}
        self._predictions[payload.location_id][payload.prediction_horizon] = payload
