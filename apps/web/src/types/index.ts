export type UserRole = "PLATFORM_ADMIN" | "WORKSPACE_ADMIN" | "ANALYST" | "VIEWER";
export type WorkspaceType = "ENTERPRISE" | "RESEARCH" | "STARTUP" | "INDIVIDUAL";
export type CloudProvider = "AWS" | "GCP" | "AZURE" | "HYBRID";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_platform_admin: boolean;
  avatar_url?: string | null;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  type: WorkspaceType;
  cloud_provider: CloudProvider;
  owner_id: string;
  role?: UserRole;
  created_at: string;
  updated_at: string;
}

export interface KpiMetric {
  key: string;
  label: string;
  value: string;
  unit?: string | null;
  change_percentage: number;
  change_type: "increase" | "decrease" | "neutral";
  status: "normal" | "warning" | "critical";
  is_demo_data: boolean;
}

export interface TimeSeriesPoint {
  timestamp: string;
  cpu_utilization: number;
  memory_utilization: number;
  cost_usd: number;
  workload_volume: number;
}

export interface CategoryDistributionPoint {
  name: string;
  value: number;
  color?: string;
}

export interface ResourceComparisonPoint {
  resource: string;
  allocated: number;
  utilized: number;
  optimized: number;
}

export interface ActivityItem {
  id: string;
  action: string;
  resource_type: string;
  user_email: string;
  timestamp: string;
  details?: string;
}

export interface DashboardSummary {
  workspace_id: string;
  workspace_name: string;
  cloud_provider: string;
  is_demo_metrics: boolean;
  disclaimer: string;
  kpis: KpiMetric[];
  cpu_memory_trend: TimeSeriesPoint[];
  workload_distribution: CategoryDistributionPoint[];
  cost_trend: TimeSeriesPoint[];
  resource_comparison: ResourceComparisonPoint[];
  actual_dataset_count: number;
  actual_project_count: number;
  actual_member_count: number;
}

