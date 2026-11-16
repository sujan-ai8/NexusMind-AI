import React, { createContext, useContext, useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { Workspace } from "@/types";
import { useAuth } from "@/contexts/AuthContext";

interface WorkspaceContextType {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  isLoading: boolean;
  setActiveWorkspace: (workspace: Workspace) => void;
  refreshWorkspaces: () => Promise<Workspace[]>;
  createWorkspace: (data: {
    name: string;
    description?: string;
    type: string;
    cloud_provider: string;
  }) => Promise<Workspace>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspaceState] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshWorkspaces = async (): Promise<Workspace[]> => {
    if (!isAuthenticated) {
      setWorkspaces([]);
      setActiveWorkspaceState(null);
      setIsLoading(false);
      return [];
    }

    try {
      setIsLoading(true);
      const list = await apiRequest<Workspace[]>("/workspaces");
      setWorkspaces(list);

      const savedActiveId = localStorage.getItem("nexusmind_active_workspace_id");
      const matched = list.find((w) => w.id === savedActiveId);

      if (matched) {
        setActiveWorkspaceState(matched);
      } else if (list.length > 0) {
        setActiveWorkspaceState(list[0]);
        localStorage.setItem("nexusmind_active_workspace_id", list[0].id);
      } else {
        setActiveWorkspaceState(null);
        localStorage.removeItem("nexusmind_active_workspace_id");
      }
      return list;
    } catch (err) {
      console.error("Failed to load workspaces:", err);
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshWorkspaces();
  }, [isAuthenticated]);

  const setActiveWorkspace = (ws: Workspace) => {
    setActiveWorkspaceState(ws);
    localStorage.setItem("nexusmind_active_workspace_id", ws.id);
  };

  const createWorkspace = async (data: {
    name: string;
    description?: string;
    type: string;
    cloud_provider: string;
  }): Promise<Workspace> => {
    const created = await apiRequest<Workspace>("/workspaces", {
      method: "POST",
      body: JSON.stringify(data),
    });

    await refreshWorkspaces();
    setActiveWorkspace(created);
    return created;
  };

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        activeWorkspace,
        isLoading,
        setActiveWorkspace,
        refreshWorkspaces,
        createWorkspace,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}

