import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  Download,
  Eye,
  FileSpreadsheet,
  Filter,
  Play,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Sliders,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingState } from "@/components/common/LoadingState";
import { apiRequest } from "@/lib/api-client";
import { formatBytes, formatDate } from "@/lib/utils";
import {
  Dataset,
  DatasetPreview,
  ColumnMappingData,
  DataQualityReportData,
  ProcessingJob,
  ProcessingLog,
  PaginatedResponse,
} from "@/types";

export function DatasetManagementPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState("");
  const [uploadDesc, setUploadDesc] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Preview modal state
  const [previewDataset, setPreviewDataset] = useState<Dataset | null>(null);
  const [previewData, setPreviewData] = useState<DatasetPreview | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  // Column Mapping modal state
  const [mappingDataset, setMappingDataset] = useState<Dataset | null>(null);
  const [mappingData, setMappingData] = useState<ColumnMappingData | null>(null);
  const [isMappingLoading, setIsMappingLoading] = useState(false);
  const [isSavingMapping, setIsSavingMapping] = useState(false);

  // Data Quality modal state
  const [qualityDataset, setQualityDataset] = useState<Dataset | null>(null);
  const [qualityReport, setQualityReport] = useState<DataQualityReportData | null>(null);
  const [isQualityLoading, setIsQualityLoading] = useState(false);

  // Process modal & logs state
  const [processDatasetTarget, setProcessDatasetTarget] = useState<Dataset | null>(null);
  const [processEngine, setProcessEngine] = useState<"PYSPARK" | "PANDAS">("PYSPARK");
  const [activeJob, setActiveJob] = useState<ProcessingJob | null>(null);
  const [jobLogs, setJobLogs] = useState<ProcessingLog[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

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

  // File Upload Handler
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError("Please select a CSV, JSON, or JSONL file to upload.");
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);

      const formData = new FormData();
      formData.append("file", selectedFile);
      if (uploadName.trim()) {
        formData.append("name", uploadName.trim());
      }
      if (uploadDesc.trim()) {
        formData.append("description", uploadDesc.trim());
      }

      await apiRequest<Dataset>("/datasets/upload", {
        method: "POST",
        body: formData,
      });

      setIsUploadOpen(false);
      setSelectedFile(null);
      setUploadName("");
      setUploadDesc("");
      fetchDatasets();
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload dataset file");
    } finally {
      setIsUploading(false);
    }
  };

  // Open Preview Modal
  const handleOpenPreview = async (dataset: Dataset) => {
    setPreviewDataset(dataset);
    setIsPreviewLoading(true);
    try {
      const res = await apiRequest<DatasetPreview>(`/datasets/${dataset.id}/preview?limit=100`);
      setPreviewData(res);
    } catch (err) {
      console.error("Failed to load preview:", err);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  // Open Mapping Modal
  const handleOpenMapping = async (dataset: Dataset) => {
    setMappingDataset(dataset);
    setIsMappingLoading(true);
    try {
      const res = await apiRequest<ColumnMappingData>(`/datasets/${dataset.id}/column-mapping`);
      setMappingData(res);
    } catch (err) {
      console.error("Failed to load column mapping:", err);
    } finally {
      setIsMappingLoading(false);
    }
  };

  // Save Mapping
  const handleSaveMapping = async () => {
    if (!mappingDataset || !mappingData) return;
    try {
      setIsSavingMapping(true);
      const res = await apiRequest<ColumnMappingData>(`/datasets/${mappingDataset.id}/column-mapping`, {
        method: "POST",
        body: JSON.stringify({ mapping: mappingData.mapping }),
      });
      setMappingData(res);
      fetchDatasets();
    } catch (err: any) {
      alert(`Error updating mapping: ${err.message}`);
    } finally {
      setIsSavingMapping(false);
    }
  };

  // Open Quality Audit Modal
  const handleOpenQuality = async (dataset: Dataset) => {
    setQualityDataset(dataset);
    setIsQualityLoading(true);
    try {
      const res = await apiRequest<DataQualityReportData | null>(`/datasets/${dataset.id}/quality`);
      if (res) {
        setQualityReport(res);
      } else {
        // Run audit if none exists
        const audited = await apiRequest<DataQualityReportData>(`/datasets/${dataset.id}/quality/audit`, {
          method: "POST",
        });
        setQualityReport(audited);
      }
    } catch (err) {
      console.error("Failed to load quality report:", err);
    } finally {
      setIsQualityLoading(false);
    }
  };

  // Trigger Processing Pipeline
  const handleTriggerProcess = async () => {
    if (!processDatasetTarget) return;
    try {
      setIsProcessing(true);
      const res = await apiRequest<ProcessingJob>(`/datasets/${processDatasetTarget.id}/process?sync=true`, {
        method: "POST",
        body: JSON.stringify({
          engine: processEngine,
          generate_features: true,
        }),
      });
      setActiveJob(res);

      // Fetch logs
      const logsRes = await apiRequest<ProcessingLog[]>(`/processing/jobs/${res.id}/logs`);
      setJobLogs(logsRes);
      fetchDatasets();
    } catch (err: any) {
      alert(`Processing error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Delete Dataset
  const handleDelete = async (datasetId: string) => {
    if (!confirm("Are you sure you want to delete this dataset and all associated parquet files?")) {
      return;
    }
    try {
      await apiRequest(`/datasets/${datasetId}`, { method: "DELETE" });
      fetchDatasets();
    } catch (err: any) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cloud Workload Dataset Management"
        description="Ingest, validate, clean, and transform large-scale cloud infrastructure telemetry with Apache Spark and Pandas."
      >
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => fetchDatasets()}>
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setIsUploadOpen(true)}>
            <UploadCloud className="w-4 h-4 mr-1.5" />
            Upload Dataset
          </Button>
        </div>
      </PageHeader>

      {/* Search & Stats Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-card p-4 rounded-lg border border-border">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search datasets by name or format..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 h-9 text-xs"
          />
        </div>
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>
            Total Datasets: <strong className="text-foreground">{total}</strong>
          </span>
          <span>
            Supported Engines: <strong className="text-foreground">PySpark 4.3.0 & Pandas</strong>
          </span>
        </div>
      </div>

      {/* Dataset List */}
      {isLoading ? (
        <LoadingState message="Loading cloud workload datasets..." />
      ) : datasets.length === 0 ? (
        <EmptyState
          title="No Datasets Ingested"
          description="Upload cloud workload telemetry CSV, JSON, or JSONL files to trigger data quality audits and distributed transformations."
          actionLabel="Upload Sample Dataset"
          onAction={() => setIsUploadOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {datasets.map((dataset) => (
            <Card key={dataset.id} className="hover:border-primary/50 transition-all">
              <CardContent className="p-5">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <div className="p-2 rounded-md bg-primary/10 text-primary">
                        <FileSpreadsheet className="w-5 h-5" />
                      </div>
                      <h3 className="font-semibold text-base text-foreground">{dataset.name}</h3>
                      <Badge variant="outline" className="text-xs uppercase font-mono">
                        {dataset.file_format}
                      </Badge>
                      <Badge
                        variant={
                          dataset.status === "PROCESSED"
                            ? "default"
                            : dataset.status === "READY"
                            ? "secondary"
                            : "destructive"
                        }
                        className="text-xs"
                      >
                        {dataset.status}
                      </Badge>
                      {dataset.quality_score !== null && dataset.quality_score !== undefined && (
                        <Badge
                          variant={dataset.quality_score >= 80 ? "default" : "secondary"}
                          className="text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                        >
                          <ShieldCheck className="w-3 h-3 mr-1" />
                          Quality: {dataset.quality_score.toFixed(0)}%
                        </Badge>
                      )}
                      <Badge variant="outline" className="text-xs text-muted-foreground">
                        <Cpu className="w-3 h-3 mr-1" />
                        {dataset.processing_engine || "PYSPARK"}
                      </Badge>
                    </div>
                    {dataset.description && (
                      <p className="text-xs text-muted-foreground pl-11">{dataset.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-muted-foreground pl-11 pt-1 flex-wrap">
                      <span>
                        Rows: <strong className="text-foreground">{dataset.row_count.toLocaleString()}</strong>
                      </span>
                      <span>
                        Columns: <strong className="text-foreground">{dataset.column_count || 17}</strong>
                      </span>
                      <span>
                        Size: <strong className="text-foreground">{formatBytes(dataset.file_size_bytes)}</strong>
                      </span>
                      <span>
                        Uploaded:{" "}
                        <strong className="text-foreground">{formatDate(dataset.created_at)}</strong>
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 self-end lg:self-center flex-wrap">
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => handleOpenPreview(dataset)}
                    >
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      Preview
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => handleOpenMapping(dataset)}
                    >
                      <Sliders className="w-3.5 h-3.5 mr-1" />
                      Mapping
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => handleOpenQuality(dataset)}
                    >
                      <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                      Quality
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      className="text-xs"
                      onClick={() => {
                        setProcessDatasetTarget(dataset);
                        setActiveJob(null);
                        setJobLogs([]);
                      }}
                    >
                      <Play className="w-3.5 h-3.5 mr-1" />
                      Process
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs text-destructive hover:text-destructive hover:bg-destructive/10"
                      onClick={() => handleDelete(dataset.id)}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal 1: Upload Dataset */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-lg rounded-xl shadow-xl overflow-hidden animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between p-5 border-b border-border">
              <div className="flex items-center gap-2">
                <UploadCloud className="w-5 h-5 text-primary" />
                <h3 className="font-semibold text-base">Upload Cloud Workload Telemetry</h3>
              </div>
              <button
                onClick={() => setIsUploadOpen(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleUploadSubmit} className="p-5 space-y-4">
              {uploadError && (
                <div className="p-3 text-xs bg-destructive/10 border border-destructive/20 text-destructive rounded-md">
                  {uploadError}
                </div>
              )}

              {/* Drag and Drop Box */}
              <div
                className="border-2 border-dashed border-border hover:border-primary/50 rounded-lg p-6 text-center cursor-pointer transition-colors bg-accent/30"
                onClick={() => document.getElementById("file-upload-input")?.click()}
              >
                <input
                  id="file-upload-input"
                  type="file"
                  accept=".csv,.json,.jsonl"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      const f = e.target.files[0];
                      setSelectedFile(f);
                      if (!uploadName) {
                        setUploadName(f.name.replace(/\.[^/.]+$/, ""));
                      }
                    }
                  }}
                />
                <UploadCloud className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm font-medium text-foreground">
                  {selectedFile ? selectedFile.name : "Click or drag telemetry file here"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Supports CSV, JSON, and JSONL workloads up to 500MB
                </p>
                {selectedFile && (
                  <Badge variant="secondary" className="mt-2 text-xs">
                    {formatBytes(selectedFile.size)}
                  </Badge>
                )}
              </div>

              <div>
                <label className="text-xs font-medium text-foreground block mb-1">
                  Dataset Name
                </label>
                <Input
                  value={uploadName}
                  onChange={(e) => setUploadName(e.target.value)}
                  placeholder="e.g. Production Cluster Telemetry 2026"
                  className="h-9 text-xs"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-foreground block mb-1">
                  Description (Optional)
                </label>
                <Input
                  value={uploadDesc}
                  onChange={(e) => setUploadDesc(e.target.value)}
                  placeholder="e.g. AWS EC2/EKS workload traces with 14-day sample"
                  className="h-9 text-xs"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-border">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsUploadOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" disabled={isUploading || !selectedFile}>
                  {isUploading ? "Uploading & Analyzing..." : "Upload & Analyze"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: Preview Dataset */}
      {previewDataset && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-5xl rounded-xl shadow-xl overflow-hidden max-h-[90vh] flex flex-col animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between p-5 border-b border-border">
              <div>
                <h3 className="font-semibold text-base">
                  Dataset Preview: {previewDataset.name}
                </h3>
                <p className="text-xs text-muted-foreground">
                  Showing first 100 rows • {previewDataset.row_count.toLocaleString()} total records
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => {
                    window.open(`/api/v1/datasets/${previewDataset.id}/download?output_type=raw`, "_blank");
                  }}
                >
                  <Download className="w-3.5 h-3.5 mr-1" />
                  Download Raw
                </Button>
                <button
                  onClick={() => setPreviewDataset(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="p-5 overflow-auto flex-1">
              {isPreviewLoading ? (
                <LoadingState message="Extracting dataset rows..." />
              ) : previewData && previewData.rows.length > 0 ? (
                <div className="border border-border rounded-lg overflow-x-auto text-xs">
                  <table className="w-full text-left">
                    <thead className="bg-muted/50 border-b border-border">
                      <tr>
                        {previewData.columns.map((col, idx) => (
                          <th key={idx} className="p-2.5 font-medium whitespace-nowrap text-foreground">
                            {col.column_name}
                            <span className="block text-[10px] text-muted-foreground font-normal">
                              {col.data_type}
                            </span>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {previewData.rows.slice(0, 100).map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-accent/30 transition-colors">
                          {previewData.columns.map((col, cIdx) => (
                            <td key={cIdx} className="p-2.5 whitespace-nowrap font-mono text-muted-foreground">
                              {String(row[col.column_name] ?? "")}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <EmptyState title="No rows found" description="The dataset file contains no previewable records." />
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal 3: Column Mapping */}
      {mappingDataset && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-2xl rounded-xl shadow-xl overflow-hidden max-h-[85vh] flex flex-col animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between p-5 border-b border-border">
              <div>
                <h3 className="font-semibold text-base">Configure Standard Column Mapping</h3>
                <p className="text-xs text-muted-foreground">
                  Map dataset columns to the standardized cloud workload intelligence schema
                </p>
              </div>
              <button
                onClick={() => setMappingDataset(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 overflow-auto flex-1 space-y-4">
              {isMappingLoading ? (
                <LoadingState message="Fetching detected schema..." />
              ) : mappingData ? (
                <>
                  <div className="p-3 bg-accent/40 rounded-lg text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">Schema Status:</span>
                      <Badge variant={mappingData.is_valid ? "default" : "destructive"} className="text-xs">
                        {mappingData.is_valid ? "Valid Cloud Schema" : "Missing Required Fields"}
                      </Badge>
                    </div>
                    {mappingData.missing_required_fields.length > 0 && (
                      <p className="text-destructive text-[11px]">
                        Missing mandatory fields: {mappingData.missing_required_fields.join(", ")}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    {Object.entries(mappingData.mapping).map(([standardField, rawCol]) => (
                      <div
                        key={standardField}
                        className="flex items-center justify-between p-2.5 rounded-md border border-border text-xs"
                      >
                        <span className="font-mono font-medium text-foreground">{standardField}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-muted-foreground mx-2" />
                        <Input
                          value={rawCol || ""}
                          onChange={(e) => {
                            setMappingData({
                              ...mappingData,
                              mapping: { ...mappingData.mapping, [standardField]: e.target.value },
                            });
                          }}
                          className="h-8 text-xs max-w-[200px]"
                        />
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <EmptyState title="No mapping data" description="Unable to load column mappings." />
              )}
            </div>

            <div className="p-4 border-t border-border flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setMappingDataset(null)}>
                Close
              </Button>
              <Button size="sm" onClick={handleSaveMapping} disabled={isSavingMapping}>
                {isSavingMapping ? "Saving..." : "Save Column Mapping"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 4: Data Quality Report */}
      {qualityDataset && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-2xl rounded-xl shadow-xl overflow-hidden max-h-[85vh] flex flex-col animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between p-5 border-b border-border">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-500" />
                <div>
                  <h3 className="font-semibold text-base">Data Quality Audit Report</h3>
                  <p className="text-xs text-muted-foreground">{qualityDataset.name}</p>
                </div>
              </div>
              <button
                onClick={() => setQualityDataset(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 overflow-auto flex-1 space-y-4">
              {isQualityLoading ? (
                <LoadingState message="Auditing telemetry quality..." />
              ) : qualityReport ? (
                <>
                  <div className="grid grid-cols-3 gap-3">
                    <Card className="p-3 text-center bg-card/60">
                      <p className="text-[11px] text-muted-foreground">Quality Score</p>
                      <p className="text-xl font-bold text-emerald-500">
                        {qualityReport.quality_score.toFixed(1)}%
                      </p>
                    </Card>
                    <Card className="p-3 text-center bg-card/60">
                      <p className="text-[11px] text-muted-foreground">Valid Records</p>
                      <p className="text-xl font-bold text-foreground">
                        {qualityReport.valid_records.toLocaleString()}
                      </p>
                    </Card>
                    <Card className="p-3 text-center bg-card/60">
                      <p className="text-[11px] text-muted-foreground">Issues Found</p>
                      <p className="text-xl font-bold text-amber-500">
                        {qualityReport.issues.length}
                      </p>
                    </Card>
                  </div>

                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold text-foreground">Audit Checks & Findings</h4>
                    {qualityReport.issues.length === 0 ? (
                      <p className="text-xs text-emerald-600 dark:text-emerald-400">
                        All validation checks passed with zero integrity anomalies.
                      </p>
                    ) : (
                      qualityReport.issues.map((issue, idx) => (
                        <div
                          key={idx}
                          className="p-3 rounded-lg border border-border text-xs space-y-1 bg-accent/20"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold font-mono text-foreground">{issue.issue_type}</span>
                            <Badge variant={issue.severity === "CRITICAL" ? "destructive" : "secondary"}>
                              {issue.severity}
                            </Badge>
                          </div>
                          <p className="text-muted-foreground">{issue.description}</p>
                          <p className="text-[11px] text-muted-foreground">
                            Affected rows: <strong>{issue.affected_rows}</strong>
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                </>
              ) : (
                <EmptyState title="No Report Available" description="Run quality audit to generate report." />
              )}
            </div>

            <div className="p-4 border-t border-border flex justify-end">
              <Button size="sm" onClick={() => setQualityDataset(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal 5: Process Dataset & Execution Logs */}
      {processDatasetTarget && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-2xl rounded-xl shadow-xl overflow-hidden max-h-[85vh] flex flex-col animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between p-5 border-b border-border">
              <div className="flex items-center gap-2">
                <Play className="w-5 h-5 text-primary" />
                <div>
                  <h3 className="font-semibold text-base">Execute Distributed Transformation</h3>
                  <p className="text-xs text-muted-foreground">{processDatasetTarget.name}</p>
                </div>
              </div>
              <button
                onClick={() => setProcessDatasetTarget(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 overflow-auto flex-1 space-y-4">
              {!activeJob && !isProcessing ? (
                <div className="space-y-4 text-xs">
                  <p className="text-muted-foreground">
                    This pipeline cleans the raw cloud traces, imputes missing values, extracts analytical
                    aggregations, saves optimized Parquet datasets, and generates Phase 3 ML feature stores.
                  </p>
                  <div>
                    <label className="font-medium text-foreground block mb-1">
                      Select Processing Engine
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <div
                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                          processEngine === "PYSPARK"
                            ? "border-primary bg-primary/10"
                            : "border-border hover:bg-accent/40"
                        }`}
                        onClick={() => setProcessEngine("PYSPARK")}
                      >
                        <p className="font-semibold text-foreground">Apache Spark (PySpark 4.3)</p>
                        <p className="text-[11px] text-muted-foreground mt-0.5">
                          Distributed transformation engine recommended for large production workloads.
                        </p>
                      </div>
                      <div
                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                          processEngine === "PANDAS"
                            ? "border-primary bg-primary/10"
                            : "border-border hover:bg-accent/40"
                        }`}
                        onClick={() => setProcessEngine("PANDAS")}
                      >
                        <p className="font-semibold text-foreground">Vectorized Pandas</p>
                        <p className="text-[11px] text-muted-foreground mt-0.5">
                          Fast in-memory transformation engine suitable for small benchmark traces.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4 text-xs">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {isProcessing ? "Executing Distributed Processing Pipeline..." : "Job Status"}
                      </span>
                      <Badge variant={activeJob?.status === "COMPLETED" ? "default" : "secondary"}>
                        {activeJob?.status || "RUNNING"}
                      </Badge>
                    </div>
                    <div className="w-full bg-accent rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-primary h-full transition-all duration-300"
                        style={{ width: `${activeJob ? activeJob.progress : 75}%` }}
                      />
                    </div>
                  </div>

                  {/* Terminal Execution Logs */}
                  <div className="bg-slate-950 text-slate-100 rounded-lg p-3 font-mono text-[11px] h-48 overflow-y-auto space-y-1">
                    {jobLogs.length > 0 ? (
                      jobLogs.map((log, idx) => (
                        <div key={idx} className="flex gap-2">
                          <span className="text-slate-500">[{log.stage}]</span>
                          <span className={log.level === "ERROR" ? "text-red-400" : "text-emerald-400"}>
                            {log.message}
                          </span>
                        </div>
                      ))
                    ) : (
                      <p className="text-slate-500">Executing pipeline and streaming logs...</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-border flex justify-end gap-2">
              <Button variant="outline" size="sm" onClick={() => setProcessDatasetTarget(null)}>
                {activeJob ? "Done" : "Cancel"}
              </Button>
              {!activeJob && (
                <Button size="sm" onClick={handleTriggerProcess} disabled={isProcessing}>
                  {isProcessing ? "Processing..." : `Run with ${processEngine}`}
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
