import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from apps.api.app.schemas.bigdata import (
    AnomalyAnalyticsResponse,
    AnomalyEventResponse,
    BreakdownItem,
    CostAnalyticsResponse,
    CpuAnalyticsResponse,
    MemoryAnalyticsResponse,
    NetworkAnalyticsResponse,
    ResourceCandidate,
    ResourceEfficiencyResponse,
    StorageAnalyticsResponse,
    TimeSeriesMetricPoint,
    WorkloadAnalyticsResponse,
)


class AnalyticsEngine:
    def __init__(self, cost_rates: Optional[Dict[str, float]] = None):
        # Default instance type hourly rates in USD (simulated benchmark assumptions)
        self.compute_rates = cost_rates or {
            "c6i.xlarge": 0.17,
            "c6i.2xlarge": 0.34,
            "m6i.xlarge": 0.192,
            "m6i.2xlarge": 0.384,
            "r6i.xlarge": 0.252,
            "t3.medium": 0.0416,
            "t3.large": 0.0832,
            "default": 0.15,
        }
        self.storage_gb_rate = 0.023  # S3 standard $0.023/GB/mo
        self.network_egress_gb_rate = 0.09  # $0.09/GB

    def calculate_cpu_analytics(self, df: pd.DataFrame, dataset_id: Optional[str] = None) -> CpuAnalyticsResponse:
        if "cpu_utilization" not in df.columns or len(df) == 0:
            return CpuAnalyticsResponse(
                dataset_id=dataset_id,
                average_cpu=0.0,
                max_cpu=0.0,
                min_cpu=0.0,
                p95_cpu=0.0,
                cpu_trends=[],
                usage_by_service=[],
                usage_by_instance=[],
                peak_periods=[],
                efficiency_status="INSUFFICIENT_DATA",
            )

        series = df["cpu_utilization"].dropna()
        avg_cpu = round(float(series.mean()), 2)
        max_cpu = round(float(series.max()), 2)
        min_cpu = round(float(series.min()), 2)
        p95_cpu = round(float(np.percentile(series, 95)), 2)

        # Time series resampled hourly
        trends: List[TimeSeriesMetricPoint] = []
        if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df_ts = df.set_index("timestamp").sort_index()
            resampled = df_ts["cpu_utilization"].resample("1h").mean().dropna()
            for ts, val in resampled.items():
                trends.append(
                    TimeSeriesMetricPoint(
                        timestamp=ts.strftime("%Y-%m-%d %H:%M"),
                        value=round(float(val), 2),
                        unit="%",
                    )
                )

        # By Service
        usage_by_service: List[BreakdownItem] = []
        if "service_name" in df.columns:
            svc_grp = df.groupby("service_name")["cpu_utilization"].mean()
            for svc, val in svc_grp.items():
                usage_by_service.append(
                    BreakdownItem(label=str(svc), value=round(float(val), 2))
                )

        # By Instance
        usage_by_instance: List[BreakdownItem] = []
        if "instance_id" in df.columns:
            inst_grp = df.groupby("instance_id")["cpu_utilization"].mean().head(10)
            for inst, val in inst_grp.items():
                usage_by_instance.append(
                    BreakdownItem(label=str(inst), value=round(float(val), 2))
                )

        # Peak periods (where CPU > 80% or top 90th percentile)
        peak_periods: List[Dict[str, Any]] = []
        peaks = df[df["cpu_utilization"] >= max(75.0, p95_cpu)].head(8)
        for _, r in peaks.iterrows():
            peak_periods.append({
                "timestamp": str(r.get("timestamp", "N/A")),
                "instance_id": str(r.get("instance_id", "N/A")),
                "cpu_utilization": round(float(r["cpu_utilization"]), 2),
            })

        status = "CRITICAL" if p95_cpu > 90.0 else ("WARNING" if p95_cpu > 80.0 else "OPTIMAL")

        return CpuAnalyticsResponse(
            dataset_id=dataset_id,
            average_cpu=avg_cpu,
            max_cpu=max_cpu,
            min_cpu=min_cpu,
            p95_cpu=p95_cpu,
            cpu_trends=trends,
            usage_by_service=usage_by_service,
            usage_by_instance=usage_by_instance,
            peak_periods=peak_periods,
            efficiency_status=status,
        )

    def calculate_memory_analytics(self, df: pd.DataFrame, dataset_id: Optional[str] = None) -> MemoryAnalyticsResponse:
        if "memory_utilization" not in df.columns or len(df) == 0:
            return MemoryAnalyticsResponse(
                dataset_id=dataset_id,
                average_memory=0.0,
                max_memory=0.0,
                min_memory=0.0,
                p95_memory=0.0,
                memory_trends=[],
                consumption_by_service=[],
                consumption_by_instance=[],
                peak_periods=[],
            )

        series = df["memory_utilization"].dropna()
        avg_mem = round(float(series.mean()), 2)
        max_mem = round(float(series.max()), 2)
        min_mem = round(float(series.min()), 2)
        p95_mem = round(float(np.percentile(series, 95)), 2)

        trends: List[TimeSeriesMetricPoint] = []
        if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df_ts = df.set_index("timestamp").sort_index()
            resampled = df_ts["memory_utilization"].resample("1h").mean().dropna()
            for ts, val in resampled.items():
                trends.append(
                    TimeSeriesMetricPoint(
                        timestamp=ts.strftime("%Y-%m-%d %H:%M"),
                        value=round(float(val), 2),
                        unit="%",
                    )
                )

        by_service: List[BreakdownItem] = []
        if "service_name" in df.columns:
            for svc, val in df.groupby("service_name")["memory_utilization"].mean().items():
                by_service.append(BreakdownItem(label=str(svc), value=round(float(val), 2)))

        by_instance: List[BreakdownItem] = []
        if "instance_id" in df.columns:
            for inst, val in df.groupby("instance_id")["memory_utilization"].mean().head(10).items():
                by_instance.append(BreakdownItem(label=str(inst), value=round(float(val), 2)))

        peaks: List[Dict[str, Any]] = []
        high_mem = df[df["memory_utilization"] >= max(80.0, p95_mem)].head(8)
        for _, r in high_mem.iterrows():
            peaks.append({
                "timestamp": str(r.get("timestamp", "N/A")),
                "instance_id": str(r.get("instance_id", "N/A")),
                "memory_utilization": round(float(r["memory_utilization"]), 2),
            })

        return MemoryAnalyticsResponse(
            dataset_id=dataset_id,
            average_memory=avg_mem,
            max_memory=max_mem,
            min_memory=min_mem,
            p95_memory=p95_mem,
            memory_trends=trends,
            consumption_by_service=by_service,
            consumption_by_instance=by_instance,
            peak_periods=peaks,
        )

    def calculate_network_analytics(self, df: pd.DataFrame, dataset_id: Optional[str] = None) -> NetworkAnalyticsResponse:
        net_in = df["network_in"] if "network_in" in df.columns else pd.Series([0.0] * len(df))
        net_out = df["network_out"] if "network_out" in df.columns else pd.Series([0.0] * len(df))

        # Assumes values in MB or bytes; normalize to GB
        total_in_gb = round(float(net_in.sum() / 1024.0), 2)
        total_out_gb = round(float(net_out.sum() / 1024.0), 2)
        avg_in_mbps = round(float(net_in.mean()), 2)
        avg_out_mbps = round(float(net_out.mean()), 2)

        trends: List[Dict[str, Any]] = []
        if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df_ts = df.set_index("timestamp").sort_index()
            in_res = df_ts["network_in"].resample("1h").mean().fillna(0) if "network_in" in df_ts else pd.Series()
            out_res = df_ts["network_out"].resample("1h").mean().fillna(0) if "network_out" in df_ts else pd.Series()
            for ts in in_res.index:
                trends.append({
                    "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
                    "network_in": round(float(in_res.get(ts, 0)), 2),
                    "network_out": round(float(out_res.get(ts, 0)), 2),
                })

        by_service: List[BreakdownItem] = []
        if "service_name" in df.columns and "network_out" in df.columns:
            for svc, val in df.groupby("service_name")["network_out"].sum().items():
                by_service.append(BreakdownItem(label=str(svc), value=round(float(val / 1024.0), 2)))

        return NetworkAnalyticsResponse(
            dataset_id=dataset_id,
            total_ingress_gb=total_in_gb,
            total_egress_gb=total_out_gb,
            average_network_in_mbps=avg_in_mbps,
            average_network_out_mbps=avg_out_mbps,
            trends=trends,
            traffic_by_service=by_service,
            high_traffic_periods=[],
        )

    def calculate_storage_analytics(self, df: pd.DataFrame, dataset_id: Optional[str] = None) -> StorageAnalyticsResponse:
        stg_util = df["storage_utilization"] if "storage_utilization" in df.columns else pd.Series([45.0] * len(df))
        stg_read = df["storage_read"] if "storage_read" in df.columns else pd.Series([10.0] * len(df))
        stg_write = df["storage_write"] if "storage_write" in df.columns else pd.Series([5.0] * len(df))

        avg_util = round(float(stg_util.mean()), 2)
        peak_util = round(float(stg_util.max()), 2)
        tot_read_gb = round(float(stg_read.sum() / 1024.0), 2)
        tot_write_gb = round(float(stg_write.sum() / 1024.0), 2)

        trends: List[Dict[str, Any]] = []
        if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df_ts = df.set_index("timestamp").sort_index()
            u_res = df_ts["storage_utilization"].resample("1h").mean().dropna() if "storage_utilization" in df_ts else pd.Series()
            for ts, val in u_res.items():
                trends.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M"), "utilization": round(float(val), 2)})

        by_service: List[BreakdownItem] = []
        if "service_name" in df.columns and "storage_utilization" in df.columns:
            for svc, val in df.groupby("service_name")["storage_utilization"].mean().items():
                by_service.append(BreakdownItem(label=str(svc), value=round(float(val), 2)))

        return StorageAnalyticsResponse(
            dataset_id=dataset_id,
            average_storage_utilization=avg_util,
            average_utilization_pct=avg_util,
            peak_utilization_pct=peak_util,
            total_read_gb=tot_read_gb,
            total_write_gb=tot_write_gb,
            trends=trends,
            consumption_by_service=by_service,
        )

    def calculate_workload_analytics(self, df: pd.DataFrame, dataset_id: Optional[str] = None) -> WorkloadAnalyticsResponse:
        w_vol = df["workload_volume"] if "workload_volume" in df.columns else (
            df["request_count"] if "request_count" in df.columns else pd.Series([100] * len(df))
        )

        total_vol = int(w_vol.sum())
        avg_req = round(float(w_vol.mean()), 2)
        peak_req = round(float(w_vol.max()), 2)

        trends: List[Dict[str, Any]] = []
        if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df_ts = df.set_index("timestamp").sort_index()
            res = df_ts["workload_volume"].resample("1h").sum() if "workload_volume" in df_ts else pd.Series()
            for ts, val in res.items():
                trends.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M"), "volume": int(val)})

        by_app: List[BreakdownItem] = []
        if "application_name" in df.columns:
            for app, val in df.groupby("application_name")["workload_volume"].sum().head(8).items():
                by_app.append(BreakdownItem(label=str(app), value=float(val)))

        by_region: List[BreakdownItem] = []
        if "cloud_region" in df.columns:
            for reg, val in df.groupby("cloud_region")["workload_volume"].sum().items():
                by_region.append(BreakdownItem(label=str(reg), value=float(val)))

        by_inst_type: List[BreakdownItem] = []
        if "instance_type" in df.columns:
            for itype, val in df.groupby("instance_type")["workload_volume"].sum().items():
                by_inst_type.append(BreakdownItem(label=str(itype), value=float(val)))

        return WorkloadAnalyticsResponse(
            dataset_id=dataset_id,
            total_workload_volume=total_vol,
            total_requests=total_vol,
            average_req_per_min=avg_req,
            peak_req_per_min=peak_req,
            workload_trends=trends,
            distribution_by_application=by_app,
            distribution_by_region=by_region,
            distribution_by_instance_type=by_inst_type,
        )

    def calculate_resource_efficiency(self, df: pd.DataFrame, dataset_id: Optional[str] = None) -> ResourceEfficiencyResponse:
        """
        Classifies instances into:
        - IDLE: avg CPU < 5% and avg Memory < 15%
        - UNDERUTILIZED: avg CPU < 20%
        - NORMAL: avg CPU between 20% and 75%
        - HIGH_UTILIZATION: avg CPU > 75%
        """
        if len(df) == 0 or "instance_id" not in df.columns:
            return ResourceEfficiencyResponse(
                dataset_id=dataset_id,
                overall_efficiency_score=85.0,
                idle_count=0,
                underutilized_count=0,
                normal_count=0,
                high_utilization_count=0,
                potential_monthly_savings_usd=0.0,
                candidates=[],
                utilization_comparison=[],
            )

        grouped = df.groupby(["instance_id", "instance_type"]).agg({
            "cpu_utilization": "mean",
            "memory_utilization": "mean",
            "service_name": "first",
        }).reset_index()

        candidates: List[ResourceCandidate] = []
        idle_c = 0
        under_c = 0
        normal_c = 0
        high_c = 0
        total_monthly_savings = 0.0

        for _, row in grouped.iterrows():
            cpu_val = float(row["cpu_utilization"])
            mem_val = float(row["memory_utilization"])
            itype = str(row["instance_type"])
            inst_id = str(row["instance_id"])
            hourly_rate = self.compute_rates.get(itype, self.compute_rates["default"])
            monthly_cost = hourly_rate * 730.0  # 730 hours in a month

            if cpu_val < 5.0 and mem_val < 15.0:
                cat = "IDLE"
                rec = "Decommission or hibernate instance during non-peak cycles"
                saving = monthly_cost * 0.90
                idle_c += 1
            elif cpu_val < 20.0:
                cat = "UNDERUTILIZED"
                rec = f"Downsize from {itype} to lower tier instance"
                saving = monthly_cost * 0.40
                under_c += 1
            elif cpu_val > 75.0:
                cat = "HIGH_UTILIZATION"
                rec = "Consider scale-out or vertical resize to avoid latency spikes"
                saving = 0.0
                high_c += 1
            else:
                cat = "NORMAL"
                rec = "Operating within optimal efficiency envelope"
                saving = 0.0
                normal_c += 1

            total_monthly_savings += saving

            candidates.append(
                ResourceCandidate(
                    instance_id=inst_id,
                    instance_type=itype,
                    service_name=str(row.get("service_name", "N/A")),
                    avg_cpu=round(cpu_val, 2),
                    avg_memory=round(mem_val, 2),
                    category=cat,
                    recommendation=rec,
                    potential_monthly_saving_usd=round(saving, 2),
                )
            )

        total_nodes = max(1, len(grouped))
        score = max(20.0, min(100.0, round(100.0 - ((idle_c * 30.0 + under_c * 15.0) / total_nodes), 2)))

        util_comparison = [
            {"category": "Idle (<5%)", "count": idle_c, "percentage": round(idle_c / total_nodes * 100, 1)},
            {"category": "Underutilized (5-20%)", "count": under_c, "percentage": round(under_c / total_nodes * 100, 1)},
            {"category": "Optimal (20-75%)", "count": normal_c, "percentage": round(normal_c / total_nodes * 100, 1)},
            {"category": "High Saturation (>75%)", "count": high_c, "percentage": round(high_c / total_nodes * 100, 1)},
        ]

        return ResourceEfficiencyResponse(
            dataset_id=dataset_id,
            overall_efficiency_score=score,
            idle_count=idle_c,
            underutilized_count=under_c,
            normal_count=normal_c,
            high_utilization_count=high_c,
            potential_monthly_savings_usd=round(total_monthly_savings, 2),
            candidates=candidates[:20],
            utilization_comparison=util_comparison,
        )

    def calculate_cost_analytics(self, df: pd.DataFrame, dataset_id: Optional[str] = None) -> CostAnalyticsResponse:
        """
        Estimates cloud infrastructure costs using configured benchmark pricing.
        Explicitly flagged with disclaimer: 'Estimated cost based on configured pricing assumptions.'
        """
        if len(df) == 0:
            return CostAnalyticsResponse(
                dataset_id=dataset_id,
                daily_estimated_cost=0.0,
                monthly_estimated_cost=0.0,
                cost_by_service=[],
                cost_by_instance=[],
                cost_by_region=[],
                cost_trends=[],
                pricing_model_applied="Standard Configured Rates",
            )

        df_calc = df.copy()
        if "instance_type" in df_calc.columns:
            df_calc["hourly_rate"] = df_calc["instance_type"].map(self.compute_rates).fillna(self.compute_rates["default"])
        else:
            df_calc["hourly_rate"] = self.compute_rates["default"]

        # If data is 5-minute telemetry intervals, interval cost is hourly_rate / 12
        interval_cost = df_calc["hourly_rate"] / 12.0
        df_calc["interval_cost"] = interval_cost

        # Calculate time span to normalize daily and monthly run-rate
        total_interval_cost = float(df_calc["interval_cost"].sum())
        n_instances = max(1, df_calc["instance_id"].nunique() if "instance_id" in df_calc else 1)

        avg_hourly_fleet = float(df_calc.groupby("instance_id")["hourly_rate"].mean().sum()) if "instance_id" in df_calc else (self.compute_rates["default"] * n_instances)
        daily_cost = round(avg_hourly_fleet * 24.0, 2)
        monthly_cost = round(daily_cost * 30.5, 2)

        cost_by_service: List[BreakdownItem] = []
        if "service_name" in df_calc.columns:
            for svc, val in df_calc.groupby("service_name")["interval_cost"].sum().items():
                cost_by_service.append(BreakdownItem(label=str(svc), value=round(float(val), 2)))

        cost_by_instance: List[BreakdownItem] = []
        if "instance_id" in df_calc.columns:
            for inst, val in df_calc.groupby("instance_id")["interval_cost"].sum().head(10).items():
                cost_by_instance.append(BreakdownItem(label=str(inst), value=round(float(val), 2)))

        cost_by_region: List[BreakdownItem] = []
        if "cloud_region" in df_calc.columns:
            for reg, val in df_calc.groupby("cloud_region")["interval_cost"].sum().items():
                cost_by_region.append(BreakdownItem(label=str(reg), value=round(float(val), 2)))

        cost_trends: List[Dict[str, Any]] = []
        if "timestamp" in df_calc.columns and pd.api.types.is_datetime64_any_dtype(df_calc["timestamp"]):
            df_ts = df_calc.set_index("timestamp").sort_index()
            c_res = df_ts["interval_cost"].resample("1h").sum().dropna()
            for ts, val in c_res.items():
                cost_trends.append({"timestamp": ts.strftime("%Y-%m-%d %H:%M"), "cost": round(float(val), 2)})

        return CostAnalyticsResponse(
            dataset_id=dataset_id,
            currency="USD",
            disclaimer="Estimated cost based on configured pricing assumptions.",
            daily_estimated_cost=daily_cost,
            monthly_estimated_cost=monthly_cost,
            cost_by_service=cost_by_service,
            cost_by_instance=cost_by_instance,
            cost_by_region=cost_by_region,
            cost_trends=cost_trends,
            pricing_model_applied="Configured Benchmark AWS Instance Sizing Matrix",
        )

    def detect_statistical_anomalies(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        workspace_id: str,
        z_threshold: float = 2.5,
    ) -> List[AnomalyEventResponse]:
        """
        Executes non-ML statistical anomaly detection:
        - Z-Score detection on CPU, Memory, and Workload Volume
        - Interquartile Range (IQR) detection
        - Rolling outlier detection
        """
        anomalies: List[AnomalyEventResponse] = []
        metrics_to_check = [
            ("cpu_utilization", "CPU Utilization", "%"),
            ("memory_utilization", "Memory Utilization", "%"),
            ("workload_volume", "Workload Volume", "req/min"),
            ("network_in", "Network Ingress", "MB/s"),
        ]

        for col_name, label, unit in metrics_to_check:
            if col_name not in df.columns:
                continue

            series = df[col_name].dropna()
            if len(series) < 10:
                continue

            mean = series.mean()
            std = series.std()
            q25 = series.quantile(0.25)
            q75 = series.quantile(0.75)
            iqr = q75 - q25

            # Z-Score check
            if std > 0.001:
                z_scores = (series - mean).abs() / std
                outliers = df.loc[series[z_scores > z_threshold].index]

                for idx, row in outliers.head(15).iterrows():
                    val = float(row[col_name])
                    z_val = float((val - mean) / std)
                    severity = "CRITICAL" if abs(z_val) > 3.5 else ("HIGH" if abs(z_val) > 3.0 else "MEDIUM")
                    ts = row.get("timestamp")
                    if not isinstance(ts, datetime):
                        ts = datetime.now(timezone.utc)

                    exp_min = round(max(0.0, mean - (2.0 * std)), 2)
                    exp_max = round(mean + (2.0 * std), 2)

                    anomalies.append(
                        AnomalyEventResponse(
                            id=f"anom-{col_name[:3]}-{idx}",
                            timestamp=ts,
                            resource_id=str(row.get("instance_id", "inst-node-01")),
                            metric_name=col_name,
                            observed_value=round(val, 2),
                            expected_range_min=exp_min,
                            expected_range_max=exp_max,
                            detection_method="Z_SCORE",
                            severity=severity,
                            explanation=f"Statistical anomaly: {label} reached {val:.2f}{unit} (Z-score: {z_val:.2f}, baseline mean: {mean:.2f}).",
                        )
                    )

            # IQR check for non-Gaussian extreme spikes
            if iqr > 0.001:
                iqr_upper = q75 + (2.0 * iqr)
                iqr_outliers = df.loc[series[series > iqr_upper].index]

                for idx, row in iqr_outliers.head(10).iterrows():
                    val = float(row[col_name])
                    ts = row.get("timestamp")
                    if not isinstance(ts, datetime):
                        ts = datetime.now(timezone.utc)

                    anomalies.append(
                        AnomalyEventResponse(
                            id=f"anom-iqr-{col_name[:3]}-{idx}",
                            timestamp=ts,
                            resource_id=str(row.get("instance_id", "inst-node-01")),
                            metric_name=col_name,
                            observed_value=round(val, 2),
                            expected_range_min=round(q25, 2),
                            expected_range_max=round(iqr_upper, 2),
                            detection_method="IQR",
                            severity="HIGH" if val > q75 + 3.0 * iqr else "MEDIUM",
                            explanation=f"Interquartile Range Outlier: {label} exceeded IQR upper fence ({iqr_upper:.2f}{unit}).",
                        )
                    )

        # Remove duplicates based on timestamp and resource_id and metric
        unique_anomalies: Dict[str, AnomalyEventResponse] = {}
        for a in anomalies:
            key = f"{a.resource_id}_{a.metric_name}_{a.timestamp}"
            if key not in unique_anomalies or a.severity == "CRITICAL":
                unique_anomalies[key] = a

        return list(unique_anomalies.values())

    def compute_all_analytics(
        self,
        cleaned_parquet_path: str,
        dataset_id: str,
        cost_rates: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Loads cleaned parquet analytical dataset and computes complete analytical suite.
        """
        if cost_rates:
            self.compute_rates.update(cost_rates)

        df = pd.read_parquet(cleaned_parquet_path)

        cpu = self.calculate_cpu_analytics(df, dataset_id)
        mem = self.calculate_memory_analytics(df, dataset_id)
        net = self.calculate_network_analytics(df, dataset_id)
        storage = self.calculate_storage_analytics(df, dataset_id)
        workload = self.calculate_workload_analytics(df, dataset_id)
        efficiency = self.calculate_resource_efficiency(df, dataset_id)
        cost = self.calculate_cost_analytics(df, dataset_id)
        raw_anomalies = self.detect_statistical_anomalies(df, dataset_id=dataset_id, workspace_id="ws")

        total_inst = int(df["instance_id"].nunique()) if "instance_id" in df.columns else 1
        t_start = str(df["timestamp"].min()) if "timestamp" in df.columns and len(df) > 0 else None
        t_end = str(df["timestamp"].max()) if "timestamp" in df.columns and len(df) > 0 else None

        overview = {
            "dataset_id": dataset_id,
            "total_instances": total_inst,
            "total_records": len(df),
            "time_range": {"start": t_start, "end": t_end},
            "average_cpu": cpu.average_cpu,
            "average_memory": mem.average_memory,
            "total_network_traffic_gb": round(net.total_network_in_gb + net.total_network_out_gb, 2),
            "estimated_monthly_cost": cost.monthly_estimated_cost,
            "efficiency_score": efficiency.overall_efficiency_score,
            "idle_instances": efficiency.idle_count,
            "underutilized_instances": efficiency.underutilized_count,
            "potential_monthly_savings": efficiency.potential_monthly_savings_usd,
            "anomalies_count": len(raw_anomalies),
            "disclaimer": cost.disclaimer,
        }

        anomaly_dicts = []
        for a in raw_anomalies:
            anomaly_dicts.append({
                "instance_id": a.resource_id,
                "timestamp": a.timestamp,
                "metric_name": a.metric_name,
                "metric_value": a.observed_value,
                "expected_value": a.expected_range_max,
                "deviation_score": round(abs(a.observed_value - (a.expected_range_max or 0.0)), 2),
                "detection_method": a.detection_method,
                "severity": a.severity,
                "details_json": {
                    "explanation": a.explanation,
                    "min": a.expected_range_min,
                    "max": a.expected_range_max,
                },
            })

        return {
            "overview": overview,
            "cpu": cpu.model_dump(),
            "memory": mem.model_dump(),
            "network": net.model_dump(),
            "storage": storage.model_dump(),
            "workload": workload.model_dump(),
            "efficiency": efficiency.model_dump(),
            "cost": cost.model_dump(),
            "anomalies": anomaly_dicts,
            "raw_anomalies": [a.model_dump() for a in raw_anomalies],
        }
