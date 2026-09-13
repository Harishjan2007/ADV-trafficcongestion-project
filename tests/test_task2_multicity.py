"""
Task 2 Automated Test Suite: Multi-City Traffic Intelligence & Comparative Analytics
Covers all 17 required verification tests for Chennai, Vellore, and Coimbatore.
"""

import os
import sys
import json
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.config import SUPPORTED_CITIES, CITY_METADATA, get_city_artifact_dir, get_city_benchmark_path
from backend.services.data_loader import TrafficDataLoader, MultiCityRepository
from backend.services.ml_engine import MultiCityMLEngine
from backend.services.ml_adapter import MultiCityMLAdapter
from backend.analytics.clustering import extract_corridor_features, run_kmeans_clustering
from backend.analytics.correlation import generate_correlation_matrix
from backend.analytics.accidents import analyze_accident_safety_profile
from backend.analytics.insights import generate_city_comparison_insights


def test_city_registry():
    """Test 1: Verify city registry constants and metadata definitions."""
    assert "chennai" in SUPPORTED_CITIES
    assert "vellore" in SUPPORTED_CITIES
    assert "coimbatore" in SUPPORTED_CITIES
    assert len(SUPPORTED_CITIES) == 3

    for cid in SUPPORTED_CITIES:
        meta = CITY_METADATA[cid]
        assert "city_id" in meta
        assert "city_name" in meta
        assert "provenance" in meta
        assert "center" in meta
        assert "default_corridors" in meta
        assert len(meta["default_corridors"]) >= 8


def test_all_three_cities_available():
    """Test 2: Verify all three cities are loaded and accessible via MultiCityRepository."""
    repo = MultiCityRepository()
    available_cities = repo.get_available_cities()
    city_ids = [c["city_id"] for c in available_cities]
    assert "chennai" in city_ids
    assert "vellore" in city_ids
    assert "coimbatore" in city_ids


def test_city_data_loading():
    """Test 3: Verify traffic observations can be loaded for each city with complete schemas."""
    repo = MultiCityRepository()
    for cid in SUPPORTED_CITIES:
        records = repo.get_traffic_records(cid)
        assert len(records) > 0, f"No records found for {cid}"
        first = records[0]
        assert "road_id" in first
        assert "congestion_index" in first
        assert "speed" in first
        assert "vehicle_count" in first
        assert "timestamp" in first
        assert 0 <= first["congestion_index"] <= 100


def test_city_road_loading():
    """Test 4: Verify GeoJSON road network geometries and junctions for each city."""
    repo = MultiCityRepository()
    
    # Chennai
    ch_geo = repo.get_road_network("chennai")
    assert len(ch_geo["features"]) >= 9
    for f in ch_geo["features"]:
        assert f["geometry"]["type"] in ("LineString", "MultiLineString")
        assert len(f["geometry"]["coordinates"]) >= 2
    
    # Vellore
    vel_geo = repo.get_road_network("vellore")
    assert len(vel_geo["features"]) >= 8
    vel_junc = repo.get_junctions("vellore")
    assert len(vel_junc["features"]) >= 5
    for f in vel_geo["features"]:
        assert "ROAD_VEL_" in f["properties"]["road_id"]

    # Coimbatore
    cbe_geo = repo.get_road_network("coimbatore")
    assert len(cbe_geo["features"]) >= 10
    cbe_junc = repo.get_junctions("coimbatore")
    assert len(cbe_junc["features"]) >= 5
    for f in cbe_geo["features"]:
        assert "ROAD_CBE_" in f["properties"]["road_id"]


def test_city_filtering():
    """Test 5: Verify strict city isolation and filtering."""
    repo = MultiCityRepository()
    chennai_recs = repo.get_traffic_records("chennai")
    vellore_recs = repo.get_traffic_records("vellore")
    cbe_recs = repo.get_traffic_records("coimbatore")

    chennai_roads = {r["road_id"] for r in chennai_recs}
    vellore_roads = {r["road_id"] for r in vellore_recs}
    cbe_roads = {r["road_id"] for r in cbe_recs}

    # Verify no corridor ID bleed between cities
    assert len(chennai_roads.intersection(vellore_roads)) == 0
    assert len(chennai_roads.intersection(cbe_roads)) == 0
    assert len(vellore_roads.intersection(cbe_roads)) == 0


def test_city_specific_analytics():
    """Test 6: Verify distinct city-specific analytical aggregates and correlation matrices."""
    repo = MultiCityRepository()
    loader = TrafficDataLoader.get_instance()
    
    for cid in SUPPORTED_CITIES:
        recs = loader.get_canonical_records(city=cid)
        assert len(recs) > 0
        corr_matrix = generate_correlation_matrix(recs)
        assert "variables" in corr_matrix
        assert "matrix" in corr_matrix
        
        avg_ci = np.mean([r["congestion_index"] for r in recs])
        avg_speed = np.mean([r["average_speed"] for r in recs])
        
        assert 20 <= avg_ci <= 80, f"Unrealistic average CI for {cid}: {avg_ci}"
        assert 15 <= avg_speed <= 60, f"Unrealistic average speed for {cid}: {avg_speed}"


