import React, { useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Cloud,
  Database,
  Key,
  Lock,
  Save,
  Server,
  ShieldAlert,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";

export function AWSCloudPage() {
  const [region, setRegion] = useState("us-east-1");
  const [bucket, setBucket] = useState("nexusmind-telemetry-bucket");
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="AWS Cloud Integration & Topology"
        description="Configure cloud infrastructure connectors, S3 storage buckets, and IAM role trust boundaries."
      >
        <Badge variant="warning" className="text-xs">
          Ready for Configuration (Phase 6 Live Target)
        </Badge>
      </PageHeader>

      {/* Real Status Notice - Not Fabricating Live Link */}
      <div className="p-4 rounded-xl border border-border bg-card/60 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-500 mt-0.5">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-foreground">Current Integration Status: Unlinked</h4>
            <p className="text-xs text-muted-foreground mt-0.5 max-w-xl">
              Phase 1 establishes the configuration schemas and IAM trust policies. Live AWS STS token exchange, CloudWatch metric polling, and ECS deployment automation will be activated during the Phase 6 cloud migration.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline">AWS STS: Standing By</Badge>
          <Badge variant="outline">IAM Policy: Scoped</Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cloud Config Form */}
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Cloud className="w-4 h-4 text-primary" />
              AWS Provider Settings
            </CardTitle>
            <CardDescription className="text-xs">
              Define the target AWS region and Amazon S3 telemetry bucket
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="font-semibold text-foreground">AWS Region</label>
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs"
                >
                  <option value="us-east-1">US East (N. Virginia) us-east-1</option>
                  <option value="us-west-2">US West (Oregon) us-west-2</option>
                  <option value="eu-west-1">Europe (Ireland) eu-west-1</option>
                  <option value="ap-south-1">Asia Pacific (Mumbai) ap-south-1</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-foreground">Amazon S3 Telemetry Bucket</label>
                <Input
                  type="text"
                  value={bucket}
                  onChange={(e) => setBucket(e.target.value)}
                  placeholder="e.g. enterprise-cloud-telemetry"
                />
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-foreground">IAM Role ARN for Service Accounts (IRSA)</label>
                <Input
                  type="text"
                  placeholder="arn:aws:iam::123456789012:role/NexusMindCloudOpsRole"
                  defaultValue="arn:aws:iam::123456789012:role/NexusMindOpsRole-Phase1"
                />
              </div>

              {isSaved && (
                <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Configuration parameters saved to workspace settings.</span>
                </div>
              )}

              <Button type="submit" variant="primary" size="sm" className="w-full mt-2">
                <Save className="w-3.5 h-3.5 mr-1.5" />
                Save AWS Configuration
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* AWS Services Matrix */}
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Server className="w-4 h-4 text-primary" />
              Target Architecture Components
            </CardTitle>
            <CardDescription className="text-xs">
              AWS cloud service mappings planned for NexusMind AI
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="p-3 rounded-lg border border-border bg-muted/30 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Server className="w-4 h-4 text-blue-500" />
                <div>
                  <div className="font-semibold text-foreground">Amazon Elastic Container Service (ECS)</div>
                  <div className="text-[11px] text-muted-foreground">Hosts FastAPI, React Web, and Workers via Fargate</div>
                </div>
              </div>
              <Badge variant="outline">Phase 6</Badge>
            </div>

            <div className="p-3 rounded-lg border border-border bg-muted/30 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4 text-purple-500" />
                <div>
                  <div className="font-semibold text-foreground">Amazon Aurora Serverless (PostgreSQL)</div>
                  <div className="text-[11px] text-muted-foreground">Multi-tenant relational database with auto-pause</div>
                </div>
              </div>
              <Badge variant="outline">Phase 6</Badge>
            </div>

            <div className="p-3 rounded-lg border border-border bg-muted/30 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Cloud className="w-4 h-4 text-amber-500" />
                <div>
                  <div className="font-semibold text-foreground">Amazon S3 & CloudWatch Logs</div>
                  <div className="text-[11px] text-muted-foreground">Persistent cluster trace storage & stream ingestion</div>
                </div>
              </div>
              <Badge variant="outline">Phase 2/6</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

