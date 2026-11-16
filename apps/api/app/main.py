from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.app.api.v1.router import api_v1_router
from apps.api.app.core.config import settings
from apps.api.app.core.errors import NexusMindException
from apps.api.app.core.logging import logger
from apps.api.app.db.init_db import init_db
from apps.api.app.db.session import SessionLocal
from apps.api.app.middleware.request_context import RequestContextMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as exc:
        logger.error(f"Database initialization warning: {exc}")
    finally:
        db.close()
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


def create_application() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Enterprise Cloud Intelligence & Resource Optimization Platform API",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Request Context Middleware
    app.add_middleware(RequestContextMiddleware)

    # Custom Exception Handlers
    @app.exception_handler(NexusMindException)
    async def custom_exception_handler(request: Request, exc: NexusMindException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "code": exc.code,
                "data": exc.extra if exc.extra else None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        first_err = exc.errors()[0] if exc.errors() else {}
        err_msg = f"{first_err.get('loc', ['field'])[-1]}: {first_err.get('msg', 'validation error')}"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": f"Invalid input: {err_msg}",
                "code": "VALIDATION_ERROR",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled server error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "An internal server error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
            },
        )

    # Mount API v1
    app.include_router(api_v1_router, prefix="/api/v1")

    # Root redirect / ping
    @app.get("/", tags=["Root"])
    def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs_url": "/docs" if settings.DEBUG else "Disabled in production",
            "api_v1": "/api/v1",
        }

    return app


app = create_application()

