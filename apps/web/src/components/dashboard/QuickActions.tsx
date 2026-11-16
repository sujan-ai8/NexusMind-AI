import React from "react";
import { Link } from "react-router-dom";
import {
  BarChart3,
  Bot,
  BrainCircuit,
  Database,
  FileText,
  Sparkles,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function QuickActions() {
  const actions = [
    {
      title: "Upload Dataset",
      desc: "Register workload telemetry CSV/Parquet",
      href: "/datasets",
      icon: Database,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
    },
    {
      title: "View Analytics",
      desc: "Analyze CPU, Memory, and cloud spend",
      href: "/analytics",
      icon: BarChart3,
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
    },
    {
      title: "Explore ML Models",
      desc: "Workload demand forecasting models",
      href: "/models",
      icon: BrainCircuit,
      color: "text-purple-500",
      bg: "bg-purple-500/10",
    },
    {
      title: "Open AI Copilot",
      desc: "Natural language cloud operations assistant",
      href: "/copilot",
      icon: Bot,
      color: "text-amber-500",
      bg: "bg-amber-500/10",
    },
    {
      title: "View Reports",
      desc: "Audit summaries & cost analysis exports",
      href: "/reports",
      icon: FileText,
      color: "text-indigo-500",
      bg: "bg-indigo-500/10",
    },
  ];

  return (
    <Card className="col-span-full lg:col-span-1">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          Quick Actions
        </CardTitle>
        <CardDescription>Rapid access to core intelligence workflows</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {actions.map((act) => {
            const Icon = act.icon;
            return (
              <Link
                key={act.title}
                to={act.href}
                className="flex items-center gap-3 p-2.5 rounded-lg border border-border bg-card hover:bg-accent hover:border-primary/30 transition-all text-xs group"
              >
                <div className={`p-2 rounded-md ${act.bg} ${act.color} flex-shrink-0 transition-transform group-hover:scale-110`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="font-semibold text-foreground group-hover:text-primary transition-colors">
                    {act.title}
                  </span>
                  <span className="text-[11px] text-muted-foreground truncate">{act.desc}</span>
                </div>
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

