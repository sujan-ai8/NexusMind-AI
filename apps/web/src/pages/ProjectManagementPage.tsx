import React, { useState } from "react";
import {
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Clock,
  FolderKanban,
  Kanban,
  Layers,
  Plus,
  ShieldAlert,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";

export function ProjectManagementPage() {
  const [activeTab, setActiveTab] = useState<"overview" | "sprints" | "tasks" | "risks">("overview");

  const tasks = [
    {
      id: "NEXUS-101",
      title: "Scaffold Full-Stack Monorepo & Dependencies",
      sprint: "Sprint 1",
      status: "DONE",
      priority: "CRITICAL",
      points: 5,
    },
    {
      id: "NEXUS-102",
      title: "Implement PostgreSQL Database Models & Alembic Migrations",
      sprint: "Sprint 1",
      status: "DONE",
      priority: "CRITICAL",
      points: 8,
    },
    {
      id: "NEXUS-103",
      title: "Develop JWT Authentication & RBAC Middleware",
      sprint: "Sprint 1",
      status: "DONE",
      priority: "HIGH",
      points: 5,
    },
    {
      id: "NEXUS-104",
      title: "Build Responsive React UI & Design System Tokens",
      sprint: "Sprint 2",
      status: "DONE",
      priority: "HIGH",
      points: 8,
    },
    {
      id: "NEXUS-105",
      title: "Telemetric Data Ingestion Engine & S3 Storage Abstraction",
      sprint: "Sprint 3",
      status: "BACKLOG",
      priority: "HIGH",
      points: 8,
    },
    {
      id: "NEXUS-106",
      title: "Big Data Workload Statistical Profiler & Anomaly Clustering",
      sprint: "Sprint 5",
      status: "BACKLOG",
      priority: "MEDIUM",
      points: 5,
    },
  ];

  const risks = [
    {
      id: "RSK-01",
      title: "High telemetry data volume memory saturation",
      severity: "MEDIUM",
      impact: "High",
      mitigation: "Chunked streaming pipelines & Celery async workers",
    },
    {
      id: "RSK-02",
      title: "Cross-tenant data exposure across workspaces",
      severity: "HIGH",
      impact: "Critical",
      mitigation: "Strict workspace_id foreign-key filtering in all ORM queries",
    },
    {
      id: "RSK-03",
      title: "RL autoscaling policy convergence instability",
      severity: "MEDIUM",
      impact: "Moderate",
      mitigation: "Utilize PPO with reward normalization and bounded actions",
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Software Project Management (SPM)"
        description="Agile project governance, sprint execution, Kanban task tracking, and risk registers."
      >
        <Badge variant="secondary" className="text-xs">
          MCA Final Year Tracking
        </Badge>
      </PageHeader>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-2 text-xs">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "overview" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <FolderKanban className="w-3.5 h-3.5" /> Project Overview
        </button>
        <button
          onClick={() => setActiveTab("sprints")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "sprints" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <Calendar className="w-3.5 h-3.5" /> Sprints & Milestones
        </button>
        <button
          onClick={() => setActiveTab("tasks")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "tasks" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <Kanban className="w-3.5 h-3.5" /> Task Board
        </button>
        <button
          onClick={() => setActiveTab("risks")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "risks" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" /> Risk Register
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="space-y-6 animate-in fade-in-50">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">Current Phase</span>
              <div className="text-xl font-bold text-primary mt-1">Phase 1 Active</div>
              <span className="text-[10px] text-muted-foreground">Foundation, Architecture & UI</span>
            </Card>
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">Sprint Progress</span>
              <div className="text-xl font-bold text-foreground mt-1">Sprint 1 & 2 Completed</div>
              <span className="text-[10px] text-emerald-500 font-semibold">100% of Phase 1 tasks closed</span>
            </Card>
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">Story Points Velocity</span>
              <div className="text-xl font-bold text-foreground mt-1">26 Points</div>
              <span className="text-[10px] text-muted-foreground">Across foundation backlog</span>
            </Card>
            <Card className="p-4 border-border">
              <span className="text-xs text-muted-foreground">Quality Gate Status</span>
              <div className="text-xl font-bold text-emerald-500 mt-1">PASSED</div>
              <span className="text-[10px] text-muted-foreground">Pytest & Vitest verified</span>
            </Card>
          </div>

          <Card className="border-border p-6 space-y-4">
            <h3 className="text-base font-bold text-foreground">Phase 1 Completion Checklist</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Monorepo scaffold with apps/web, apps/api, apps/worker
              </div>
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> PostgreSQL 13 schema models & Alembic migrations
              </div>
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> JWT auth with bcrypt password hashing & RBAC
              </div>
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> 4-Step workspace onboarding wizard
              </div>
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Interactive Recharts telemetry dashboards with DEMO labels
              </div>
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> 12 complete SPM project management deliverables
              </div>
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Docker Compose configuration for web, api, and postgres
              </div>
              <div className="flex items-center gap-2 text-foreground font-medium">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Automated Pytest backend test suite executing clean
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Sprints Tab */}
      {activeTab === "sprints" && (
        <Card className="border-border p-6 space-y-4 animate-in fade-in-50">
          <h3 className="text-base font-bold text-foreground">Agile Sprint Cadence</h3>
          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-lg border border-primary/30 bg-primary/5 flex items-center justify-between">
              <div>
                <span className="font-bold text-foreground">Sprint 1 & 2: Enterprise Foundation & Architecture</span>
                <p className="text-muted-foreground text-[11px] mt-0.5">Scaffold, database models, auth, design system, dashboard</p>
              </div>
              <Badge variant="success">Completed</Badge>
            </div>
            <div className="p-3.5 rounded-lg border border-border bg-card flex items-center justify-between">
              <div>
                <span className="font-bold text-foreground">Sprint 3 & 4: Telemetric Ingestion & Cloud Storage</span>
                <p className="text-muted-foreground text-[11px] mt-0.5">S3 storage adapter, synthetic workload generator, schema normalizer</p>
              </div>
              <Badge variant="outline">Phase 2 Planned</Badge>
            </div>
            <div className="p-3.5 rounded-lg border border-border bg-card flex items-center justify-between">
              <div>
                <span className="font-bold text-foreground">Sprint 5 & 6: Big Data Analytics & Anomaly Detection</span>
                <p className="text-muted-foreground text-[11px] mt-0.5">Statistical profiling, Isolation Forest, saturation metrics</p>
              </div>
              <Badge variant="outline">Phase 3 Planned</Badge>
            </div>
          </div>
        </Card>
      )}

      {/* Tasks Tab */}
      {activeTab === "tasks" && (
        <Card className="border-border overflow-hidden animate-in fade-in-50">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-muted/40 font-semibold text-muted-foreground">
                  <th className="p-3.5">Key</th>
                  <th className="p-3.5">Task Description</th>
                  <th className="p-3.5">Sprint</th>
                  <th className="p-3.5">Priority</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Story Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {tasks.map((t) => (
                  <tr key={t.id} className="hover:bg-muted/30 transition-colors">
                    <td className="p-3.5 font-mono font-bold text-primary">{t.id}</td>
                    <td className="p-3.5 font-medium text-foreground">{t.title}</td>
                    <td className="p-3.5 text-muted-foreground">{t.sprint}</td>
                    <td className="p-3.5">
                      <span className={`font-semibold ${t.priority === "CRITICAL" ? "text-destructive" : "text-amber-500"}`}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <Badge variant={t.status === "DONE" ? "success" : "secondary"}>
                        {t.status}
                      </Badge>
                    </td>
                    <td className="p-3.5 text-right font-mono">{t.points} pts</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Risks Tab */}
      {activeTab === "risks" && (
        <Card className="border-border overflow-hidden animate-in fade-in-50">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-muted/40 font-semibold text-muted-foreground">
                  <th className="p-3.5">Risk ID</th>
                  <th className="p-3.5">Description</th>
                  <th className="p-3.5">Severity</th>
                  <th className="p-3.5">Mitigation Strategy</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {risks.map((r) => (
                  <tr key={r.id} className="hover:bg-muted/30 transition-colors">
                    <td className="p-3.5 font-mono font-bold text-destructive">{r.id}</td>
                    <td className="p-3.5 font-medium text-foreground">{r.title}</td>
                    <td className="p-3.5 font-semibold text-amber-500">{r.severity}</td>
                    <td className="p-3.5 text-muted-foreground">{r.mitigation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

