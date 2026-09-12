# Machine Learning Feature Data Dictionary
## Chennai Traffic Intelligence Platform

---

## 1. Raw Observations & Static Road Network Properties

| Column Name | Data Type | Units / Format | Physical Range | Source | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `record_id` | String | `REC_{road}_{date}_{hr}` | N/A | System | Unique primary key for the observation row. |
| `timestamp` | String (ISO) | `YYYY-MM-DDTHH:MM:SS+05:30` | 2026-08 to Present | Ingestion | Observation timestamp in Indian Standard Time (IST). |
| `road_id` | String | Categorical | 14 Corridors | GIS Network | Standardized road corridor identifier (e.g. `ROAD_ANNA_SALAI_1`). |
| `road_name` | String | Text | N/A | GIS Network | Human-readable name of the monitored segment. |
| `zone` | String | Categorical | Central, South, etc. | GIS Network | Administrative municipal zone in Chennai. |
| `road_type` | String | Categorical | Arterial, Expressway | GIS Network | Functional classification of the roadway. |
| `road_capacity` | Integer | veh/hr | 2,500 – 5,000 | OpenStreetMap/GIS | Maximum design throughput for the directional segment. |
| `speed_limit` | Float | km/h | 40.0 – 80.0 | Traffic Police / GIS | Legal posted speed limit. |
| `lane_count` | Integer | Count | 2 – 5 | GIS Network | Number of active traffic lanes in directional segment. |
| `vehicle_count` | Integer | veh/hr | 0 – 6,000 | Sensor / Ingestion | Total vehicle count observed during the sampling window. |
| `average_speed` | Float | km/h | 5.0 – 80.0 | Sensor / Ingestion | Space-mean speed of monitored vehicular flow. |
| `rainfall` | Float | mm/hr | 0.0 – 50.0 | Weather Feed | Hourly precipitation accumulation. |
| `temperature` | Float | °C | 20.0 – 42.0 | Weather Feed | Ambient temperature. |
| `accident_count` | Integer | Count | 0 – 3 | Incident Feed | Number of active incidents recorded on the segment. |

---

## 2. Derived Canonical Traffic Metrics

| Metric Name | Formula / Definition | Range | Classification | Description |
| :--- | :--- | :--- | :--- | :--- |
| `traffic_utilization` | $\text{vehicle\_count} / \text{road\_capacity}$ | $[0.0, 1.8]$ | `DERIVED` | Volume-to-capacity (V/C) ratio indicating saturation. |
| `speed_reduction` | $\max(0.0, (\text{speed\_limit} - \text{average\_speed}) / \text{speed\_limit})$ | $[0.0, 1.0]$ | `DERIVED` | Proportional speed deficit relative to legal free-flow limit. |
| `congestion_index` | $(0.45 \cdot \min(1.0, \frac{\text{util}}{1.2}) \cdot 100) + (0.55 \cdot \text{speed\_reduction} \cdot 100)$ | $[0.0, 100.0]$ | `DERIVED` | Canonical composite congestion severity index. |
| `congestion_level` | Categorical mapping of `congestion_index` | 4 Levels | `DERIVED` | Low ($<30$), Moderate ($30-55$), High ($55-75$), Severe ($\ge 75$). |

---

## 3. Supervised Model Feature Matrix (26 Features)

All features below are strictly backward-looking. Shift $k \ge 1$ guarantees zero future data leakage.

