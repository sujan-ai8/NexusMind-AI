from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_active_workspace, get_current_user
from apps.api.app.models.entities import Dataset, ProcessedDataset, User, Workspace, AnalyticsSnapshot, AnomalyEvent
from apps.api.app.schemas.common import APIResponse
from apps.api.app.schemas.bigdata import (
    AnomalyAnalyticsResponse,
    AnomalyEventResponse,
    CostAnalyticsResponse,
    CpuAnalyticsResponse,
    MemoryAnalyticsResponse,
    NetworkAnalyticsResponse,
    ResourceEfficiencyResponse,
    StorageAnalyticsResponse,
    WorkloadAnalyticsResponse,
)
from apps.api.app.services.storage.local_storage import LocalStorageService
from apps.api.app.services.bigdata.analytics_engine import AnalyticsEngine

router = APIRouter(prefix="/analytics", tags=["Cloud Intelligence Analytics Engine"])


def _resolve_analytics_df(
    db: Session,
    workspace_id: str,
    dataset_id: Optional[str] = None,
) -> tuple[Optional[Dataset], Optional[pd.DataFrame]]:
    storage = LocalStorageService()

    if dataset_id:
        dataset = db.execute(
            select(Dataset).where(Dataset.id == dataset_id, Dataset.workspace_id == workspace_id)
        ).scalar_one_or_none()
    else:
        # Find latest processed or ready dataset in workspace
        dataset = db.execute(
            select(Dataset)
            .where(Dataset.workspace_id == workspace_id, Dataset.status.in_(["PROCESSED", "READY"]))
            .order_by(Dataset.updated_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    if not dataset:
        return None, None

    # Try loading cleaned parquet first
    processed = db.execute(
        select(ProcessedDataset)
        .where(ProcessedDataset.dataset_id == dataset.id)
        .order_by(ProcessedDataset.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if processed and processed.storage_uri:
        abs_p = storage.resolve_path(processed.storage_uri)
        try:
            df = pd.read_parquet(abs_p)
            return dataset, df
        except Exception:
            pass

    # Fallback to reading raw dataset file
    if dataset.storage_uri:
        try:
            df = storage.read_raw_dataframe(dataset.storage_uri, dataset.file_format)
            return dataset, df
        except Exception:
            pass

    return dataset, None


@router.get("/overview", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_analytics_overview(
    dataset_id: Optional[str] = Query(None, description="Dataset ID (defaults to latest in workspace)"),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve overarching cloud telemetry and intelligence summary."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)

    if not dataset or df is None or len(df) == 0:
        return APIResponse(
            success=True,
            message="No processed cloud telemetry available. Upload and process a dataset to view analytics.",
            data={
                "dataset_id": dataset_id,
                "total_instances": 0,
                "total_records": 0,
                "time_range": {"start": None, "end": None},
                "average_cpu": 0.0,
                "average_memory": 0.0,
                "total_network_traffic_gb": 0.0,
                "estimated_monthly_cost": 0.0,
                "efficiency_score": 100.0,
                "idle_instances": 0,
                "underutilized_instances": 0,
                "potential_monthly_savings": 0.0,
                "anomalies_count": 0,
                "disclaimer": "Estimated cost based on configured pricing assumptions.",
            },
        )

    # Check for existing snapshot
    snapshot = db.execute(
        select(AnalyticsSnapshot)
        .where(AnalyticsSnapshot.dataset_id == dataset.id)
        .order_by(AnalyticsSnapshot.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if snapshot and snapshot.metrics_json:
        return APIResponse(
            success=True,
            message="Analytics overview retrieved",
            data=snapshot.metrics_json,
        )

    # Compute on the fly
    engine = AnalyticsEngine()
    cpu = engine.calculate_cpu_analytics(df, dataset.id)
    mem = engine.calculate_memory_analytics(df, dataset.id)
    net = engine.calculate_network_analytics(df, dataset.id)
    efficiency = engine.calculate_resource_efficiency(df, dataset.id)
    cost = engine.calculate_cost_analytics(df, dataset.id)
    anomalies = engine.detect_statistical_anomalies(df, dataset_id=dataset.id, workspace_id=workspace.id)

    total_inst = int(df["instance_id"].nunique()) if "instance_id" in df.columns else 1
    t_start = str(df["timestamp"].min()) if "timestamp" in df.columns and len(df) > 0 else None
    t_end = str(df["timestamp"].max()) if "timestamp" in df.columns and len(df) > 0 else None

    data = {
        "dataset_id": dataset.id,
        "dataset_name": dataset.name,
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
        "anomalies_count": len(anomalies),
        "disclaimer": cost.disclaimer,
    }

    return APIResponse(
        success=True,
        message="Analytics overview retrieved",
        data=data,
    )


@router.get("/cpu", response_model=APIResponse[CpuAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_cpu_analytics(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed CPU utilization statistics, distributions, and time series trends."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    engine = AnalyticsEngine()
    if df is None:
        df = pd.DataFrame()
    res = engine.calculate_cpu_analytics(df, dataset_id=dataset.id if dataset else None)
    return APIResponse(success=True, message="CPU analytics retrieved", data=res)


@router.get("/memory", response_model=APIResponse[MemoryAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_memory_analytics(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed Memory utilization statistics and saturation metrics."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    engine = AnalyticsEngine()
    if df is None:
        df = pd.DataFrame()
    res = engine.calculate_memory_analytics(df, dataset_id=dataset.id if dataset else None)
    return APIResponse(success=True, message="Memory analytics retrieved", data=res)


@router.get("/network", response_model=APIResponse[NetworkAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_network_analytics(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get network I/O throughput, transfer volumes, and ingress/egress ratios."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    engine = AnalyticsEngine()
    if df is None:
        df = pd.DataFrame()
    res = engine.calculate_network_analytics(df, dataset_id=dataset.id if dataset else None)
    return APIResponse(success=True, message="Network analytics retrieved", data=res)


@router.get("/storage", response_model=APIResponse[StorageAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_storage_analytics(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get storage utilization and disk read/write throughput."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    engine = AnalyticsEngine()
    if df is None:
        df = pd.DataFrame()
    res = engine.calculate_storage_analytics(df, dataset_id=dataset.id if dataset else None)
    return APIResponse(success=True, message="Storage analytics retrieved", data=res)


@router.get("/workload", response_model=APIResponse[WorkloadAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_workload_analytics(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get request rates, concurrency patterns, and hourly/daily workload cycles."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    engine = AnalyticsEngine()
    if df is None:
        df = pd.DataFrame()
    res = engine.calculate_workload_analytics(df, dataset_id=dataset.id if dataset else None)
    return APIResponse(success=True, message="Workload pattern analytics retrieved", data=res)


@router.get("/resources", response_model=APIResponse[ResourceEfficiencyResponse], status_code=status.HTTP_200_OK)
def get_resource_efficiency(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Identify idle and underutilized infrastructure candidates and potential savings."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    engine = AnalyticsEngine()
    if df is None:
        df = pd.DataFrame()
    res = engine.calculate_resource_efficiency(df, dataset_id=dataset.id if dataset else None)
    return APIResponse(success=True, message="Resource efficiency analysis retrieved", data=res)


@router.get("/cost", response_model=APIResponse[CostAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_cost_analytics(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Estimate cloud infrastructure cost by instance, service, and region with disclaimer."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    engine = AnalyticsEngine()
    if df is None:
        df = pd.DataFrame()
    res = engine.calculate_cost_analytics(df, dataset_id=dataset.id if dataset else None)
    return APIResponse(success=True, message="Cost estimation retrieved", data=res)


@router.get("/anomalies", response_model=APIResponse[AnomalyAnalyticsResponse], status_code=status.HTTP_200_OK)
def get_anomalies(
    dataset_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None, description="Filter by CRITICAL, HIGH, MEDIUM, LOW"),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve statistical anomaly detections (Z-score and IQR)."""
    dataset, df = _resolve_analytics_df(db, workspace.id, dataset_id)
    if not dataset:
        return APIResponse(
            success=True,
            message="No anomalies detected",
            data=AnomalyAnalyticsResponse(
                dataset_id=dataset_id,
                total_anomalies=0,
                critical_count=0,
                high_count=0,
                medium_count=0,
                low_count=0,
                events=[],
            ),
        )

    # Check DB for saved anomalies first
    stmt = select(AnomalyEvent).where(AnomalyEvent.dataset_id == dataset.id)
    if severity:
        stmt = stmt.where(AnomalyEvent.severity == severity.upper())
    stmt = stmt.order_by(AnomalyEvent.timestamp.desc()).limit(100)
    db_anomalies = list(db.execute(stmt).scalars().all())

    if db_anomalies:
        events = [
            AnomalyEventResponse(
                id=a.id,
                timestamp=a.timestamp,
                resource_id=a.instance_id,
                metric_name=a.metric_name,
                observed_value=a.metric_value,
                expected_range_min=a.details_json.get("min") if a.details_json else None,
                expected_range_max=a.expected_value,
                detection_method=a.detection_method,
                severity=a.severity,
                explanation=a.details_json.get("explanation", f"Anomaly detected in {a.metric_name}") if a.details_json else f"Anomaly detected in {a.metric_name}",
            )
            for a in db_anomalies
        ]
    else:
        engine = AnalyticsEngine()
        raw_events = engine.detect_statistical_anomalies(df, dataset_id=dataset.id, workspace_id=workspace.id)
        if severity:
            raw_events = [e for e in raw_events if e.severity == severity.upper()]
        events = raw_events

    crit = sum(1 for e in events if e.severity == "CRITICAL")
    hi = sum(1 for e in events if e.severity == "HIGH")
    med = sum(1 for e in events if e.severity == "MEDIUM")
    low = sum(1 for e in events if e.severity == "LOW")

    res = AnomalyAnalyticsResponse(
        dataset_id=dataset.id,
        total_anomalies=len(events),
        critical_count=crit,
        high_count=hi,
        medium_count=med,
        low_count=low,
        events=events,
    )
    return APIResponse(success=True, message="Statistical anomalies retrieved", data=res)


@router.get("/data-quality", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_data_quality_summary(
    dataset_id: Optional[str] = Query(None),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve comprehensive data quality metrics across datasets."""
    dataset, _ = _resolve_analytics_df(db, workspace.id, dataset_id)
    if not dataset:
        return APIResponse(
            success=True,
            message="No dataset found",
            data={
                "quality_score": 100.0,
                "quality_status": "PENDING",
                "total_records": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "missing_values_count": 0,
                "duplicate_records_count": 0,
            },
        )

    from apps.api.app.services.dataset_service import DatasetService
    service = DatasetService(db)
    report = service.get_latest_quality_report(workspace_id=workspace.id, dataset_id=dataset.id)
    if not report:
        return APIResponse(
            success=True,
            message="Data quality audit not yet run for this dataset",
            data={
                "dataset_id": dataset.id,
                "quality_score": dataset.quality_score or 100.0,
                "quality_status": dataset.quality_status or "PENDING",
                "total_records": dataset.row_count,
                "valid_records": dataset.row_count,
                "invalid_records": 0,
                "missing_values_count": 0,
                "duplicate_records_count": 0,
            },
        )

    return APIResponse(success=True, message="Data quality summary retrieved", data=report)
