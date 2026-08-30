# System Architecture: Chennai Traffic Intelligence Platform

**Date:** 2026-08-30  
**Status:** Approved Architectural Blueprint (Phase 0)

---

## 1. High-Level Architectural Diagram

```
                             ┌────────────────────────────────────────────────┐
                             │             TRAFFIC AUTHORITY USER             │
                             └───────────────────────┬────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       FRONTEND APPLICATION SHELL                                        │
│                                  (React 18 + Vite + TypeScript)                                         │
│                                                                                                         │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────────────────────┐  │
│  │   INTERACTIVE CHENNAI   │  │  LOCATION INTELLIGENCE  │  │           GLOBAL CONTROLS               │  │
│  │       MAP CANVAS        │  │      DRAWER / PANEL     │  │                                         │  │
│  │  (MapLibre GL / Canvas) │  │  (Plotly / ECharts /    │  │ • Coordinated Filter Bar                │  │
│  │ • Congestion Layers     │  │   D3 Micro-Charts)      │  │ • Time Slider & Playback Engine         │  │
│  │ • Accident Markers      │  │ • KPIs & Health Score   │  │ • Layer Toggles & Preset Selectors      │  │
│  │ • Directional Flow Lines│  │ • Time Series Trends    │  │ • State Mode Indicator (Obs/Sim/Pred)   │  │
│  │ • Prediction Overlays   │  │ • Speed vs Volume       │  │                                         │  │
│  │ • Cluster Boundaries    │  │ • Day × Hour Matrix     │  │                                         │  │
│  └────────────┬────────────┘  └────────────┬────────────┘  └────────────────────┬────────────────────┘  │
│               │                            │                                    │                       │
│               └────────────────────────────┼────────────────────────────────────┘                       │
│                                            ▼                                                            │
│                         FRONTEND STATE STORE & DATA ORCHESTRATOR                                        │
│                             (Zustand / React Context API)                                               │
└────────────────────────────────────────────┬────────────────────────────────────────────────────────────┘
                                             │ HTTP / REST & Local Fast Cache
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  BACKEND & ANALYTICS SERVICE LAYER                                      │
│                                        (Python FastAPI API)                                             │
│                                                                                                         │
│  ┌───────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────┐  │
│  │    DATA INGESTION     │  │   ANALYTICS ENGINE     │  │     INSIGHT ENGINE     │  │  ML ADAPTER    │  │
│  │      & ADAPTERS       │  │                        │  │                        │  │                │  │
│  │ • CSV / Parquet Reader│  │ • Speed-Density Calc   │  │ • Bottleneck Detector  │  │ • JSON Contract│  │
│  │ • Schema Validator    │  │ • Congestion Index     │  │ • Association Rule Mnr │  │   Validator    │  │
│  │ • Geo Coordinate Norm │  │ • Clustering (DBSCAN)  │  │ • Priority Scorer      │  │ • Inference    │  │
│  │ • Missing Value Imput │  │ • Temporal Aggregation │  │ • Anomaly Flags        │  │   Consumer     │  │
│  └───────────┬───────────┘  └───────────┬────────────┘  └───────────┬────────────┘  └───────┬────────┘  │
└──────────────┼──────────────────────────┼───────────────────────────┼───────────────────────┼───────────┘
               │                          │                           │                       │
               ▼                          ▼                           ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                             DATA LAYER                                                  │
│                                                                                                         │
│  ┌─────────────────────────────────┐  ┌───────────────────────────────┐  ┌───────────────────────────┐  │
│  │      RAW / CANONICAL DATA       │  │     SPATIAL ASSETS (GIS)      │  │   EXTERNAL ML WORKSTREAM  │  │
│  │ • `data/processed/*.parquet`    │  │ • `data/geo/chennai_network.  │  │ • Decoupled Predictions   │  │
│  │ • `data/raw/*.csv`              │  │   geojson`                    │  │   (`ml-contract/*.json`)  │  │
│  │ • `data/synthetic/*.parquet`    │  │ • Chennai Arterial Polylines  │  │ • Model Meta & Confidence │  │
│  └─────────────────────────────────┘  └───────────────────────────────┘  └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architectural Principles & Separation of Concerns

### A. Strict Decoupling of Frontend & Business Logic
1. **Frontend Presentation:** Responsible exclusively for user interactions, map layer composition, responsive layouts, chart rendering, and filter coordination.
2. **Analytics & Inference Engine:** All aggregation, spatial calculations, clustering, congestion index evaluations, and automated insight generation reside in pure Python backend services (or isolated pure-function computational modules for offline client mode).
3. **Data Layer:** Standardized on Parquet format for fast column reads and GeoJSON for spatial topology, abstracting underlying storage so future migration to PostgreSQL/PostGIS is zero-impact to frontend consumers.

### B. Map-Centric Interaction Architecture
- **Single Source of Spatial Truth:** When a road or junction is selected on the map:
  - The map controller dispatches a `SELECT_LOCATION(location_id)` action.
  - The state store updates the active selection and queries the Analytics Service for the location's multi-dimensional profile.
  - The **Location Intelligence Drawer** renders smoothly without re-rendering or panning the parent map canvas unexpectedly.
  - Contextual filters (time window, weather condition, day of week) automatically filter the sub-charts within the drawer.

### C. ML Service Isolation Boundary
- The dashboard is completely decoupled from model training scripts, PyTorch/TensorFlow runtimes, and feature engineering pipelines.
- Communication with ML outputs is governed strictly by the formal specification in `docs/ml-integration.md`.
- When ML predictions are present, the UI renders predictive visual layers; when absent, the system operates seamlessly with observed analytics without throwing runtime exceptions.

---

## 3. Directory Layout & Module Structure

```text
advmainproject/
├── backend/
│   ├── api/                   # FastAPI route controllers
│   │   ├── routes_traffic.py  # Map data & traffic condition endpoints
│   │   ├── routes_analytics.py# Location drilldown & time-series endpoints
│   │   ├── routes_insights.py # Automated insight & priority endpoints
│   │   └── routes_ml.py       # Prediction ingestion & query endpoints
│   ├── analytics/             # Core analytical & statistical algorithms
│   │   ├── congestion.py      # Congestion index & speed reduction calculators
│   │   ├── clustering.py      # Spatial & temporal clustering logic
│   │   └── insights.py        # Rule-based insight & priority scoring engine
│   ├── services/              # Data services & repository layer
│   │   ├── data_loader.py     # Parquet/GeoJSON loader & cache
│   │   └── normalizer.py      # Canonical schema transformer
│   ├── models/                # Pydantic data contract schemas
│   └── main.py                # FastAPI entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── common/        # Buttons, badges, sliders, modals, loaders
│   │   │   ├── layout/        # Header, sidebar, filter bar, status docks
│   │   │   ├── map/           # MapLibre container, layer controls, legends
│   │   │   ├── drawer/        # Location Intelligence drawer & tabs
│   │   │   └── charts/        # Plotly/ECharts wrappers (TimeSeries, Heatmap, Scatter)
│   │   ├── context/ or store/ # State management (Zustand / React Context)
│   │   ├── hooks/             # Custom hooks (useTrafficData, useMapLayers, useTimeSlider)
│   │   ├── services/          # API client for backend communication
│   │   ├── types/             # TypeScript interfaces for Canonical Data & ML Contracts
│   │   ├── styles/            # Design system, CSS variables, glassmorphism tokens
│   │   ├── App.tsx            # Main application layout
│   │   └── main.tsx           # Entry point
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   ├── raw/                   # Unprocessed raw CSV/JSON files
│   ├── processed/             # Cleaned Parquet & standardized GeoJSON files
│   ├── geo/                   # Chennai GIS network polylines & junction nodes
│   └── synthetic/             # Explicitly labeled SIMULATED development fixtures
│
├── ml-contract/               # Formal schemas & sample prediction payloads
│   ├── schema_prediction.json
│   └── sample_prediction.json
│
├── tests/                     # Unit, integration, and contract tests
│   ├── test_normalization.py
│   ├── test_congestion.py
│   ├── test_insights.py
│   └── test_api_contracts.py
│
├── docs/                      # Comprehensive documentation suite
└── README.md
```

---

## 4. Performance & Scalability Strategy

1. **Spatial Rendering:** Vector polylines for Chennai roads use GPU-accelerated WebGL layers (MapLibre GL JS), ensuring smooth 60 FPS panning, zooming, and hover detection.
2. **Data Streaming & Caching:** Time-slice datasets are pre-computed into optimized Parquet blocks and indexed by `(location_id, hour, date)`.
3. **Throttled Time Playback:** Temporal slider animations utilize `requestAnimationFrame` with debounce/throttle to prevent UI thread lock.
