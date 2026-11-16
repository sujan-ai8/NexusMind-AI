import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  Cpu,
  Database,
  DollarSign,
  FileText,
  HardDrive,
  RefreshCw,
  Server,
  Sparkles,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { DemoBadge } from "@/components/common/DemoBadge";
import { LoadingState } from "@/components/common/LoadingState";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { TrendChart } from "@/components/dashboard/TrendChart";
import { CostChart } from "@/components/dashboard/CostChart";
import { WorkloadDistributionChart } from "@/components/dashboard/WorkloadDistributionChart";
import { ResourceComparisonChart } from "@/components/dashboard/ResourceComparisonChart";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { apiRequest } from "@/lib/api-client";
import { useWorkspace } from "@/contexts/WorkspaceContext";
import { ActivityItem, DashboardSummary } from "@/types";

export function DashboardPage() {
  const { activeWorkspace } = useWorkspace();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    if (!activeWorkspace) return;
    try {
      setIsRefreshing(true);
      const [sumData, actData] = await Promise.all([
        apiRequest<DashboardSummary>("/dashboard/summary"),
        apiRequest<ActivityItem[]>("/dashboard/activity"),
      ]);
      setSummary(sumData);
      setActivities(actData);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [activeWorkspace?.id]);

  if (isLoading) {
    return <LoadingState message="Aggregating workspace telemetry and model summaries..." />;
  }

  const kpiIcons: Record<string, any> = {
    cpu_utilization: Cpu,
    memory_utilization: HardDrive,
    workload_volume: Zap,
    estimated_cost: DollarSign,
    resource_efficiency: Activity,
  };

  return (
    <div className="space-y-6">
      {/* 1. Page Header with Disclaimer */}
      <PageHeader
        title="Infrastructure Intelligence Overview"
        description="Unified observability, predictive demand telemetry, and resource optimization insights."
        badge={<DemoBadge />}
      >
        <Button
          onClick={fetchDashboardData}
          variant="outline"
          size="sm"
          isLoading={isRefreshing}
          className="text-xs"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh Metrics
        </Button>
      </PageHeader>

      {/* 2. Phase 1 Demo Data Transparency Banner */}
      <div className="p-3.5 rounded-lg border border-amber-500/20 bg-amber-500/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5 text-amber-500">
          <DemoBadge />
          <span className="text-muted-foreground font-medium">
            Telemetry metrics below are simulated preview feeds for Phase 1 UI and architecture validation. Live AWS CloudWatch streaming begins in Phase 2.
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px] text-muted-foreground">
          <span>Tenant: <strong className="text-foreground">{activeWorkspace?.name}</strong></span>
          <span>•</span>
          <span>Provider: <strong className="text-foreground">{activeWorkspace?.cloud_provider}</strong></span>
        </div>
      </div>

      {/* 3. KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {summary?.kpis.map((kpi) => (
          <KpiCard key={kpi.key} metric={kpi} icon={kpiIcons[kpi.key]} />
        ))}
      </div>

      {/* 4. Primary Charts Row: Telemetry Trend + Cost Bar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {summary && <TrendChart data={summary.cpu_memory_trend} />}
        {summary && <CostChart data={summary.cost_trend} />}
      </div>

      {/* 5. Secondary Analytics Row: Workload Distribution + Resource Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {summary && <WorkloadDistributionChart data={summary.workload_distribution} />}
        {summary && <ResourceComparisonChart data={summary.resource_comparison} />}
      </div>

      {/* 6. Operational Row: Recent Activity + Quick Actions + System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ActivityFeed activities={activities} />
        <QuickActions />
      </div>

      {/* 7. Actual Workspace Assets Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Registered Datasets</div>
              <div className="text-lg font-bold text-foreground">{summary?.actual_dataset_count ?? 0} Datasets</div>
            </div>
          </div>
          <Link to="/datasets">
            <Button variant="ghost" size="sm" className="text-xs">
              Manage <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </Link>
        </Card>

        <Card className="p-4 border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Agile SPM Projects</div>
              <div className="text-lg font-bold text-foreground">{summary?.actual_project_count ?? 1} Initiatives</div>
            </div>
          </div>
          <Link to="/spm">
            <Button variant="ghost" size="sm" className="text-xs">
              View Tasks <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </Link>
        </Card>

        <Card className="p-4 border-border flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-500">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Operational Reports</div>
              <div className="text-lg font-bold text-foreground">1 Active Audit</div>
            </div>
          </div>
          <Link to="/reports">
            <Button variant="ghost" size="sm" className="text-xs">
              Explore <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </Link>
        </Card>
      </div>
    </div>
  );
}

