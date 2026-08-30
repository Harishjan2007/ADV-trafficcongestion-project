# Data Source Strategy: Chennai Traffic Intelligence Platform

**Date:** 2026-08-30  
**Status:** Approved Strategy (Phase 0)

---

## 1. Data Source Principles

1. **Prioritize Real Chennai Datasets:** The platform is engineered specifically for Chennai's urban geography, traffic patterns, major arterial corridors, and monsoon weather dynamics.
2. **Strict Isolation of Simulated Data:** Whenever real datasets are unavailable, simulated fixtures must be stored exclusively in `data/synthetic/` and rendered with clear visual badges (`SIMULATED DATA`) to avoid misleading users or reviewers.
3. **Reproducible Preprocessing:** All raw data transformations into the Canonical Parquet/GeoJSON format must be executed via auditable scripts in `backend/services/`.

---

## 2. Inventory of Chennai Data Assets & Target Sources

| Source Identifier | Source Category | Target Coverage / Resolution | Status | Storage Location | Notes & Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`GEO_CHENNAI_ROADS`** | Geospatial Network | Major Chennai Arterial Network (~25 major corridors, 80+ segments, 30+ junctions) | Target / Fixture | `data/geo/chennai_road_network.geojson` | Derived from OpenStreetMap / Chennai GIS; provides exact coordinates and topology. |
| **`TRAFFIC_CHENNAI_CORRIDORS`** | Traffic Volume & Speed | 15-minute / hourly vehicle counts, average speeds, density | Target / Fixture | `data/processed/chennai_traffic.parquet` | Covers key arterial corridors: Anna Salai, GST Road, OMR (IT Corridor), Poonamallee High Rd, 100 Feet Road, ECR, Mount-Poonamallee Rd. |
| **`ACCIDENTS_CHENNAI_LOGS`** | Incident / Accidents | Historical accident incidents with severity, date/time, and junction linkage | Target / Fixture | `data/processed/chennai_accidents.parquet` | Mapped to Chennai accident blackspots (e.g., Kathipara, Guindy, Koyambedu, Airport Jn, Madhya Kailash). |
| **`WEATHER_CHENNAI_IMD`** | Weather / Precipitation | Hourly temperature, rainfall (mm), humidity, and visibility | Target / Fixture | `data/processed/chennai_weather.parquet` | Simulates/captures Chennai monsoon and coastal atmospheric conditions. |
| **`SYNTHETIC_DEV_FIXTURE`** | Complete Multi-day Fixture | 7-day multi-corridor canonical traffic dataset | Available in Dev | `data/synthetic/chennai_dev_traffic.parquet` | Complete calibrated dataset adhering 100% to the Canonical Contract for local development & automated tests. |

---

## 3. Chennai Geographic Corridors Covered

The platform targets key high-volume transportation corridors in Chennai:
1. **Anna Salai (Mount Road - NH 45):** Central Chennai to Guindy (including LIC, Gemini Flyover, Nandanam, Saidapet, Guindy).
2. **Old Mahabalipuram Road (OMR - Rajiv Gandhi Salai):** Madhya Kailash to Sholinganallur / Siruseri IT corridor.
3. **Grand Southern Trunk Road (GST Road):** Guindy / Kathipara $\rightarrow$ Chennai International Airport $\rightarrow$ Tambaram.
4. **Poonamallee High Road (NH 48):** Chennai Central $\rightarrow$ Kilpauk $\rightarrow$ Aminjikarai $\rightarrow$ Koyambedu $\rightarrow$ Maduravoyal.
5. **Inner Ring Road (100 Feet Road / Jawaharlal Nehru Road):** Koyambedu $\rightarrow$ Vadapalani $\rightarrow$ Ashok Nagar $\rightarrow$ Kathipara.
6. **East Coast Road (ECR):** Thiruvanmiyur $\rightarrow$ Kottivakkam $\rightarrow$ Akkarai.
7. **Arcot Road:** Nungambakkam $\rightarrow$ Kodambakkam $\rightarrow$ Vadapalani $\rightarrow$ Porur.
8. **Mount-Poonamallee Road:** Kathipara $\rightarrow$ Ramapuram $\rightarrow$ Porur $\rightarrow$ Iyyappanthangal.
9. **Nelson Manickam Road & Harrington Road:** Aminjikarai $\rightarrow$ Nungambakkam.
10. **EVR Periyar Salai & Rajaji Salai:** George Town / Chennai Port corridor.

---

## 4. Dataset Metadata Contract

Every processed dataset file must be accompanied by a `metadata.json` descriptor containing:
```json
{
  "source_name": "Chennai Mobility Corpus",
  "dataset_version": "1.0.0",
  "coverage_period": {
    "start": "2026-08-01T00:00:00+05:30",
    "end": "2026-08-31T23:59:59+05:30"
  },
  "geographic_bounding_box": {
    "min_lat": 12.8500,
    "max_lat": 13.2500,
    "min_lng": 80.1000,
    "max_lng": 80.3500
  },
  "temporal_resolution": "15min",
  "spatial_resolution": "Road Segment / Junction Level",
  "is_simulated": false,
  "license": "Research & Academic Evaluation",
  "limitations": "Sensor coverage concentrated on primary urban arterials."
}
```
