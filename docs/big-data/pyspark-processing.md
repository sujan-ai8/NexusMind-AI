# PySpark Distributed Processing Engine

## 1. Engine Configuration & Runtime

NexusMind AI integrates Apache Spark via PySpark 4.3.0 running on Java 21 LTS.

- **Master Mode**: `local[*]` (dynamically scales across all available physical CPU cores)
- **Driver Memory**: `2g`
- **Executor Memory**: `2g`
- **Shuffle Partitions**: `4` (optimized for local multi-core development and testing)
- **Warehouse Directory**: `/storage/spark_warehouse`
- **Driver Bind Address**: `127.0.0.1` (UI disabled to eliminate port contention)

---

## 2. Distributed Transformation Lifecycle

1. **SparkSession Initialization**:
   - `PySparkProcessingEngine.get_spark_session()` initializes or reuses the local Spark context.
2. **DataFrame Ingestion**:
   - Telemetry is ingested via `spark.read.option("header", "true").option("inferSchema", "true").csv()`.
3. **Partitioned Transformations**:
   - Distributed grouping, capacity aggregations, and rolling windows are applied across instance, service, and temporal partitions.
4. **Optimized Parquet Generation**:
   - Output datasets are serialized using **Apache Parquet with Snappy compression** into:
     `/storage/processed/{workspace_id}/{dataset_id}/analytics_data.parquet`
5. **Phase 3 Feature Store Generation**:
   - Time-lagged demand features and calendar encodings are calculated and persisted to:
     `/storage/features/{workspace_id}/{dataset_id}/ml_features.parquet`
6. **Execution Engine Transparency**:
   - The engine explicitly reports whether distributed PySpark or vectorized Pandas was used in the `engine_used` field of the `processed_datasets` table and job summary.
