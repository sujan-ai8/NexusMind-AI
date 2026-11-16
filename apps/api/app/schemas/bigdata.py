from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# Dataset Ingestion & Metadata Schemas
# ==========================================


class ColumnStat(BaseModel):
    name: Optional[str] = None
    column_name: Optional[str] = None
    raw_name: Optional[str] = None
    data_type: str = "string"
    missing_count: int = 0
    unique_count: Optional[int] = None
    sample_values: List[Any] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class DatasetSchemaResponse(BaseModel):
    dataset_id: str
    columns: List[Any] = Field(default_factory=list)
    row_count: Optional[int] = 0
    column_count: Optional[int] = 0
    detected_fields: Optional[Dict[str, Optional[str]]] = None
    inferred_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class DatasetPreviewResponse(BaseModel):
    dataset_id: str
    dataset_name: Optional[str] = None
    total_rows: int = 0
    total_columns: Optional[int] = 0
    columns: List[Any] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)  # First 100 rows
    preview_count: Optional[int] = None
    summary: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class ColumnMappingRequest(BaseModel):
    mapping: Dict[str, str]  # standard_field -> raw_column_name


ColumnMappingUpdateRequest = ColumnMappingRequest


class ColumnMappingResponse(BaseModel):
    dataset_id: str
    mapping: Dict[str, str] = Field(default_factory=dict)
    is_valid: bool = True
    is_validated: Optional[bool] = True
    missing_required_fields: List[str] = Field(default_factory=list)
    unmapped_mandatory: List[str] = Field(default_factory=list)
    unmapped_optional: List[str] = Field(default_factory=list)
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="ignore", from_attributes=True)


# ==========================================
# Data Quality Engine Schemas
# ==========================================


class QualityIssue(BaseModel):
    issue_type: str
    column: Optional[str] = None
    affected_rows: int = 0
    severity: str = "WARNING"  # "WARNING", "ERROR", "CRITICAL"
    description: str

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class CleaningAction(BaseModel):
    action_type: str
    column: Optional[str] = None
    affected_rows: int = 0
    description: str

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class DataQualityReportResponse(BaseModel):
    id: Optional[str] = None
    dataset_id: str
    workspace_id: Optional[str] = None
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    duplicate_records: Optional[int] = 0
    duplicate_records_count: Optional[int] = 0
    missing_values_count: int = 0
    corrected_records: Optional[int] = 0
    rejected_records: Optional[int] = 0
    out_of_bound_records_count: Optional[int] = 0
    quality_score: float = 100.0  # 0.0 - 100.0
    quality_status: Optional[str] = "PASSED"
    status: Optional[str] = "PASSED"
    issues: List[Any] = Field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None
    cleaning_actions: List[CleaningAction] = Field(default_factory=list)
    rejected_records_uri: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(extra="ignore", from_attributes=True)


# ==========================================
# Background Processing & Job Schemas
# ==========================================


class ProcessingJobSubmitRequest(BaseModel):
    engine: str = Field(default="PYSPARK", description="'PYSPARK' or 'PANDAS'")
    cleaning_strategy: Optional[str] = Field(default="impute_or_drop")
    generate_features: bool = Field(default=True, description="Generate Phase 3 feature dataset")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


ProcessDatasetRequest = ProcessingJobSubmitRequest


class ProcessingLogItem(BaseModel):
    id: Optional[str] = None
    job_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    log_level: Optional[str] = "INFO"
    level: Optional[str] = "INFO"
    stage: Optional[str] = "EXECUTION"
    message: str

    model_config = ConfigDict(extra="ignore", from_attributes=True)


ProcessingLogResponse = ProcessingLogItem


class ProcessingJobResponse(BaseModel):
    id: str
    dataset_id: Optional[str] = None
    workspace_id: str
    job_type: str
    status: str
    engine: str
    progress: float = 0.0
    execution_duration_ms: Optional[int] = None
    records_processed: int = 0
    records_failed: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class ProcessingJobDetailResponse(ProcessingJobResponse):
    logs: List[ProcessingLogItem] = Field(default_factory=list)
    spark_config: Optional[Dict[str, Any]] = None


# ==========================================
# Analytics Engine Schemas
# ==========================================


