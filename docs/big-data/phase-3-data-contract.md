# Phase 3 Data Contract & Feature Store Specification

## 1. Objective

Phase 2 acts as the authoritative data provider for **Phase 3: Advanced Machine Learning and Predictive Analytics**. The distributed PySpark pipeline extracts and pre-computes time-series lag and rolling demand features, serializing them into a standardized feature store.

---

## 2. Storage Location

Cleaned analytical feature stores are persisted to:
```
/storage/features/{workspace_id}/{dataset_id}/ml_features.parquet
```

---

## 3. Schema & Feature Definitions

In addition to the 17 standardized telemetry columns, the Phase 3 feature dataset includes:

| Feature Name | Data Type | Computation Logic | Purpose for Phase 3 ML |
|---|---|---|---|
| `hour` | Integer (0-23) | `timestamp.dt.hour` | Captures diurnal periodic patterns |
| `day_of_week` | Integer (0-6) | `timestamp.dt.dayofweek` | Day-of-week seasonality (Monday=0) |
| `is_weekend` | Integer (0 or 1) | `day_of_week in [5, 6]` | Weekend vs. weekday workload shift |
| `rolling_cpu_average` | Float | `rolling(window=6, min_periods=1).mean()` | 30-minute smoothed CPU baseline |
| `rolling_memory_average` | Float | `rolling(window=6, min_periods=1).mean()` | 30-minute smoothed memory trend |
| `historical_workload` | Float | `workload_volume.shift(1)` | Lag-1 auto-regressive demand predictor |

---

## 4. Guarantees & Constraints

- **Sorted by Time**: Records are guaranteed to be sorted in ascending chronological order (`timestamp ASC`).
- **Null-Free Features**: Rolling averages and lag features handle boundary initialization using `min_periods=1` and column mean imputation.
- **Format**: Standard Apache Parquet with Snappy compression for high-throughput zero-copy reads by PyTorch, Scikit-learn, and XGBoost in Phase 3.
