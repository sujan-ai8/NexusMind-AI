import React from "react";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DemoBadge } from "@/components/common/DemoBadge";
import { CategoryDistributionPoint } from "@/types";

export function WorkloadDistributionChart({ data }: { data: CategoryDistributionPoint[] }) {
  const COLORS = ["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"];

  return (
    <Card className="col-span-full md:col-span-1">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Workload Distribution</CardTitle>
          <CardDescription>Infrastructure resource allocation</CardDescription>
        </div>
        <DemoBadge />
      </CardHeader>
      <CardContent>
        <div className="h-[260px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  borderColor: "hsl(var(--border))",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "hsl(var(--card-foreground))",
                }}
                formatter={(val: any) => [`${val}%`, "Share"]}
              />
              <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "5px" }} />
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

