import { create } from 'zustand';
import { CanonicalRecord, CityOverview, MapLayerToggles, MLPrediction } from '../types/traffic';

interface TrafficState {
  currentHour: number;
  isPlaying: boolean;
  selectedRoadId: string | null;
  selectedRoadData: CanonicalRecord | null;
  cityOverview: CityOverview | null;
  layers: MapLayerToggles;
  selectedZone: string;
  selectedSeverity: string;
  mlPrediction: MLPrediction | null;

  // Actions
  setHour: (hour: number) => void;
  togglePlay: () => void;
  selectRoad: (roadId: string | null) => void;
  setLayers: (layers: Partial<MapLayerToggles>) => void;
  setZoneFilter: (zone: string) => void;
  setSeverityFilter: (severity: string) => void;
}

export const useTrafficStore = create<TrafficState>((set) => ({
  currentHour: 8,
  isPlaying: false,
  selectedRoadId: 'ROAD_ANNA_SALAI_1',
  selectedRoadData: null,
  cityOverview: {
    timestamp: '2026-08-30T08:00:00+05:30',
    total_monitored_roads: 10,
    average_city_speed: 18.4,
    average_congestion_index: 74.2,
    severe_congestion_count: 4,
    high_priority_count: 3,
    total_active_accidents: 3,
    monitored_vehicle_volume: 44820,
    data_state: 'SIMULATED'
  },
  layers: {
    congestion: true,
    accidents: true,
    flow: false,
    priority: true,
    prediction: false,
    clusters: false
  },
  selectedZone: '',
  selectedSeverity: '',
  mlPrediction: null,

  setHour: (hour: number) => set({ currentHour: hour }),
  togglePlay: () => set((state: TrafficState) => ({ isPlaying: !state.isPlaying })),
  selectRoad: (roadId: string | null) => set({ selectedRoadId: roadId }),
  setLayers: (updated: Partial<MapLayerToggles>) => set((state: TrafficState) => ({ layers: { ...state.layers, ...updated } })),
  setZoneFilter: (zone: string) => set({ selectedZone: zone }),
  setSeverityFilter: (severity: string) => set({ selectedSeverity: severity })
}));
