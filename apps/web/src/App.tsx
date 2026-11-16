import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ThemeProvider } from "@/contexts/ThemeContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { WorkspaceProvider } from "@/contexts/WorkspaceContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";

import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { OnboardingPage } from "@/pages/OnboardingPage";

import { DashboardPage } from "@/pages/DashboardPage";
import { WorkloadsPage } from "@/pages/WorkloadsPage";
import { DatasetManagementPage } from "@/pages/DatasetManagementPage";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { MLModelsPage } from "@/pages/MLModelsPage";
import { OptimizationPage } from "@/pages/OptimizationPage";
import { AICopilotPage } from "@/pages/AICopilotPage";
import { AWSCloudPage } from "@/pages/AWSCloudPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { ProjectManagementPage } from "@/pages/ProjectManagementPage";
import { SettingsPage } from "@/pages/SettingsPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <WorkspaceProvider>
            <BrowserRouter>
              <Routes>
                {/* Public Marketing & Auth Routes */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Workspace Onboarding (Protected) */}
                <Route
                  path="/onboarding"
                  element={
                    <ProtectedRoute>
                      <OnboardingPage />
                    </ProtectedRoute>
                  }
                />

                {/* Authenticated Application Shell */}
                <Route
                  element={
                    <ProtectedRoute>
                      <AppLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/workloads" element={<WorkloadsPage />} />
                  <Route path="/datasets" element={<DatasetManagementPage />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/models" element={<MLModelsPage />} />
                  <Route path="/optimization" element={<OptimizationPage />} />
                  <Route path="/copilot" element={<AICopilotPage />} />
                  <Route path="/cloud" element={<AWSCloudPage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/spm" element={<ProjectManagementPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Route>

                {/* Catch-all Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>
          </WorkspaceProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

