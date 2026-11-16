from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now
from apps.api.app.models.enums import (
    CloudProviderEnum,
    DatasetStatusEnum,
    ExperimentStatusEnum,
    JobStatusEnum,
    ModelStatusEnum,
    ProjectStatusEnum,
    RoleEnum,
    SprintStatusEnum,
    TaskPriorityEnum,
    TaskStatusEnum,
    WorkspaceTypeEnum,
)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_platform_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    owned_workspaces: Mapped[List["Workspace"]] = relationship(
        "Workspace", back_populates="owner", cascade="all, delete-orphan"
    )
    memberships: Mapped[List["WorkspaceMember"]] = relationship(
        "WorkspaceMember", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")


class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(
        String(32), default=WorkspaceTypeEnum.ENTERPRISE.value, nullable=False
    )
    cloud_provider: Mapped[str] = mapped_column(
        String(32), default=CloudProviderEnum.AWS.value, nullable=False
    )
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_workspaces")
    members: Mapped[List["WorkspaceMember"]] = relationship(
        "WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan"
    )
    settings: Mapped[Optional["WorkspaceSettings"]] = relationship(
        "WorkspaceSettings", back_populates="workspace", uselist=False, cascade="all, delete-orphan"
    )
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset", back_populates="workspace", cascade="all, delete-orphan"
    )
    models: Mapped[List["MLModel"]] = relationship(
        "MLModel", back_populates="workspace", cascade="all, delete-orphan"
    )
    experiments: Mapped[List["OptimizationExperiment"]] = relationship(
        "OptimizationExperiment", back_populates="workspace", cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report", back_populates="workspace", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="workspace", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="workspace", cascade="all, delete-orphan"
    )


class WorkspaceMember(Base, TimestampMixin):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(32), default=RoleEnum.VIEWER.value, nullable=False
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")


class WorkspaceSettings(Base):
    __tablename__ = "workspace_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    telemetry_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    aws_region: Mapped[str] = mapped_column(String(32), default="us-east-1", nullable=False)
    alert_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cost_threshold: Mapped[float] = mapped_column(Float, default=1000.0, nullable=False)
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    settings_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationship
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="settings")


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_format: Mapped[str] = mapped_column(String(32), default="CSV", nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(512), nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=DatasetStatusEnum.READY.value, nullable=False
    )
    uploaded_by: Mapped[str] = mapped_column(String(36), nullable=False)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="datasets")
    jobs: Mapped[List["ProcessingJob"]] = relationship(
        "ProcessingJob", back_populates="dataset", cascade="all, delete-orphan"
    )


class ProcessingJob(Base, TimestampMixin):
    __tablename__ = "processing_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=JobStatusEnum.QUEUED.value, nullable=False
    )
    parameters_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    dataset: Mapped[Optional["Dataset"]] = relationship("Dataset", back_populates="jobs")


class MLModel(Base, TimestampMixin):
    __tablename__ = "ml_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_type: Mapped[str] = mapped_column(String(64), nullable=False)  # TimeSeries, Regressor, etc.
    version: Mapped[str] = mapped_column(String(32), default="v1.0.0", nullable=False)
    framework: Mapped[str] = mapped_column(String(64), default="PyTorch", nullable=False)
    metrics_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    artifact_uri: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default=ModelStatusEnum.TRAINED.value, nullable=False
    )

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="models")


class OptimizationExperiment(Base, TimestampMixin):
    __tablename__ = "optimization_experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(64), default="PPO", nullable=False)
    target_metric: Mapped[str] = mapped_column(String(64), default="Cost Efficiency", nullable=False)
    baseline_metric: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    optimized_metric: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=ExperimentStatusEnum.CONVERGED.value, nullable=False
    )
    results_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="experiments")


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(64), default="Executive Summary", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="GENERATED", nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_uri: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="reports")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default=ProjectStatusEnum.IN_PROGRESS.value, nullable=False
    )
    lead_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="projects")
    sprints: Mapped[List["Sprint"]] = relationship(
        "Sprint", back_populates="project", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )


class Sprint(Base, TimestampMixin):
    __tablename__ = "sprints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default=SprintStatusEnum.ACTIVE.value, nullable=False
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="sprints")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="sprint")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sprint_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("sprints.id", ondelete="SET NULL"), nullable=True, index=True
    )
    key: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(
        String(32), default=TaskPriorityEnum.MEDIUM.value, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), default=TaskStatusEnum.TODO.value, nullable=False
    )
    assignee_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    reporter_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    story_points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    sprint: Mapped[Optional["Sprint"]] = relationship("Sprint", back_populates="tasks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    details_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )

    workspace: Mapped[Optional["Workspace"]] = relationship("Workspace", back_populates="audit_logs")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

