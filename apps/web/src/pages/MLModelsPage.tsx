import React, { useState } from "react";
import {
  BrainCircuit,
  CheckCircle2,
  Cpu,
  History,
  Layers,
  LineChart,
  Play,
  Plus,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { DemoBadge } from "@/components/common/DemoBadge";

export function MLModelsPage() {
  const [isTrainModalOpen, setIsTrainModalOpen] = useState(false);
  const [modelType, setModelType] = useState("LSTM");
  const [epochs, setEpochs] = useState("50");

  const models = [
    {
      id: "mdl-1",
      name: "Nexus-LSTM-Demand-Forecaster",
      type: "Deep Learning (LSTM)",
      version: "v1.2.0",
      framework: "PyTorch 2.2",
      metrics: { rmse: "3.42", mae: "2.18", mape: "4.82%" },
      status: "TRAINED",
      target: "CPU & Memory (Next 6h)",
      updated: "Phase 1 Baseline",
    },
    {
      id: "mdl-2",
      name: "Prophet-Workload-Seasonality",
      type: "Additive Regression (Prophet)",
      version: "v1.0.1",
      framework: "Facebook Prophet",
      metrics: { rmse: "5.10", mae: "3.84", mape: "7.15%" },
      status: "TRAINED",
      target: "Daily / Weekly Seasonality",
      updated: "Phase 1 Baseline",
    },
    {
      id: "mdl-3",
      name: "ARIMA-Rapid-Autoregressor",
      type: "Statistical Time Series",
      version: "v0.9.4",
      framework: "Statsmodels",
      metrics: { rmse: "6.85", mae: "4.92", mape: "9.60%" },
      status: "BENCHMARKED",
      target: "Short Horizon (15min)",
      updated: "Phase 1 Baseline",
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Machine Learning Model Registry"
        description="Versioned predictive workload models, loss evaluation curves, and inference history."
      >
        <Button onClick={() => setIsTrainModalOpen(true)} variant="primary" size="sm">
          <Plus className="w-3.5 h-3.5 mr-1.5" />
          Train New Architecture
        </Button>
      </PageHeader>

      {/* Model Performance Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 border-border">
          <span className="text-xs text-muted-foreground">Best Benchmark MAPE</span>
          <div className="text-2xl font-bold text-emerald-500 mt-1">4.82%</div>
          <span className="text-[10px] text-muted-foreground font-mono">Nexus-LSTM-Demand-Forecaster</span>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs text-muted-foreground">Active Model Artifacts</span>
          <div className="text-2xl font-bold text-foreground mt-1">3 Models</div>
          <span className="text-[10px] text-muted-foreground">Ready for Phase 4 distributed training</span>
        </Card>
        <Card className="p-4 border-border">
          <span className="text-xs text-muted-foreground">Target Prediction Window</span>
          <div className="text-2xl font-bold text-foreground mt-1">6 Hours Ahead</div>
          <span className="text-[10px] text-primary font-medium">Pre-scaling reactive buffer</span>
        </Card>
      </div>

      {/* Model Registry Table */}
      <Card className="border-border overflow-hidden">
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle>Registered Forecasting Architectures</CardTitle>
            <CardDescription>Managed ML pipeline checkpoints and evaluation metrics</CardDescription>
          </div>
          <DemoBadge />
        </CardHeader>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-border bg-muted/40 font-semibold text-muted-foreground">
                <th className="p-3.5">Model Name & Framework</th>
                <th className="p-3.5">Architecture</th>
                <th className="p-3.5">Version</th>
                <th className="p-3.5">Evaluation Metrics</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {models.map((m) => (
                <tr key={m.id} className="hover:bg-muted/30 transition-colors">
                  <td className="p-3.5">
                    <div className="flex items-center gap-2.5">
                      <div className="p-1.5 rounded-md bg-purple-500/10 text-purple-500">
                        <BrainCircuit className="w-4 h-4" />
                      </div>
                      <div className="flex flex-col">
                        <span className="font-semibold text-foreground">{m.name}</span>
                        <span className="text-[11px] text-muted-foreground font-mono">{m.framework}</span>
                      </div>
                    </div>
                  </td>
                  <td className="p-3.5">{m.type}</td>
                  <td className="p-3.5 font-mono text-muted-foreground">{m.version}</td>
                  <td className="p-3.5">
                    <div className="flex items-center gap-2 font-mono text-[11px]">
                      <span className="text-emerald-500 font-semibold">MAPE: {m.metrics.mape}</span>
                      <span className="text-muted-foreground">• RMSE: {m.metrics.rmse}</span>
                    </div>
                  </td>
                  <td className="p-3.5">
                    <Badge variant="success">{m.status}</Badge>
                  </td>
                  <td className="p-3.5 text-right">
                    <Button variant="ghost" size="sm" className="h-7 px-2 text-xs">
                      Inspect
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Train Modal Preview */}
      {isTrainModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-primary" />
                Configure ML Training Job
              </h3>
              <button onClick={() => setIsTrainModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </div>
            <div className="py-4 space-y-4 text-xs">
              <div className="p-3 rounded-lg border border-amber-500/20 bg-amber-500/5 text-amber-500">
                <strong className="block mb-0.5">Phase 1 Architecture Foundation Notice:</strong>
                Distributed GPU/CPU model training pipelines will be executed via Celery background workers in Phase 4.
              </div>
              <div className="space-y-1.5">
                <label className="font-semibold text-foreground">Select Model Architecture</label>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs"
                >
                  <option value="LSTM">Long Short-Term Memory (LSTM)</option>
                  <option value="GRU">Gated Recurrent Unit (GRU)</option>
                  <option value="Transformer">Temporal Fusion Transformer</option>
                  <option value="Prophet">Additive Regression (Prophet)</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="font-semibold text-foreground">Training Epochs</label>
                <input
                  type="number"
                  value={epochs}
                  onChange={(e) => setEpochs(e.target.value)}
                  className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-border">
              <Button onClick={() => setIsTrainModalOpen(false)} variant="outline" size="sm">
                Cancel
              </Button>
              <Button onClick={() => setIsTrainModalOpen(false)} variant="primary" size="sm">
                Queue Training Job
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

