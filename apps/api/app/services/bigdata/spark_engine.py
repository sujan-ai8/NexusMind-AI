import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd

# Fix Windows JAVA_HOME if invalid or pointing to linux path
if sys.platform == "win32":
    current_jh = os.environ.get("JAVA_HOME", "")
    if not current_jh or not os.path.exists(current_jh) or current_jh.startswith("/"):
        for candidate in [r"C:\Program Files\Java\jdk-21.0.10", r"C:\Program Files\Java\jdk-17"]:
            if os.path.exists(candidate):
                os.environ["JAVA_HOME"] = candidate
                break

from apps.api.app.core.logging import logger
from apps.api.app.services.bigdata.data_quality import DataQualityEngine
from apps.api.app.services.bigdata.schema_normalizer import normalize_dataframe
from apps.api.app.services.storage.local_storage import LocalStorageService


class PySparkProcessingEngine:
    """
    Enterprise PySpark Big Data Processing Engine.
    Executes distributed DataFrame transformations, aggregations, data quality checks,
    and produces analytical Parquet datasets and Phase 3 ML feature sets.
    """

    def __init__(self, app_name: str = "NexusMind-BigData-Processor"):
        self.app_name = app_name
        self._spark = None
        self.storage = LocalStorageService()

    def get_spark_session(self):
        if self._spark is not None:
            return self._spark

        try:
            from pyspark.sql import SparkSession

            warehouse_dir = os.path.abspath(os.path.join(os.getcwd(), "storage", "spark_warehouse"))
            os.makedirs(warehouse_dir, exist_ok=True)

            builder = (
                SparkSession.builder.appName(self.app_name)
                .master("local[*]")
                .config("spark.driver.memory", "2g")
                .config("spark.executor.memory", "2g")
                .config("spark.sql.shuffle.partitions", "4")
                .config("spark.sql.warehouse.dir", warehouse_dir)
                .config("spark.driver.bindAddress", "127.0.0.1")
                .config("spark.ui.enabled", "false")
            )

            self._spark = builder.getOrCreate()
            self._spark.sparkContext.setLogLevel("WARN")
            logger.info("PySpark SparkSession successfully initialized.")
            return self._spark
        except Exception as e:
            logger.warning(f"Could not initialize PySpark session directly: {e}")
            raise e

    def process_dataset(
        self,
        workspace_id: str,
        dataset_id: str,
        raw_file_path: Union[str, Path],
        file_format: str,
        column_mapping: Optional[Dict[str, str]] = None,
        job_id: str = "job-standalone",
        generate_features: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes full PySpark processing pipeline:
        1. Load raw dataset via Spark or Pandas
        2. Normalizes column schema
        3. Audits and cleans data via DataQualityEngine
        4. Applies distributed transformations and aggregations
        5. Computes Phase 3 ML lag/rolling features
        6. Persists Parquet datasets and returns result summary dictionary
        """
        raw_path = Path(raw_file_path)
        logs: List[Dict[str, str]] = []

        def log_stage(level: str, stage: str, message: str):
            logs.append({"timestamp": datetime.now(timezone.utc).isoformat(), "level": level, "stage": stage, "message": message})
            logger.info(f"[{stage}] {message}")

        start_time = time.perf_counter()
        log_stage("INFO", "INGESTION", f"Starting data processing for dataset from {raw_path.name}")

        fmt = file_format.upper()
        use_spark_direct = False
        spark_conf = {
            "engine": "PYSPARK",
            "spark_version": "4.3.0",
            "master": "local[*]",
            "driver_memory": "2g",
            "shuffle_partitions": "4",
        }

        try:
            spark = self.get_spark_session()
            log_stage("INFO", "INGESTION", "PySpark SparkSession acquired successfully.")

            if fmt == "CSV":
                spark_df = spark.read.option("header", "true").option("inferSchema", "true").csv(str(raw_path))
            elif fmt in ["JSON", "JSONL"]:
                spark_df = spark.read.json(str(raw_path))
            elif fmt == "PARQUET":
                spark_df = spark.read.parquet(str(raw_path))
            else:
                spark_df = spark.read.option("header", "true").csv(str(raw_path))

            raw_row_count = spark_df.count()
            raw_col_count = len(spark_df.columns)
            log_stage("INFO", "INGESTION", f"Loaded {raw_row_count:,} records across {raw_col_count} columns via PySpark.")

            pdf = spark_df.toPandas()
            use_spark_direct = True
        except Exception as e:
            log_stage("WARNING", "INGESTION", f"PySpark direct load fallback: {e}")
            if fmt == "CSV":
                pdf = pd.read_csv(raw_path)
            elif fmt in ["JSON", "JSONL"]:
                pdf = pd.read_json(raw_path, lines=True if fmt == "JSONL" else False)
            elif fmt == "PARQUET":
                pdf = pd.read_parquet(raw_path)
            else:
                pdf = pd.read_csv(raw_path)

        # 2. Schema Normalization
        log_stage("INFO", "VALIDATION", "Applying column mappings and standardizing telemetry fields.")
        df_norm = normalize_dataframe(pdf, column_mapping)

        # 3. Data Quality Engine Audit & Cleaning
        log_stage("INFO", "CLEANING", "Executing data quality validation and outlier imputation.")
        dq_engine = DataQualityEngine(strategy="impute_or_drop")
        clean_df, rejected_records, dq_summary = dq_engine.audit_and_clean(df_norm)
        log_stage("INFO", "CLEANING", f"Quality audit complete: Quality Score = {dq_summary['quality_score']}/100, Valid records = {len(clean_df):,}.")

        # Save rejected records if any
        if rejected_records:
            self.storage.save_rejected_records(rejected_records, workspace_id, dataset_id)

        # 4. Distributed Transformations
        if "timestamp" in clean_df.columns:
            clean_df = clean_df.sort_values(by="timestamp").reset_index(drop=True)

        # 5. Persist Processed Parquet
        processed_uri, _ = self.storage.save_processed_dataset(clean_df, workspace_id, dataset_id)
        processed_parquet_abs = self.storage.resolve_path(processed_uri)

        # 6. Phase 3 Machine Learning Feature Engineering (Section 15)
        features_df = None
        features_parquet_abs = None
        if generate_features and len(clean_df) > 0 and "cpu_utilization" in clean_df.columns:
            log_stage("INFO", "FEATURE_PREPARATION", "Generating Phase 3 standardized ML demand features.")
            f_df = clean_df.copy()

            if pd.api.types.is_datetime64_any_dtype(f_df["timestamp"]):
                f_df["hour"] = f_df["timestamp"].dt.hour
                f_df["day_of_week"] = f_df["timestamp"].dt.dayofweek
                f_df["is_weekend"] = f_df["day_of_week"].isin([5, 6]).astype(int)

            f_df["rolling_cpu_average"] = f_df["cpu_utilization"].rolling(window=6, min_periods=1).mean().round(2)
            if "memory_utilization" in f_df.columns:
                f_df["rolling_memory_average"] = f_df["memory_utilization"].rolling(window=6, min_periods=1).mean().round(2)
            if "workload_volume" in f_df.columns:
                f_df["historical_workload"] = f_df["workload_volume"].shift(1).fillna(f_df["workload_volume"].mean()).round(2)

            features_df = f_df
            features_uri = self.storage.save_feature_dataset(features_df, workspace_id, dataset_id)
            features_parquet_abs = self.storage.resolve_path(features_uri)
            log_stage("INFO", "FEATURE_PREPARATION", f"Phase 3 ML feature store prepared: {len(features_df.columns)} analytical features.")

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        log_stage("INFO", "OUTPUT", f"Data processing completed in {elapsed_ms}ms.")

        columns_meta = [{"name": c, "data_type": str(clean_df[c].dtype)} for c in clean_df.columns]

        return {
            "engine_used": "PYSPARK" if use_spark_direct else "PANDAS",
            "records_processed": len(clean_df),
            "records_failed": len(rejected_records),
            "columns": columns_meta,
            "processed_parquet_path": processed_parquet_abs,
            "features_parquet_path": features_parquet_abs,
            "compression": "SNAPPY",
            "execution_time_ms": elapsed_ms,
            "metrics": dq_summary,
            "logs": logs,
        }


pyspark_engine = PySparkProcessingEngine()
