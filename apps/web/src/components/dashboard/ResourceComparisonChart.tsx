import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DemoBadge } from "@/components/common/DemoBadge";
import { ResourceComparisonPoint } from "@/types";

export function ResourceComparisonChart({ data }: { data: ResourceComparisonPoint[] }) {
  return (
    <Card className="col-span-full md:col-span-2">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Resource Allocation vs. Utilization</CardTitle>
          <CardDescription>Over-provisioning vs. RL recommended optimal sizing</CardDescription>
        </div>
        <DemoBadge />
      </CardHeader>
      <CardContent>
        <div className="h-[260px] w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
              <XAxis dataKey="resource" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  borderColor: "hsl(var(--border))",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "hsl(var(--card-foreground))",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "5px" }} />
              <Bar dataKey="allocated" name="Current Allocated" fill="#64748B" radius={[3, 3, 0, 0]} />
              <Bar dataKey="utilized" name="Actual Peak Utilized" fill="#3B82F6" radius={[3, 3, 0, 0]} />
              <Bar dataKey="optimized" name="RL Optimized Target" fill="#10B981" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

