"""Phase 2 Big Data Analytics & Data Engineering Schema

Revision ID: 002_phase2_bigdata_analytics
Revises: 001_initial_schema
Create Date: 2026-11-16 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_phase2_bigdata_analytics'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extend datasets table
    with op.batch_alter_table('datasets') as batch_op:
        batch_op.add_column(sa.Column('original_filename', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('column_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('quality_status', sa.String(length=32), nullable=False, server_default='PENDING'))
        batch_op.add_column(sa.Column('quality_score', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('processing_engine', sa.String(length=32), nullable=False, server_default='PYSPARK'))

    # 2. Extend processing_jobs table
    with op.batch_alter_table('processing_jobs') as batch_op:
        batch_op.add_column(sa.Column('engine', sa.String(length=32), nullable=False, server_default='PYSPARK'))
        batch_op.add_column(sa.Column('progress', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('execution_duration_ms', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('records_failed', sa.Integer(), nullable=False, server_default='0'))

    # 3. Create dataset_versions
    op.create_table(
        'dataset_versions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('version_number', sa.Integer(), nullable=False, default=1),
        sa.Column('storage_uri', sa.String(length=512), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, default=0),
        sa.Column('row_count', sa.Integer(), nullable=False, default=0),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 4. Create dataset_schemas
    op.create_table(
        'dataset_schemas',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('columns_json', sa.JSON(), nullable=False),
        sa.Column('detected_fields_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 5. Create dataset_column_mappings
    op.create_table(
        'dataset_column_mappings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('mapping_json', sa.JSON(), nullable=False),
        sa.Column('is_validated', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 6. Create data_quality_reports
    op.create_table(
        'data_quality_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('total_records', sa.Integer(), nullable=False, default=0),
        sa.Column('valid_records', sa.Integer(), nullable=False, default=0),
        sa.Column('invalid_records', sa.Integer(), nullable=False, default=0),
        sa.Column('duplicate_records', sa.Integer(), nullable=False, default=0),
        sa.Column('missing_values_count', sa.Integer(), nullable=False, default=0),
        sa.Column('corrected_records', sa.Integer(), nullable=False, default=0),
        sa.Column('rejected_records', sa.Integer(), nullable=False, default=0),
        sa.Column('quality_score', sa.Float(), nullable=False, default=100.0),
        sa.Column('status', sa.String(length=32), nullable=False, default='PASSED'),
        sa.Column('issues_json', sa.JSON(), nullable=False),
        sa.Column('cleaning_actions_json', sa.JSON(), nullable=False),
        sa.Column('rejected_records_uri', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 7. Create processing_logs
    op.create_table(
        'processing_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('job_id', sa.String(length=36), sa.ForeignKey('processing_jobs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('level', sa.String(length=16), nullable=False, default='INFO'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('stage', sa.String(length=64), nullable=False, default='PROCESSING'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    )

    # 8. Create processed_datasets
    op.create_table(
        'processed_datasets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('job_id', sa.String(length=36), sa.ForeignKey('processing_jobs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('storage_uri', sa.String(length=512), nullable=False),
        sa.Column('feature_store_uri', sa.String(length=512), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=False, default=0),
        sa.Column('column_count', sa.Integer(), nullable=False, default=0),
        sa.Column('schema_json', sa.JSON(), nullable=False),
        sa.Column('engine_used', sa.String(length=32), nullable=False, default='PYSPARK'),
        sa.Column('spark_config_json', sa.JSON(), nullable=False),
        sa.Column('lineage_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 9. Create analytics_snapshots
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('job_id', sa.String(length=36), sa.ForeignKey('processing_jobs.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('snapshot_type', sa.String(length=64), nullable=False),
        sa.Column('data_json', sa.JSON(), nullable=False),
        sa.Column('metrics_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 10. Create anomaly_events
    op.create_table(
        'anomaly_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('dataset_id', sa.String(length=36), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resource_id', sa.String(length=64), nullable=False),
        sa.Column('metric_name', sa.String(length=64), nullable=False),
        sa.Column('observed_value', sa.Float(), nullable=False),
        sa.Column('expected_range_min', sa.Float(), nullable=False),
        sa.Column('expected_range_max', sa.Float(), nullable=False),
        sa.Column('detection_method', sa.String(length=32), nullable=False, default='Z_SCORE'),
        sa.Column('severity', sa.String(length=16), nullable=False, default='MEDIUM'),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 11. Create cost_configurations
    op.create_table(
        'cost_configurations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(length=128), nullable=False, default='Default AWS Pricing'),
        sa.Column('currency', sa.String(length=8), nullable=False, default='USD'),
        sa.Column('compute_hourly_rates_json', sa.JSON(), nullable=False),
        sa.Column('storage_gb_month_rate', sa.Float(), nullable=False, default=0.023),
        sa.Column('network_egress_gb_rate', sa.Float(), nullable=False, default=0.09),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('cost_configurations')
    op.drop_table('anomaly_events')
    op.drop_table('analytics_snapshots')
    op.drop_table('processed_datasets')
    op.drop_table('processing_logs')
    op.drop_table('data_quality_reports')
    op.drop_table('dataset_column_mappings')
    op.drop_table('dataset_schemas')
    op.drop_table('dataset_versions')

    with op.batch_alter_table('processing_jobs') as batch_op:
        batch_op.drop_column('records_failed')
        batch_op.drop_column('records_processed')
        batch_op.drop_column('execution_duration_ms')
        batch_op.drop_column('progress')
        batch_op.drop_column('engine')

    with op.batch_alter_table('datasets') as batch_op:
        batch_op.drop_column('processing_engine')
        batch_op.drop_column('quality_score')
        batch_op.drop_column('quality_status')
        batch_op.drop_column('column_count')
        batch_op.drop_column('original_filename')
