import React, { useState } from "react";
import {
  Download,
  Eye,
  FileCheck,
  FileText,
  Plus,
  Printer,
  Share2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";

export function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<any | null>(null);

  const reports = [
    {
      id: "rep-1",
      title: "Executive Cloud Efficiency & Cost Audit (Q4)",
      type: "Executive Summary",
      status: "GENERATED",
      author: "Platform Automation",
      date: "2026-10-31",
      savings: "$4,280 / mo",
      summary:
        "Comprehensive infrastructure review identifying 32% compute over-provisioning across benchmarked EC2 worker nodes. Recommends autoscaling threshold adjustments.",
    },
    {
      id: "rep-2",
      title: "Cluster Telemetry Workload Anomaly Report",
      type: "Technical Audit",
      status: "GENERATED",
      author: "Isolation Forest Engine",
      date: "2026-10-28",
      savings: "SLA Risk Mitigated",
      summary:
        "Identified three transient CPU saturation events exceeding 90% utilization between 09:00 and 12:00 UTC. Root cause attributed to batch ETL task overlapping with peak customer traffic.",
    },
    {
      id: "rep-3",
      title: "Reinforcement Learning Policy Benchmark",
      type: "Algorithm Performance",
      status: "ARCHIVED",
      author: "RL Optimization Engine",
      date: "2026-10-25",
      savings: "28.5% Compute Savings",
      summary:
        "Evaluation of PPO policy agent versus standard threshold-based Kubernetes Horizontal Pod Autoscaler (HPA).",
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Executive & Technical Reports"
        description="Audit documents, cloud efficiency summaries, and automated architectural insights."
      >
        <Button variant="primary" size="sm">
          <Plus className="w-3.5 h-3.5 mr-1.5" />
          Generate New Report
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {reports.map((rep) => (
          <Card key={rep.id} className="border-border hover:border-primary/40 transition-all flex flex-col justify-between">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between mb-2">
                <Badge variant="outline" className="text-[10px] font-mono">
                  {rep.type}
                </Badge>
                <Badge variant="success">{rep.status}</Badge>
              </div>
              <CardTitle className="text-sm font-bold text-foreground leading-snug">
                {rep.title}
              </CardTitle>
              <CardDescription className="text-xs mt-1">
                Generated {rep.date} by {rep.author}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4 pt-0">
              <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                {rep.summary}
              </p>

              <div className="p-2.5 rounded-lg bg-muted/40 border border-border flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Impact:</span>
                <span className="font-bold text-emerald-500">{rep.savings}</span>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-border">
                <Button
                  onClick={() => setSelectedReport(rep)}
                  variant="outline"
                  size="sm"
                  className="flex-1 text-xs"
                >
                  <Eye className="w-3.5 h-3.5 mr-1" /> View
                </Button>
                <Button
                  onClick={() => alert(`Downloading ${rep.title} (PDF export will be provided in Phase 6)`)}
                  variant="ghost"
                  size="sm"
                  className="text-xs"
                  title="Export Report"
                >
                  <Download className="w-3.5 h-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Report Modal */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl rounded-xl border border-border bg-card p-6 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-emerald-500" />
                {selectedReport.title}
              </h3>
              <button onClick={() => setSelectedReport(null)} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </div>
            <div className="py-4 space-y-3 text-xs text-muted-foreground leading-relaxed">
              <div className="flex justify-between py-1 border-b border-border">
                <span>Classification:</span>
                <strong className="text-foreground">{selectedReport.type}</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-border">
                <span>Date:</span>
                <strong className="text-foreground">{selectedReport.date}</strong>
              </div>
              <div className="flex justify-between py-1 border-b border-border">
                <span>Estimated Impact:</span>
                <strong className="text-emerald-500">{selectedReport.savings}</strong>
              </div>
              <div className="pt-2">
                <span className="font-semibold text-foreground block mb-1">Executive Summary:</span>
                <p className="p-3 rounded-lg bg-muted/40 border border-border text-foreground">
                  {selectedReport.summary}
                </p>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-border">
              <Button onClick={() => setSelectedReport(null)} variant="primary" size="sm">
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

