"""
Automated Test Runner for Chennai Traffic Intelligence Platform
Runs all unit, analytics, clustering, insights, filter, and ML integration test suites.
"""

import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.test_normalization import (
    test_calculate_derived_metrics_free_flow,
    test_calculate_derived_metrics_severe_congestion,
    test_normalize_raw_record_defensive_fallbacks
)
from tests.test_analytics import (
    test_pearson_correlation_perfect_positive,
    test_pearson_correlation_perfect_negative,
    test_pearson_correlation_edge_cases,
    test_generate_correlation_matrix,
    test_accident_safety_profile
)
from tests.test_clustering import (
    test_extract_corridor_features,
    test_run_kmeans_clustering
)
from tests.test_insights import (
    test_generate_live_insights_bottleneck_detection,
    test_generate_live_insights_empty_handling
)
from tests.test_filters import (
    test_time_slice_filtering,
    test_zone_and_severity_coordination
)
from tests.test_ml_contract import (
    test_ml_prediction_multi_horizon,
    test_ml_feature_contributions,
    test_ml_ingestion_and_fallback
)


def run_all_tests():
    test_cases = [
        ("test_calculate_derived_metrics_free_flow", test_calculate_derived_metrics_free_flow),
        ("test_calculate_derived_metrics_severe_congestion", test_calculate_derived_metrics_severe_congestion),
        ("test_normalize_raw_record_defensive_fallbacks", test_normalize_raw_record_defensive_fallbacks),
        ("test_pearson_correlation_perfect_positive", test_pearson_correlation_perfect_positive),
        ("test_pearson_correlation_perfect_negative", test_pearson_correlation_perfect_negative),
        ("test_pearson_correlation_edge_cases", test_pearson_correlation_edge_cases),
        ("test_generate_correlation_matrix", test_generate_correlation_matrix),
        ("test_accident_safety_profile", test_accident_safety_profile),
        ("test_extract_corridor_features", test_extract_corridor_features),
        ("test_run_kmeans_clustering", test_run_kmeans_clustering),
        ("test_generate_live_insights_bottleneck_detection", test_generate_live_insights_bottleneck_detection),
        ("test_generate_live_insights_empty_handling", test_generate_live_insights_empty_handling),
        ("test_time_slice_filtering", test_time_slice_filtering),
        ("test_zone_and_severity_coordination", test_zone_and_severity_coordination),
        ("test_ml_prediction_multi_horizon", test_ml_prediction_multi_horizon),
        ("test_ml_feature_contributions", test_ml_feature_contributions),
        ("test_ml_ingestion_and_fallback", test_ml_ingestion_and_fallback),
    ]

    print("=" * 75)
    print("RUNNING COMPLETE CHENNAI TRAFFIC INTELLIGENCE PLATFORM TEST SUITE")
    print(f"Test Root: {PROJECT_ROOT}")
    print("=" * 75)

    start_time = time.time()
    passed = 0
    failed = 0
    errors = 0

    for name, func in test_cases:
        try:
            func()
            print(f"  [PASS] {name}")
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {name}: Assertion failed ({e})")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {name}: Unexpected error ({e})")
            errors += 1

    elapsed = time.time() - start_time
    total = len(test_cases)

    print("=" * 75)
    print(f"TEST RESULTS: {total} total | {passed} passed | {failed} failed | {errors} errors")
    print(f"Execution time: {elapsed:.4f}s")
    print("=" * 75)

    return total, passed, failed, errors


if __name__ == "__main__":
    total, passed, failed, errors = run_all_tests()
    if failed > 0 or errors > 0:
        sys.exit(1)
    sys.exit(0)
