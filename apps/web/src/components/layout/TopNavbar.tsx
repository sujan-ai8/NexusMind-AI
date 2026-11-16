import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Bell,
  Check,
  ChevronDown,
  Globe,
  HelpCircle,
  LogOut,
  Menu,
  Moon,
  Plus,
  Search,
  Sun,
  User as UserIcon,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useWorkspace } from "@/contexts/WorkspaceContext";
import { useTheme } from "@/contexts/ThemeContext";
import { Button } from "@/components/ui/button";

interface TopNavbarProps {
  setIsMobileOpen: (open: boolean) => void;
}

export function TopNavbar({ setIsMobileOpen }: TopNavbarProps) {
  const { user, logout } = useAuth();
  const { workspaces, activeWorkspace, setActiveWorkspace } = useWorkspace();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const [isWorkspaceOpen, setIsWorkspaceOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-card/90 px-4 backdrop-blur-md">
      {/* Left: Mobile trigger & Workspace Switcher */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="p-2 rounded-md text-muted-foreground hover:bg-accent lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Workspace Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              setIsWorkspaceOpen(!isWorkspaceOpen);
              setIsProfileOpen(false);
              setIsNotificationsOpen(false);
            }}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg border border-border bg-background hover:bg-accent text-sm font-medium transition-colors"
          >
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="max-w-[140px] md:max-w-[200px] truncate">
              {activeWorkspace?.name || "Select Workspace"}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
          </button>

          {isWorkspaceOpen && (
            <div className="absolute left-0 mt-2 w-64 rounded-lg border border-border bg-card p-1 shadow-lg z-50 animate-in fade-in-50 zoom-in-95">
              <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Active Workspaces
              </div>
              <div className="space-y-0.5 max-h-56 overflow-y-auto">
                {workspaces.map((ws) => (
                  <button
                    key={ws.id}
                    onClick={() => {
                      setActiveWorkspace(ws);
                      setIsWorkspaceOpen(false);
                    }}
                    className="flex w-full items-center justify-between px-3 py-2 text-sm rounded-md hover:bg-accent transition-colors text-left"
                  >
                    <div className="flex flex-col truncate">
                      <span className="font-medium text-foreground truncate">{ws.name}</span>
                      <span className="text-[11px] text-muted-foreground">{ws.cloud_provider} • {ws.type}</span>
                    </div>
                    {activeWorkspace?.id === ws.id && (
                      <Check className="w-4 h-4 text-primary flex-shrink-0" />
                    )}
                  </button>
                ))}
              </div>
              <div className="p-1 border-t border-border mt-1">
                <button
                  onClick={() => {
                    setIsWorkspaceOpen(false);
                    navigate("/onboarding");
                  }}
                  className="flex w-full items-center gap-2 px-3 py-2 text-xs font-medium text-primary hover:bg-primary/10 rounded-md transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Create New Workspace
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Center: Global Search Bar */}
      <div className="hidden md:flex items-center flex-1 max-w-md mx-6">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search workloads, metrics, models, datasets... (Ctrl + K)"
            className="w-full h-9 pl-9 pr-4 rounded-md border border-input bg-background/60 text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring transition-colors"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Notifications Popover */}
        <div className="relative">
          <button
            onClick={() => {
              setIsNotificationsOpen(!isNotificationsOpen);
              setIsProfileOpen(false);
              setIsWorkspaceOpen(false);
            }}
            className="relative p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary" />
          </button>

          {isNotificationsOpen && (
            <div className="absolute right-0 mt-2 w-80 rounded-lg border border-border bg-card p-3 shadow-lg z-50 animate-in fade-in-50 zoom-in-95">
              <div className="flex items-center justify-between pb-2 border-b border-border">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  System Alerts
                </span>
                <span className="text-[10px] text-primary cursor-pointer hover:underline">
                  Mark all read
                </span>
              </div>
              <div className="py-2 space-y-2 text-xs">
                <div className="p-2 rounded-md bg-muted/40 border border-border">
                  <p className="font-semibold text-foreground">Phase 1 Foundation Active</p>
                  <p className="text-muted-foreground text-[11px] mt-0.5">
                    FastAPI backend and React UI connected. Telemetry demo engine ready.
                  </p>
                  <span className="text-[10px] text-muted-foreground/60 font-mono">Just now</span>
                </div>
                <div className="p-2 rounded-md bg-muted/40 border border-border">
                  <p className="font-semibold text-foreground">AWS Telemetry Trace Seeded</p>
                  <p className="text-muted-foreground text-[11px] mt-0.5">
                    Initial sample cluster dataset available for workload exploration.
                  </p>
                  <span className="text-[10px] text-muted-foreground/60 font-mono">10m ago</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Help & Documentation Modal Trigger */}
        <button
          onClick={() => setIsHelpOpen(true)}
          className="p-2 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          title="Platform Documentation & Help"
        >
          <HelpCircle className="w-4 h-4" />
        </button>

        {/* User Profile Dropdown */}
        <div className="relative ml-1">
          <button
            onClick={() => {
              setIsProfileOpen(!isProfileOpen);
              setIsWorkspaceOpen(false);
              setIsNotificationsOpen(false);
            }}
            className="flex items-center gap-2 p-1.5 rounded-full hover:bg-accent transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary font-bold text-xs">
              {user?.full_name?.charAt(0) || "U"}
            </div>
          </button>

          {isProfileOpen && (
            <div className="absolute right-0 mt-2 w-56 rounded-lg border border-border bg-card p-1 shadow-lg z-50 animate-in fade-in-50 zoom-in-95">
              <div className="px-3 py-2 border-b border-border">
                <p className="text-sm font-semibold text-foreground truncate">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground truncate font-mono">{user?.email}</p>
                {user?.is_platform_admin && (
                  <span className="inline-block mt-1 text-[10px] font-semibold text-primary uppercase">
                    Platform Administrator
                  </span>
                )}
              </div>
              <div className="p-1 space-y-0.5">
                <Link
                  to="/settings"
                  onClick={() => setIsProfileOpen(false)}
                  className="flex w-full items-center gap-2 px-3 py-2 text-xs rounded-md text-foreground hover:bg-accent transition-colors"
                >
                  <UserIcon className="w-3.5 h-3.5" />
                  Account Settings
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 px-3 py-2 text-xs rounded-md text-destructive hover:bg-destructive/10 transition-colors"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Help Modal */}
      {isHelpOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between pb-4 border-b border-border">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Globe className="w-5 h-5 text-primary" />
                NexusMind AI Platform Guide
              </h3>
              <button
                onClick={() => setIsHelpOpen(false)}
                className="text-muted-foreground hover:text-foreground text-sm font-semibold"
              >
                ✕
              </button>
            </div>
            <div className="py-4 space-y-3 text-sm text-muted-foreground">
              <p>
                <strong className="text-foreground">NexusMind AI</strong> is an AI-driven cloud intelligence platform. Phase 1 provides the foundational architecture, user onboarding, role-based security, and UI structure.
              </p>
              <div className="rounded-lg bg-muted/50 p-3 space-y-1 font-mono text-xs text-foreground">
                <p>• API Docs: <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-primary hover:underline">/docs</a></p>
                <p>• Architecture Spec: <span className="text-muted-foreground">docs/architecture/system-architecture.md</span></p>
                <p>• SPM Deliverables: <span className="text-muted-foreground">docs/spm/</span> (12 documents)</p>
              </div>
            </div>
            <div className="flex justify-end pt-2 border-t border-border">
              <Button onClick={() => setIsHelpOpen(false)} variant="primary" size="sm">
                Got it
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

