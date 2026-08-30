# Chennai Traffic Intelligence Platform: Demonstration Walkthrough & Operator Guide

**Platform Status:** Operational Baseline (Reviews 1, 2, & 3 Completed)  
**Target Audience:** Metropolitan Traffic Authority Controllers, Transportation Analysts, and Project Evaluators  
**Date:** 2026-08-30  

---

## 1. Quick Start & Accessing the Platform

1. **Standalone Visual Platform:**
   - Open [`index.html`](file:///c:/Users/haris/OneDrive/Desktop/advmainproject/index.html) in Google Chrome, Microsoft Edge, or Firefox.
   - Zero installation required (MapLibre GL, Plotly.js, and Lucide are bundled via high-speed CDNs).
2. **Backend API Services (Optional REST Layer):**
   - Start the FastAPI backend:
     ```bash
     uvicorn backend.main:app --reload --port 8000
     ```
   - Interactive Swagger API Documentation is accessible at `http://localhost:8000/docs`.

---

## 2. 10-Step Interactive Demonstration Walkthrough

Follow this 10-step sequence to demonstrate the platform capabilities across all Master PRD requirements:

### Step 1: Real-Time Spatial Overview (Review 1 Baseline)
- **Action:** Open the platform and inspect the central dark MapLibre GL map.
- **Observation:** Chennai arterial corridors are rendered as colored vector polylines:
  - 🔴 **Crimson Red ($CI \ge 75$):** Severe bottlenecks (e.g. Anna Salai, GST Road near Kathipara).
  - 🟠 **Orange ($55 \le CI < 75$):** High congestion.
  - 🟡 **Amber Gold ($30 \le CI < 55$):** Moderate volume.
  - 🟢 **Emerald Green ($CI < 30$):** Free-flow traffic (e.g. ECR coastal corridor).
  - ⚠️ **Yellow Markers:** Active collision blackspots at major junctions.

### Step 2: Top KPI Telemetry
- **Action:** Inspect the 4 floating KPI cards at the top-left of the map.
- **Observation:** Live city aggregate speed (`18.4 km/h`), active vehicular flow (`44,820 veh/hr`), severe corridor count (`4 roads`), and incident blackspots (`3 active`).

### Step 3: 24-Hour Temporal Slider & Animation (Review 2 Baseline)
- **Action:**
  1. Scrub the time slider from `08:00` (Morning Peak) to `14:00` (Afternoon Off-Peak) to `18:00` (Evening Rush).
  2. Click the ▶ **Play** button to initiate automated playback.
  3. Click **`5x`** speed multiplier to rapidly watch tidal traffic progression across 24 hours.
- **Observation:** Road colors, KPIs, rankings, and insights continuously recalculate and animate with zero page reloads.

### Step 4: Coordinated Multi-Filters
- **Action:**
  1. In the top filter bar, change the **Zone** selector to `South Zone`.
  2. Change **Congestion Severity** to `Severe`.
- **Observation:** The map polylines and left leaderboard instantly filter to show only severe corridors in South Chennai (e.g. GST Road).

### Step 5: Corridor Leaderboard & Fly-To Navigation
- **Action:** Click on the #1 ranked corridor in the left dock (`GST Road` or `Anna Salai`).
- **Observation:** The map camera smoothly flies and zooms into the selected corridor, activating a glowing highlight, while the **Location Intelligence Drawer** slides out on the right.

### Step 6: Location Intelligence & Tactical Decision Support
- **Action:** Review the **Overview** tab in the right drawer.
- **Observation:** Displays granular corridor metrics: speed vs speed limit (-71% deficit), volume vs capacity (92.6% utilization), Congestion Index ($CI = 78.2$), Priority Score (`CRITICAL PRIORITY: 82.5`), and automated Dispatch Recommendations for traffic wardens.

### Step 7: Advanced Visualizations (Tabs 3–8)
- **Action:** Cycle through the drawer analytical tabs:
  - **`24h Trend`:** Dual-axis bar and line chart showing diurnal congestion curve.
  - **`Speed vs Vol`:** 2D scatter plot with Greenshields fundamental capacity curve.
  - **`Correlation`:** $5 \times 5$ Pearson correlation matrix. Hover over cells to see exact $r$ values and non-causal statistical interpretations.
  - **`Safety`:** Stacked bar chart of Minor vs Major collisions with precipitation overlay.
  - **`Day × Hour`:** 7-day $\times$ 24-hour diurnal matrix heatmap.

### Step 8: Unsupervised Behavioral Clustering (Phase 7)
- **Action:**
  1. In the top filter bar, click the **`Clusters`** chip toggle.
  2. In the right drawer, click the **`Clusters`** tab.
- **Observation:** Roads recolor based on algorithmically computed K-Means clusters (Pink = High-Peak Chokepoints, Cyan = Rain-Sensitive Arterials, Green = Steady Flow Arterials). The **Polar Radar Spider Chart** displays the 5-dimensional centroid footprint.

### Step 9: Directional Traffic Flow Vectors (Phase 6)
- **Action:** Click the **`Flow Vectors`** chip toggle in the filter bar.
- **Observation:** Cyan animated flow vectors travel along the corridors, visually communicating tidal directional movement.

### Step 10: Predictive ML Forecasting (+30m Horizon) (Review 3 / Phase 9)
- **Action:**
  1. Click the **`+30m ML Forecast`** chip toggle in the filter bar.
  2. Open the **`✦ ML Forecast`** tab in the Location Intelligence Drawer.
- **Observation:** The predictive map layer lights up in violet/purple. The forecast chart displays the observed baseline against the +30m predicted curve with shaded 95% confidence bands and the **Top Contributing Drivers** (e.g. *Rainfall Accumulation +42%, Upstream Inflow +31%*).

---

## 3. Data Tiering & Lineage Summary

| Data Tier | Implementation | Where Seen in Platform |
| :--- | :--- | :--- |
| **`OBSERVED`** | Real Chennai road vector linestrings and landmark junction coordinates. | Map canvas geometry, road names, speed limits. |
| **`DERIVED`** | Mathematical formulas for $U$, $R_v$, $CI$, Priority Score ($PS$), Pearson $r$, K-Means centroids. | KPI cards, Leaderboard rankings, Correlation matrix, Radar chart. |
| **`PREDICTED`** | Spatio-temporal ML predictions from `ST-GCN-Chennai-v2.1` with confidence metrics. | Purple map layer, Forecast chart with 95% band, Feature importance chart. |
| **`SIMULATED`** | Calibrated 24-hour synthetic fixtures representing Chennai diurnal patterns. | Explicitly labeled **`SIMULATED DATA`** badge in header and drawer. |
