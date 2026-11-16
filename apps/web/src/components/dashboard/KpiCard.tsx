import React from "react";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { DemoBadge } from "@/components/common/DemoBadge";
import { KpiMetric } from "@/types";
import { cn } from "@/lib/utils";

export function KpiCard({ metric, icon: Icon }: { metric: KpiMetric; icon?: React.ElementType }) {
  const isPositive = metric.change_percentage > 0;
  const isNegative = metric.change_percentage < 0;

  return (
    <Card className="hover:border-primary/40 transition-all shadow-sm">
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted-foreground">{metric.label}</span>
          <div className="flex items-center gap-1.5">
            {metric.is_demo_data && <DemoBadge />}
            {Icon && (
              <div className="p-1.5 rounded-md bg-primary/10 text-primary">
                <Icon className="w-4 h-4" />
              </div>
            )}
          </div>
        </div>

        <div className="mt-3 flex items-baseline justify-between">
          <div className="text-2xl font-bold tracking-tight text-foreground">
            {metric.value}
            {metric.unit && (
              <span className="ml-1 text-xs font-normal text-muted-foreground">{metric.unit}</span>
            )}
          </div>

          <div
            className={cn(
              "flex items-center text-xs font-semibold",
              metric.change_type === "decrease" && metric.key.includes("cost")
                ? "text-emerald-500"
                : isNegative
                ? "text-emerald-500"
                : isPositive
                ? "text-blue-500"
                : "text-muted-foreground"
            )}
          >
            {isPositive && <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />}
            {isNegative && <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
            {!isPositive && !isNegative && <Minus className="w-3.5 h-3.5 mr-0.5" />}
            {Math.abs(metric.change_percentage)}%
          </div>
        </div>

        <p className="mt-2 text-[11px] text-muted-foreground/80">
          vs. previous 24h baseline
        </p>
      </CardContent>
    </Card>
  );
}

