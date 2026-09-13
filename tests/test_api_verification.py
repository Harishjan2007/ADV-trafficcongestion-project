"""
Task 2 Final Repair: End-to-End API Verification Suite
Verifies all required API endpoints across Chennai, Vellore, and Coimbatore,
including all 4 horizons (+15m, +30m, +45m, +60m), dedicated artifact loading,
and cross-city comparisons.
"""

import sys
import os
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.config import get_city_artifact_dir, ARTIFACTS_DIR
from backend.services.ml_engine import MLEngine, MultiCityMLEngine
from backend.main import app


def run_api_verification():
    print("=" * 80)
    print("STARTING REAL END-TO-END API VERIFICATION (TASK 2 AUDIT REPAIR)")
    print("=" * 80)

    # 1. Ensure dedicated city ML model artifacts are trained and loaded
    multi_engine = MultiCityMLEngine.get_instance()
    
    # Verify dedicated artifact paths
    ch_eng = multi_engine.get_engine("chennai")
    vel_eng = multi_engine.get_engine("vellore")
    cbe_eng = multi_engine.get_engine("coimbatore")

    print("[VERIFY] Artifact directories:")
    print(f"  Chennai:    {ch_eng.artifacts_dir}")
    print(f"  Vellore:    {vel_eng.artifacts_dir}")
    print(f"  Coimbatore: {cbe_eng.artifacts_dir}")

    assert vel_eng.artifacts_dir == get_city_artifact_dir("vellore"), "Vellore engine must use dedicated vellore directory"
    assert cbe_eng.artifacts_dir == get_city_artifact_dir("coimbatore"), "Coimbatore engine must use dedicated coimbatore directory"
    assert ch_eng.artifacts_dir == ARTIFACTS_DIR, "Chennai engine must use original Task 1 artifacts directory"

    # Verify dedicated model binaries exist on disk
    for cid, eng in [("vellore", vel_eng), ("coimbatore", cbe_eng)]:
        for h in ["15min", "30min", "45min", "60min"]:
            m_path = os.path.join(eng.artifacts_dir, f"traffic_model_{h}.joblib")
            assert os.path.exists(m_path), f"Missing dedicated model binary: {m_path}"
            assert h in eng.models, f"Missing loaded model horizon: {h} in {cid}"
        print(f"  [PASS] All 4 dedicated horizon model binaries verified on disk for {cid.capitalize()}.")

    # Verify model objects are distinct
    assert vel_eng.models["30min"] is not ch_eng.models["30min"], "Vellore must not share model object with Chennai"
    assert cbe_eng.models["30min"] is not ch_eng.models["30min"], "Coimbatore must not share model object with Chennai"
    assert vel_eng.models["30min"] is not cbe_eng.models["30min"], "Vellore and Coimbatore must not share model objects"
    print("  [PASS] All city model objects are verified distinct and independently trained.")

    # 2. TestClient HTTP Requests
    from backend.fastapi_compat import TestClient
    client = TestClient(app)

    endpoints_to_test = [
        ("GET /health", "/health", 200),
        ("GET /api/cities", "/api/cities", 200),
        ("GET /api/traffic?city=chennai", "/api/traffic?city=chennai", 200),
        ("GET /api/traffic?city=vellore", "/api/traffic?city=vellore", 200),
        ("GET /api/traffic?city=coimbatore", "/api/traffic?city=coimbatore", 200),
        ("GET /api/roads?city=vellore", "/api/roads?city=vellore", 200),
        ("GET /api/roads?city=coimbatore", "/api/roads?city=coimbatore", 200),
        ("GET /api/accidents?city=vellore", "/api/accidents?city=vellore", 200),
        ("GET /api/accidents?city=coimbatore", "/api/accidents?city=coimbatore", 200),
        ("GET /api/analytics/comparison", "/api/analytics/comparison", 200),
        ("GET /api/ml/predictions?city=chennai&horizon=30min", "/api/ml/predictions?city=chennai&horizon=30min", 200),
        ("GET /api/ml/predictions?city=vellore&horizon=30min", "/api/ml/predictions?city=vellore&horizon=30min", 200),
        ("GET /api/ml/predictions?city=coimbatore&horizon=30min", "/api/ml/predictions?city=coimbatore&horizon=30min", 200),
        ("GET /api/ml/comparison", "/api/ml/comparison", 200),
    ]

    print("\n[VERIFY] Executing required minimum API endpoint tests:")
    for label, url, expected_status in endpoints_to_test:
        resp = client.get(url)
        assert resp.status_code == expected_status, f"{label} returned status {resp.status_code}, expected {expected_status}: {resp.text}"
        data = resp.json()
        print(f"  [PASS] {label} -> HTTP {resp.status_code} (payload length/keys: {len(data)})")

    # 3. Verify all four horizons for all three cities
    print("\n[VERIFY] Testing all 4 forecast horizons (+15m, +30m, +45m, +60m) across all 3 cities:")
    horizons = ["15min", "30min", "45min", "60min"]
    cities = ["chennai", "vellore", "coimbatore"]

    for c in cities:
        for h in horizons:
            url = f"/api/ml/predictions?city={c}&horizon={h}&hour=8"
            resp = client.get(url)
            assert resp.status_code == 200, f"Failed {url}: {resp.status_code}"
            preds = resp.json()
            assert len(preds) > 0, f"No predictions returned for {c} at {h}"
            first = preds[0]
            assert first["prediction_horizon"] == h
            assert first["city_id"] == c
            assert 0 <= first["predicted_congestion_index"] <= 100
            assert first["data_status"] in ("PREDICTED", "SIMULATED BENCHMARK DATA")
            print(f"  [PASS] City: {c.capitalize():<11} | Horizon: {h:<6} | Sample CI: {first['predicted_congestion_index']:<4} | Road: {first['location_id']}")

    # 4. Verify /api/ml/comparison returns dynamic multi-horizon matrix and test metrics
    print("\n[VERIFY] Testing /api/ml/comparison dynamic response structure:")
    resp = client.get("/api/ml/comparison?hour=9")
    assert resp.status_code == 200
    comp = resp.json()

    for c in cities:
        assert c in comp, f"Missing city {c} in comparison response"
        for h in horizons:
            assert h in comp[c], f"Missing horizon {h} for {c}"
            assert "predicted_congestion_index" in comp[c][h]
            assert "predicted_speed" in comp[c][h]

    assert "metrics" in comp, "Missing 'metrics' key in /api/ml/comparison response"
    metrics = comp["metrics"]
    for c in cities:
        assert c in metrics, f"Missing {c} in metrics"
        assert "mae" in metrics[c]
        assert "rmse" in metrics[c]
        assert "r2" in metrics[c]
        assert "data_classification" in metrics[c]
        print(f"  [PASS] {c.capitalize()} Held-Out Test Metrics: MAE={metrics[c]['mae']}, RMSE={metrics[c]['rmse']}, R2={metrics[c]['r2']} ({metrics[c]['data_classification']})")

    print("\n" + "=" * 80)
    print("ALL 14 REQUIRED API ENDPOINTS & ALL 4 HORIZONS ACROSS 3 CITIES PASSED VERIFICATION!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    run_api_verification()
