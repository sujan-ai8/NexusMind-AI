from typing import List
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from apps.api.app.models.entities import (
    AuditLog,
    Dataset,
    Project,
    Workspace,
    WorkspaceMember,
)
from apps.api.app.repositories.audit_repository import AuditRepository
from apps.api.app.schemas.dashboard import (
    ActivityItemResponse,
    CategoryDistributionPoint,
    DashboardSummaryResponse,
    KpiMetric,
    ResourceComparisonPoint,
    TimeSeriesPoint,
)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)

    def get_summary(self, workspace: Workspace) -> DashboardSummaryResponse:
        # Retrieve actual counts from DB
        dataset_count = self.db.execute(
            select(func.count(Dataset.id)).where(Dataset.workspace_id == workspace.id)
        ).scalar() or 0

        project_count = self.db.execute(
            select(func.count(Project.id)).where(Project.workspace_id == workspace.id)
        ).scalar() or 0

        member_count = self.db.execute(
            select(func.count(WorkspaceMember.id)).where(WorkspaceMember.workspace_id == workspace.id)
        ).scalar() or 0

        # High-fidelity realistic telemetry samples clearly flagged as DEMO DATA for Phase 1 UI validation
        kpis = [
            KpiMetric(
                key="cpu_utilization",
                label="Avg CPU Utilization",
                value="43.8",
                unit="%",
                change_percentage=-4.2,
                change_type="decrease",
                status="normal",
                is_demo_data=True,
            ),
            KpiMetric(
                key="memory_utilization",
                label="Avg Memory Utilization",
                value="68.2",
                unit="%",
                change_percentage=2.1,
                change_type="increase",
                status="normal",
                is_demo_data=True,
            ),
            KpiMetric(
                key="workload_volume",
                label="Active Workload Volume",
                value="142.5",
                unit="k req/min",
                change_percentage=12.4,
                change_type="increase",
                status="normal",
                is_demo_data=True,
            ),
            KpiMetric(
                key="estimated_cost",
                label="Est. Cloud Run Rate",
                value="$1,248.50",
                unit="/mo",
                change_percentage=-8.6,
                change_type="decrease",
                status="normal",
                is_demo_data=True,
            ),
            KpiMetric(
                key="resource_efficiency",
                label="Resource Efficiency Score",
                value="89.4",
                unit="/100",
                change_percentage=5.3,
                change_type="increase",
                status="normal",
                is_demo_data=True,
            ),
        ]

        # 24-hour hourly trend sample
        cpu_memory_trend = [
            TimeSeriesPoint(timestamp="00:00", cpu_utilization=38.2, memory_utilization=61.0, cost_usd=42.1, workload_volume=95),
            TimeSeriesPoint(timestamp="04:00", cpu_utilization=32.4, memory_utilization=59.4, cost_usd=39.5, workload_volume=82),
            TimeSeriesPoint(timestamp="08:00", cpu_utilization=56.8, memory_utilization=72.1, cost_usd=55.2, workload_volume=145),
            TimeSeriesPoint(timestamp="12:00", cpu_utilization=64.1, memory_utilization=78.5, cost_usd=62.8, workload_volume=178),
            TimeSeriesPoint(timestamp="16:00", cpu_utilization=58.9, memory_utilization=74.3, cost_usd=58.1, workload_volume=160),
            TimeSeriesPoint(timestamp="20:00", cpu_utilization=45.3, memory_utilization=67.0, cost_usd=48.4, workload_volume=122),
            TimeSeriesPoint(timestamp="23:59", cpu_utilization=43.8, memory_utilization=68.2, cost_usd=46.9, workload_volume=115),
        ]

        workload_distribution = [
            CategoryDistributionPoint(name="Compute (EC2/EKS)", value=48.0, color="#3B82F6"),
            CategoryDistributionPoint(name="Storage (S3/EBS)", value=22.0, color="#10B981"),
            CategoryDistributionPoint(name="Database (RDS)", value=18.0, color="#8B5CF6"),
            CategoryDistributionPoint(name="Networking & CDN", value=12.0, color="#F59E0B"),
        ]

        cost_trend = cpu_memory_trend

        resource_comparison = [
            ResourceComparisonPoint(resource="CPU Cores (vCPU)", allocated=128.0, utilized=64.0, optimized=80.0),
            ResourceComparisonPoint(resource="Memory (GB)", allocated=512.0, utilized=350.0, optimized=400.0),
            ResourceComparisonPoint(resource="Block Storage (TB)", allocated=25.0, utilized=14.2, optimized=18.0),
            ResourceComparisonPoint(resource="Bandwidth (TB/mo)", allocated=50.0, utilized=32.0, optimized=38.0),
        ]

        return DashboardSummaryResponse(
            workspace_id=workspace.id,
            workspace_name=workspace.name,
            cloud_provider=workspace.cloud_provider,
            is_demo_metrics=True,
            disclaimer="DEMO DATA: Telemetry metrics shown are simulated previews for Phase 1 UI validation and do not represent live cloud infrastructure.",
            kpis=kpis,
            cpu_memory_trend=cpu_memory_trend,
            workload_distribution=workload_distribution,
            cost_trend=cost_trend,
            resource_comparison=resource_comparison,
            actual_dataset_count=dataset_count,
            actual_project_count=project_count,
            actual_member_count=member_count,
        )

    def get_recent_activity(self, workspace_id: str) -> List[ActivityItemResponse]:
        logs = self.audit_repo.list_by_workspace(workspace_id=workspace_id, limit=8)
        items = []
        for l in logs:
            items.append(
                ActivityItemResponse(
                    id=l.id,
                    action=l.action,
                    resource_type=l.resource_type,
                    user_email=l.user.email if l.user else "system",
                    timestamp=l.created_at,
                    details=f"Resource {l.resource_type} modified" if not l.details_json else str(l.details_json),
                )
            )
        return items

