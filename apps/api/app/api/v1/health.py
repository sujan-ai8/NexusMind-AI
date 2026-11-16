from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.app.core.config import settings
from apps.api.app.db.session import get_db
from apps.api.app.schemas.common import HealthResponse

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return HealthResponse(
        status="ok" if db_connected else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database_connected=db_connected,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe for Kubernetes / Docker container orchestrators."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "ready": True}
    except Exception as exc:
        return {"status": "unready", "ready": False, "error": str(exc)}

