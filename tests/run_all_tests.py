"""
Automated Test Runner for Chennai Traffic Intelligence Platform
Runs all unit, analytics, clustering, insights, filter, and ML pipeline test suites.
"""

import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Core Platform Tests
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

# Machine Learning Pipeline Tests
from tests.test_ml_data_audit import (
    test_data_audit_rejects_single_day_fixture,
    test_data_audit_approves_multiday_benchmark
)
from tests.test_ml_features import (
    test_preprocessing_integrity,
    test_feature_engineering_columns_and_bounds,
    test_target_construction
)
from tests.test_ml_data_leakage import (
    test_zero_future_leakage_temporal_alignment,
    test_zero_future_leakage_perturbation_test,
    test_rolling_statistics_exclude_current_time
)
from tests.test_ml_baselines import (
    test_calculate_metrics_exact_values,
    test_persistence_baseline_logic,
    test_historical_average_baseline_grouping
)
from tests.test_ml_training import (
    test_candidate_models_fit_and_predict,
    test_non_trivial_prediction_sensitivity,
    test_multi_horizon_model_wrapper
)
from tests.test_ml_inference import (
    test_model_explainer_dynamic_instance_attribution,
    test_ml_adapter_prediction_contract,
    test_ml_adapter_all_corridors_predictions,
    test_ml_engine_status_reporting
)
from tests.test_ml_contract import (
    test_ml_prediction_multi_horizon,
    test_ml_feature_contributions,
    test_ml_ingestion_and_fallback
)


def run_all_tests():
    test_cases = [
        # Normalization & Core Derived Metrics
        ("test_calculate_derived_metrics_free_flow", test_calculate_derived_metrics_free_flow),
        ("test_calculate_derived_metrics_severe_congestion", test_calculate_derived_metrics_severe_congestion),
        ("test_normalize_raw_record_defensive_fallbacks", test_normalize_raw_record_defensive_fallbacks),
        
        # Analytics & Correlation
        ("test_pearson_correlation_perfect_positive", test_pearson_correlation_perfect_positive),
        ("test_pearson_correlation_perfect_negative", test_pearson_correlation_perfect_negative),
        ("test_pearson_correlation_edge_cases", test_pearson_correlation_edge_cases),
        ("test_generate_correlation_matrix", test_generate_correlation_matrix),
        ("test_accident_safety_profile", test_accident_safety_profile),
        
        # Clustering & Insights & Filters
        ("test_extract_corridor_features", test_extract_corridor_features),
        ("test_run_kmeans_clustering", test_run_kmeans_clustering),
        ("test_generate_live_insights_bottleneck_detection", test_generate_live_insights_bottleneck_detection),
        ("test_generate_live_insights_empty_handling", test_generate_live_insights_empty_handling),
        ("test_time_slice_filtering", test_time_slice_filtering),
        ("test_zone_and_severity_coordination", test_zone_and_severity_coordination),
        
        # ML Data Audit & Readiness Gate
        ("test_data_audit_rejects_single_day_fixture", test_data_audit_rejects_single_day_fixture),
        ("test_data_audit_approves_multiday_benchmark", test_data_audit_approves_multiday_benchmark),
        
        # ML Preprocessing & Feature Engineering
        ("test_preprocessing_integrity", test_preprocessing_integrity),
        ("test_feature_engineering_columns_and_bounds", test_feature_engineering_columns_and_bounds),
        ("test_target_construction", test_target_construction),
        
        # ML Zero Future Data Leakage
        ("test_zero_future_leakage_temporal_alignment", test_zero_future_leakage_temporal_alignment),
        ("test_zero_future_leakage_perturbation_test", test_zero_future_leakage_perturbation_test),
        ("test_rolling_statistics_exclude_current_time", test_rolling_statistics_exclude_current_time),
        
        # ML Baselines
        ("test_calculate_metrics_exact_values", test_calculate_metrics_exact_values),
        ("test_persistence_baseline_logic", test_persistence_baseline_logic),
        ("test_historical_average_baseline_grouping", test_historical_average_baseline_grouping),
        
        # ML Candidate Training & Sensitivity
        ("test_candidate_models_fit_and_predict", test_candidate_models_fit_and_predict),
        ("test_non_trivial_prediction_sensitivity", test_non_trivial_prediction_sensitivity),
        ("test_multi_horizon_model_wrapper", test_multi_horizon_model_wrapper),
        
        # ML Inference & Explainability
        ("test_model_explainer_dynamic_instance_attribution", test_model_explainer_dynamic_instance_attribution),
        ("test_ml_adapter_prediction_contract", test_ml_adapter_prediction_contract),
        ("test_ml_adapter_all_corridors_predictions", test_ml_adapter_all_corridors_predictions),
        ("test_ml_engine_status_reporting", test_ml_engine_status_reporting),
        
        # ML REST Ingestion Contract
        ("test_ml_prediction_multi_horizon", test_ml_prediction_multi_horizon),
        ("test_ml_feature_contributions", test_ml_feature_contributions),
        ("test_ml_ingestion_and_fallback", test_ml_ingestion_and_fallback),
    ]

    print("=" * 80)
    print("RUNNING COMPLETE CHENNAI TRAFFIC INTELLIGENCE PLATFORM TEST SUITE")
    print(f"Test Root: {PROJECT_ROOT}")
    print(f"Total Test Cases Registered: {len(test_cases)}")
    print("=" * 80)

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

    print("=" * 80)
    print(f"TEST RESULTS: {total} total | {passed} passed | {failed} failed | {errors} errors")
    print(f"Execution time: {elapsed:.4f}s")
    print("=" * 80)

    return total, passed, failed, errors


if __name__ == "__main__":
    total, passed, failed, errors = run_all_tests()
    if failed > 0 or errors > 0:
        sys.exit(1)
    sys.exit(0)
