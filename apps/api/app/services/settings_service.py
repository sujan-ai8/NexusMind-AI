from apps.api.app.core.config import settings
from apps.api.app.schemas.settings import SystemSettingsResponse


class SettingsService:
    @staticmethod
    def get_system_settings() -> SystemSettingsResponse:
        db_type = "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite (Local Dev)"
        return SystemSettingsResponse(
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            database_type=db_type,
            supported_cloud_providers=["AWS", "GCP", "AZURE", "HYBRID"],
            max_upload_size_mb=100,
            features_enabled={
                "big_data_analytics": True,
                "ml_model_registry": True,
                "rl_optimization": True,
                "genai_copilot": True,
                "aws_integration": True,
                "spm_tracker": True,
            },
        )

