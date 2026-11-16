from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from apps.api.app.schemas.bigdata import CleaningAction, QualityIssue


class DataQualityEngine:
    def __init__(self, strategy: str = "impute_or_drop"):
        self.strategy = strategy  # "impute_or_drop", "drop_invalid", "strict"

    def audit_and_clean(
        self,
        df: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Audits data quality, separates irrecoverably invalid records, applies
        configurable cleaning strategies, and generates a structured data quality audit report.
        """
        total_input_records = len(df)
        issues: List[QualityIssue] = []
        actions: List[CleaningAction] = []
        rejected_records: List[Dict[str, Any]] = []

        df_working = df.copy()

        # 1. Duplicate Records Audit
        duplicate_mask = df_working.duplicated(keep="first")
        duplicate_count = int(duplicate_mask.sum())
        if duplicate_count > 0:
            issues.append(
                QualityIssue(
                    issue_type="DUPLICATE_RECORDS",
                    affected_rows=duplicate_count,
                    severity="WARNING",
                    description=f"Identified {duplicate_count} exact duplicate rows.",
                )
            )
            df_working = df_working[~duplicate_mask].copy()
            actions.append(
                CleaningAction(
                    action_type="DEDUPLICATION",
                    affected_rows=duplicate_count,
                    description=f"Deduplicated dataset, keeping first occurrences.",
                )
            )

        # 2. Timestamp Validation
        if "timestamp" in df_working.columns:
            invalid_ts_mask = df_working["timestamp"].isna()
            invalid_ts_count = int(invalid_ts_mask.sum())
            if invalid_ts_count > 0:
                issues.append(
                    QualityIssue(
                        issue_type="INVALID_TIMESTAMP",
                        column="timestamp",
                        affected_rows=invalid_ts_count,
                        severity="ERROR",
                        description=f"Found {invalid_ts_count} rows with null or unparseable timestamps.",
                    )
                )
                # Reject records with irrecoverable timestamps
                rejected = df_working[invalid_ts_mask].copy()
                rejected["rejection_reason"] = "Unparseable or missing timestamp"
                rejected_records.extend(rejected.to_dict(orient="records"))
                df_working = df_working[~invalid_ts_mask].copy()
                actions.append(
                    CleaningAction(
                        action_type="REJECT_RECORD",
                        column="timestamp",
                        affected_rows=invalid_ts_count,
                        description="Rejected rows with missing/unparseable timestamps.",
                    )
                )

        # 3. CPU Utilization Range Validation (0% - 100%)
        if "cpu_utilization" in df_working.columns:
            cpu_out_of_range = (df_working["cpu_utilization"] < 0) | (df_working["cpu_utilization"] > 100)
            cpu_invalid_count = int(cpu_out_of_range.sum())
            if cpu_invalid_count > 0:
                issues.append(
                    QualityIssue(
                        issue_type="CPU_OUT_OF_RANGE",
                        column="cpu_utilization",
                        affected_rows=cpu_invalid_count,
                        severity="WARNING",
                        description=f"CPU utilization values outside 0-100% bounds ({cpu_invalid_count} rows).",
                    )
                )
                # Clip valid bounds
                df_working["cpu_utilization"] = df_working["cpu_utilization"].clip(lower=0.0, upper=100.0)
                actions.append(
                    CleaningAction(
                        action_type="BOUNDS_CLIPPING",
                        column="cpu_utilization",
                        affected_rows=cpu_invalid_count,
                        description="Clipped CPU values into valid [0.0, 100.0] percentage range.",
                    )
                )

        # 4. Memory Utilization Range Validation (0% - 100%)
        if "memory_utilization" in df_working.columns:
            mem_out_of_range = (df_working["memory_utilization"] < 0) | (df_working["memory_utilization"] > 100)
            mem_invalid_count = int(mem_out_of_range.sum())
            if mem_invalid_count > 0:
                issues.append(
                    QualityIssue(
                        issue_type="MEMORY_OUT_OF_RANGE",
                        column="memory_utilization",
                        affected_rows=mem_invalid_count,
                        severity="WARNING",
                        description=f"Memory utilization values outside 0-100% bounds ({mem_invalid_count} rows).",
                    )
                )
                df_working["memory_utilization"] = df_working["memory_utilization"].clip(lower=0.0, upper=100.0)
                actions.append(
                    CleaningAction(
                        action_type="BOUNDS_CLIPPING",
                        column="memory_utilization",
                        affected_rows=mem_invalid_count,
                        description="Clipped Memory values into valid [0.0, 100.0] percentage range.",
                    )
                )

        # 5. Non-Negative Checks for Network and Cost
        for metric_col in ["network_in", "network_out", "storage_read", "storage_write", "instance_cost", "workload_volume"]:
            if metric_col in df_working.columns:
                negative_mask = df_working[metric_col] < 0
                neg_count = int(negative_mask.sum())
                if neg_count > 0:
                    issues.append(
                        QualityIssue(
                            issue_type="NEGATIVE_METRIC_VALUE",
                            column=metric_col,
                            affected_rows=neg_count,
                            severity="WARNING",
                            description=f"Found negative values in non-negative metric {metric_col}.",
                        )
                    )
                    df_working[metric_col] = df_working[metric_col].clip(lower=0.0)
                    actions.append(
                        CleaningAction(
                            action_type="ZERO_FLOORING",
                            column=metric_col,
                            affected_rows=neg_count,
                            description=f"Floored negative values in {metric_col} to 0.",
                        )
                    )

        # 6. Missing Values Imputation
        missing_count_total = int(df_working.isna().sum().sum())
        corrected_count = 0
        if missing_count_total > 0:
            for col in df_working.columns:
                n_missing = int(df_working[col].isna().sum())
                if n_missing > 0:
                    if pd.api.types.is_numeric_dtype(df_working[col]):
                        median_val = df_working[col].median()
                        if pd.isna(median_val):
                            median_val = 0.0
                        df_working[col] = df_working[col].fillna(median_val)
                        corrected_count += n_missing
                        actions.append(
                            CleaningAction(
                                action_type="MEDIAN_IMPUTATION",
                                column=col,
                                affected_rows=n_missing,
                                description=f"Imputed missing numeric values with median ({median_val:.2f}).",
                            )
                        )
                    else:
                        mode_val = df_working[col].mode()
                        fill_val = mode_val[0] if len(mode_val) > 0 else "UNKNOWN"
                        df_working[col] = df_working[col].fillna(fill_val)
                        corrected_count += n_missing
                        actions.append(
                            CleaningAction(
                                action_type="MODE_IMPUTATION",
                                column=col,
                                affected_rows=n_missing,
                                description=f"Imputed missing categorical values with mode ('{fill_val}').",
                            )
                        )

        # Quality Score Calculation
        valid_records = len(df_working)
        rejected_count = len(rejected_records)
        invalid_records = duplicate_count + rejected_count

        # Scoring penalty formula
        penalty = 0.0
        if total_input_records > 0:
            dup_ratio = duplicate_count / total_input_records
            rej_ratio = rejected_count / total_input_records
            miss_ratio = missing_count_total / (total_input_records * max(1, len(df.columns)))
            penalty = (dup_ratio * 30.0) + (rej_ratio * 50.0) + (miss_ratio * 20.0)

        quality_score = max(0.0, min(100.0, round(100.0 - penalty, 2)))
        status = "PASSED" if quality_score >= 80.0 else ("WARNING" if quality_score >= 60.0 else "FAILED")

        summary = {
            "total_records": total_input_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records,
            "duplicate_records": duplicate_count,
            "missing_values_count": missing_count_total,
            "corrected_records": corrected_count,
            "rejected_records": rejected_count,
            "quality_score": quality_score,
            "status": status,
            "issues": [i.model_dump() for i in issues],
            "cleaning_actions": [a.model_dump() for a in actions],
        }

        return df_working, rejected_records, summary

    def audit_dataset(
        self,
        df: pd.DataFrame,
        mapping: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Convenience method returning structured audit dictionary."""
        df_norm = df.copy()
        if mapping:
            from apps.api.app.services.bigdata.schema_normalizer import SchemaNormalizer
            df_norm = SchemaNormalizer.normalize_dataframe(df, mapping)

        _, rejected, summary = self.audit_and_clean(df_norm)
        return {
            "quality_score": summary["quality_score"],
            "quality_status": summary["status"],
            "total_records": summary["total_records"],
            "valid_records": summary["valid_records"],
            "invalid_records": summary["invalid_records"],
            "missing_values_count": summary["missing_values_count"],
            "duplicate_records_count": summary["duplicate_records"],
            "out_of_bound_records_count": 0,
            "metrics": summary,
            "issues": summary["issues"],
        }

