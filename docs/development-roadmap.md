# Detailed Development Roadmap: Chennai Traffic Intelligence Platform

**Date:** 2026-08-30  
**Status:** Approved Roadmap (Phase 0)

---

## 1. Development Phases Overview

The project is structured into 11 strictly phased work packages to ensure incremental validation, zero technical debt, and continuous testability.

```
PHASE 0: Project Discovery & Architecture Design (COMPLETED)
   │
   ▼
PHASE 1: Project & Application Shell Foundation
   │
   ▼
PHASE 2: Data Foundation & Canonical Ingestion Pipeline
   │
   ▼
PHASE 3: Chennai Map Engine & Geographic Visualization MVP
   │
   ▼
PHASE 4: Map Interaction & Location Intelligence Drawer
   │
   ▼
PHASE 5: Advanced Multidimensional Visualizations
   │
   ▼
PHASE 6: Temporal Slider, Animation & Directional Flow
   │
   ▼
PHASE 7: Geographic & Behavioral Clustering
   │
   ▼
PHASE 8: Automated Insight & Priority Decision Engine
   │
   ▼
PHASE 9: ML Prediction Contract & Forecast Visualizer
   │
   ▼
PHASE 10: Production Hardening, Quality Assurance & Demo Validation
```

---

## 2. Phase-by-Phase Specification

### Phase 0: Project Discovery & Architecture Design
- **Objective:** Perform repository audit, synthesize Master PRD, design canonical contracts, define visualization methodology, and establish complete documentation baseline.
- **Dependencies:** Master PRD.
- **Files / Artifacts:** `docs/project-audit.md`, `docs/prd-summary.md`, `docs/architecture.md`, `docs/data-contract.md`, `docs/data-sources.md`, `docs/ml-integration.md`, `docs/visualization-methodology.md`, `docs/development-roadmap.md`, `docs/progress.md`, `docs/decisions.md`.
- **Deliverables:** Complete architectural specification and plan approval.
- **Acceptance Criteria:** All documentation files created and aligned with Master PRD; zero unverified assumptions.
- **Estimated Complexity:** Moderate (Completed in Phase 0).

---

### Phase 1: Project & Application Shell Foundation
- **Objective:** Establish the modular repository structure, initialize the TypeScript frontend (Vite + React) and Python backend (FastAPI), establish design tokens (tactical traffic dark mode), and build the base layout shell.
- **Dependencies:** Phase 0.
- **Files / Modules:**
  - `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`
  - `frontend/src/styles/theme.css` (color tokens: Emerald `#10B981`, Amber `#F59E0B`, Orange `#F97316`, Red `#EF4444`, dark slate surfaces)
  - `frontend/src/components/layout/Header.tsx`, `frontend/src/components/layout/AppShell.tsx`
  - `backend/main.py`, `backend/requirements.txt`
- **Deliverables:** Runnable frontend and backend servers; professional command-center header, filter container, and map viewport.
- **Acceptance Criteria:** `npm run dev` and `uvicorn backend.main:app` execute cleanly with zero errors; UI displays responsive command shell.
- **Estimated Complexity:** Low - Medium.

---

### Phase 2: Data Foundation & Canonical Ingestion Pipeline
- **Objective:** Create the canonical data normalization service, Pydantic schemas, coordinate transformers, derived metric calculators ($U$, $R_v$, $CI$, Priority), and calibrated Chennai development fixtures (`data/geo/chennai_network.geojson`, `data/synthetic/chennai_dev_traffic.parquet`).
- **Dependencies:** Phase 1.
- **Files / Modules:**
  - `backend/models/schemas.py`
  - `backend/services/normalizer.py`
  - `backend/services/congestion_calc.py`
  - `backend/services/data_loader.py`
  - `data/geo/chennai_network.geojson` (real Chennai arterial polylines & coordinates)
  - `data/synthetic/chennai_dev_traffic.parquet`
  - `tests/test_normalization.py`
- **Deliverables:** Validated data ingestion pipeline capable of streaming time-sliced canonical records to API endpoints.
- **Acceptance Criteria:** 100% test pass on data normalization and metric formulas; strict adherence to `docs/data-contract.md`.
- **Estimated Complexity:** Medium.

---

### Phase 3: Chennai Map Engine & Geographic Visualization MVP
- **Objective:** Implement the MapLibre GL map engine centered on Chennai (`[80.2707, 13.0827]`), render road network polylines colored by congestion severity, render distinct accident point layers, and provide interactive legends and layer toggles.
- **Dependencies:** Phase 2.
- **Files / Modules:**
  - `frontend/src/components/map/MapContainer.tsx`
  - `frontend/src/components/map/MapLegend.tsx`
  - `frontend/src/components/map/LayerControls.tsx`
  - `frontend/src/hooks/useMapLayers.ts`
  - `frontend/src/types/traffic.ts`
- **Deliverables:** High-performance, GPU-accelerated interactive Chennai map showing colored congestion lines and incident markers.
- **Acceptance Criteria:** Smooth panning/zooming; clear visual distinction of Low/Moderate/High/Severe congestion; accident layer toggleable.
- **Estimated Complexity:** Medium.

---

### Phase 4: Map Interaction & Location Intelligence Drawer
- **Objective:** Enable click-to-investigate workflow on any Chennai road or junction, displaying selected-road visual highlight on map and opening the responsive Location Intelligence right-side drawer with instant KPIs.
- **Dependencies:** Phase 3.
- **Files / Modules:**
  - `frontend/src/components/drawer/LocationDrawer.tsx`
  - `frontend/src/components/drawer/LocationHeader.tsx`
  - `frontend/src/components/drawer/QuickMetrics.tsx`
  - `frontend/src/components/map/RoadHighlightLayer.tsx`
  - `frontend/src/store/trafficStore.ts`
