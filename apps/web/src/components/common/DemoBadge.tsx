import React from "react";
import { AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function DemoBadge({ className }: { className?: string }) {
  return (
    <Badge
      variant="demo"
      className={`gap-1 font-semibold border border-amber-500/30 text-amber-500 bg-amber-500/10 ${className || ""}`}
      title="Simulated preview data for Phase 1 architectural evaluation. Not connected to live cloud infrastructure."
    >
      <AlertCircle className="w-3 h-3" />
      DEMO DATA
    </Badge>
  );
}

