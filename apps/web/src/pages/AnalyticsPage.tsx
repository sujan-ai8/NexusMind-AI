import React, { useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Cpu,
  DollarSign,
  Download,
  HardDrive,
  Layers,
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
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { DemoBadge } from "@/components/common/DemoBadge";

export function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "workload" | "cpu" | "memory" | "cost" | "anomaly"
  >("overview");

  // Telemetry samples clearly flagged as demo data
  const hourlyData = [
    { time: "00:00", cpu: 32, memory: 58, cost: 42, reqs: 85, anomalies: 0 },
    { time: "03:00", cpu: 28, memory: 56, cost: 38, reqs: 70, anomalies: 0 },
    { time: "06:00", cpu: 45, memory: 64, cost: 49, reqs: 110, anomalies: 0 },
    { time: "09:00", cpu: 78, memory: 82, cost: 84, reqs: 240, anomalies: 1 },
    { time: "12:00", cpu: 84, memory: 88, cost: 92, reqs: 280, anomalies: 2 },
    { time: "15:00", cpu: 68, memory: 76, cost: 72, reqs: 190, anomalies: 0 },
    { time: "18:00", cpu: 52, memory: 69, cost: 58, reqs: 140, anomalies: 0 },
    { time: "21:00", cpu: 40, memory: 62, cost: 46, reqs: 105, anomalies: 0 },
  ];

  const anomalyPoints = [
    { cpu: 89, memory: 94, z: 200, label: "Spike A (09:15 UTC)" },
    { cpu: 94, memory: 91, z: 300, label: "Spike B (12:40 UTC)" },
    { cpu: 35, memory: 40, z: 50, label: "Baseline" },
    { cpu: 42, memory: 55, z: 80, label: "Nominal" },
    { cpu: 58, memory: 65, z: 100, label: "Nominal" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Big Data Workload Analytics"
        description="Multi-dimensional statistical profiling, resource saturation curves, and cluster anomaly inspection."
        badge={<DemoBadge />}
      >
        <Button variant="outline" size="sm" className="text-xs">
          <Download className="w-3.5 h-3.5 mr-1.5" />
          Export Analysis CSV
        </Button>
      </PageHeader>

      {/* Analytics Tabs */}
      <div className="flex items-center gap-1.5 border-b border-border overflow-x-auto pb-2 text-xs">
        {[
          { id: "overview", label: "Analytics Overview", icon: BarChart3 },
          { id: "workload", label: "Workload Volume", icon: Activity },
          { id: "cpu", label: "CPU Analysis", icon: Cpu },
          { id: "memory", label: "Memory Analysis", icon: HardDrive },
          { id: "cost", label: "Cloud Cost Analysis", icon: DollarSign },
          { id: "anomaly", label: "Anomaly Detection", icon: AlertTriangle },
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
            </button>
          );
        })}
      </div>

      {/* Tab 1: Overview */}
      {activeTab === "overview" && (
        <div className="space-y-6 animate-in fade-in-50">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">p99 CPU Saturation</span>
              <div className="text-2xl font-bold text-foreground mt-1">84.2%</div>
              <span className="text-[10px] text-amber-500 font-medium">Headroom safety margin: 15.8%</span>
            </Card>
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">p95 Memory Usage</span>
              <div className="text-2xl font-bold text-foreground mt-1">88.0%</div>
              <span className="text-[10px] text-blue-500 font-medium">Within nominal cluster limits</span>
            </Card>
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">Cluster Anomaly Events</span>
              <div className="text-2xl font-bold text-foreground mt-1">3 Detected</div>
              <span className="text-[10px] text-destructive font-medium">Investigate peak spikes</span>
            </Card>
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">Simulated Daily Spend</span>
              <div className="text-2xl font-bold text-foreground mt-1">$41.60</div>
              <span className="text-[10px] text-emerald-500 font-medium">↓ $6.40 vs standard baseline</span>
            </Card>
          </div>

          <Card className="border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>Composite Cluster Telemetry Profile</CardTitle>
                <CardDescription>Correlation between workload volume, compute demand, and spend</CardDescription>
              </div>
              <DemoBadge />
            </CardHeader>
            <CardContent>
              <div className="h-[320px] w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={hourlyData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
                    <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                    <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
                    <Area type="monotone" dataKey="cpu" name="CPU (%)" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.2} />
                    <Area type="monotone" dataKey="memory" name="Memory (%)" stroke="#10B981" fill="#10B981" fillOpacity={0.2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab 2: Workload */}
      {activeTab === "workload" && (
        <Card className="border-border animate-in fade-in-50">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Request Volume Throughput</CardTitle>
              <CardDescription>Thousands of incoming HTTP microservice transactions per minute</CardDescription>
            </div>
            <DemoBadge />
          </CardHeader>
          <CardContent>
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
                  <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} unit="k" />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                  <Bar dataKey="reqs" name="Workload Throughput (k req/min)" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 3: CPU */}
      {activeTab === "cpu" && (
        <Card className="border-border animate-in fade-in-50">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>vCPU Core Saturation Curve</CardTitle>
              <CardDescription>Multi-node core distribution across provisioned nodes</CardDescription>
            </div>
            <DemoBadge />
          </CardHeader>
          <CardContent>
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
                  <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} unit="%" domain={[0, 100]} />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                  <Area type="monotone" dataKey="cpu" name="CPU Core Saturation" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 4: Memory */}
      {activeTab === "memory" && (
        <Card className="border-border animate-in fade-in-50">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Memory Resident Set Size (RSS)</CardTitle>
              <CardDescription>Heap allocation vs cached buffer memory utilization</CardDescription>
            </div>
            <DemoBadge />
          </CardHeader>
          <CardContent>
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
                  <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} unit="%" domain={[0, 100]} />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                  <Area type="monotone" dataKey="memory" name="RAM Allocation (%)" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 5: Cost */}
      {activeTab === "cost" && (
        <Card className="border-border animate-in fade-in-50">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Hourly Cloud Run Rate Breakdown</CardTitle>
              <CardDescription>Simulated compute instance costs per 3-hour billing bracket</CardDescription>
            </div>
            <DemoBadge />
          </CardHeader>
          <CardContent>
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
                  <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} unit="$" />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                  <Bar dataKey="cost" name="Estimated Cost ($)" fill="#EC4899" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tab 6: Anomaly */}
      {activeTab === "anomaly" && (
        <Card className="border-border animate-in fade-in-50">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Cluster Telemetry Anomaly Scatter Plot</CardTitle>
              <CardDescription>Isolation Forest anomaly scores plotted across CPU vs Memory space</CardDescription>
            </div>
            <DemoBadge />
          </CardHeader>
          <CardContent>
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid stroke="hsl(var(--border))" opacity={0.6} />
                  <XAxis type="number" dataKey="cpu" name="CPU (%)" unit="%" stroke="hsl(var(--muted-foreground))" domain={[0, 100]} />
                  <YAxis type="number" dataKey="memory" name="Memory (%)" unit="%" stroke="hsl(var(--muted-foreground))" domain={[0, 100]} />
                  <ZAxis type="number" dataKey="z" range={[60, 400]} />
                  <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                  <Scatter name="Telemetry Cluster Points" data={anomalyPoints} fill="#EF4444" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

