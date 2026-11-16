import React from "react";
import { Clock, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ActivityItem } from "@/types";
import { formatDate } from "@/lib/utils";

export function ActivityFeed({ activities }: { activities: ActivityItem[] }) {
  return (
    <Card className="col-span-full lg:col-span-2">
      <CardHeader className="pb-3">
        <CardTitle>Recent Workspace Activity</CardTitle>
        <CardDescription>Audited operational events and telemetry actions</CardDescription>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-xs text-muted-foreground">
            No recent activity recorded for this workspace.
          </div>
        ) : (
          <div className="divide-y divide-border">
            {activities.map((act) => (
              <div key={act.id} className="py-2.5 flex items-start justify-between gap-3 text-xs">
                <div className="flex items-start gap-2.5 min-w-0">
                  <div className="p-1 rounded-full bg-primary/10 text-primary mt-0.5">
                    <Clock className="w-3.5 h-3.5" />
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="font-semibold text-foreground truncate">
                      {act.action.replace(/_/g, " ")}
                    </span>
                    <span className="text-[11px] text-muted-foreground truncate">
                      User: {act.user_email} • Resource: {act.resource_type}
                    </span>
                  </div>
                </div>
                <span className="text-[10px] text-muted-foreground whitespace-nowrap font-mono">
                  {formatDate(act.timestamp)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

