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
  file_format: string;
  file_size_bytes: number;
  storage_uri: string;
  row_count: number;
  status: string;
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

