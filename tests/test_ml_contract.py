"""
Unit Tests for Machine Learning Integration Contract
Validates schema conformity, multi-horizon handling, and explainability formatting.
"""

from backend.services.ml_adapter import MLPredictionAdapter
from backend.models.schemas import MLPredictionPayload, FeatureContribution


def test_ml_prediction_multi_horizon():
    adapter = MLPredictionAdapter.get_instance()
    
    for horizon in ["15min", "30min", "45min", "60min"]:
        pred = adapter.get_prediction("ROAD_ANNA_SALAI_1", horizon=horizon)
        assert pred.location_id == "ROAD_ANNA_SALAI_1"
        assert pred.prediction_horizon == horizon
        assert 0.0 <= pred.predicted_congestion_index <= 100.0
        assert 0.0 <= pred.confidence <= 1.0
        assert pred.predicted_congestion_level in ["Low", "Moderate", "High", "Severe"]


def test_ml_feature_contributions():
    adapter = MLPredictionAdapter.get_instance()
    pred = adapter.get_prediction("ROAD_GST_1", horizon="30min")
    assert len(pred.top_contributing_features) >= 1
    
    first_feat = pred.top_contributing_features[0]
    assert isinstance(first_feat.feature_name, str)
    assert 0.0 <= first_feat.importance_score <= 1.0
    assert first_feat.direction in ["increases_congestion", "decreases_congestion"]


def test_ml_ingestion_and_fallback():
    adapter = MLPredictionAdapter.get_instance()
    
    # Ingestion test
    new_payload = MLPredictionPayload(
        location_id="ROAD_CUSTOM_99",
        prediction_timestamp="2026-08-30T09:00:00+05:30",
        prediction_horizon="30min",
        predicted_congestion_level="Severe",
        predicted_congestion_index=95.0,
        predicted_vehicle_count=5000,
        predicted_speed=8.0,
        confidence=0.96,
        model_version="XGBoost-Custom-v1",
        top_contributing_features=[
            FeatureContribution(feature_name="Heavy Downpour", importance_score=0.70, direction="increases_congestion")
        ]
    )
    adapter.ingest_prediction(new_payload)
    retrieved = adapter.get_prediction("ROAD_CUSTOM_99", horizon="30min")
    assert retrieved.predicted_congestion_index == 95.0
    assert retrieved.confidence == 0.96

    # Fallback test for unknown road and horizon
    fallback = adapter.get_prediction("ROAD_NONEXISTENT", horizon="45min")
    assert fallback.location_id == "ROAD_NONEXISTENT"
    assert fallback.confidence > 0.0
