from sqlalchemy.orm import Session
from apps.api.app.core.config import settings
from apps.api.app.core.logging import logger
from apps.api.app.core.security import get_password_hash
from apps.api.app.db.base import Base
from apps.api.app.db.session import SessionLocal, engine
from apps.api.app.models.entities import (
    AuditLog,
    Dataset,
    MLModel,
    OptimizationExperiment,
    Project,
    Report,
    Sprint,
    Task,
    User,
    Workspace,
    WorkspaceMember,
    WorkspaceSettings,
)
from apps.api.app.models.enums import RoleEnum


def init_db(db: Session) -> None:
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

    # Check if admin user exists
    admin_user = db.query(User).filter(User.email == "admin@nexusmind.ai").first()
    if not admin_user:
        logger.info("Seeding initial administrator and demo workspace for Phase 1...")
        admin = User(
            email="admin@nexusmind.ai",
            hashed_password=get_password_hash("NexusAdmin@2026"),
            full_name="NexusMind Platform Admin",
            is_active=True,
            is_platform_admin=True,
        )
        db.add(admin)
        db.flush()

        # Create demo enterprise workspace
        workspace = Workspace(
            name="Cloud Intelligence Demo",
            slug="cloud-intelligence-demo",
            description="Production cloud optimization workspace for demonstration and testing",
            type="ENTERPRISE",
            cloud_provider="AWS",
            owner_id=admin.id,
        )
        db.add(workspace)
        db.flush()

        # Add member role
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=admin.id,
            role=RoleEnum.WORKSPACE_ADMIN.value,
        )
        db.add(member)

        # Settings
        settings_record = WorkspaceSettings(
            workspace_id=workspace.id,
            telemetry_enabled=True,
            aws_region="us-east-1",
            cost_threshold=1500.0,
            max_concurrent_jobs=10,
        )
        db.add(settings_record)

        # Initial seed dataset
        dataset = Dataset(
            workspace_id=workspace.id,
            name="aws_ec2_workload_telemetry_2026.csv",
            description="Sample 30-day AWS EC2 cluster utilization trace for ML benchmarking",
            file_format="CSV",
            file_size_bytes=10485760,  # 10 MB
            storage_uri="s3://nexusmind-sample-storage/datasets/aws_ec2_workload_telemetry_2026.csv",
            row_count=86400,
            status="READY",
            uploaded_by=admin.id,
        )
        db.add(dataset)

        # Initial seed project
        project = Project(
            workspace_id=workspace.id,
            key="NEXUS",
            name="Cloud Cost Optimization Initiative",
            description="Quarterly initiative to reduce idle cloud compute capacity and improve efficiency",
            status="IN_PROGRESS",
            lead_id=admin.id,
        )
        db.add(project)
        db.flush()

        sprint = Sprint(
            project_id=project.id,
            name="Sprint 1 - Foundation & Telemetry",
            goal="Establish Phase 1 enterprise foundation and UI baseline",
            status="ACTIVE",
        )
        db.add(sprint)
        db.flush()

        task = Task(
            project_id=project.id,
            sprint_id=sprint.id,
            key="NEXUS-101",
            title="Deploy Phase 1 Enterprise SaaS Architecture",
            description="Implement full-stack React + FastAPI architecture with RBAC and Docker support",
            priority="CRITICAL",
            status="DONE",
            assignee_id=admin.id,
            reporter_id=admin.id,
            story_points=5,
        )
        db.add(task)

        # Initial audit log
        audit = AuditLog(
            workspace_id=workspace.id,
            user_id=admin.id,
            action="WORKSPACE_INITIALIZED",
            resource_type="WORKSPACE",
            resource_id=workspace.id,
            details_json={"note": "Phase 1 initial workspace and sample datasets configured"},
            ip_address="127.0.0.1",
        )
        db.add(audit)

        db.commit()
        logger.info("Demo data seeded: admin@nexusmind.ai / NexusAdmin@2026")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

