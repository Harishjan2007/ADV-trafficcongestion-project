"""
Canonical Data Models and Schema Definitions for Chennai Traffic Intelligence Platform
Adheres strictly to docs/data-contract.md and docs/ml-integration.md
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CanonicalTrafficRecord(BaseModel):
    # Identity
    record_id: str = Field(..., description="Unique record identifier")
    timestamp: str = Field(..., description="ISO 8601 Timestamp string")

    # Geography
    latitude: float = Field(..., ge=12.80, le=13.35, description="WGS84 Latitude")
    longitude: float = Field(..., ge=80.00, le=80.40, description="WGS84 Longitude")
    road_id: str = Field(..., description="Standardized Road ID")
    road_name: str = Field(..., description="Recognized road name")
    junction: Optional[str] = Field(None, description="Major intersection or landmark")
    zone: str = Field(..., description="Administrative Zone")
    road_type: str = Field("Arterial", description="Arterial, Sub-Arterial, Expressway")

    # Traffic
    vehicle_count: int = Field(..., ge=0, description="Vehicles per hour")
    average_speed: float = Field(..., ge=0.0, description="Average speed in km/h")
    traffic_density: Optional[float] = Field(None, ge=0.0, description="Vehicles/km/lane")
    vehicle_type: Optional[str] = Field(None, description="Dominant vehicle type")
    direction: Optional[str] = Field(None, description="Northbound, Southbound, etc.")

    # Time
    date: str = Field(..., description="YYYY-MM-DD")
    hour: int = Field(..., ge=0, le=23, description="Hour of the day (0-23)")
    day_of_week: str = Field(..., description="Monday - Sunday")
    weekend_flag: bool = Field(False, description="Is weekend")
    peak_hour_flag: bool = Field(False, description="Is peak hour")

    # Weather
    weather_condition: Optional[str] = Field(None, description="Clear, Light Rain, Heavy Rain, etc.")
    rainfall: Optional[float] = Field(None, ge=0.0, description="Rainfall in mm/hr")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    visibility: Optional[float] = Field(None, ge=0.0, description="Visibility in km")

    # Road & Capacity
    road_condition: Optional[str] = Field("Dry", description="Dry, Wet, Waterlogged")
    road_capacity: int = Field(3600, ge=100, description="Design capacity in veh/hr")
    lane_count: int = Field(3, ge=1, description="Lanes per direction")
    speed_limit: float = Field(50.0, ge=10.0, description="Speed limit in km/h")

    # Accidents
    accident_count: int = Field(0, ge=0, description="Recorded incidents in window")
    accident_severity: Optional[str] = Field(None, description="Minor, Major, Fatal, None")

    # Derived
    traffic_utilization: float = Field(..., ge=0.0, description="V/C ratio")
    speed_reduction: float = Field(..., ge=0.0, le=1.0, description="Normalized speed deficit")
    congestion_index: float = Field(..., ge=0.0, le=100.0, description="0-100 composite index")
    congestion_level: str = Field("Low", description="Low, Moderate, High, Severe")
    priority_score: float = Field(0.0, ge=0.0, le=100.0, description="Decision support index")
    priority_level: str = Field("Low", description="Low, Medium, High, Critical")


class FilterQuery(BaseModel):
    date: Optional[str] = None
    hour: Optional[int] = None
    time_window: Optional[str] = None
    zone: Optional[str] = None
    congestion_level: Optional[str] = None
    weather_condition: Optional[str] = None
    has_accidents: Optional[bool] = None
    search: Optional[str] = None


class CityOverviewSummary(BaseModel):
    timestamp: str
    total_monitored_roads: int
    average_city_speed: float
    average_congestion_index: float
    severe_congestion_count: int
    high_priority_count: int
    total_active_accidents: int
    monitored_vehicle_volume: int
    data_state: str = "OBSERVED"  # OBSERVED, DERIVED, PREDICTED, SIMULATED


class FeatureContribution(BaseModel):
    feature_name: str
    importance_score: float
    direction: str  # increases_congestion / decreases_congestion


class MLPredictionPayload(BaseModel):
    location_id: str
    prediction_timestamp: str
    prediction_horizon: str  # 15min, 30min, 45min, 60min
    predicted_congestion_level: str  # Low, Moderate, High, Severe
    predicted_congestion_index: float
    predicted_vehicle_count: Optional[int] = None
    predicted_speed: Optional[float] = None
    confidence: float
    model_version: Optional[str] = "1.0.0"
    top_contributing_features: Optional[List[FeatureContribution]] = None


class AutomatedInsight(BaseModel):
    insight_id: str
    category: str  # BOTTLENECK, ACCIDENT_RISK, TEMPORAL_SPIKE, WEATHER_IMPACT, PREDICTIVE_ALERT
    title: str
    description: str
    severity: str  # INFO, WARNING, CRITICAL
    affected_locations: List[str]
    supporting_metric: str
    timestamp: str
