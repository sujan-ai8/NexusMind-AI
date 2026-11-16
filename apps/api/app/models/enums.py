import enum


class RoleEnum(str, enum.Enum):
    PLATFORM_ADMIN = "PLATFORM_ADMIN"
    WORKSPACE_ADMIN = "WORKSPACE_ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"


class WorkspaceTypeEnum(str, enum.Enum):
    ENTERPRISE = "ENTERPRISE"
    RESEARCH = "RESEARCH"
    STARTUP = "STARTUP"
    INDIVIDUAL = "INDIVIDUAL"


class CloudProviderEnum(str, enum.Enum):
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"
    HYBRID = "HYBRID"


class DatasetStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class JobStatusEnum(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ModelStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"
    DEPLOYED = "DEPLOYED"
    ARCHIVED = "ARCHIVED"


class ExperimentStatusEnum(str, enum.Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    CONVERGED = "CONVERGED"
    FAILED = "FAILED"


class ProjectStatusEnum(str, enum.Enum):
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class SprintStatusEnum(str, enum.Enum):
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class TaskPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatusEnum(str, enum.Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"