| Feature Identifier | Transformation / Lag | Type | Leakage Guard | Expected Physical Impact on Congestion |
| :--- | :--- | :--- | :--- | :--- |
| `hour` | `dt.hour` | Integer [0, 23] | Time at $T$ | Captures diurnal baseline commute trends. |
| `hour_sin` | $\sin(2\pi \cdot \text{hour} / 24)$ | Float [-1, 1] | Time at $T$ | Continuous circular time encoding. |
| `hour_cos` | $\cos(2\pi \cdot \text{hour} / 24)$ | Float [-1, 1] | Time at $T$ | Continuous circular time encoding. |
| `day_of_week_sin` | $\sin(2\pi \cdot \text{dow} / 7)$ | Float [-1, 1] | Time at $T$ | Weekly cycle encoding. |
| `day_of_week_cos` | $\cos(2\pi \cdot \text{dow} / 7)$ | Float [-1, 1] | Time at $T$ | Weekly cycle encoding. |
| `is_weekend` | `dow.isin([5, 6])` | Binary [0, 1] | Time at $T$ | Decreases congestion (commute reduction). |
| `is_peak_hour` | Weekday 8–11 or 17–20 | Binary [0, 1] | Time at $T$ | Strongly increases congestion. |
| `road_capacity` | Corridor design capacity | Integer | Static GIS | Higher capacity accommodates larger volume. |
| `speed_limit` | Corridor speed limit | Float | Static GIS | Reference speed for deficit calculation. |
| `lane_count` | Number of lanes | Integer | Static GIS | Physical cross-sectional throughput limit. |
| `vehicle_count_lag_1` | `groupby(road_id)['vehicle_count'].shift(1)` | Integer | $T-1$ slice | Positive: high prior volume indicates queue build-up. |
| `vehicle_count_lag_2` | `groupby(road_id)['vehicle_count'].shift(2)` | Integer | $T-2$ slice | Positive: captures multi-hour volume wave propagation. |
| `vehicle_count_lag_3` | `groupby(road_id)['vehicle_count'].shift(3)` | Integer | $T-3$ slice | Positive: baseline trend 3 hours prior. |
| `speed_lag_1` | `groupby(road_id)['average_speed'].shift(1)` | Float | $T-1$ slice | Negative: higher speed at $T-1$ decreases future congestion. |
| `speed_lag_2` | `groupby(road_id)['average_speed'].shift(2)` | Float | $T-2$ slice | Negative: speed recovery trend. |
| `speed_lag_3` | `groupby(road_id)['average_speed'].shift(3)` | Float | $T-3$ slice | Negative: historical free-flow baseline. |
| `congestion_lag_1` | `groupby(road_id)['congestion_index'].shift(1)` | Float [0, 100] | $T-1$ slice | Strongest auto-regressive driver (inertia). |
| `congestion_lag_2` | `groupby(road_id)['congestion_index'].shift(2)` | Float [0, 100] | $T-2$ slice | Inertia decay over 2 time steps. |
| `rolling_speed_mean_3h` | `shift(1).rolling(3).mean()` | Float | $T-1$ to $T-3$ | Smoothed velocity trend excluding observation at $T$. |
| `rolling_vol_mean_3h` | `shift(1).rolling(3).mean()` | Float | $T-1$ to $T-3$ | Inflow momentum. |
| `rolling_ci_mean_3h` | `shift(1).rolling(3).mean()` | Float | $T-1$ to $T-3$ | Moving congestion severity. |
| `rolling_ci_std_3h` | `shift(1).rolling(3).std()` | Float | $T-1$ to $T-3$ | Flow volatility / breakdown instability indicator. |
| `neighbor_congestion_lag_1` | Mean adjacent corridor CI at $T-1$ | Float [0, 100] | $T-1$ slice | Positive: network spillover and upstream chokepoint queuing. |
| `rainfall` | Precipitation at $T$ | Float [mm/hr] | Weather at $T$ | Increases congestion (reduces operating speeds). |
| `temperature` | Temperature at $T$ | Float [°C] | Weather at $T$ | Environmental context. |
| `is_raining` | `rainfall > 0.0` | Binary [0, 1] | Weather at $T$ | Binary road surface friction penalty flag. |
| `accident_lag_1` | Incidents on corridor at $T-1$ | Integer | $T-1$ slice | Strongly increases congestion due to lane blockages. |

---

## 4. Supervised Target Variables

| Target Name | Shift Lead | Units / Format | Prediction Horizon | Description |
| :--- | :--- | :--- | :--- | :--- |
| `target_congestion_index` | `shift(-1)` or `shift(-2)` | Continuous [0, 100] | +15m, +30m, +45m, +60m | Ground-truth congestion index at forward timestamp. |
| `target_congestion_level` | Documented mapping | Categorical (4) | +15m, +30m, +45m, +60m | Discrete congestion severity label. |
| `target_speed` | `shift(-h)` | Float [km/h] | Multi-horizon | Predicted average vehicular velocity. |
| `target_vehicle_count` | `shift(-h)` | Integer [veh/hr] | Multi-horizon | Predicted corridor traffic volume. |
