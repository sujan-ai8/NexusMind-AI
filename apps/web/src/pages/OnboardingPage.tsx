import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Briefcase,
  CheckCircle2,
  Cloud,
  Layers,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useWorkspace } from "@/contexts/WorkspaceContext";

export function OnboardingPage() {
  const { createWorkspace } = useWorkspace();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [workspaceName, setWorkspaceName] = useState("");
  const [description, setDescription] = useState("");
  const [workspaceType, setWorkspaceType] = useState("ENTERPRISE");
  const [cloudProvider, setCloudProvider] = useState("AWS");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const workspaceTypes = [
    { id: "ENTERPRISE", name: "Enterprise Operations", desc: "Production multi-region cluster telemetry & compliance" },
    { id: "RESEARCH", name: "Research & Benchmarking", desc: "ML model exploration and algorithm training" },
    { id: "STARTUP", name: "Startup / Scaleup", desc: "Agile cloud cost control & fast autoscaling policies" },
    { id: "INDIVIDUAL", name: "Individual / Sandbox", desc: "Development, prototyping, and testing environment" },
  ];

  const cloudProviders = [
    { id: "AWS", name: "Amazon Web Services (AWS)", desc: "EC2, EKS, CloudWatch, S3, RDS Aurora (Recommended)", badge: "Primary" },
    { id: "GCP", name: "Google Cloud Platform (GCP)", desc: "GKE, Compute Engine, Cloud Storage, BigQuery", badge: "Supported" },
    { id: "AZURE", name: "Microsoft Azure", desc: "AKS, Azure VMs, Blob Storage, CosmosDB", badge: "Supported" },
    { id: "HYBRID", name: "Hybrid / Multi-Cloud", desc: "Federated cross-cloud workloads and private datacenters", badge: "Preview" },
  ];

  const handleNext = () => {
    if (step === 1 && !workspaceName.trim()) {
      setError("Please enter a workspace name");
      return;
    }
    setError(null);
    setStep((prev) => Math.min(prev + 1, 4));
  };

  const handleBack = () => {
    setError(null);
    setStep((prev) => Math.max(prev - 1, 1));
  };

  const handleComplete = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await createWorkspace({
        name: workspaceName.trim(),
        description: description.trim() || undefined,
        type: workspaceType,
        cloud_provider: cloudProvider,
      });
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to initialize workspace");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 selection:bg-primary/20 selection:text-primary">
      <div className="w-full max-w-xl space-y-6">
        {/* Brand header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 p-2 rounded-xl bg-primary/10 border border-primary/20 text-primary mb-1">
            <Layers className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Configure Your Intelligence Workspace
          </h1>
          <p className="text-sm text-muted-foreground">
            Set up your organization's environment in 4 simple steps
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-between px-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center gap-2">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  step === i
                    ? "bg-primary text-primary-foreground ring-4 ring-primary/20"
                    : step > i
                    ? "bg-emerald-500 text-white"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {step > i ? <CheckCircle2 className="w-4 h-4" /> : i}
              </div>
              <span className="hidden sm:inline text-xs font-medium text-muted-foreground">
                {i === 1 && "Name"}
                {i === 2 && "Type"}
                {i === 3 && "Cloud"}
                {i === 4 && "Confirm"}
              </span>
              {i < 4 && <div className="hidden sm:block w-8 h-0.5 bg-border mx-1" />}
            </div>
          ))}
        </div>

        {/* Wizard Card */}
        <Card className="border-border shadow-2xl">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>
                {step === 1 && "Step 1: Workspace Name & Details"}
                {step === 2 && "Step 2: Workspace Operating Model"}
                {step === 3 && "Step 3: Preferred Cloud Infrastructure"}
                {step === 4 && "Step 4: Verify & Complete Onboarding"}
              </span>
              <span className="text-xs font-mono font-normal text-muted-foreground">
                Step {step} of 4
              </span>
            </CardTitle>
            <CardDescription className="text-xs">
              {step === 1 && "Choose a clear name representing your cloud project or operational team."}
              {step === 2 && "Select how your organization intends to utilize NexusMind AI."}
              {step === 3 && "Specify your target infrastructure provider for telemetry ingestion."}
              {step === 4 && "Review your workspace parameters before launching the platform."}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4 pt-2">
            {error && (
              <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20 text-xs text-destructive">
                {error}
              </div>
            )}

            {/* Step 1: Name */}
            {step === 1 && (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-foreground">
                    Workspace Name <span className="text-destructive">*</span>
                  </label>
                  <Input
                    type="text"
                    placeholder="e.g. Cloud Operations Alpha"
                    value={workspaceName}
                    onChange={(e) => setWorkspaceName(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-foreground">
                    Description <span className="text-muted-foreground font-normal">(Optional)</span>
                  </label>
                  <Input
                    type="text"
                    placeholder="e.g. Production microservice telemetry & autoscaling"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Step 2: Workspace Type */}
            {step === 2 && (
              <div className="space-y-2">
                {workspaceTypes.map((t) => (
                  <div
                    key={t.id}
                    onClick={() => setWorkspaceType(t.id)}
                    className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                      workspaceType === t.id
                        ? "border-primary bg-primary/5 text-foreground ring-1 ring-primary"
                        : "border-border hover:bg-accent text-muted-foreground"
                    }`}
                  >
                    <Briefcase className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-foreground">{t.name}</span>
                      <span className="text-[11px] text-muted-foreground">{t.desc}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Step 3: Cloud Provider */}
            {step === 3 && (
              <div className="space-y-2">
                {cloudProviders.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => setCloudProvider(c.id)}
                    className={`flex items-start justify-between gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                      cloudProvider === c.id
                        ? "border-primary bg-primary/5 text-foreground ring-1 ring-primary"
                        : "border-border hover:bg-accent text-muted-foreground"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <Cloud className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                      <div className="flex flex-col">
                        <span className="text-xs font-bold text-foreground">{c.name}</span>
                        <span className="text-[11px] text-muted-foreground">{c.desc}</span>
                      </div>
                    </div>
                    <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-muted text-muted-foreground">
                      {c.badge}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Step 4: Review & Confirm */}
            {step === 4 && (
              <div className="space-y-3 rounded-lg bg-muted/40 p-4 border border-border text-xs">
                <div className="flex justify-between py-1 border-b border-border">
                  <span className="text-muted-foreground">Workspace Name:</span>
                  <span className="font-bold text-foreground">{workspaceName}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-border">
                  <span className="text-muted-foreground">Operating Model:</span>
                  <span className="font-semibold text-foreground">{workspaceType}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-border">
                  <span className="text-muted-foreground">Primary Cloud:</span>
                  <span className="font-semibold text-foreground">{cloudProvider}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-muted-foreground">Security Role:</span>
                  <span className="font-semibold text-primary font-mono">WORKSPACE_ADMIN</span>
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="pt-2 border-t border-border flex justify-between">
            {step > 1 ? (
              <Button onClick={handleBack} variant="outline" size="sm" disabled={isLoading}>
                <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
                Back
              </Button>
            ) : <div />}

            {step < 4 ? (
              <Button onClick={handleNext} variant="primary" size="sm">
                Next Step
                <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
              </Button>
            ) : (
              <Button onClick={handleComplete} variant="primary" size="sm" isLoading={isLoading}>
                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                Launch Workspace
              </Button>
            )}
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