- **Deliverables:** Seamless transition from city-wide map view to localized corridor intelligence with instant metrics (Speed, Volume, Congestion Index, Incidents).
- **Acceptance Criteria:** Clicking any road segment highlights it clearly on map, opens drawer within 100ms, preserves map context, and provides a clear close/back button.
- **Estimated Complexity:** Medium.

---

### Phase 5: Advanced Multidimensional Visualizations
- **Objective:** Implement full suite of analytical charts inside the Location Drawer: 24-hour congestion/volume time-series, $7 \times 24$ Day $\times$ Hour recurring heatmap, vehicle count vs. speed scatter plot with regression trendline, and accident temporal breakdown.
- **Dependencies:** Phase 4.
- **Files / Modules:**
  - `frontend/src/components/charts/TimeSeriesChart.tsx`
  - `frontend/src/components/charts/DayHourHeatmap.tsx`
  - `frontend/src/components/charts/VolumeSpeedScatter.tsx`
  - `frontend/src/components/charts/AccidentBreakdownChart.tsx`
  - `backend/api/routes_analytics.py`
- **Deliverables:** Rich analytical visual deep-dive for any selected Chennai location.
- **Acceptance Criteria:** All charts render smoothly; tooltip inspections provide units and context; defensive fallbacks if weather/accidents are null.
- **Estimated Complexity:** High.

---

### Phase 6: Temporal Slider, Animation & Directional Flow
- **Objective:** Add interactive time slider with play/pause animation across historical time steps (e.g. 08:00 $\rightarrow$ 08:30 $\rightarrow$ 09:00), update map state dynamically, and implement directional flow vectors (animated line arrows).
- **Dependencies:** Phase 5.
- **Files / Modules:**
  - `frontend/src/components/controls/TimeSlider.tsx`
  - `frontend/src/components/map/TrafficFlowLayer.tsx`
  - `frontend/src/hooks/useTimePlayback.ts`
- **Deliverables:** Dynamic temporal playback of traffic buildup and arterial flow vectors.
- **Acceptance Criteria:** Slider scrub updates all active map segments synchronously; exact historical timestamp displayed; no UI freezing during animation.
- **Estimated Complexity:** Medium - High.

---

### Phase 7: Geographic & Behavioral Clustering
- **Objective:** Implement unsupervised clustering (K-Means/DBSCAN) grouping Chennai corridors exhibiting similar congestion signatures (e.g., peak-hour bottlenecks vs. steady-flow expressways vs. monsoon-vulnerable arterials) and render visual cluster overlays on the map.
- **Dependencies:** Phase 6.
- **Files / Modules:**
  - `backend/analytics/clustering.py`
  - `frontend/src/components/map/ClusterLayer.tsx`
  - `frontend/src/components/charts/ClusterRadarChart.tsx`
- **Deliverables:** Behavioral cluster classification layer and cluster profile inspector.
- **Acceptance Criteria:** Roads categorized into interpretable behavioral groups; visual map boundary/color coding; clear cluster explanation tooltips.
- **Estimated Complexity:** Medium.

---

### Phase 8: Automated Insight & Priority Decision Engine
- **Objective:** Build deterministic insight generator computing plain-language analytical observations (peak windows, speed deficits, accident concentrations) and multi-factor Priority Decision Support scores (Low, Medium, High, Critical).
- **Dependencies:** Phase 7.
- **Files / Modules:**
  - `backend/analytics/insights.py`
  - `backend/api/routes_insights.py`
  - `frontend/src/components/drawer/InsightsTab.tsx`
  - `frontend/src/components/common/PriorityBadge.tsx`
  - `tests/test_insights.py`
- **Deliverables:** Rule-based automated insights panel and ranked priority triage list for traffic authorities.
- **Acceptance Criteria:** Insights dynamically generated from active filter/location state without hardcoding; zero unsubstantiated causal claims.
- **Estimated Complexity:** Medium.

---

### Phase 9: ML Prediction Contract & Forecast Visualizer
- **Objective:** Implement the decoupled ML prediction adapter, load future forecast vectors (+30 min / +60 min), render the predictive congestion map layer, and display confidence envelopes and feature contributions in the Location Drawer.
- **Dependencies:** Phase 8.
- **Files / Modules:**
  - `backend/api/routes_ml.py`
  - `backend/services/ml_adapter.py`
  - `ml-contract/schema_prediction.json`
  - `frontend/src/components/drawer/PredictionTab.tsx`
  - `frontend/src/components/map/PredictionMapLayer.tsx`
  - `tests/test_ml_contract.py`
- **Deliverables:** Fully functioning predictive intelligence module seamlessly integrated via the formal ML contract.
- **Acceptance Criteria:** Visible `PREDICTED` badges; prediction layer toggle; confidence scores and top contributing factors displayed accurately.
- **Estimated Complexity:** Medium - High.

---

### Phase 10: Production Hardening, Quality Assurance & Demo Validation
- **Objective:** Implement comprehensive error boundaries, loading skeletons, responsive drawer transitions, performance benchmarking, end-to-end user scenario validation (Review 1-3 & Final Demo flows), and final documentation updates.
- **Dependencies:** Phase 9.
- **Files / Modules:**
  - `frontend/src/components/common/ErrorBoundary.tsx`
  - `frontend/src/components/common/LoadingSkeleton.tsx`
  - `tests/e2e/test_traffic_workflow.py`
  - `docs/walkthrough.md`
- **Deliverables:** Production-grade, resilient, polished traffic authority intelligence platform ready for academic defense and live authority demonstration.
- **Acceptance Criteria:** Zero console warnings/errors; lighthouse performance > 90; flawless execution of the end-to-end Master PRD narrative.
- **Estimated Complexity:** Medium.
