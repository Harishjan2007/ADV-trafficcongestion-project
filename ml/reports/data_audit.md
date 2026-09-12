# ML Data Readiness Audit Report

**Dataset:** `Chennai Urban Arterial Calibrated Multi-Day Development Benchmark`  
**Data Classification:** `SIMULATED`  
**Simulated Benchmark:** `True`  
**Audit Timestamp:** `2026-09-12T20:07:10.918291`  
**Readiness Gate Status:** **READY**

---

## 1. Executive Gate Decision

| Metric | Target Requirement | Measured Value | Gate Assessment |
| :--- | :--- | :--- | :--- |
| **Unique Days Coverage** | $\ge 7$ days | **14 days** | PASS |
| **Total Observation Rows** | $\ge 1000$ records | **4704 rows** | PASS |
| **Monitored Road Corridors** | $\ge 5$ corridors | **14 corridors** | PASS |
| **Min Obs per Corridor** | $\ge 50$ obs/road | **336 obs** | PASS |
| **Duplicate Records** | 0 duplicates | **0 duplicates** | PASS |
| **Target Construction** | Valid forward step | **Feasible** | PASS |

---

## 2. Dataset Temporal & Spatial Properties

- **Date Range:** `2026-08-17` $\rightarrow$ `2026-08-30`
- **Sampling Interval:** `60 minutes`
- **Total Corridors:** `14`
- **Corridors Monitored:** `ROAD_100FT_1`, `ROAD_ANNA_SALAI_1`, `ROAD_ANNA_SALAI_2`, `ROAD_ARCOT_1`, `ROAD_ECR_1`, `ROAD_GST_1`, `ROAD_GST_2`, `ROAD_MARINA_1`, `ROAD_MOUNT_POON_1`, `ROAD_OMR_1`, `ROAD_OMR_2`, `ROAD_PH_1`, `ROAD_PH_2`, `ROAD_SP_ROAD_1`

---

## 3. Data Integrity & Missing Values

- **Missing Road IDs:** `0`
- **Missing Timestamps:** `0`
- **Missing Vehicle Volume:** `0`
- **Missing Speed Observations:** `0`
- **Missing Congestion Indices:** `0`
- **Duplicate (road_id + timestamp) Pairs:** `0`

---

## 4. Gate Failure Analysis

### Status: All Gate Criteria Satisfied

- ✅ Sufficient temporal depth and observations available for chronological train/validation/test splitting.
- ✅ Zero future leakage path verified for lag-feature generation.
- ℹ️ **Provenance Notice:** Labeled as `SIMULATED` for development/validation.
