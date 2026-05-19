"""
YAMA AI — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import chat, laws, analyze, health
from app.api.routes import situation
from app.api.routes import ingestion as ingestion_routes
from app.api.routes import cases, documents, reports
from app.api.routes.lawyer import router as lawyer_router
from app.db.database import engine
from app.db.models import Base

logger = logging.getLogger("yama_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed data automatically."""
    logger.info("Starting YAMA AI — creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Auto-seed if the law_sections table is empty
    from app.db.database import SessionLocal
    from app.db.models import LawSection
    db = SessionLocal()
    try:
        count = db.query(LawSection).count()
        if count == 0:
            logger.info("Empty database detected — running seed...")
            from app.db.init_db import seed_categories, seed_laws
            seed_categories(db)
            seed_laws(db)
            logger.info("Seed complete.")

            # Index into ChromaDB
            try:
                from app.services.retrieval_engine.indexer import index_all_laws
                index_all_laws()
            except Exception as e:
                logger.warning(f"ChromaDB indexing skipped: {e}")
        else:
            logger.info(f"Database has {count} law sections — skipping seed.")
    finally:
        db.close()

    logger.info(f"YAMA AI v{settings.APP_VERSION} ready — LLM provider: {settings.LLM_PROVIDER}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "YAMA AI — Indian Justice Analysis System. "
        "A neutral legal analysis platform that provides objective legal analysis "
        "based on Indian laws using the IRAC framework."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(laws.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(situation.router, prefix="/api/v1")
app.include_router(ingestion_routes.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(lawyer_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Indian Justice Analysis System",
        "docs": "/docs",
        "health": "/api/v1/health",
        "analyze_situation": "/api/v1/analyze-situation",
    }
