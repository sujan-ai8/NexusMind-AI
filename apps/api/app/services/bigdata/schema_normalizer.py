import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from apps.api.app.schemas.bigdata import ColumnStat

STANDARD_FIELDS = [
    "timestamp",
    "instance_id",
    "instance_type",
    "service_name",
    "application_name",
    "cloud_provider",
    "cloud_region",
    "cpu_utilization",
    "memory_utilization",
    "network_in",
    "network_out",
    "storage_utilization",
    "storage_read",
    "storage_write",
    "request_count",
    "workload_volume",
    "instance_cost",
    "status",
]

MANDATORY_FIELDS = ["timestamp"]

FIELD_ALIASES: Dict[str, List[str]] = {
    "timestamp": ["timestamp", "time", "date", "datetime", "ts", "recorded_at", "event_time"],
    "instance_id": ["instance_id", "node_id", "host", "hostname", "server_id", "instance", "vm_id"],
    "instance_type": ["instance_type", "flavor", "machine_type", "type", "size"],
    "service_name": ["service_name", "service", "app", "application", "component", "microservice"],
    "application_name": ["application_name", "application", "app_name", "workload", "job_name"],
    "cloud_provider": ["cloud_provider", "provider", "cloud", "csp"],
    "cloud_region": ["cloud_region", "region", "zone", "availability_zone", "location"],
    "cpu_utilization": ["cpu_utilization", "cpu_pct", "cpu_percent", "cpu_usage", "cpu", "cpu_util", "avg_cpu"],
    "memory_utilization": ["memory_utilization", "mem_pct", "memory_percent", "mem_usage", "mem", "memory_util", "avg_mem"],
    "network_in": ["network_in", "net_in", "bytes_in", "network_rx", "rx_bytes", "net_rx"],
    "network_out": ["network_out", "net_out", "bytes_out", "network_tx", "tx_bytes", "net_tx"],
    "storage_utilization": ["storage_utilization", "disk_utilization", "disk_pct", "storage_pct", "disk_usage"],
    "storage_read": ["storage_read", "disk_read", "disk_read_bytes", "read_iops", "read_bytes"],
    "storage_write": ["storage_write", "disk_write", "disk_write_bytes", "write_iops", "write_bytes"],
    "request_count": ["request_count", "requests", "req_count", "calls", "transaction_count", "total_requests"],
    "workload_volume": ["workload_volume", "volume", "throughput", "workload", "load"],
    "instance_cost": ["instance_cost", "cost", "cost_usd", "hourly_cost", "spend", "rate"],
    "status": ["status", "state", "health", "instance_status"],
}


def sanitize_column_name(col: str) -> str:
    cleaned = re.sub(r"[^\w\s]", "", str(col).strip().lower())
    return re.sub(r"[\s\-]+", "_", cleaned)


class SchemaNormalizer:
    @staticmethod
    def detect_column_mapping(column_names: List[str]) -> Dict[str, str]:
        """Automatically infers column mapping from raw column names."""
        normalized_cols = {sanitize_column_name(col): col for col in column_names}
        detected_mapping: Dict[str, str] = {}

        for std_field, aliases in FIELD_ALIASES.items():
            for alias in aliases:
                cleaned_alias = sanitize_column_name(alias)
                if cleaned_alias in normalized_cols:
                    detected_mapping[std_field] = normalized_cols[cleaned_alias]
                    break

        return detected_mapping

    @staticmethod
    def validate_mapping(mapping: Dict[str, str]) -> Dict[str, Any]:
        """Validates that mandatory fields are mapped."""
        missing = [f for f in MANDATORY_FIELDS if f not in mapping or not mapping[f]]
        return {
            "is_valid": len(missing) == 0,
            "missing_required": missing,
        }

    @staticmethod
    def detect_schema(df: pd.DataFrame) -> Tuple[List[ColumnStat], Dict[str, Optional[str]]]:
        """Analyzes a dataframe to extract column metadata and infer column mappings."""
        columns: List[ColumnStat] = []
        detected_mapping = SchemaNormalizer.detect_column_mapping(list(df.columns))

        # Analyze each column
        for col in df.columns:
            series = df[col]
            dtype = str(series.dtype)
            missing_count = int(series.isna().sum())
            unique_count = int(series.nunique()) if len(series) < 50000 else None

            sample_vals = series.dropna().head(5).tolist()
            sample_clean = []
            for v in sample_vals:
                if isinstance(v, (np.integer, int)):
                    sample_clean.append(int(v))
                elif isinstance(v, (np.floating, float)):
                    sample_clean.append(float(v))
                else:
                    sample_clean.append(str(v))

            columns.append(
                ColumnStat(
                    name=sanitize_column_name(col),
                    column_name=sanitize_column_name(col),
                    raw_name=str(col),
                    data_type=dtype,
                    missing_count=missing_count,
                    unique_count=unique_count,
                    sample_values=sample_clean,
                )
            )

        return columns, detected_mapping

    @staticmethod
    def normalize_dataframe(
        df: pd.DataFrame,
        mapping: Optional[Dict[str, str]] = None,
    ) -> pd.DataFrame:
        """Applies column mapping and standardizes timestamps, numbers, and types."""
        df_out = df.copy()

        # Apply mapping
        if mapping:
            rename_dict = {}
            for std_name, raw_name in mapping.items():
                if raw_name in df_out.columns:
                    rename_dict[raw_name] = std_name
            df_out = df_out.rename(columns=rename_dict)

        # Standardize timestamp
        if "timestamp" in df_out.columns:
            df_out["timestamp"] = pd.to_datetime(df_out["timestamp"], errors="coerce", utc=True)
        else:
            # Generate synthetic timestamp index if completely missing
            df_out["timestamp"] = pd.date_range(end=datetime.now(timezone.utc), periods=len(df_out), freq="5min", tz="UTC")

        # Numeric standardization
        numeric_fields = [
            "cpu_utilization",
            "memory_utilization",
            "network_in",
            "network_out",
            "storage_utilization",
            "storage_read",
            "storage_write",
            "request_count",
            "workload_volume",
            "instance_cost",
        ]

        for num_col in numeric_fields:
            if num_col in df_out.columns:
                df_out[num_col] = pd.to_numeric(df_out[num_col], errors="coerce")

        # Provide defaults for missing critical identifiers
        if "instance_id" not in df_out.columns:
            df_out["instance_id"] = "inst-node-default"
        else:
            df_out["instance_id"] = df_out["instance_id"].fillna("inst-node-default").astype(str)

        if "instance_type" not in df_out.columns:
            df_out["instance_type"] = "c6i.xlarge"
        else:
            df_out["instance_type"] = df_out["instance_type"].fillna("c6i.xlarge").astype(str)

        if "service_name" not in df_out.columns:
            df_out["service_name"] = "core-service"
        else:
            df_out["service_name"] = df_out["service_name"].fillna("core-service").astype(str)

        if "cloud_provider" not in df_out.columns:
            df_out["cloud_provider"] = "AWS"

        if "cloud_region" not in df_out.columns:
            df_out["cloud_region"] = "us-east-1"

        return df_out


# Backward-compatible function exports
detect_schema = SchemaNormalizer.detect_schema
normalize_dataframe = SchemaNormalizer.normalize_dataframe
