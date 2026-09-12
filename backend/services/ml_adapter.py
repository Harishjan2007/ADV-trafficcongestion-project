"""
Machine Learning Ingestion Adapter & Forecasting Service
Integrates genuine MLEngine model inference with traffic data loader and REST API contracts.
Replaces all static hardcoded prediction fixtures and fake ST-GCN claims.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.models.schemas import MLPredictionPayload, FeatureContribution
from backend.services.ml_engine import MLEngine
from backend.services.data_loader import TrafficDataLoader

logger = logging.getLogger("chennai_traffic_ml_adapter")


class MLPredictionAdapter:
    """
    Manages serving of genuine ML predictions and external prediction ingestion.
    Queries the MLEngine with live corridor state features.
    """
    _instance: Optional["MLPredictionAdapter"] = None

    def __init__(self):
        self.ml_engine = MLEngine.get_instance()
        self.data_loader = TrafficDataLoader.get_instance()
        self._ingested_predictions: Dict[str, Dict[str, MLPredictionPayload]] = {}

    @classmethod
    def get_instance(cls) -> "MLPredictionAdapter":
        if cls._instance is None:
            cls._instance = MLPredictionAdapter()
        return cls._instance

    def _extract_corridor_features(self, road_id: str, hour: int = 8) -> Dict[str, Any]:
        """Extracts current observed features for a road to pass to ML engine."""
        slice_records = self.data_loader.get_time_slice(hour)
        rec = next((r for r in slice_records if r["road_id"] == road_id), None)
        
        if not rec:
            # Check single road profile
            prof = self.data_loader.get_location_profile(road_id)
            if prof and prof.get("hourly_series"):
                rec = prof["hourly_series"][min(hour, len(prof["hourly_series"])-1)]

        if rec:
            speed_limit = float(rec.get("speed_limit", 50.0))
            road_cap = int(rec.get("road_capacity", 3600))
            lane_count = int(rec.get("lane_count", 3))
            curr_spd = float(rec.get("average_speed", 30.0))
            curr_vol = int(rec.get("vehicle_count", 2000))
            curr_ci = float(rec.get("congestion_index", 50.0))
            rain = float(rec.get("rainfall", 0.0))
            acc = int(rec.get("accident_count", 0))
        else:
            speed_limit, road_cap, lane_count = 50.0, 3600, 3
            curr_spd, curr_vol, curr_ci, rain, acc = 30.0, 2000, 50.0, 0.0, 0

        import numpy as np
        is_weekend = 0
        is_peak = 1 if ((8 <= hour <= 11) or (17 <= hour <= 20)) and not is_weekend else 0

        features = {
            "hour": hour,
            "minute": 0,
            "day_of_week": 0,  # Monday baseline
            "is_weekend": is_weekend,
            "is_peak_hour": is_peak,
            "hour_sin": float(np.sin(2 * np.pi * hour / 24.0)),
            "hour_cos": float(np.cos(2 * np.pi * hour / 24.0)),
            "day_of_week_sin": float(np.sin(2 * np.pi * 0 / 7.0)),
            "day_of_week_cos": float(np.cos(2 * np.pi * 0 / 7.0)),
            "road_capacity": road_cap,
            "speed_limit": speed_limit,
            "lane_count": lane_count,
            "vehicle_count_lag_1": curr_vol,
            "vehicle_count_lag_2": int(curr_vol * 0.95),
            "vehicle_count_lag_3": int(curr_vol * 0.90),
            "speed_lag_1": curr_spd,
            "speed_lag_2": float(min(speed_limit, curr_spd * 1.05)),
            "speed_lag_3": float(min(speed_limit, curr_spd * 1.10)),
            "congestion_lag_1": curr_ci,
            "congestion_lag_2": float(max(0.0, curr_ci * 0.95)),
            "rolling_speed_mean_3h": curr_spd,
            "rolling_vol_mean_3h": float(curr_vol),
            "rolling_ci_mean_3h": curr_ci,
            "rolling_ci_std_3h": 3.5,
            "neighbor_congestion_lag_1": curr_ci,
            "rainfall": rain,
            "temperature": 30.0,
            "is_raining": 1 if rain > 0 else 0,
            "accident_lag_1": acc
        }
        return features

    def _normalize_horizon(self, horizon: str) -> str:
        """Normalizes user/client horizon strings into canonical keys ('15min', '30min', '45min', '60min')."""
        h = str(horizon).strip().lower().replace("+", "").replace(" ", "")
        if "15" in h:
            return "15min"
        elif "45" in h:
            return "45min"
        elif "60" in h:
            return "60min"
        elif "30" in h or "30m" in h:
            return "30min"
        return "30min"

    def get_prediction(self, road_id: str, horizon: str = "30min", hour: int = 8) -> MLPredictionPayload:
        """Retrieves prediction from ingested cache, or executes genuine MLEngine inference."""
        canon_h = self._normalize_horizon(horizon)

        # 1. Check if externally ingested prediction exists
        if road_id in self._ingested_predictions and canon_h in self._ingested_predictions[road_id]:
            return self._ingested_predictions[road_id][canon_h]

        lookup_id = road_id
        if road_id.isdigit():
            c_keys = list(self.data_loader.corridor_lookup.keys())
            idx = int(road_id) - 1
            if 0 <= idx < len(c_keys):
                lookup_id = c_keys[idx]
            elif c_keys:
                lookup_id = c_keys[0]

        feats = self._extract_corridor_features(lookup_id, hour=hour)
        road_meta = self.data_loader.corridor_lookup.get(lookup_id, {})
        props = road_meta.get("properties", {})
        road_name = props.get("road_name") or road_meta.get("road_name") or feats.get("road_name", road_id)
        curr_ci = float(feats.get("congestion_lag_1", 50.0))
        curr_spd = float(feats.get("speed_lag_1", 30.0))
        curr_vol = int(feats.get("vehicle_count_lag_1", 2000))

        from ml.config import get_congestion_level
        curr_level = get_congestion_level(curr_ci)

        # 2. Check if MLEngine has trained artifacts available
        if self.ml_engine.is_available():
            try:
                pred = self.ml_engine.predict(road_id, features=feats, horizon=canon_h)
                pred.road_name = road_name
                pred.observed_congestion_index = round(curr_ci, 1)
                pred.observed_congestion_level = curr_level
                pred.observed_speed = round(curr_spd, 1)
                pred.observed_vehicle_count = curr_vol
                pred.data_status = "SIMULATED"
                pred.model_status = "ACTIVE"
                return pred
            except Exception as e:
                logger.error(f"Inference error for {road_id}: {e}")

        # 3. Defensive Offline Fallback (Explicitly labeled as OFFLINE DEVELOPMENT FALLBACK)
        return MLPredictionPayload(
            location_id=road_id,
            road_name=road_name,
            prediction_timestamp=datetime.now().isoformat(),
            prediction_horizon=canon_h,
            predicted_congestion_level="Moderate",
            predicted_congestion_index=48.0,
            predicted_vehicle_count=2200,
            predicted_speed=32.5,
            confidence=0.72,
            model_version="OFFLINE-DEVELOPMENT-FALLBACK",
            observed_congestion_index=round(curr_ci, 1),
            observed_congestion_level=curr_level,
            observed_speed=round(curr_spd, 1),
            observed_vehicle_count=curr_vol,
            data_status="SIMULATED",
            model_status="OFFLINE",
            top_contributing_features=[
                FeatureContribution(
                    feature_name="Historical Diurnal Baseline",
                    importance_score=0.80,
                    direction="increases_congestion"
                )
            ]
        )

    def get_all_predictions(self, horizon: str = "30min", hour: int = 8) -> List[MLPredictionPayload]:
        """Returns predictions for all monitored Chennai road corridors."""
        canon_h = self._normalize_horizon(horizon)
        road_ids = list(self.data_loader.corridor_lookup.keys())
        if not road_ids:
            # Fallback list of major Chennai corridors
            road_ids = [
                "ROAD_ANNA_SALAI_1", "ROAD_ANNA_SALAI_2", "ROAD_GST_1", "ROAD_GST_2",
                "ROAD_OMR_1", "ROAD_OMR_2", "ROAD_PH_1", "ROAD_PH_2",
                "ROAD_100FT_1", "ROAD_ECR_1", "ROAD_MOUNT_POON_1", "ROAD_ARCOT_1",
                "ROAD_SP_ROAD_1", "ROAD_MARINA_1"
            ]

        results = []
        for rid in road_ids:
            results.append(self.get_prediction(rid, horizon=canon_h, hour=hour))
        return results

    def ingest_prediction(self, payload: MLPredictionPayload):
        """Ingests external prediction payload conforming to JSON Schema."""
        if payload.location_id not in self._ingested_predictions:
            self._ingested_predictions[payload.location_id] = {}
        self._ingested_predictions[payload.location_id][payload.prediction_horizon] = payload
