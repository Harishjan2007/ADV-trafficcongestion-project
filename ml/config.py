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