class TimeSeriesMetricPoint(BaseModel):
    timestamp: str
    value: float
    unit: Optional[str] = None

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class BreakdownItem(BaseModel):
    label: str
    value: float
    percentage: Optional[float] = None
    count: Optional[int] = None

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class CpuAnalyticsResponse(BaseModel):
    dataset_id: Optional[str] = None
    average_cpu: float = 0.0
    max_cpu: float = 0.0
    min_cpu: float = 0.0
    p95_cpu: float = 0.0
    cpu_trends: List[TimeSeriesMetricPoint] = Field(default_factory=list)
    usage_by_service: List[BreakdownItem] = Field(default_factory=list)
    usage_by_instance: List[BreakdownItem] = Field(default_factory=list)
    peak_periods: List[Dict[str, Any]] = Field(default_factory=list)
    efficiency_status: str = "OPTIMAL"

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class MemoryAnalyticsResponse(BaseModel):
    dataset_id: Optional[str] = None
    average_memory: float = 0.0
    max_memory: float = 0.0
    min_memory: float = 0.0
    p95_memory: float = 0.0
    memory_trends: List[TimeSeriesMetricPoint] = Field(default_factory=list)
    consumption_by_service: List[BreakdownItem] = Field(default_factory=list)
    consumption_by_instance: List[BreakdownItem] = Field(default_factory=list)
    peak_periods: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class NetworkAnalyticsResponse(BaseModel):
    dataset_id: Optional[str] = None
    total_ingress_gb: float = 0.0
    total_egress_gb: float = 0.0
    total_network_in_gb: float = 0.0
    total_network_out_gb: float = 0.0
    average_network_in_mbps: float = 0.0
    average_network_out_mbps: float = 0.0
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    network_trends: List[TimeSeriesMetricPoint] = Field(default_factory=list)
    traffic_by_service: List[BreakdownItem] = Field(default_factory=list)
    high_traffic_periods: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class StorageAnalyticsResponse(BaseModel):
    dataset_id: Optional[str] = None
    average_storage_utilization: float = 0.0
    average_utilization_pct: float = 0.0
    peak_utilization_pct: float = 0.0
    total_read_gb: float = 0.0
    total_write_gb: float = 0.0
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    consumption_by_service: List[BreakdownItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class WorkloadAnalyticsResponse(BaseModel):
    dataset_id: Optional[str] = None
    total_workload_volume: int = 0
    total_requests: int = 0
    average_req_per_min: float = 0.0
    peak_req_per_min: float = 0.0
    workload_trends: List[Dict[str, Any]] = Field(default_factory=list)
    distribution_by_application: List[BreakdownItem] = Field(default_factory=list)
    distribution_by_region: List[BreakdownItem] = Field(default_factory=list)
    distribution_by_instance_type: List[BreakdownItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class ResourceCandidate(BaseModel):
    instance_id: str
    instance_type: str
    service_name: Optional[str] = None
    avg_cpu: float
    avg_memory: float
    category: str  # "IDLE", "UNDERUTILIZED", "NORMAL", "HIGH_UTILIZATION"
    recommendation: str
    potential_monthly_saving_usd: float

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class ResourceEfficiencyResponse(BaseModel):
    dataset_id: Optional[str] = None
    overall_efficiency_score: float = 85.0  # 0-100
    idle_count: int = 0
    underutilized_count: int = 0
    normal_count: int = 0
    high_utilization_count: int = 0
    potential_monthly_savings_usd: float = 0.0
    candidates: List[ResourceCandidate] = Field(default_factory=list)
    utilization_comparison: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class CostAnalyticsResponse(BaseModel):
    dataset_id: Optional[str] = None
    currency: str = "USD"
    disclaimer: str = "Estimated cost based on configured pricing assumptions."
    daily_estimated_cost: float = 0.0
    monthly_estimated_cost: float = 0.0
    cost_by_service: List[BreakdownItem] = Field(default_factory=list)
    cost_by_instance: List[BreakdownItem] = Field(default_factory=list)
    cost_by_region: List[BreakdownItem] = Field(default_factory=list)
    cost_trends: List[Dict[str, Any]] = Field(default_factory=list)
    pricing_model_applied: str = "Standard Benchmark Rates"

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class AnomalyEventResponse(BaseModel):
    id: str
    timestamp: datetime
    resource_id: str
    metric_name: str
    observed_value: float
    expected_range_min: Optional[float] = None
    expected_range_max: Optional[float] = None
    detection_method: str = "Z_SCORE"  # "Z_SCORE", "IQR", "ROLLING_THRESHOLD"
    severity: str = "MEDIUM"  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    explanation: str

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class AnomalyAnalyticsResponse(BaseModel):
    dataset_id: Optional[str] = None
    total_anomalies: int = 0
    critical_count: Optional[int] = 0
    high_count: Optional[int] = 0
    medium_count: Optional[int] = 0
    low_count: Optional[int] = 0
    severity_distribution: Dict[str, int] = Field(default_factory=dict)
    method_distribution: Dict[str, int] = Field(default_factory=dict)
    events: List[AnomalyEventResponse] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


class AnalyticsOverviewResponse(BaseModel):
    workspace_id: str
    total_datasets: int = 0
    total_records_processed: int = 0
    total_processing_jobs: int = 0
    failed_jobs: int = 0
    overall_quality_score: float = 100.0
    avg_cpu: float = 0.0
    avg_memory: float = 0.0
    total_network_gb: float = 0.0
    total_workload_requests: int = 0
    estimated_monthly_cost: float = 0.0
    cost_disclaimer: str = "Estimated cost based on configured pricing assumptions."
    anomaly_count: int = 0
    recent_jobs: List[ProcessingJobResponse] = Field(default_factory=list)
    recent_anomalies: List[AnomalyEventResponse] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", from_attributes=True)


# ==========================================
# Export Schemas
# ==========================================


class ExportRequest(BaseModel):
    dataset_id: str
    export_type: str = Field(default="PROCESSED_CSV", description="'PROCESSED_CSV', 'ANALYTICS_JSON', 'QUALITY_REPORT_JSON', 'FEATURES_PARQUET'")
    include_anomalies: bool = True
    include_quality_report: bool = True


class ExportResponse(BaseModel):
    export_id: str
    dataset_id: str
    export_type: str
    status: str
    file_name: str
    file_size_bytes: int
    download_url: str
    created_at: datetime
