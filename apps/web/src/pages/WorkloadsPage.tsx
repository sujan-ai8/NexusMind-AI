import React from "react";
import { Cpu, HardDrive, Network, Server, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { DemoBadge } from "@/components/common/DemoBadge";

export function WorkloadsPage() {
  const workloads = [
    {
      id: "node-cluster-01",
      name: "Prod-API-Cluster-Alpha",
      instances: 8,
      type: "c6i.2xlarge",
      cpuPct: 48,
      memPct: 64,
      status: "HEALTHY",
      zone: "us-east-1a",
    },
    {
      id: "node-cluster-02",
      name: "Streaming-Telemetry-Ingestion",
      instances: 4,
      type: "m6i.xlarge",
      cpuPct: 72,
      memPct: 81,
      status: "WARNING",
      zone: "us-east-1b",
    },
    {
      id: "node-cluster-03",
      name: "Background-Worker-Fleet",
      instances: 6,
      type: "r6i.xlarge",
      cpuPct: 34,
      memPct: 52,
      status: "HEALTHY",
      zone: "us-east-1c",
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Active Workload Clusters"
        description="Monitor multi-zone cloud compute nodes, containerized microservices, and live allocation curves."
        badge={<DemoBadge />}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {workloads.map((w) => (
          <Card key={w.id} className="border-border hover:border-primary/40 transition-all">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] font-mono text-muted-foreground">{w.zone}</span>
                <Badge variant={w.status === "HEALTHY" ? "success" : "warning"}>
                  {w.status}
                </Badge>
              </div>
              <CardTitle className="text-base font-bold text-foreground">{w.name}</CardTitle>
              <CardDescription className="text-xs font-mono">{w.type} • {w.instances} Nodes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 pt-0 text-xs">
              <div>
                <div className="flex justify-between text-muted-foreground mb-1">
                  <span>CPU Allocation</span>
                  <span className="font-semibold text-foreground">{w.cpuPct}%</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${w.cpuPct}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-muted-foreground mb-1">
                  <span>Memory Allocation</span>
                  <span className="font-semibold text-foreground">{w.memPct}%</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${w.memPct}%` }} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

