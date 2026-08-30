export type CongestionLevel = 'Low' | 'Moderate' | 'High' | 'Severe';
export type PriorityLevel = 'Low' | 'Medium' | 'High' | 'Critical';
export type DataState = 'OBSERVED' | 'DERIVED' | 'PREDICTED' | 'SIMULATED';

export interface CanonicalRecord {
  record_id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  road_id: string;
  road_name: string;
  junction?: string;
  zone: string;
  road_type: string;
  vehicle_count: number;
  average_speed: number;
  traffic_density?: number;
  vehicle_type?: string;
  direction?: string;
  date: string;
  hour: number;
  day_of_week: string;
  weekend_flag: boolean;
  peak_hour_flag: boolean;
  weather_condition?: string;
  rainfall?: number;
  temperature?: number;
  visibility?: number;
  road_condition?: string;
  road_capacity: number;
  lane_count: number;
  speed_limit: number;
  accident_count: number;
  accident_severity?: string;
  traffic_utilization: number;
  speed_reduction: number;
  congestion_index: number;
  congestion_level: CongestionLevel;
  priority_score: number;
  priority_level: PriorityLevel;
}

export interface CityOverview {
  timestamp: string;
  total_monitored_roads: number;
  average_city_speed: number;
  average_congestion_index: number;
  severe_congestion_count: number;
  high_priority_count: number;
  total_active_accidents: number;
  monitored_vehicle_volume: number;
  data_state: DataState;
}

export interface FeatureContribution {
  feature_name: string;
  importance_score: number;
  direction: 'increases_congestion' | 'decreases_congestion';
}

export interface MLPrediction {
  location_id: string;
  prediction_timestamp: string;
  prediction_horizon: string;
  predicted_congestion_level: CongestionLevel;
  predicted_congestion_index: number;
  predicted_vehicle_count?: number;
  predicted_speed?: number;
  confidence: number;
  model_version?: string;
  top_contributing_features?: FeatureContribution[];
}

export interface AutomatedInsight {
  insight_id: string;
  category: 'BOTTLENECK' | 'ACCIDENT_RISK' | 'TEMPORAL_SPIKE' | 'WEATHER_IMPACT' | 'PREDICTIVE_ALERT';
  title: string;
  description: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  affected_locations: string[];
  supporting_metric: string;
  timestamp: string;
}

export interface MapLayerToggles {
  congestion: boolean;
  accidents: boolean;
  flow: boolean;
  priority: boolean;
  prediction: boolean;
  clusters: boolean;
}

export interface FilterState {
  zone: string;
  congestionLevel: string;
  weather: string;
  accidentsOnly: boolean;
  searchQuery: string;
}