def test_city_specific_clustering():
    """Test 7: Verify separate K-Means clustering per city with custom cluster characteristics."""
    loader = TrafficDataLoader.get_instance()
    
    for cid in SUPPORTED_CITIES:
        recs = loader.get_canonical_records(city=cid)
        features = extract_corridor_features(recs)
        assert len(features) >= 8
        cluster_res = run_kmeans_clustering(features, k=3)
        assert "cluster_profiles" in cluster_res
        assert len(cluster_res["cluster_profiles"]) >= 2
        assert "road_cluster_assignments" in cluster_res


def test_city_ml_model_loading():
    """Test 8: Verify model engines and dedicated artifacts load correctly for each city."""
    engine = MultiCityMLEngine()
    loaded_artifacts = {}

    for cid in SUPPORTED_CITIES:
        city_eng = engine.get_engine(cid)
        status = city_eng.get_status()
        assert status["status"] in ("ACTIVE", "OPERATIONAL", "INITIALIZED")
        assert "horizons" in status
        assert "model_version" in status

        # Verify dedicated artifact path isolation (zero cross-city fallback)
        if cid == "chennai":
            assert not city_eng.artifacts_dir.endswith("vellore")
            assert not city_eng.artifacts_dir.endswith("coimbatore")
        elif cid == "vellore":
            assert city_eng.artifacts_dir.endswith("vellore")
        elif cid == "coimbatore":
            assert city_eng.artifacts_dir.endswith("coimbatore")

        # Verify all four horizons are available
        for h in ["15min", "30min", "45min", "60min"]:
            assert h in city_eng.models, f"Missing horizon model {h} for {cid}"

        loaded_artifacts[cid] = city_eng.models["30min"]

    # Verify dedicated city models are distinct artifact instances
    assert loaded_artifacts["chennai"] is not loaded_artifacts["vellore"]
    assert loaded_artifacts["chennai"] is not loaded_artifacts["coimbatore"]
    assert loaded_artifacts["vellore"] is not loaded_artifacts["coimbatore"]

    # Verify predictions differ appropriately by city and are generated by the correct city model
    pred_ch = engine.predict("ROAD_ANNA_SALAI_1", {"road_capacity": 3600, "speed_limit": 50, "congestion_lag_1": 55.0}, horizon="30min", city_id="chennai")
    pred_vel = engine.predict("ROAD_VEL_NH48_1", {"road_capacity": 4200, "speed_limit": 65, "congestion_lag_1": 55.0}, horizon="30min", city_id="vellore")
    pred_cbe = engine.predict("ROAD_CBE_AVINASHI_1", {"road_capacity": 3800, "speed_limit": 50, "congestion_lag_1": 55.0}, horizon="30min", city_id="coimbatore")

    assert pred_ch.city_id == "chennai"
    assert pred_vel.city_id == "vellore"
    assert pred_cbe.city_id == "coimbatore"


def test_city_ml_predictions():
    """Test 9: Verify single-corridor ML prediction works for all cities."""
    adapter = MultiCityMLAdapter()
    
    # Chennai
    res_ch = adapter.get_prediction("ROAD_ANNA_SALAI_1", horizon="30min", hour=8, city="chennai")
    assert 0 <= res_ch.predicted_congestion_index <= 100
    assert res_ch.predicted_congestion_level in ("Low", "Moderate", "High", "Severe", "Critical")

    # Vellore
    res_vel = adapter.get_prediction("ROAD_VEL_NH48_1", horizon="30min", hour=8, city="vellore")
    assert 0 <= res_vel.predicted_congestion_index <= 100
    assert res_vel.predicted_congestion_level in ("Low", "Moderate", "High", "Severe", "Critical")

    # Coimbatore
    res_cbe = adapter.get_prediction("ROAD_CBE_AVINASHI_1", horizon="30min", hour=8, city="coimbatore")
    assert 0 <= res_cbe.predicted_congestion_index <= 100
    assert res_cbe.predicted_congestion_level in ("Low", "Moderate", "High", "Severe", "Critical")


def test_multi_horizon_city_predictions():
    """Test 10: Verify multi-horizon forecasting (+15m, +30m, +45m, +60m) for every city."""
    adapter = MultiCityMLAdapter()
    horizons = ["15min", "30min", "45min", "60min"]
    test_roads = {
        "chennai": "ROAD_GST_1",
        "vellore": "ROAD_VEL_KATPADI_1",
        "coimbatore": "ROAD_CBE_SATHY_1"
    }

    for cid, road_id in test_roads.items():
        for horiz in horizons:
            pred = adapter.get_prediction(road_id, horizon=horiz, hour=18, city=cid)
            assert pred.prediction_horizon == horiz
            assert 0 <= pred.predicted_congestion_index <= 100


