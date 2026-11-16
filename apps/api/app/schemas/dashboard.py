from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class KpiMetric(BaseModel):
    key: str
    label: str
    value: str
    unit: Optional[str] = None
    change_percentage: float
    change_type: str  # "increase", "decrease", "neutral"
    status: str  # "normal", "warning", "critical"
    is_demo_data: bool = True


class TimeSeriesPoint(BaseModel):
    timestamp: str
    cpu_utilization: float
    memory_utilization: float
    cost_usd: float
    workload_volume: int


class CategoryDistributionPoint(BaseModel):
    name: str
    value: float
    color: Optional[str] = None


class ResourceComparisonPoint(BaseModel):
    resource: str
    allocated: float
    utilized: float
    optimized: float


class ActivityItemResponse(BaseModel):
    id: str
    action: str
    resource_type: str
    user_email: str
    timestamp: datetime
    details: Optional[str] = None


class DashboardSummaryResponse(BaseModel):
    workspace_id: str
    workspace_name: str
    cloud_provider: str
    is_demo_metrics: bool = True
    disclaimer: str = "DEMO DATA: Telemetry metrics shown are simulated previews for Phase 1 UI validation and do not represent live cloud infrastructure."
    kpis: List[KpiMetric]
    cpu_memory_trend: List[TimeSeriesPoint]
    workload_distribution: List[CategoryDistributionPoint]
    cost_trend: List[TimeSeriesPoint]
    resource_comparison: List[ResourceComparisonPoint]
    actual_dataset_count: int
    actual_project_count: int
    actual_member_count: int

