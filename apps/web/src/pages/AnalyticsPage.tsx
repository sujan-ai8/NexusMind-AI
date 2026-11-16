import React, { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Cpu,
  Database,
  DollarSign,
  Download,
  Filter,
  HardDrive,
  Layers,
  Network,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { LoadingState } from "@/components/common/LoadingState";
import { EmptyState } from "@/components/common/EmptyState";
import { apiRequest } from "@/lib/api-client";
import {
  AnalyticsOverview,
  CpuAnalytics,
  MemoryAnalytics,
  NetworkAnalytics,
  StorageAnalytics,
  WorkloadAnalytics,
  ResourceEfficiency,
  CostAnalytics,
  AnomalyAnalytics,
  Dataset,
  PaginatedResponse,
} from "@/types";

export function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "cpu" | "memory" | "network_storage" | "workload" | "efficiency_cost" | "anomalies"
  >("overview");

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);

  // Analytics states
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [cpuData, setCpuData] = useState<CpuAnalytics | null>(null);
  const [memData, setMemData] = useState<MemoryAnalytics | null>(null);
  const [netData, setNetData] = useState<NetworkAnalytics | null>(null);
  const [stgData, setStgData] = useState<StorageAnalytics | null>(null);
  const [workloadData, setWorkloadData] = useState<WorkloadAnalytics | null>(null);
  const [efficiencyData, setEfficiencyData] = useState<ResourceEfficiency | null>(null);
  const [costData, setCostData] = useState<CostAnalytics | null>(null);
  const [anomalyData, setAnomalyData] = useState<AnomalyAnalytics | null>(null);

  // Fetch available datasets for the dropdown
  useEffect(() => {
    const loadDatasets = async () => {
      try {
        const res = await apiRequest<PaginatedResponse<Dataset>>("/datasets", {
          params: { page: 1, page_size: 50 },
        });
        setDatasets(res.items);
        if (res.items.length > 0 && !selectedDatasetId) {
          // Default to the first processed or ready dataset
          const processed = res.items.find((d) => d.status === "PROCESSED") || res.items[0];
          setSelectedDatasetId(processed.id);
        }
      } catch (err) {
        console.error("Failed to load datasets for analytics:", err);
      }
    };
    loadDatasets();
  }, []);

  // Fetch analytics data when selected dataset changes
  const fetchAnalytics = async () => {
    try {
      setIsLoading(true);
      const params = selectedDatasetId ? { dataset_id: selectedDatasetId } : {};

      const [ov, cpu, mem, net, stg, wlk, eff, cst, anom] = await Promise.all([
        apiRequest<AnalyticsOverview>("/analytics/overview", { params }),
        apiRequest<CpuAnalytics>("/analytics/cpu", { params }),
        apiRequest<MemoryAnalytics>("/analytics/memory", { params }),
        apiRequest<NetworkAnalytics>("/analytics/network", { params }),
        apiRequest<StorageAnalytics>("/analytics/storage", { params }),
        apiRequest<WorkloadAnalytics>("/analytics/workload", { params }),
        apiRequest<ResourceEfficiency>("/analytics/resources", { params }),
        apiRequest<CostAnalytics>("/analytics/cost", { params }),
        apiRequest<AnomalyAnalytics>("/analytics/anomalies", { params }),
      ]);

      setOverview(ov);
      setCpuData(cpu);
      setMemData(mem);
      setNetData(net);
      setStgData(stg);
      setWorkloadData(wlk);
      setEfficiencyData(eff);
      setCostData(cst);
      setAnomalyData(anom);
    } catch (err) {
      console.error("Failed to load analytics metrics:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [selectedDatasetId]);

  // Handle Export
  const handleExport = async (format: "CSV" | "JSON" = "CSV") => {
    if (!selectedDatasetId) return;
    try {
      setIsExporting(true);
      const res = await apiRequest<{ download_url: string }>("/exports/analytics", {
        method: "POST",
        body: JSON.stringify({
          dataset_id: selectedDatasetId,
          export_format: format,
          report_type: "PROCESSED_DATA",
        }),
      });
      window.open(res.download_url, "_blank");
    } catch (err: any) {
      alert(`Export failed: ${err.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cloud Intelligence & Big Data Analytics"
        description="Multi-dimensional statistical workload intelligence, distributed capacity metrics, and resource efficiency."
      >
        <div className="flex items-center gap-2">
          {/* Dataset Selector */}
          <select
            value={selectedDatasetId}
            onChange={(e) => setSelectedDatasetId(e.target.value)}
            className="h-8 px-2.5 text-xs rounded-md border border-border bg-card text-foreground font-medium"
          >
            <option value="">Latest Active Cluster Dataset</option>
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.file_format} • {d.row_count.toLocaleString()} rows)
              </option>
            ))}
          </select>

          <Button
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={fetchAnalytics}
            disabled={isLoading}
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>

          <Button
            variant="primary"
            size="sm"
            className="text-xs"
            onClick={() => handleExport("CSV")}
            disabled={isExporting || !selectedDatasetId}
          >
            <Download className="w-3.5 h-3.5 mr-1.5" />
            {isExporting ? "Exporting..." : "Export CSV"}
          </Button>
        </div>
      </PageHeader>

      {/* Analytics Tabs */}
      <div className="flex items-center gap-1.5 border-b border-border overflow-x-auto pb-2 text-xs">
        {[
          { id: "overview", label: "Executive Overview", icon: BarChart3 },
          { id: "cpu", label: "CPU Utilization", icon: Cpu },
          { id: "memory", label: "Memory Saturation", icon: HardDrive },
          { id: "network_storage", label: "Network & Storage I/O", icon: Network },
          { id: "workload", label: "Workload Cycles", icon: Activity },
          { id: "efficiency_cost", label: "Efficiency & Cost", icon: DollarSign },
          { id: "anomalies", label: "Statistical Anomalies", icon: AlertTriangle },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-md font-medium transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
              {tab.id === "anomalies" && overview && overview.anomalies_count > 0 && (
                <span className="ml-1 px-1.5 py-0.2 rounded-full bg-red-500 text-white text-[10px]">
                  {overview.anomalies_count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <LoadingState message="Computing distributed telemetry analytics..." />
      ) : !overview || overview.total_records === 0 ? (
        <EmptyState
          title="No Processed Analytics Available"
          description="Upload and process a cloud workload telemetry dataset in Dataset Management to view multi-dimensional analytics."
          actionLabel="Go to Dataset Management"
          onAction={() => (window.location.href = "/datasets")}
        />
      ) : (
        <div className="space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="p-4 bg-card/60">
              <p className="text-xs text-muted-foreground">Monitored Fleet</p>
              <p className="text-2xl font-bold text-foreground mt-1">
                {overview.total_instances} <span className="text-xs font-normal text-muted-foreground">Nodes</span>
              </p>
              <p className="text-[11px] text-muted-foreground mt-1">
                {overview.total_records.toLocaleString()} data points
              </p>
            </Card>

            <Card className="p-4 bg-card/60">
              <p className="text-xs text-muted-foreground">Average CPU / Memory</p>
              <p className="text-2xl font-bold text-foreground mt-1">
                {overview.average_cpu.toFixed(1)}%{" "}
                <span className="text-xs font-normal text-muted-foreground">/ {overview.average_memory.toFixed(1)}%</span>
              </p>
              <p className="text-[11px] text-emerald-500 mt-1">Efficiency: {overview.efficiency_score.toFixed(0)}/100</p>
            </Card>

            <Card className="p-4 bg-card/60">
              <p className="text-xs text-muted-foreground">Estimated Monthly Run-Rate</p>
              <p className="text-2xl font-bold text-foreground mt-1">
                ${overview.estimated_monthly_cost.toLocaleString()}
              </p>
              <p className="text-[11px] text-emerald-500 mt-1">
                Potential Savings: ${overview.potential_monthly_savings.toLocaleString()}
              </p>
            </Card>

            <Card className="p-4 bg-card/60">
              <p className="text-xs text-muted-foreground">Statistical Anomalies</p>
              <p className="text-2xl font-bold text-amber-500 mt-1">{overview.anomalies_count}</p>
              <p className="text-[11px] text-muted-foreground mt-1">
                {overview.idle_instances} idle • {overview.underutilized_instances} underutilized
              </p>
            </Card>
          </div>

          {/* TAB 1: EXECUTIVE OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Cost Disclaimer Callout */}
              <div className="p-3 bg-muted/40 border border-border rounded-lg text-xs flex items-center justify-between text-muted-foreground">
                <span>
                  <strong>Notice:</strong> {overview.disclaimer}
                </span>
                <Badge variant="outline" className="text-[10px]">
                  Configured AWS Benchmarks
                </Badge>
              </div>

              {/* Diurnal CPU and Workload Trend */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">Cluster CPU Utilization Timeline</CardTitle>
                  <CardDescription className="text-xs">
                    Hourly average CPU saturation across all active nodes in the cluster
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={cpuData?.cpu_trends || []}>
                        <defs>
                          <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                        <XAxis dataKey="timestamp" stroke="#888888" fontSize={10} tickLine={false} />
                        <YAxis stroke="#888888" fontSize={10} tickLine={false} unit="%" />
                        <Tooltip />
                        <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} fill="url(#cpuGradient)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Service & Instance Breakdowns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-semibold">Average CPU by Service</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-60 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={cpuData?.usage_by_service || []} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                          <XAxis type="number" stroke="#888888" fontSize={10} unit="%" />
                          <YAxis dataKey="label" type="category" stroke="#888888" fontSize={10} width={110} />
                          <Tooltip />
                          <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-semibold">Resource Efficiency Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-60 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={efficiencyData?.utilization_comparison || []}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                          <XAxis dataKey="category" stroke="#888888" fontSize={10} />
                          <YAxis stroke="#888888" fontSize={10} />
                          <Tooltip />
                          <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* TAB 2: CPU UTILIZATION */}
          {activeTab === "cpu" && (
            <div className="space-y-6">
              <div className="grid grid-cols-4 gap-4">
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Mean CPU</p>
                  <p className="text-xl font-bold">{cpuData?.average_cpu.toFixed(1)}%</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Max Peak CPU</p>
                  <p className="text-xl font-bold text-red-500">{cpuData?.max_cpu.toFixed(1)}%</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">95th Percentile</p>
                  <p className="text-xl font-bold">{cpuData?.p95_cpu.toFixed(1)}%</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Min Baseline</p>
                  <p className="text-xl font-bold">{cpuData?.min_cpu.toFixed(1)}%</p>
                </Card>
              </div>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">Top Instances by CPU Usage</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={cpuData?.usage_by_instance || []}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                        <XAxis dataKey="label" stroke="#888888" fontSize={10} />
                        <YAxis stroke="#888888" fontSize={10} unit="%" />
                        <Tooltip />
                        <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* TAB 3: MEMORY SATURATION */}
          {activeTab === "memory" && (
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Mean Memory</p>
                  <p className="text-xl font-bold">{memData?.average_memory.toFixed(1)}%</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Peak Memory</p>
                  <p className="text-xl font-bold text-amber-500">{memData?.max_memory.toFixed(1)}%</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">95th Percentile</p>
                  <p className="text-xl font-bold">{memData?.p95_memory.toFixed(1)}%</p>
                </Card>
              </div>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">Memory Consumption by Service</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={memData?.consumption_by_service || []}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                        <XAxis dataKey="label" stroke="#888888" fontSize={10} />
                        <YAxis stroke="#888888" fontSize={10} unit="%" />
                        <Tooltip />
                        <Bar dataKey="value" fill="#ec4899" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* TAB 4: NETWORK & STORAGE */}
          {activeTab === "network_storage" && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Total Ingress</p>
                  <p className="text-xl font-bold">{netData?.total_network_in_gb.toFixed(1)} GB</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Total Egress</p>
                  <p className="text-xl font-bold">{netData?.total_network_out_gb.toFixed(1)} GB</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Storage Read</p>
                  <p className="text-xl font-bold">{stgData?.total_read_gb.toFixed(1)} GB</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Storage Write</p>
                  <p className="text-xl font-bold">{stgData?.total_write_gb.toFixed(1)} GB</p>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-semibold">Network Traffic by Service</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={netData?.traffic_by_service || []}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                          <XAxis dataKey="label" stroke="#888888" fontSize={10} />
                          <YAxis stroke="#888888" fontSize={10} unit="MB/s" />
                          <Tooltip />
                          <Bar dataKey="value" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-semibold">Storage Consumption by Service</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={stgData?.consumption_by_service || []}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                          <XAxis dataKey="label" stroke="#888888" fontSize={10} />
                          <YAxis stroke="#888888" fontSize={10} unit="%" />
                          <Tooltip />
                          <Bar dataKey="value" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* TAB 5: WORKLOAD CYCLES */}
          {activeTab === "workload" && (
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Total Requests</p>
                  <p className="text-xl font-bold">{workloadData?.total_requests.toLocaleString()}</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Avg Throughput</p>
                  <p className="text-xl font-bold">{workloadData?.average_req_per_min.toFixed(0)} req/min</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Peak Burst Throughput</p>
                  <p className="text-xl font-bold text-primary">{workloadData?.peak_req_per_min.toFixed(0)} req/min</p>
                </Card>
              </div>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">Workload Distribution by Application</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={workloadData?.distribution_by_application || []}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                        <XAxis dataKey="label" stroke="#888888" fontSize={10} />
                        <YAxis stroke="#888888" fontSize={10} />
                        <Tooltip />
                        <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* TAB 6: RESOURCE EFFICIENCY & COST */}
          {activeTab === "efficiency_cost" && (
            <div className="space-y-6">
              <div className="p-3 bg-muted/40 border border-border rounded-lg text-xs flex items-center justify-between text-muted-foreground">
                <span>
                  <strong>Notice:</strong> {costData?.disclaimer}
                </span>
                <Badge variant="outline" className="text-[10px]">
                  {costData?.pricing_model_applied}
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Daily Run-Rate</p>
                  <p className="text-xl font-bold">${costData?.daily_estimated_cost.toFixed(2)}</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Monthly Estimated Cost</p>
                  <p className="text-xl font-bold">${costData?.monthly_estimated_cost.toFixed(2)}</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Potential Optimization Savings</p>
                  <p className="text-xl font-bold text-emerald-500">
                    ${efficiencyData?.potential_monthly_savings_usd.toFixed(2)}
                  </p>
                </Card>
              </div>

              {/* Optimization Candidates Table */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">
                    Idle & Underutilized Right-Sizing Candidates
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Instances identified for termination, hibernation, or instance-type downsizing
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border border-border rounded-lg overflow-x-auto text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-muted/50 border-b border-border">
                        <tr>
                          <th className="p-2.5 font-medium text-foreground">Instance ID</th>
                          <th className="p-2.5 font-medium text-foreground">Type</th>
                          <th className="p-2.5 font-medium text-foreground">Service</th>
                          <th className="p-2.5 font-medium text-foreground">Avg CPU</th>
                          <th className="p-2.5 font-medium text-foreground">Avg Mem</th>
                          <th className="p-2.5 font-medium text-foreground">Category</th>
                          <th className="p-2.5 font-medium text-foreground">Recommendation</th>
                          <th className="p-2.5 font-medium text-foreground text-right">Potential Savings</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {efficiencyData?.candidates && efficiencyData.candidates.length > 0 ? (
                          efficiencyData.candidates.map((cand, idx) => (
                            <tr key={idx} className="hover:bg-accent/30 transition-colors">
                              <td className="p-2.5 font-mono text-foreground">{cand.instance_id}</td>
                              <td className="p-2.5 text-muted-foreground font-mono">{cand.instance_type}</td>
                              <td className="p-2.5 text-muted-foreground">{cand.service_name || "N/A"}</td>
                              <td className="p-2.5 font-mono">{cand.avg_cpu.toFixed(1)}%</td>
                              <td className="p-2.5 font-mono">{cand.avg_memory.toFixed(1)}%</td>
                              <td className="p-2.5">
                                <Badge
                                  variant={
                                    cand.category === "IDLE"
                                      ? "destructive"
                                      : cand.category === "UNDERUTILIZED"
                                      ? "secondary"
                                      : "outline"
                                  }
                                  className="text-[10px]"
                                >
                                  {cand.category}
                                </Badge>
                              </td>
                              <td className="p-2.5 text-muted-foreground">{cand.recommendation}</td>
                              <td className="p-2.5 text-right font-semibold text-emerald-500">
                                ${cand.potential_monthly_saving_usd.toFixed(2)}/mo
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={8} className="p-4 text-center text-muted-foreground">
                              No idle or underutilized instances detected. Fleet is operating optimally.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* TAB 7: STATISTICAL ANOMALY DETECTION */}
          {activeTab === "anomalies" && (
            <div className="space-y-6">
              <div className="grid grid-cols-4 gap-4">
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Total Anomalies</p>
                  <p className="text-xl font-bold">{anomalyData?.total_anomalies || 0}</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Critical Severity</p>
                  <p className="text-xl font-bold text-red-500">{anomalyData?.critical_count || 0}</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">High Severity</p>
                  <p className="text-xl font-bold text-amber-500">{anomalyData?.high_count || 0}</p>
                </Card>
                <Card className="p-4 text-center">
                  <p className="text-xs text-muted-foreground">Detection Algorithms</p>
                  <p className="text-sm font-semibold text-foreground mt-1">Z-Score & IQR</p>
                </Card>
              </div>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">Detected Telemetry Anomalies</CardTitle>
                  <CardDescription className="text-xs">
                    Non-ML statistical deviation detections based on 3-sigma thresholds and interquartile range upper fences
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="border border-border rounded-lg overflow-x-auto text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-muted/50 border-b border-border">
                        <tr>
                          <th className="p-2.5 font-medium text-foreground">Timestamp</th>
                          <th className="p-2.5 font-medium text-foreground">Instance</th>
                          <th className="p-2.5 font-medium text-foreground">Metric</th>
                          <th className="p-2.5 font-medium text-foreground">Observed</th>
                          <th className="p-2.5 font-medium text-foreground">Expected Fence</th>
                          <th className="p-2.5 font-medium text-foreground">Method</th>
                          <th className="p-2.5 font-medium text-foreground">Severity</th>
                          <th className="p-2.5 font-medium text-foreground">Explanation</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {anomalyData?.events && anomalyData.events.length > 0 ? (
                          anomalyData.events.map((anom, idx) => (
                            <tr key={idx} className="hover:bg-accent/30 transition-colors">
                              <td className="p-2.5 font-mono whitespace-nowrap text-muted-foreground">
                                {new Date(anom.timestamp).toLocaleString()}
                              </td>
                              <td className="p-2.5 font-mono text-foreground whitespace-nowrap">
                                {anom.resource_id}
                              </td>
                              <td className="p-2.5 whitespace-nowrap font-medium text-foreground">
                                {anom.metric_name}
                              </td>
                              <td className="p-2.5 font-mono font-semibold text-foreground">
                                {anom.observed_value.toFixed(2)}
                              </td>
                              <td className="p-2.5 font-mono text-muted-foreground whitespace-nowrap">
                                {anom.expected_range_min !== undefined && anom.expected_range_max !== undefined
                                  ? `[${anom.expected_range_min.toFixed(1)}, ${anom.expected_range_max.toFixed(1)}]`
                                  : "N/A"}
                              </td>
                              <td className="p-2.5">
                                <Badge variant="outline" className="text-[10px] font-mono">
                                  {anom.detection_method}
                                </Badge>
                              </td>
                              <td className="p-2.5">
                                <Badge
                                  variant={
                                    anom.severity === "CRITICAL"
                                      ? "destructive"
                                      : anom.severity === "HIGH"
                                      ? "secondary"
                                      : "outline"
                                  }
                                  className="text-[10px]"
                                >
                                  {anom.severity}
                                </Badge>
                              </td>
                              <td className="p-2.5 text-muted-foreground">{anom.explanation}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={8} className="p-4 text-center text-muted-foreground">
                              No statistical anomalies detected in this telemetry slice.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
