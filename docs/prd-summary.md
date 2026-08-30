# Master PRD Summary: Chennai Traffic Intelligence Platform

**Document Reference:** `Chennai_Traffic_Intelligence_Master_PRD (1).pdf`  
**Purpose:** Developer & stakeholder quick-reference summary of core requirements, visual standards, and boundaries.

---

## 1. Product Vision & Philosophy

- **Product Name:** Chennai Traffic Intelligence & Multidimensional Visualization Platform
- **Core Principle:** An interactive **Traffic Authority Command & Intelligence System**, NOT a generic static analytics dashboard.
- **Hero Element:** The interactive **Chennai Geographic Map** is the central anchor of the entire product. All analytical views, drill-downs, and predictions are entered through geographic exploration.
- **Analytical Story Arc:**
  $$\text{WHERE} \longrightarrow \text{WHEN} \longrightarrow \text{WHAT IS HAPPENING} \longrightarrow \text{WHAT FACTORS ARE ASSOCIATED} \longrightarrow \text{WHAT IS LIKELY NEXT} \longrightarrow \text{WHAT NEEDS ATTENTION}$$

---

## 2. Target Users & Workflow

- **Primary Persona:** Traffic Authorities, Traffic Inspectors, and Urban Mobility Analysts in Chennai.
- **Core User Journey:**
  1. Open Platform $\rightarrow$ View full Chennai city-wide map.
  2. Visually scan colored congestion network (Green $\rightarrow$ Yellow $\rightarrow$ Orange $\rightarrow$ Red) and distinct incident markers ($\triangle$).
  3. Identify high-priority hotspots (combining severe congestion + accidents).
  4. Click a specific road/junction/corridor.
  5. Contextually open the **Location Intelligence Panel** (drawer) without losing the map view.
  6. Inspect real-time/historical KPIs, traffic trends, speed-vs-volume scatter plots, accident patterns, and weather associations.
  7. Move the Time Slider to inspect temporal evolution and historical playback.
  8. Switch to the ML Prediction layer to inspect future estimated congestion (+30 min) and model explanations.
  9. Review system-generated Decision Support Priority status (Low / Medium / High / Critical) for operational deployment.

---

## 3. Key Functional & Visualization Requirements

### A. Geospatial (Map) Visualizations
- **Road Congestion Layer:** Road-level polyline coloring based on canonical severity:
  - `Low`: Emerald Green (`#10B981`)
  - `Moderate`: Amber Yellow (`#F59E0B`)
  - `High`: Orange-Coral (`#F97316`)
  - `Severe`: Crimson Red (`#EF4444`)
  - Accessible redundant encoding (tooltips, badges, pattern options).
- **Accident Layer:** Distinct visual markers indicating incident frequency and severity.
- **Priority Highlights:** Visual halo/glow/badge for multi-factor critical hotspots.
- **Traffic Flow / Trajectories:** Directional flow lines or animated particles indicating arterial movement.

### B. Analytical Visualizations (Location Panel & Deep-Dives)
- **Time-Series Analysis:** Congestion index, vehicle volume, and speed dynamics across 24-hour cycles.
- **Day $\times$ Hour Heatmap:** Matrix visualizing recurring peak hours vs. days of the week.
- **Multivariate Scatter Plots:** Speed vs. Vehicle Density/Volume with regression trendlines.
- **Correlation Matrix:** Statistical associations between rainfall, visibility, lane capacity, volume, and speed reduction.
- **Accident Breakdown:** Incident frequency by time of day, weather condition, and severity.
- **Geographic Clustering:** Unsupervised grouping of Chennai corridors with similar congestion patterns.

### C. Time Interaction & Coordinated Filters
- **Temporal Controls:** Date selector, hour range filter, and smooth Play/Pause time slider with exact timestamp indicators.
- **Coordinated Filtering:** Applying a filter (e.g., Zone: Central, Weather: Rain, Congestion: Severe) updates the Map, Location Drawer, KPIs, Visualizations, and Insights simultaneously.

### D. Insights & Decision Support Engine
- Automatically extracts data-backed observations (e.g., *"Peak congestion at Kathipara Junction occurs between 08:30-09:30, with speed reduced by 64%"*).
- Formulates multi-criteria Priority Scores (**Low**, **Medium**, **High**, **Critical**) based on volume, speed deficit, incident counts, and predicted persistence.

---

## 4. Operational Boundaries & Non-Goals

1. **No Autonomous Signal Control:** The system is strictly an intelligence, analytical, and decision-support platform.
2. **Strict Data State Demarcation:** The UI must explicitly and visually label all data points as:
   - `OBSERVED`: Verified historical/sensor observations.
   - `DERIVED`: Numerically computed metrics (e.g., Congestion Index, Speed Deficit).
   - `PREDICTED`: Machine learning model inferences.
   - `SIMULATED`: Clearly watermarked synthetic development fixtures.
3. **No Correlation as Causation:** Analytical text must never claim unverified causal mechanisms.
4. **No Fabricated Data:** If a metric (e.g., weather or accident record) is absent from the dataset, display `"Data Unavailable"` rather than generating artificial placeholders.
5. **Decoupled ML Workstream:** ML model development is separate. The platform connects through a clean REST / JSON prediction contract (`docs/ml-integration.md`).

---

## 5. Review & Academic Milestones

| Milestone | Deliverables & Scope |
| :--- | :--- |
| **Review 1** | Problem definition, architecture, interactive Chennai map MVP, congestion coloring, accident layer, hover/click interaction, sample data loading, and foundation roadmap. |
| **Review 2** | Full interactive analysis: Location Intelligence drawer, temporal animation slider, day $\times$ hour heatmaps, multivariate scatter plots, traffic flow visualization, geographic clustering, and coordinated multi-filters. |
| **Review 3** | ML Prediction integration, future congestion layer (+30 min), prediction time-series, feature importance/confidence indicators, and automated Insight Engine. |
| **Final Review** | Complete end-to-end traffic authority command platform demonstration with seamless city-to-hotspot investigative workflow and production hardening. |