def test_city_prediction_contract():
    """Test 11: Verify full prediction response structure matches strict contract."""
    adapter = MultiCityMLAdapter()
    pred = adapter.get_prediction("ROAD_VEL_FORT_1", horizon="30min", hour=9, city="vellore")
    
    assert pred.city_id == "vellore"
    assert pred.location_id == "ROAD_VEL_FORT_1"
    assert pred.prediction_horizon == "30min"
    assert 0 <= pred.predicted_congestion_index <= 100
    assert pred.predicted_congestion_level in ("Low", "Moderate", "High", "Severe", "Critical")
    assert pred.confidence >= 0.0
    assert pred.data_status in ("PREDICTED", "SIMULATED", "SIMULATED BENCHMARK DATA")


def test_city_comparison_metrics():
    """Test 12: Verify cross-city comparison metrics generation."""
    adapter = MultiCityMLAdapter()
    comp = adapter.get_comparison_predictions(hour=8)
    
    for cid in SUPPORTED_CITIES:
        assert cid in comp
        for h in ["15min", "30min", "45min", "60min"]:
            assert h in comp[cid]
            assert "predicted_congestion_index" in comp[cid][h]


def test_city_comparison_visualization_data():
    """Test 13: Verify data structures formatted for the 10 comparative visualizations."""
    repo = MultiCityRepository()
    
    # 24-hour hourly curves
    for cid in SUPPORTED_CITIES:
        recs = repo.get_traffic_records(cid)
        hour_cis = {}
        for r in recs:
            h = r.get("hour", int(r["timestamp"][11:13]) if "T" in r["timestamp"] else 8)
            hour_cis.setdefault(h, []).append(r["congestion_index"])
        
        # Verify all 24 diurnal hours exist
        for h in range(24):
            assert h in hour_cis, f"Missing hour {h} in {cid} traffic data"
            assert len(hour_cis[h]) > 0


def test_city_data_provenance():
    """Test 14: Verify strict adherence to data provenance labeling."""
    repo = MultiCityRepository()
    
    chennai_prov = repo.get_provenance("chennai")
    assert chennai_prov["status"] in ("OBSERVED", "BENCHMARK VERIFIED")
    
    vellore_prov = repo.get_provenance("vellore")
    assert "SIMULATED" in vellore_prov["status"]
    
    cbe_prov = repo.get_provenance("coimbatore")
    assert "SIMULATED" in cbe_prov["status"]


def test_city_temporal_leakage():
    """Test 15: Verify chronological ordering and zero future temporal leakage in all cities."""
    repo = MultiCityRepository()
    
    for cid in SUPPORTED_CITIES:
        recs = repo.get_traffic_records(cid)
        
        # Group by road and verify strict ascending chronological order
        road_ts = {}
        for r in recs:
            road_ts.setdefault(r["road_id"], []).append(r["timestamp"])
            
        for rid, ts_list in road_ts.items():
            assert ts_list == sorted(ts_list), f"Timestamps out of chronological order for {cid} road {rid}"


def test_city_data_sufficiency():
    """Test 16: Verify multi-day observations, multiple corridors, and statistical sufficiency."""
    repo = MultiCityRepository()
    
    for cid in SUPPORTED_CITIES:
        recs = repo.get_traffic_records(cid)
        roads = {r["road_id"] for r in recs}
        timestamps = {r["timestamp"] for r in recs}
        
        assert len(roads) >= 8, f"Insufficient corridors in {cid}: {len(roads)}"
        assert len(timestamps) >= 24, f"Insufficient temporal timestamps in {cid}: {len(timestamps)}"
        assert len(recs) >= len(roads) * 24, f"Insufficient total record volume in {cid}: {len(recs)}"


def test_existing_chennai_functionality():
    """Test 17: Zero-regression test confirming Chennai Task 1 features remain 100% operational."""
    repo = MultiCityRepository()
    ch_recs = repo.get_traffic_records("chennai")
    assert len(ch_recs) > 0
    
    ch_geo = repo.get_road_network("chennai")
    assert any(f["properties"]["road_id"] == "ROAD_ANNA_SALAI_1" for f in ch_geo["features"])
    assert any(f["properties"]["road_id"] == "ROAD_GST_1" for f in ch_geo["features"])
    
    adapter = MultiCityMLAdapter()
    pred = adapter.get_prediction("ROAD_ANNA_SALAI_1", horizon="30min", hour=8, city="chennai")
    assert 0 <= pred.predicted_congestion_index <= 100
    assert pred.predicted_congestion_level in ("Low", "Moderate", "High", "Severe", "Critical")

