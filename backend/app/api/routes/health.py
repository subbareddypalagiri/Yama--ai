"""
YAMA AI — Health Check Route
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.models.schemas import HealthResponse
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Check system health: API, database, and vector store."""

    # Check database
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_type = "sqlite" if settings.is_sqlite else "postgresql"
        db_status = f"connected ({db_type})"
    except Exception:
        db_status = "error"

    # Check vector store
    vector_status = "unknown"
    try:
        from app.services.retrieval_engine.vector_store import get_vector_store
        vs = get_vector_store()
        count = vs.get_count()
        vector_status = f"connected ({count} documents)"
    except Exception:
        vector_status = "not initialized"

    return HealthResponse(
        status="healthy" if "connected" in db_status else "degraded",
        version=settings.APP_VERSION,
        database=db_status,
        vector_store=vector_status,
    )
