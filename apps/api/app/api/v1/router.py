from fastapi import APIRouter
from apps.api.app.api.v1.auth import router as auth_router
from apps.api.app.api.v1.dashboard import router as dashboard_router
from apps.api.app.api.v1.datasets import router as datasets_router
from apps.api.app.api.v1.health import router as health_router
from apps.api.app.api.v1.settings import router as settings_router
from apps.api.app.api.v1.workspaces import router as workspaces_router
from apps.api.app.api.v1.processing import router as processing_router
from apps.api.app.api.v1.analytics import router as analytics_router
from apps.api.app.api.v1.exports import router as exports_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(workspaces_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(datasets_router)
api_v1_router.include_router(processing_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(exports_router)
api_v1_router.include_router(settings_router)