export interface Dataset {
  id: string;
  workspace_id: string;
  name: string;
  description?: string | null;
  original_filename?: string | null;
  file_format: string;
  file_size_bytes: number;
  storage_uri: string;
  row_count: number;
  column_count?: number;
  status: string;
  quality_status?: string;
  quality_score?: number | null;
  processing_engine?: string;
  uploaded_by: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface APIResponse<T> {
  success: boolean;
  message?: string;
  data: T;
  error?: string;
}

// ==========================================
// Phase 2 Big Data & Analytics Types
// ==========================================

export interface ColumnStat {
  column_name: string;
  data_type: string;
  missing_count?: number;
  unique_count?: number;
  sample_values?: any[];
}

export interface DatasetPreview {
  dataset_id: string;
  total_rows: number;
  columns: ColumnStat[];
  rows: Record<string, any>[];
  summary: {
    file_name: string;
    file_size_bytes: number;
    format: string;
    total_columns: number;
  };
}

export interface ColumnMappingData {
  dataset_id: string;
  mapping: Record<string, string>;
  is_valid: boolean;
  missing_required_fields: string[];
}

export interface QualityIssue {
  issue_type: string;
  column?: string;
  affected_rows: number;
  severity: "WARNING" | "ERROR" | "CRITICAL";
  description: string;
}

export interface DataQualityReportData {
  id?: string;
  dataset_id: string;
  quality_score: number;
  quality_status: string;
  total_records: number;
  valid_records: number;
  invalid_records: number;
  missing_values_count: number;
  duplicate_records_count: number;
  issues: QualityIssue[];
}

export interface ProcessingJob {
  id: string;
  dataset_id?: string;
  workspace_id: string;
  job_type: string;
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";
  engine: "PYSPARK" | "PANDAS";
  progress: number;
  execution_duration_ms?: number;
  records_processed: number;
  records_failed: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  created_at: string;
}

export interface ProcessingLog {
  id?: string;
  job_id?: string;
  level: string;
  stage: string;
  message: string;
  timestamp: string;
}

export interface AnalyticsOverview {
  dataset_id?: string;
  dataset_name?: string;
  total_instances: number;
  total_records: number;
  time_range: { start?: string | null; end?: string | null };
  average_cpu: number;
  average_memory: number;
  total_network_traffic_gb: number;
  estimated_monthly_cost: number;
  efficiency_score: number;
  idle_instances: number;
  underutilized_instances: number;
  potential_monthly_savings: number;
  anomalies_count: number;
  disclaimer: string;
}

export interface BreakdownItem {
  label: string;
  value: number;
  percentage?: number;
  count?: number;
}

export interface TimeSeriesMetricPoint {
  timestamp: string;
  value: number;
  unit?: string;
}

export interface CpuAnalytics {
  dataset_id?: string;
  average_cpu: number;
  max_cpu: number;
  min_cpu: number;
  p95_cpu: number;
  cpu_trends: TimeSeriesMetricPoint[];
  usage_by_service: BreakdownItem[];
  usage_by_instance: BreakdownItem[];
  peak_periods: any[];
  efficiency_status: string;
}

export interface MemoryAnalytics {
  dataset_id?: string;
  average_memory: number;
  max_memory: number;
  min_memory: number;
  p95_memory: number;
  memory_trends: TimeSeriesMetricPoint[];
  consumption_by_service: BreakdownItem[];
  consumption_by_instance: BreakdownItem[];
}

export interface NetworkAnalytics {
  dataset_id?: string;
  total_network_in_gb: number;
  total_network_out_gb: number;
  average_network_in_mbps: number;
  average_network_out_mbps: number;
  trends: any[];
  traffic_by_service: BreakdownItem[];
}

export interface StorageAnalytics {
  dataset_id?: string;
  average_storage_utilization: number;
  peak_utilization_pct: number;
  total_read_gb: number;
  total_write_gb: number;
  trends: any[];
  consumption_by_service: BreakdownItem[];
}

export interface WorkloadAnalytics {
  dataset_id?: string;
  total_workload_volume: number;
  total_requests: number;
  average_req_per_min: number;
  peak_req_per_min: number;
  workload_trends: any[];
  distribution_by_application: BreakdownItem[];
  distribution_by_region: BreakdownItem[];
}

export interface ResourceCandidate {
  instance_id: string;
  instance_type: string;
  service_name?: string;
  avg_cpu: number;
  avg_memory: number;
  category: "IDLE" | "UNDERUTILIZED" | "NORMAL" | "HIGH_UTILIZATION";
  recommendation: string;
  potential_monthly_saving_usd: number;
}

export interface ResourceEfficiency {
  dataset_id?: string;
  overall_efficiency_score: number;
  idle_count: number;
  underutilized_count: number;
  normal_count: number;
  high_utilization_count: number;
  potential_monthly_savings_usd: number;
  candidates: ResourceCandidate[];
  utilization_comparison: any[];
}

export interface CostAnalytics {
  dataset_id?: string;
  currency: string;
  disclaimer: string;
  daily_estimated_cost: number;
  monthly_estimated_cost: number;
  cost_by_service: BreakdownItem[];
  cost_by_instance: BreakdownItem[];
  cost_by_region: BreakdownItem[];
  cost_trends: any[];
  pricing_model_applied: string;
}

export interface AnomalyEventItem {
  id: string;
  timestamp: string;
  resource_id: string;
  metric_name: string;
  observed_value: number;
  expected_range_min?: number;
  expected_range_max?: number;
  detection_method: "Z_SCORE" | "IQR" | "ROLLING_THRESHOLD";
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  explanation: string;
}

export interface AnomalyAnalytics {
  dataset_id?: string;
  total_anomalies: number;
  critical_count?: number;
  high_count?: number;
  medium_count?: number;
  low_count?: number;
  events: AnomalyEventItem[];
}
