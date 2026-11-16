/**
 * NexusMind AI Shared Constants and Enum Definitions
 * Phase 1 Foundation
 */

export enum UserRole {
  PLATFORM_ADMIN = "PLATFORM_ADMIN",
  WORKSPACE_ADMIN = "WORKSPACE_ADMIN",
  ANALYST = "ANALYST",
  VIEWER = "VIEWER",
}

export enum WorkspaceType {
  ENTERPRISE = "ENTERPRISE",
  RESEARCH = "RESEARCH",
  STARTUP = "STARTUP",
  INDIVIDUAL = "INDIVIDUAL",
}

export enum CloudProvider {
  AWS = "AWS",
  GCP = "GCP",
  AZURE = "AZURE",
  HYBRID = "HYBRID",
}

export enum DatasetStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  READY = "READY",
  FAILED = "FAILED",
}

export enum ProjectStatus {
  PLANNING = "PLANNING",
  IN_PROGRESS = "IN_PROGRESS",
  BLOCKED = "BLOCKED",
  COMPLETED = "COMPLETED",
}

export enum SprintStatus {
  UPCOMING = "UPCOMING",
  ACTIVE = "ACTIVE",
  COMPLETED = "COMPLETED",
}

export enum TaskPriority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum TaskStatus {
  BACKLOG = "BACKLOG",
  TODO = "TODO",
  IN_PROGRESS = "IN_PROGRESS",
  REVIEW = "REVIEW",
  DONE = "DONE",
}

export const APP_CONFIG = {
  name: "NexusMind AI",
  tagline: "An AI-Driven Cloud Intelligence and Resource Optimization Platform",
  version: "1.0.0-phase1",
  apiPrefix: "/api/v1",
} as const;

