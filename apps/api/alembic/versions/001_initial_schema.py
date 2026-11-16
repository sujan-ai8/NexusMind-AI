"""Initial schema for NexusMind AI Phase 1

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-31 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_platform_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('cloud_provider', sa.String(length=32), nullable=False),
        sa.Column('owner_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Workspace Members
    op.create_table(
        'workspace_members',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_member'),
    )

    # Workspace Settings
    op.create_table(
        'workspace_settings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('telemetry_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('aws_region', sa.String(length=32), nullable=False, default='us-east-1'),
        sa.Column('alert_email', sa.String(length=255), nullable=True),
        sa.Column('cost_threshold', sa.Float(), nullable=False, default=1000.0),
        sa.Column('max_concurrent_jobs', sa.Integer(), nullable=False, default=5),
        sa.Column('settings_json', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Datasets
    op.create_table(
        'datasets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_format', sa.String(length=32), nullable=False, default='CSV'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, default=0),
        sa.Column('storage_uri', sa.String(length=512), nullable=False),
        sa.Column('row_count', sa.Integer(), nullable=False, default=0),
        sa.Column('status', sa.String(length=32), nullable=False, default='READY'),
        sa.Column('uploaded_by', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Processing Jobs
    op.create_table(
        'processing_jobs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('job_type', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, default='QUEUED'),
        sa.Column('parameters_json', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # ML Models
    op.create_table(
        'ml_models',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('model_type', sa.String(length=64), nullable=False),
        sa.Column('version', sa.String(length=32), nullable=False, default='v1.0.0'),
        sa.Column('framework', sa.String(length=64), nullable=False, default='PyTorch'),
        sa.Column('metrics_json', sa.JSON(), nullable=True),
        sa.Column('artifact_uri', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, default='TRAINED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Optimization Experiments
    op.create_table(
        'optimization_experiments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('algorithm', sa.String(length=64), nullable=False, default='PPO'),
        sa.Column('target_metric', sa.String(length=64), nullable=False, default='Cost Efficiency'),
        sa.Column('baseline_metric', sa.Float(), nullable=False, default=0.0),
        sa.Column('optimized_metric', sa.Float(), nullable=False, default=0.0),
        sa.Column('status', sa.String(length=32), nullable=False, default='CONVERGED'),
        sa.Column('results_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Reports
    op.create_table(
        'reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('report_type', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, default='GENERATED'),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('file_uri', sa.String(length=512), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Projects
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('key', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, default='IN_PROGRESS'),
        sa.Column('lead_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Sprints
    op.create_table(
        'sprints',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, default='ACTIVE'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sprint_id', sa.String(length=36), sa.ForeignKey('sprints.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('key', sa.String(length=32), nullable=False, index=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=32), nullable=False, default='MEDIUM'),
        sa.Column('status', sa.String(length=32), nullable=False, default='TODO'),
        sa.Column('assignee_id', sa.String(length=36), nullable=True),
        sa.Column('reporter_id', sa.String(length=36), nullable=True),
        sa.Column('story_points', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=False),
        sa.Column('resource_id', sa.String(length=64), nullable=True),
        sa.Column('details_json', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('tasks')
    op.drop_table('sprints')
    op.drop_table('projects')
    op.drop_table('reports')
    op.drop_table('optimization_experiments')
    op.drop_table('ml_models')
    op.drop_table('processing_jobs')
    op.drop_table('datasets')
    op.drop_table('workspace_settings')
    op.drop_table('workspace_members')
    op.drop_table('workspaces')
    op.drop_table('users')

