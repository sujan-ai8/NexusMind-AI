import React, { useState } from "react";
import {
  Activity,
  ArrowUpRight,
  CheckCircle2,
  Cpu,
  Layers,
  Play,
  Settings2,
  Sparkles,
} from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { DemoBadge } from "@/components/common/DemoBadge";

export function OptimizationPage() {
  const [algorithm, setAlgorithm] = useState("PPO");

  const rewardConvergence = [
    { episode: 0, reward: -45.2, baselineCost: 100, agentCost: 100 },
    { episode: 200, reward: -28.4, baselineCost: 100, agentCost: 92 },
    { episode: 400, reward: -15.1, baselineCost: 100, agentCost: 84 },
    { episode: 600, reward: -6.8, baselineCost: 100, agentCost: 76 },
    { episode: 800, reward: 8.4, baselineCost: 100, agentCost: 71 },
    { episode: 1000, reward: 14.2, baselineCost: 100, agentCost: 68 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reinforcement Learning Resource Optimization"
        description="Autonomous cluster autoscaling policies, reward convergence curves, and SLA compliance trade-offs."
        badge={<DemoBadge />}
      >
        <Button variant="primary" size="sm">
          <Play className="w-3.5 h-3.5 mr-1.5" />
          Run Simulation Experiment
        </Button>
      </PageHeader>

      {/* KPI Optimization Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 border-border">
          <span className="text-xs text-muted-foreground">Demonstrated Cost Reduction</span>
          <div className="text-2xl font-bold text-emerald-500 mt-1">32.0%</div>
          <span className="text-[10px] text-muted-foreground">vs. Static Peak Over-provisioning</span>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs text-muted-foreground">SLA Violation Rate</span>
          <div className="text-2xl font-bold text-foreground mt-1">0.04%</div>
          <span className="text-[10px] text-emerald-500 font-semibold">Strict 99.9% availability target met</span>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs text-muted-foreground">Policy Algorithm</span>
          <div className="text-2xl font-bold text-primary mt-1">PPO (Clipped)</div>
          <span className="text-[10px] text-muted-foreground">Actor-Critic Policy Gradient</span>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs text-muted-foreground">Simulated Cloud Gym Steps</span>
          <div className="text-2xl font-bold text-foreground mt-1">100,000</div>
          <span className="text-[10px] text-muted-foreground">Trained on 30-day cluster trace</span>
        </Card>
      </div>

      {/* Reward Convergence Chart */}
      <Card className="border-border">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle>Reinforcement Learning Policy Convergence</CardTitle>
            <CardDescription>Reward trajectory and compute cost reduction over simulation episodes</CardDescription>
          </div>
          <DemoBadge />
        </CardHeader>
        <CardContent>
          <div className="h-[320px] w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={rewardConvergence}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
                <XAxis dataKey="episode" stroke="hsl(var(--muted-foreground))" fontSize={11} unit=" eps" />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", borderColor: "hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
                <Line type="monotone" dataKey="reward" name="Cumulative Reward Score" stroke="#8B5CF6" strokeWidth={2.5} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="agentCost" name="Normalized Cluster Cost" stroke="#10B981" strokeWidth={2} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

