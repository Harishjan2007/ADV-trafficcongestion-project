# ML Integration Contract: Chennai Traffic Intelligence Platform

**Date:** 2026-08-30  
**Status:** Approved Integration Specification (Phase 0)

---

## 1. Integration Boundary & Principles

1. **Decoupled Architecture:** The Machine Learning model training, loss optimization, feature engineering pipelines, and hyperparameter tuning are maintained independently by the ML workstream.
2. **Standardized Ingestion Contract:** The traffic platform consumes ML outputs purely via a defined JSON / REST API / Parquet prediction contract.
3. **Explicit Labeling:** All machine learning predictions displayed in the UI (predicted congestion layer, predicted speed/volume graphs, anomaly likelihood) MUST be visibly labeled as `PREDICTED` and include calibrated confidence metrics when supplied.
4. **Graceful Fallback:** If ML prediction payloads are absent or the ML service is offline, the platform continues all historical, analytical, and real-time monitoring functions uninterrupted.

---

## 2. Prediction Payload Schema

The ML service supplies predictions conforming to the following JSON structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChennaiTrafficPredictionPayload",
  "type": "object",
  "required": [
    "location_id",
    "prediction_timestamp",
    "prediction_horizon",
    "predicted_congestion_level",
    "predicted_congestion_index",
    "confidence"
  ],
  "properties": {
    "location_id": {
      "type": "string",
      "description": "Canonical Road Corridor or Junction ID matching the spatial road network.",
      "examples": ["ROAD_ANNA_SALAI_S1", "JUNC_KATHIPARA"]
    },
    "prediction_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp for which the prediction is made (ISO 8601).",
      "examples": ["2026-08-30T09:00:00+05:30"]
    },
    "prediction_horizon": {
      "type": "string",
      "enum": ["15min", "30min", "45min", "60min"],
      "description": "Lead time ahead of the current observation window."
    },
    "predicted_congestion_level": {
      "type": "string",
      "enum": ["Low", "Moderate", "High", "Severe"],
      "description": "Categorical predicted congestion severity."
    },
    "predicted_congestion_index": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 100.0,
      "description": "Continuous predicted congestion score."
    },
    "predicted_vehicle_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Estimated vehicular volume in the forecast window."
    },
    "predicted_speed": {
      "type": "number",
      "minimum": 0.0,
      "description": "Estimated mean vehicular speed (km/h)."
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Calibrated statistical confidence score of the prediction."
    },
    "model_metadata": {
      "type": "object",
      "properties": {
        "model_name": { "type": "string", "examples": ["ST-GCN-Chennai-v2", "XGBoost-Traffic-Lag3"] },
        "model_version": { "type": "string", "examples": ["2.1.0"] },
        "inference_latency_ms": { "type": "number" }
      }
    },
    "top_contributing_features": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "feature_name": { "type": "string", "examples": ["Rainfall Intensity", "Upstream Volume (Guindy)", "Peak Hour Lag"] },
          "importance_score": { "type": "number" },
          "direction": { "type": "string", "enum": ["increases_congestion", "decreases_congestion"] }
        }
      }
    }
  }
}
```

---

## 3. UI Display Patterns for ML Predictions

| Location in Platform | Visual Representation | Interaction & Details |
| :--- | :--- | :--- |
| **Map Prediction Layer** | Glowing dashed or distinct-tint road polylines displaying future congestion (e.g. +30 min). | Hovering reveals: *"Predicted Severe Congestion in +30 min (Confidence: 89%)"*. |
| **Location Drawer: Prediction Tab** | Dual-line chart comparing Observed Traffic vs. Predicted Forecast Line (with shaded confidence intervals). | Displays top 3 contributing factors (e.g., *Rainfall (+35%), Upstream Inflow (+28%)*). |
| **Priority Decision Matrix** | Prediction alerts incorporated into Priority ranking (e.g., *"Elevated to CRITICAL: Severe congestion forecast within 30 min"*). | Allows traffic authority to proactively dispatch personnel prior to gridlock. |
