# AWS Cloud Infrastructure Blueprint (Phase 1 Baseline)

This directory outlines the cloud architecture requirements and upcoming infrastructure-as-code (Terraform / CloudFormation) manifests for NexusMind AI.

## Architecture Target (Phase 5/6 Deployment)
- **VPC & Subnets**: Multi-AZ VPC with Public, Private, and Database subnets.
- **Compute**: Amazon ECS (Fargate) or Amazon EKS for containerized FastAPI, React Web, and Celery Workers.
- **Storage**: Amazon S3 for cloud telemetry datasets, model checkpoints, and generated executive reports.
- **Database**: Amazon Aurora Serverless PostgreSQL (Multi-AZ) with automated backups and KMS encryption.
- **Caching & Broker**: Amazon ElastiCache (Redis) for real-time telemetry caching and Celery task queuing.
- **Security & IAM**: IAM Roles for Service Accounts (IRSA), AWS Secrets Manager, and AWS KMS customer managed keys.
- **Observability**: Amazon CloudWatch Container Insights, X-Ray distributed tracing, and Prometheus metrics.

> **Phase 1 Status:** Infrastructure placeholders and IAM permission schemes defined. Live AWS integration modules will be activated in later phases.

