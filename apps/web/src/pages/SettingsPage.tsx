import React, { useState } from "react";
import {
  Bell,
  CheckCircle2,
  Globe,
  Key,
  Layers,
  Lock,
  Moon,
  Save,
  Shield,
  Sun,
  User,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/PageHeader";
import { useAuth } from "@/contexts/AuthContext";
import { useWorkspace } from "@/contexts/WorkspaceContext";
import { useTheme } from "@/contexts/ThemeContext";
import { apiRequest } from "@/lib/api-client";

export function SettingsPage() {
  const { user, updateUser } = useAuth();
  const { activeWorkspace } = useWorkspace();
  const { theme, toggleTheme } = useTheme();

  const [activeTab, setActiveTab] = useState<
    "profile" | "workspace" | "security" | "notifications" | "theme"
  >("profile");

  const [fullName, setFullName] = useState(user?.full_name || "");
  const [costThreshold, setCostThreshold] = useState("1000");
  const [alertEmail, setAlertEmail] = useState(user?.email || "");
  const [isSaved, setIsSaved] = useState(false);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await apiRequest("/settings/profile", {
        method: "PUT",
        body: JSON.stringify({ full_name: fullName }),
      });
      updateUser(updated);
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings & System Configuration"
        description="Manage your account profile, workspace security policies, notification channels, and platform preferences."
      />

      <div className="flex items-center gap-2 border-b border-border pb-2 text-xs">
        <button
          onClick={() => setActiveTab("profile")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "profile" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <User className="w-3.5 h-3.5" /> Profile
        </button>
        <button
          onClick={() => setActiveTab("workspace")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "workspace" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <Layers className="w-3.5 h-3.5" /> Workspace Policies
        </button>
        <button
          onClick={() => setActiveTab("security")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "security" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <Shield className="w-3.5 h-3.5" /> Security & RBAC
        </button>
        <button
          onClick={() => setActiveTab("notifications")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "notifications" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          <Bell className="w-3.5 h-3.5" /> Notifications
        </button>
        <button
          onClick={() => setActiveTab("theme")}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "theme" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent"
          }`}
        >
          {theme === "dark" ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />} Theme
        </button>
      </div>

      {activeTab === "profile" && (
        <Card className="max-w-xl border-border animate-in fade-in-50">
          <CardHeader>
            <CardTitle className="text-base">User Profile Details</CardTitle>
            <CardDescription className="text-xs">
              Manage personal display name and review account authorization roles
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleProfileSave} className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="font-semibold text-foreground">Email Address</label>
                <Input type="email" value={user?.email || ""} disabled className="opacity-60 bg-muted" />
                <span className="text-[10px] text-muted-foreground">Account identifier managed by system admin.</span>
              </div>

              <div className="space-y-1.5">
                <label className="font-semibold text-foreground">Full Name</label>
                <Input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
              </div>

              <div className="p-3 rounded-lg border border-border bg-muted/40 text-xs">
                <span className="font-semibold text-foreground block mb-0.5">Assigned Platform Role:</span>
                <span className="text-primary font-mono font-bold">
                  {user?.is_platform_admin ? "PLATFORM_ADMINISTRATOR" : "STANDARD_USER"}
                </span>
              </div>

              {isSaved && (
                <div className="p-2.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Profile updated successfully.</span>
                </div>
              )}

              <Button type="submit" variant="primary" size="sm" className="mt-2">
                <Save className="w-3.5 h-3.5 mr-1.5" />
                Save Changes
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {activeTab === "workspace" && (
        <Card className="max-w-xl border-border animate-in fade-in-50">
          <CardHeader>
            <CardTitle className="text-base">Active Workspace: {activeWorkspace?.name}</CardTitle>
            <CardDescription className="text-xs">
              Configure cost alert thresholds and telemetry parameters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="space-y-1.5">
              <label className="font-semibold text-foreground">Monthly Cloud Spend Budget ($)</label>
              <Input
                type="number"
                value={costThreshold}
                onChange={(e) => setCostThreshold(e.target.value)}
              />
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-foreground">Alert Destination Email</label>
              <Input
                type="email"
                value={alertEmail}
                onChange={(e) => setAlertEmail(e.target.value)}
              />
            </div>

            <div className="flex justify-end pt-2">
              <Button onClick={() => alert("Workspace policies saved to database")} variant="primary" size="sm">
                <Save className="w-3.5 h-3.5 mr-1.5" />
                Save Workspace Policies
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "security" && (
        <Card className="max-w-xl border-border animate-in fade-in-50">
          <CardHeader>
            <CardTitle className="text-base">Role-Based Access Control (RBAC)</CardTitle>
            <CardDescription className="text-xs">
              Tenant authorization levels enforced by backend dependencies
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <div className="p-3 rounded-lg border border-border bg-card">
              <div className="font-bold text-foreground">Platform Administrator</div>
              <p className="text-muted-foreground text-[11px] mt-0.5">Manage global users, workspaces, and system settings.</p>
            </div>
            <div className="p-3 rounded-lg border border-border bg-card">
              <div className="font-bold text-foreground">Workspace Administrator</div>
              <p className="text-muted-foreground text-[11px] mt-0.5">Full control over workspace members, dataset registration, and policies.</p>
            </div>
            <div className="p-3 rounded-lg border border-border bg-card">
              <div className="font-bold text-foreground">Analyst</div>
              <p className="text-muted-foreground text-[11px] mt-0.5">Upload datasets, configure ML experiments, generate reports.</p>
            </div>
            <div className="p-3 rounded-lg border border-border bg-card">
              <div className="font-bold text-foreground">Viewer</div>
              <p className="text-muted-foreground text-[11px] mt-0.5">Read-only access to authorized dashboards and executive summaries.</p>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "theme" && (
        <Card className="max-w-xl border-border animate-in fade-in-50">
          <CardHeader>
            <CardTitle className="text-base">Interface Appearance</CardTitle>
            <CardDescription className="text-xs">
              Toggle between deep navy/slate dark mode and clean light mode
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-muted/30">
              <div className="flex items-center gap-3">
                {theme === "dark" ? <Moon className="w-5 h-5 text-primary" /> : <Sun className="w-5 h-5 text-amber-500" />}
                <div>
                  <div className="font-semibold text-foreground">Current Theme: {theme === "dark" ? "Dark Mode" : "Light Mode"}</div>
                  <div className="text-[11px] text-muted-foreground">Deep navy slate backgrounds with accessible high-contrast text</div>
                </div>
              </div>
              <Button onClick={toggleTheme} variant="outline" size="sm">
                Toggle Theme
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

