import React, { useEffect, useState } from "react";
import {
  Database,
  Download,
  Eye,
  FileSpreadsheet,
  Filter,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  UploadCloud,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingState } from "@/components/common/LoadingState";
import { apiRequest } from "@/lib/api-client";
import { formatBytes, formatDate } from "@/lib/utils";
import { Dataset, PaginatedResponse } from "@/types";

export function DatasetManagementPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadName, setUploadName] = useState("");
  const [uploadDesc, setUploadDesc] = useState("");
  const [uploadFormat, setUploadFormat] = useState("CSV");
  const [uploadRows, setUploadRows] = useState("50000");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  // Preview state
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);

  const fetchDatasets = async () => {
    try {
      setIsLoading(true);
      const res = await apiRequest<PaginatedResponse<Dataset>>("/datasets", {
        params: { search: search || undefined, page, page_size: 10 },
      });
      setDatasets(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error("Failed to load datasets:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, [page, search]);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadName.trim()) {
      setModalError("Dataset name is required");
      return;
    }

    try {
      setIsSubmitting(true);
      setModalError(null);
      await apiRequest<Dataset>("/datasets", {
        method: "POST",
        body: JSON.stringify({
          name: uploadName.trim(),
          description: uploadDesc.trim() || undefined,
          file_format: uploadFormat,
          file_size_bytes: parseInt(uploadRows, 10) * 128,
          row_count: parseInt(uploadRows, 10) || 0,
        }),
      });

      setIsUploadOpen(false);
      setUploadName("");
      setUploadDesc("");
      fetchDatasets();
    } catch (err: any) {
      setModalError(err.message || "Failed to register dataset");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dataset Management"
        description="Catalog, inspect, and register cloud telemetry traces for big data analytics and machine learning pipelines."
      >
        <Button onClick={() => setIsUploadOpen(true)} variant="primary" size="sm">
          <Plus className="w-3.5 h-3.5 mr-1.5" />
          Register Telemetry Trace
        </Button>
      </PageHeader>

      {/* Filters & Search Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search datasets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 h-9 text-xs"
          />
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          <Button onClick={fetchDatasets} variant="outline" size="sm" className="text-xs">
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Datasets Table / List */}
      {isLoading ? (
        <LoadingState message="Fetching registered cloud datasets..." />
      ) : datasets.length === 0 ? (
        <EmptyState
          icon={<FileSpreadsheet className="w-8 h-8 text-primary" />}
          title="No Telemetry Datasets Registered"
          description="Register your first AWS cluster utilization trace or synthetic benchmark file to commence analytics."
          actionLabel="Register Telemetry Trace"
          onAction={() => setIsUploadOpen(true)}
        />
      ) : (
        <Card className="border-border overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border bg-muted/40 font-semibold text-muted-foreground">
                  <th className="p-3.5">Dataset Name & Storage URI</th>
                  <th className="p-3.5">Format</th>
                  <th className="p-3.5">Records</th>
                  <th className="p-3.5">Size</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Registered Date</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {datasets.map((ds) => (
                  <tr key={ds.id} className="hover:bg-muted/30 transition-colors">
                    <td className="p-3.5">
                      <div className="flex items-center gap-2.5">
                        <div className="p-1.5 rounded-md bg-primary/10 text-primary flex-shrink-0">
                          <Database className="w-4 h-4" />
                        </div>
                        <div className="flex flex-col min-w-0">
                          <span className="font-semibold text-foreground truncate max-w-xs">{ds.name}</span>
                          <span className="text-[11px] text-muted-foreground font-mono truncate max-w-xs">
                            {ds.storage_uri}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="p-3.5 font-mono">{ds.file_format}</td>
                    <td className="p-3.5 font-mono">{ds.row_count.toLocaleString()} rows</td>
                    <td className="p-3.5 font-mono">{formatBytes(ds.file_size_bytes)}</td>
                    <td className="p-3.5">
                      <Badge variant="success">{ds.status}</Badge>
                    </td>
                    <td className="p-3.5 text-muted-foreground">{formatDate(ds.created_at)}</td>
                    <td className="p-3.5 text-right">
                      <Button
                        onClick={() => setSelectedDataset(ds)}
                        variant="ghost"
                        size="sm"
                        className="h-7 px-2 text-xs"
                      >
                        <Eye className="w-3.5 h-3.5 mr-1" />
                        Preview
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <h3 className="text-base font-bold text-foreground flex items-center gap-2">
                <UploadCloud className="w-5 h-5 text-primary" />
                Register Telemetry Dataset
              </h3>
              <button onClick={() => setIsUploadOpen(false)} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </div>

            {modalError && (
              <div className="mt-3 p-2.5 rounded bg-destructive/10 border border-destructive/20 text-xs text-destructive">
                {modalError}
              </div>
            )}

            <form onSubmit={handleUploadSubmit} className="space-y-4 pt-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Dataset File Name</label>
                <Input
                  type="text"
                  placeholder="e.g. cluster_workload_traces_2026.csv"
                  value={uploadName}
                  onChange={(e) => setUploadName(e.target.value)}
                  autoFocus
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-foreground">Description</label>
                <Input
                  type="text"
                  placeholder="e.g. 30-day AWS EC2 cluster telemetry trace"
                  value={uploadDesc}
                  onChange={(e) => setUploadDesc(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-foreground">File Format</label>
                  <select
                    value={uploadFormat}
                    onChange={(e) => setUploadFormat(e.target.value)}
                    className="w-full h-9 rounded-md border border-input bg-background px-3 text-xs"
                  >
                    <option value="CSV">CSV (.csv)</option>
                    <option value="PARQUET">Apache Parquet (.parquet)</option>
                    <option value="JSON">JSON Lines (.jsonl)</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-foreground">Row Count</label>
                  <Input
                    type="number"
                    value={uploadRows}
                    onChange={(e) => setUploadRows(e.target.value)}
                  />
                </div>
              </div>

              <div className="p-3 rounded-lg border border-dashed border-border bg-muted/30 text-center text-xs text-muted-foreground">
                <FileSpreadsheet className="w-6 h-6 mx-auto mb-1 text-primary" />
                <span>Simulated storage endpoint: S3 URI will be assigned automatically.</span>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-border">
                <Button type="button" onClick={() => setIsUploadOpen(false)} variant="outline" size="sm">
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
                  Register Dataset
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Dataset Preview Modal */}
      {selectedDataset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl rounded-xl border border-border bg-card p-6 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div>
                <h3 className="text-base font-bold text-foreground">{selectedDataset.name}</h3>
                <span className="text-xs font-mono text-muted-foreground">{selectedDataset.storage_uri}</span>
              </div>
              <button onClick={() => setSelectedDataset(null)} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </div>

            <div className="py-4 space-y-4">
              <div className="grid grid-cols-3 gap-3 text-xs">
                <div className="p-2.5 rounded bg-muted/40 border border-border">
                  <span className="text-muted-foreground">Total Records</span>
                  <div className="font-bold text-foreground text-sm mt-0.5">{selectedDataset.row_count.toLocaleString()}</div>
                </div>
                <div className="p-2.5 rounded bg-muted/40 border border-border">
                  <span className="text-muted-foreground">Byte Size</span>
                  <div className="font-bold text-foreground text-sm mt-0.5">{formatBytes(selectedDataset.file_size_bytes)}</div>
                </div>
                <div className="p-2.5 rounded bg-muted/40 border border-border">
                  <span className="text-muted-foreground">Format</span>
                  <div className="font-bold text-foreground text-sm mt-0.5">{selectedDataset.file_format}</div>
                </div>
              </div>

              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-foreground">Sample Schema & Header Preview:</span>
                <div className="p-3 rounded-lg bg-background border border-border font-mono text-xs overflow-x-auto text-muted-foreground space-y-1">
                  <p className="text-foreground font-semibold">timestamp, instance_id, cpu_util_pct, mem_util_pct, disk_read_bytes, network_in_bytes, cost_usd</p>
                  <p>2026-10-31T00:00:00Z, i-08a9f4c3, 38.2, 61.0, 1048576, 4194304, 0.096</p>
                  <p>2026-10-31T00:05:00Z, i-08a9f4c3, 34.5, 59.8, 838860,  3145728, 0.096</p>
                  <p>2026-10-31T00:10:00Z, i-08a9f4c3, 41.0, 63.2, 1258291, 5242880, 0.096</p>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-border">
              <Button onClick={() => setSelectedDataset(null)} variant="primary" size="sm">
                Close Preview
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

