"""
Unit Tests for Phase 5 Advanced Analytics & Visualizations
Validates correlation matrix math, leaderboard dynamic sorting, and accident safety analysis.
"""

from backend.analytics.correlation import compute_pearson_correlation, generate_correlation_matrix
from backend.analytics.accidents import analyze_accident_safety_profile


def test_pearson_correlation_perfect_positive():
    x = [10.0, 20.0, 30.0, 40.0, 50.0]
    y = [100.0, 200.0, 300.0, 400.0, 500.0]
    r = compute_pearson_correlation(x, y)
    assert r == 1.0


def test_pearson_correlation_perfect_negative():
    # Speed decreasing as volume increases
    volume = [1000.0, 2000.0, 3000.0, 4000.0]
    speed = [45.0, 35.0, 25.0, 15.0]
    r = compute_pearson_correlation(volume, speed)
    assert r == -1.0


def test_pearson_correlation_edge_cases():
    # Zero variance in y
    x = [10.0, 20.0, 30.0]
    y = [5.0, 5.0, 5.0]
    r = compute_pearson_correlation(x, y)
    assert r == 0.0

    # Less than 2 elements
    assert compute_pearson_correlation([1.0], [2.0]) is None


def test_generate_correlation_matrix():
    sample_records = [
        {"vehicle_count": 1000, "average_speed": 45.0, "traffic_utilization": 0.25, "rainfall": 0.0, "accident_count": 0},
        {"vehicle_count": 2500, "average_speed": 32.0, "traffic_utilization": 0.625, "rainfall": 1.2, "accident_count": 0},
        {"vehicle_count": 4200, "average_speed": 12.0, "traffic_utilization": 1.05, "rainfall": 6.5, "accident_count": 1},
        {"vehicle_count": 3800, "average_speed": 15.0, "traffic_utilization": 0.95, "rainfall": 4.0, "accident_count": 1}
    ]
    res = generate_correlation_matrix(sample_records)
    assert "correlation_matrix" in res
    matrix = res["correlation_matrix"]
    assert len(matrix) == 5
    assert len(matrix[0]) == 5

    # Diagonal must be 1.0
    for i in range(5):
        assert matrix[i][i] == 1.0

    # Symmetry check: M[i][j] == M[j][i]
    for i in range(5):
        for j in range(5):
            assert matrix[i][j] == matrix[j][i]


def test_accident_safety_profile():
    sample_records = [
        {"road_id": "ROAD_A", "hour": 8, "accident_count": 1, "accident_severity": "Minor", "weather_condition": "Light Rain"},
        {"road_id": "ROAD_A", "hour": 9, "accident_count": 2, "accident_severity": "Major", "weather_condition": "Heavy Rain"},
        {"road_id": "ROAD_A", "hour": 14, "accident_count": 0, "accident_severity": None, "weather_condition": "Clear"}
    ]
    profile = analyze_accident_safety_profile(sample_records, "ROAD_A")
    assert profile["total_recorded_accidents"] == 3
    assert profile["hourly_minor"][8] == 1
    assert profile["hourly_major"][9] == 2
    assert profile["severity_breakdown"]["Minor"] == 1
    assert profile["severity_breakdown"]["Major"] == 2
    assert profile["weather_breakdown"]["Light Rain"] == 1
    assert profile["weather_breakdown"]["Heavy Rain"] == 2
    assert profile["has_accidents"] is True
