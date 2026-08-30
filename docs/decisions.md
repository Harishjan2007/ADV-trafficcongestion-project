# Architectural Decisions Log: Chennai Traffic Intelligence Platform

**Date:** 2026-08-30  
**Status:** Active Record (Full Platform Baseline: Reviews 1, 2, & 3 Completed)

---

## Decision Record 001: Separation of Frontend and Backend Services
- **Status:** Approved
- **Context:** High-performance spatial rendering in browser while performing multi-variate statistical aggregations and clustering.
- **Decision:** Use React 18 + TypeScript + MapLibre GL for the web application shell and Python FastAPI for backend analytics.

---

## Decision Record 002: Mapping Engine Selection (MapLibre GL JS)
- **Status:** Approved
- **Context:** Hardware-accelerated vector polyline coloring for Chennai corridors, sub-millisecond click hit-testing, and dynamic layer overlays.
- **Decision:** Adopt MapLibre GL JS with custom dark command center basemap tiles.

---

## Decision Record 003: Columnar Analytical Storage (Parquet & GeoJSON)
- **Status:** Approved
- **Context:** Fast queries for time-sliced traffic data without heavy SQL infrastructure.
- **Decision:** Store canonical analytical series in Parquet and spatial road vectors in GeoJSON.

---

## Decision Record 004: Decoupled Machine Learning Contract
- **Status:** Approved (Phase 0 / Phase 9)
- **Context:** Independent ML workstream without coupling model training frameworks to UI.
- **Decision:** Consume predictions strictly via JSON Schema Draft-07 prediction contract (`docs/ml-integration.md`).

---

## Decision Record 005: Explicit Four-Tier Data State Tagging
- **Status:** Approved
- **Context:** Scientific integrity and authority transparency.
- **Decision:** Enforce 4 explicit states (`OBSERVED`, `DERIVED`, `PREDICTED`, `SIMULATED`) across data contracts and UI badges.

---

## Decision Record 006: Dynamic Pearson Correlation & Statistical Association
- **Status:** Approved (Phase 5)
- **Context:** Master PRD explicitly mandates that statistical correlation must not be presented as direct causation.
- **Decision:** Implement dynamic Pearson correlation across 5 dimensions ($V, S, U, \text{Rain}, \text{Accidents}$) with descriptive statistical association tooltips and explicit non-causal disclaimers.

---

## Decision Record 007: Dynamic Corridor Leaderboard Ranking
- **Status:** Approved (Phase 5)
- **Context:** Rankings must reflect active dataset and filter parameters rather than hard-coded strings.
- **Decision:** Compute leaderboard rankings dynamically on the client and backend sorted by `congestion_index` descending, supporting one-click map camera fly-to interaction.

---

## Decision Record 008: Unsupervised K-Means Behavioral Clustering
- **Status:** Approved (Review 2 / Phase 7)
- **Context:** Master PRD strictly prohibits manually hardcoding roads to cluster groups.
- **Decision:** Execute unsupervised K-Means clustering dynamically on extracted 5-dimensional feature vectors $[ \text{Peak } CI, \, \text{Off-Peak } CI, \, \text{Speed Variance}, \, \text{Rain Sensitivity}, \, \text{Accidents} ]$, with labels derived from centroid properties.

---

## Decision Record 009: Documented Multi-Factor Decision Support Priority Score
- **Status:** Approved (Review 2 / Phase 8)
- **Context:** Priority scoring must be mathematically justified and transparent before deployment.
- **Decision:** Formulate Priority Score as:
  $$PS = \min\left(100.0, \, 0.40 \cdot CI + 0.30 \cdot (R_v \cdot 100) + 0.20 \cdot \min(100, \text{Accidents} \times 50) + 0.10 \cdot (\text{Peak} ? 100 : 0)\right)$$
  Document clearly that $PS$ is exclusively a decision support triage index for human operators, not an autonomous traffic control system.

---

## Decision Record 010: Multi-Horizon Predictive ML Adapter & Explainability
- **Status:** Approved (Review 3 / Phase 9)
- **Context:** Traffic authorities need proactive 15–60 minute lead time forecasts to deploy traffic wardens prior to peak gridlock.
- **Decision:** Implement the `MLPredictionAdapter` providing spatio-temporal predictions (+15m, +30m, +45m, +60m), 95% confidence bounds, and SHAP feature importance driver weights in the Location Drawer.
