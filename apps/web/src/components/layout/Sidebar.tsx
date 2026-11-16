import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Activity,
  BarChart3,
  Bot,
  BrainCircuit,
  Cloud,
  Cpu,
  Database,
  FileText,
  FolderKanban,
  LayoutDashboard,
  Layers,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkspace } from "@/contexts/WorkspaceContext";

interface SidebarProps {
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
  isMobileOpen: boolean;
  setIsMobileOpen: (open: boolean) => void;
}

export function Sidebar({
  isCollapsed,
  setIsCollapsed,
  isMobileOpen,
  setIsMobileOpen,
}: SidebarProps) {
  const location = useLocation();
  const { activeWorkspace } = useWorkspace();

  const navigationItems = [
    { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { name: "Workloads", href: "/workloads", icon: Cpu },
    { name: "Datasets", href: "/datasets", icon: Database },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "ML Models", href: "/models", icon: BrainCircuit },
    { name: "Optimization", href: "/optimization", icon: Activity },
    { name: "AI Copilot", href: "/copilot", icon: Bot },
    { name: "AWS Cloud", href: "/cloud", icon: Cloud },
    { name: "Reports", href: "/reports", icon: FileText },
    { name: "Project Management", href: "/spm", icon: FolderKanban },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={cn(
          "fixed top-0 bottom-0 left-0 z-50 flex flex-col border-r border-border bg-card transition-all duration-300 ease-in-out lg:static lg:z-auto",
          isCollapsed ? "w-20" : "w-64",
          isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Brand / Logo */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          <Link
            to="/dashboard"
            className="flex items-center gap-2.5 overflow-hidden font-bold tracking-tight text-foreground"
          >
            <div className="w-9 h-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary flex-shrink-0">
              <Layers className="w-5 h-5 text-primary" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="text-base font-extrabold tracking-tight bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent">
                  NexusMind AI
                </span>
                <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-mono">
                  Cloud Intelligence
                </span>
              </div>
            )}
          </Link>

          {/* Desktop Collapse Toggle */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden lg:flex p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
            {!isCollapsed ? "Modules & Analytics" : "•"}
          </div>

          {navigationItems.map((item) => {
            const isActive =
              location.pathname === item.href ||
              (item.href !== "/dashboard" && location.pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setIsMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all group relative",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )}
                title={isCollapsed ? item.name : undefined}
              >
                <Icon className={cn("w-4 h-4 flex-shrink-0 transition-transform group-hover:scale-110", isActive ? "text-primary-foreground" : "text-muted-foreground group-hover:text-foreground")} />
                {!isCollapsed && <span className="truncate">{item.name}</span>}
                {isActive && !isCollapsed && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white/80" />
                )}
              </Link>
            );
          })}
        </div>

        {/* Role & Workspace badge footer */}
        <div className="p-3 border-t border-border bg-card/60">
          <div className={cn("flex items-center gap-2.5 p-2 rounded-md bg-muted/40", isCollapsed ? "justify-center" : "")}>
            <ShieldCheck className="w-4 h-4 text-primary flex-shrink-0" />
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-foreground truncate">
                  {activeWorkspace?.name || "Workspace"}
                </span>
                <span className="text-[10px] text-muted-foreground truncate uppercase font-mono">
                  Role: {activeWorkspace?.role || "WORKSPACE_ADMIN"}
                </span>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}

