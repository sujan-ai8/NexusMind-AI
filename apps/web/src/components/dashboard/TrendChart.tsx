import React from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DemoBadge } from "@/components/common/DemoBadge";
import { TimeSeriesPoint } from "@/types";

interface TrendChartProps {
  data: TimeSeriesPoint[];
}

export function TrendChart({ data }: TrendChartProps) {
  return (
    <Card className="col-span-full lg:col-span-2">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle>Compute Telemetry Trend</CardTitle>
          <CardDescription>24-hour CPU vs Memory utilization profile</CardDescription>
        </div>
        <DemoBadge />
      </CardHeader>
      <CardContent>
        <div className="h-[280px] w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
              <XAxis dataKey="timestamp" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} domain={[0, 100]} unit="%" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  borderColor: "hsl(var(--border))",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "hsl(var(--card-foreground))",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
              <Area
                type="monotone"
                dataKey="cpu_utilization"
                name="CPU Utilization (%)"
                stroke="#3B82F6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#cpuGradient)"
              />
              <Area
                type="monotone"
                dataKey="memory_utilization"
                name="Memory Utilization (%)"
                stroke="#10B981"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#memGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

