"""
Unit Tests for Phase 7 Behavioral & Geographic Clustering Engine
Validates feature extraction, normalization, and K-Means mathematical convergence.
"""

from backend.analytics.clustering import extract_corridor_features, run_kmeans_clustering


def test_extract_corridor_features():
    sample_records = [
        {"road_id": "ROAD_1", "road_name": "Anna Salai", "zone": "Central", "hour": 8, "congestion_index": 85.0, "average_speed": 14.0, "accident_count": 1, "rainfall": 2.0},
        {"road_id": "ROAD_1", "road_name": "Anna Salai", "zone": "Central", "hour": 9, "congestion_index": 88.0, "average_speed": 12.0, "accident_count": 0, "rainfall": 1.0},
        {"road_id": "ROAD_1", "road_name": "Anna Salai", "zone": "Central", "hour": 14, "congestion_index": 35.0, "average_speed": 40.0, "accident_count": 0, "rainfall": 0.0},
        {"road_id": "ROAD_2", "road_name": "ECR", "zone": "South", "hour": 8, "congestion_index": 20.0, "average_speed": 45.0, "accident_count": 0, "rainfall": 0.0},
        {"road_id": "ROAD_2", "road_name": "ECR", "zone": "South", "hour": 14, "congestion_index": 15.0, "average_speed": 48.0, "accident_count": 0, "rainfall": 0.0}
    ]

    features = extract_corridor_features(sample_records)
    assert "ROAD_1" in features
    assert "ROAD_2" in features

    assert features["ROAD_1"]["metrics"]["peak_ci"] == 88.0
    assert features["ROAD_1"]["metrics"]["total_accidents"] == 1
    assert features["ROAD_2"]["metrics"]["peak_ci"] == 20.0
    assert features["ROAD_2"]["metrics"]["total_accidents"] == 0


def test_run_kmeans_clustering():
    sample_records = [
        # Road A: Heavy peak congestion & accidents
        {"road_id": "ROAD_A", "road_name": "Corridor A", "zone": "Central", "hour": 8, "congestion_index": 90.0, "average_speed": 12.0, "accident_count": 2, "rainfall": 5.0},
        {"road_id": "ROAD_A", "road_name": "Corridor A", "zone": "Central", "hour": 14, "congestion_index": 40.0, "average_speed": 35.0, "accident_count": 0, "rainfall": 0.0},
        # Road B: Also heavy peak congestion
        {"road_id": "ROAD_B", "road_name": "Corridor B", "zone": "South", "hour": 8, "congestion_index": 85.0, "average_speed": 15.0, "accident_count": 1, "rainfall": 4.0},
        {"road_id": "ROAD_B", "road_name": "Corridor B", "zone": "South", "hour": 14, "congestion_index": 38.0, "average_speed": 38.0, "accident_count": 0, "rainfall": 0.0},
        # Road C: Free flow steady
        {"road_id": "ROAD_C", "road_name": "Corridor C", "zone": "Coastal", "hour": 8, "congestion_index": 20.0, "average_speed": 46.0, "accident_count": 0, "rainfall": 0.0},
        {"road_id": "ROAD_C", "road_name": "Corridor C", "zone": "Coastal", "hour": 14, "congestion_index": 18.0, "average_speed": 48.0, "accident_count": 0, "rainfall": 0.0}
    ]

    features = extract_corridor_features(sample_records)
    clustering_res = run_kmeans_clustering(features, k=2)

    assert "cluster_profiles" in clustering_res
    assert "road_cluster_assignments" in clustering_res
    assert len(clustering_res["cluster_profiles"]) <= 2

    # Road A and Road B should logically belong to the same cluster due to similar feature vectors
    assign_a = clustering_res["road_cluster_assignments"]["ROAD_A"]["cluster_id"]
    assign_b = clustering_res["road_cluster_assignments"]["ROAD_B"]["cluster_id"]
    assign_c = clustering_res["road_cluster_assignments"]["ROAD_C"]["cluster_id"]

    assert assign_a == assign_b
    assert assign_a != assign_c
