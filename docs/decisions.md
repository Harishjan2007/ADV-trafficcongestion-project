# Architectural Decisions Log: Chennai Traffic Intelligence Platform

**Date:** 2026-08-30  
**Status:** Active Record (Phase 0)

---

## Decision Record 001: Separation of Frontend and Backend Services
- **Status:** Approved
- **Context:** The application requires high-performance spatial rendering in the browser while performing heavy multi-variate statistical aggregations, clustering, and ML payload validations.
- **Decision:** Use **React 18 + Vite + TypeScript** for the client application shell and **Python FastAPI** for the analytics, data ingestion, and ML integration services.
- **Consequences:** Provides clean separation of concerns, guarantees type safety across complex spatial schemas, and allows scientific Python packages (Pandas, Polars, Scikit-learn, Shapely) to handle analytics natively.

---

## Decision Record 002: Mapping Engine Selection (MapLibre GL JS)
- **Status:** Approved
- **Context:** The platform requires hardware-accelerated vector polyline coloring for Chennai corridors, sub-millisecond click hit-testing, custom dark command center basemaps, and multiple dynamic overlay layers (congestion, accidents, flow, predictions).
- **Decision:** Adopt **MapLibre GL JS** (open-source WebGL GIS rendering engine) as the core mapping technology.
- **Consequences:** Delivers 60 FPS performance during panning and time-slider scrubbing, eliminates vendor lock-in, and natively supports GeoJSON vector line/point styling.

---

## Decision Record 003: Storage & Analytical Serialization (Parquet + GeoJSON)
- **Status:** Approved
- **Context:** The application needs fast query times for time-sliced traffic data without requiring a complex PostgreSQL database setup during initial development phases.
- **Decision:** Standardize on columnar **Apache Parquet** for analytical time-series records and standardized **GeoJSON** for spatial road geometries.
- **Consequences:** Sub-second query times, minimal file size on disk, zero installation overhead for local development, and trivial forward migration to PostGIS if required in future releases.

---

## Decision Record 004: Decoupled Machine Learning Contract
- **Status:** Approved
- **Context:** The ML model development is an independent workstream. The dashboard must consume model outputs without depending on PyTorch/TensorFlow runtime dependencies or training code.
- **Decision:** Formalize a strict JSON schema contract (`docs/ml-integration.md` / `ml-contract/schema_prediction.json`) consumed via REST API or cached files.
- **Consequences:** The dashboard can be fully tested and demonstrated with verified sample predictions; ML models can be swapped or upgraded without modifying a single line of frontend code.

---

## Decision Record 005: Explicit Four-Tier Data State Tagging
- **Status:** Approved
- **Context:** Scientific integrity and authority trust require that users never confuse actual sensor measurements with calculated metrics, ML predictions, or synthetic fixtures.
- **Decision:** Enforce 4 explicit states (`OBSERVED`, `DERIVED`, `PREDICTED`, `SIMULATED`) across data contracts, API payloads, and UI visual indicators.
- **Consequences:** 100% transparent data lineage, compliant with Master PRD non-goals and academic defense scrutiny.
