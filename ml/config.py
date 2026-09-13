"""
Machine Learning Pipeline Configuration
Chennai Traffic Intelligence Platform
"""

import os

# Base paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
GEO_NETWORK_PATH = os.path.join(DATA_DIR, "geo", "chennai_network.geojson")
SINGLE_DAY_FIXTURE_PATH = os.path.join(DATA_DIR, "synthetic", "chennai_traffic_fixture.json")
BENCHMARK_DATASET_PATH = os.path.join(DATA_DIR, "synthetic", "chennai_traffic_multiday_benchmark.json")

# Model Artifacts Directory
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "backend", "models", "artifacts")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "ml", "reports")

# Multi-City Path Resolvers
SUPPORTED_CITIES = ["chennai", "vellore", "coimbatore"]

def get_geo_network_path(city_id: str = "chennai") -> str:
    c = str(city_id).lower().strip()
    path = os.path.join(DATA_DIR, "geo", f"{c}_network.geojson")
    if os.path.exists(path):
        return path
    return GEO_NETWORK_PATH

def get_fixture_path(city_id: str = "chennai") -> str:
    c = str(city_id).lower().strip()
    path = os.path.join(DATA_DIR, "synthetic", f"{c}_traffic_fixture.json")
    if os.path.exists(path):
        return path
    return SINGLE_DAY_FIXTURE_PATH

def get_benchmark_path(city_id: str = "chennai") -> str:
    c = str(city_id).lower().strip()
    path = os.path.join(DATA_DIR, "synthetic", f"{c}_traffic_multiday_benchmark.json")
    if os.path.exists(path):
        return path
    return BENCHMARK_DATASET_PATH

def get_artifacts_dir(city_id: str = "chennai") -> str:
    c = str(city_id).lower().strip()
    if c == "chennai":
        return ARTIFACTS_DIR
    city_artifacts = os.path.join(ARTIFACTS_DIR, c)
    os.makedirs(city_artifacts, exist_ok=True)
    return city_artifacts

# Canonical multi-city aliases required by tests and pipelines
get_city_artifact_dir = get_artifacts_dir
get_city_benchmark_path = get_benchmark_path

# City Registry Metadata
CITY_METADATA = {
    "chennai": {
        "city_id": "chennai",
        "city_name": "Chennai",
        "provenance": "OBSERVED",
        "center": [80.2207, 13.0327],
        "default_corridors": [
            "ROAD_ANNA_SALAI_1", "ROAD_ANNA_SALAI_2", "ROAD_GST_1", "ROAD_GST_2",
            "ROAD_OMR_1", "ROAD_OMR_2", "ROAD_100FT_1", "ROAD_PH_1", "ROAD_ECR_1"
        ]
    },
    "vellore": {
        "city_id": "vellore",
        "city_name": "Vellore",
        "provenance": "SIMULATED BENCHMARK DATA",
        "center": [79.1325, 12.9165],
        "default_corridors": [
            "ROAD_VEL_NH48_1", "ROAD_VEL_KATPADI_1", "ROAD_VEL_ARNI_1", "ROAD_VEL_FORT_1",
            "ROAD_VEL_BYPASS_1", "ROAD_VEL_CHITTOOR_1", "ROAD_VEL_GANDHI_1", "ROAD_VEL_RANIPET_1"
        ]
    },
    "coimbatore": {
        "city_id": "coimbatore",
        "city_name": "Coimbatore",
        "provenance": "SIMULATED BENCHMARK DATA",
        "center": [76.9558, 11.0168],
        "default_corridors": [
            "ROAD_CBE_AVINASHI_1", "ROAD_CBE_AVINASHI_2", "ROAD_CBE_TRICHY_1", "ROAD_CBE_SATHY_1",
            "ROAD_CBE_POLLACHI_1", "ROAD_CBE_METTUPALAYAM_1", "ROAD_CBE_CROSS_CUT_1", "ROAD_CBE_DB_ROAD_1"
        ]
    }
}


# Target Definitions
PRIMARY_TARGET = "congestion_index"
SECONDARY_TARGETS = ["predicted_speed", "predicted_vehicle_count"]

# Forecast Horizons (in minutes)
DEFAULT_HORIZON = 30
SUPPORTED_HORIZONS = [15, 30, 45, 60]

# Chronological Split Ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Random Seed for Reproducibility
RANDOM_SEED = 42

# Congestion Thresholds (Documented Project Standard)
CONGESTION_THRESHOLDS = {
    "Low": (0.0, 30.0),
    "Moderate": (30.0, 55.0),
    "High": (55.0, 75.0),
    "Severe": (75.0, 100.0)
}

def get_congestion_level(index: float) -> str:
    """Derives categorical congestion level from continuous congestion index."""
    if index >= 75.0:
        return "Severe"
    elif index >= 55.0:
        return "High"
    elif index >= 30.0:
        return "Moderate"
    return "Low"

# Data Sufficiency Gate Minimums
GATE_MIN_UNIQUE_DAYS = 7
GATE_MIN_RECORDS = 1000
GATE_MIN_OBSERVATIONS_PER_ROAD = 50
GATE_REQUIRED_TRAFFIC_COLS = ["vehicle_count", "average_speed", "congestion_index"]

# Authoritative Feature Columns Definition
from ml.features import FEATURE_COLUMNS

