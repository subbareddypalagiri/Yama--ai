"""
YAMA AI — Ingestion API Routes
Endpoints for managing the legal data ingestion pipeline via HTTP.

Endpoints:
    POST   /api/v1/ingestion/load       — Load a JSON dataset
    POST   /api/v1/ingestion/crawl      — Trigger a crawler
    GET    /api/v1/ingestion/status      — Get ingestion run history
    POST   /api/v1/ingestion/export      — Export data to file
    GET    /api/v1/ingestion/scheduler   — Get scheduler status
"""

import os
import sys
import json
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Ensure ingestion package is importable
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app.db.database import get_db
from app.db.models import IngestionLog, LawSection

logger = logging.getLogger("yama_ai.api.ingestion")

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


# ── Request/Response Models ──

class LoadDatasetRequest(BaseModel):
    """Request to load a list of legal records."""
    laws: List[dict] = Field(..., description="List of law record dicts to ingest")
    source_name: str = Field("api_upload", description="Name to log this ingestion under")


class CrawlRequest(BaseModel):
    """Request to trigger a crawler."""
    source: str = Field(..., description="Source to crawl: india_code, constitution, supreme_court, gazette, state_laws")


class ExportRequest(BaseModel):
    """Request to export data."""
    format: str = Field("json", description="Export format: json, csv, sql, embeddings, all")
    category: Optional[str] = Field(None, description="Filter by category")
    jurisdiction: Optional[str] = Field(None, description="Filter by jurisdiction")


class IngestionLogResponse(BaseModel):
    id: int
    source_name: str
    run_type: str
    status: str
    records_found: int
    records_inserted: int
    records_updated: int
    records_skipped: int
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True


class IngestionStatsResponse(BaseModel):
    total_laws: int
    by_jurisdiction: dict
    by_category: dict
    by_law_type: dict
    by_act: List[dict]
    last_ingestion: Optional[IngestionLogResponse]


# ── Endpoints ──

@router.post("/load")
async def load_dataset(request: LoadDatasetRequest, db: Session = Depends(get_db)):
    """
    Load a list of legal records through the full cleaning + tagging + storage pipeline.
    """
    from ingestion.data_cleaner import DataCleaner
    from ingestion.metadata_tagger import MetadataTagger
    from ingestion.storage_pipeline import StoragePipeline

    if not request.laws:
        raise HTTPException(400, "No laws provided")

    cleaner = DataCleaner()
    tagger = MetadataTagger()
    pipeline = StoragePipeline()

    cleaned, skipped = cleaner.clean_batch(request.laws)
    cleaned = cleaner.deduplicate(cleaned)
    tagged = tagger.tag_batch(cleaned)
    stats = pipeline.store(tagged, source_name=request.source_name)

    return {
        "status": "success",
        "source_name": request.source_name,
        "input_records": len(request.laws),
        "cleaned": len(cleaned),
        "skipped": skipped,
        **stats,
    }


@router.post("/load-file")
async def load_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a JSON file and ingest its contents.
    File should be JSON with a "laws" key containing a list of records.
    """
    from ingestion.data_cleaner import DataCleaner
    from ingestion.metadata_tagger import MetadataTagger
    from ingestion.storage_pipeline import StoragePipeline

    if not file.filename.endswith(".json"):
        raise HTTPException(400, "Only .json files are supported")

    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON file")

    records = data.get("laws", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise HTTPException(400, "Expected a list of law records (or {\"laws\": [...]})")

    cleaner = DataCleaner()
    tagger = MetadataTagger()
    pipeline = StoragePipeline()

    cleaned, skipped = cleaner.clean_batch(records)
    cleaned = cleaner.deduplicate(cleaned)
    tagged = tagger.tag_batch(cleaned)
    stats = pipeline.store(tagged, source_name=f"file:{file.filename}")

    return {
        "status": "success",
        "filename": file.filename,
        "input_records": len(records),
        "cleaned": len(cleaned),
        "skipped": skipped,
        **stats,
    }


@router.post("/crawl")
async def trigger_crawl(request: CrawlRequest):
    """
    Trigger a crawl for a specific data source.
    The crawl runs synchronously and returns results.
    """
    from ingestion.data_cleaner import DataCleaner
    from ingestion.metadata_tagger import MetadataTagger
    from ingestion.storage_pipeline import StoragePipeline

    valid_sources = ["india_code", "constitution", "supreme_court", "high_courts", "gazette", "state_laws"]
    if request.source not in valid_sources:
        raise HTTPException(400, f"Invalid source. Choose from: {valid_sources}")

    # Import and run the appropriate crawler
    try:
        if request.source == "india_code":
            from ingestion.crawlers.india_code_crawler import IndiaCodeCrawler
            crawler = IndiaCodeCrawler()
        elif request.source == "constitution":
            from ingestion.crawlers.constitution_crawler import ConstitutionCrawler
            crawler = ConstitutionCrawler()
        elif request.source == "supreme_court":
            from ingestion.crawlers.court_crawler import SupremeCourtCrawler
            crawler = SupremeCourtCrawler()
        elif request.source == "high_courts":
            from ingestion.crawlers.court_crawler import HighCourtCrawler
            crawler = HighCourtCrawler()
        elif request.source == "gazette":
            from ingestion.crawlers.gazette_crawler import GazetteCrawler
            crawler = GazetteCrawler()
        elif request.source == "state_laws":
            from ingestion.crawlers.gazette_crawler import StateLawCrawler
            crawler = StateLawCrawler()

        with crawler:
            raw_records = crawler.crawl()

        cleaner = DataCleaner()
        tagger = MetadataTagger()
        pipeline = StoragePipeline()

        dicts = [r.to_dict() for r in raw_records]
        cleaned, skipped = cleaner.clean_batch(dicts)
        cleaned = cleaner.deduplicate(cleaned)
        tagged = tagger.tag_batch(cleaned)
        stats = pipeline.store(tagged, source_name=request.source)

        return {
            "status": "success",
            "source": request.source,
            "raw_records": len(raw_records),
            "cleaned": len(cleaned),
            "skipped": skipped,
            **stats,
        }

    except Exception as e:
        logger.error(f"Crawl failed for {request.source}: {e}")
        raise HTTPException(500, f"Crawl failed: {str(e)}")


@router.get("/status", response_model=List[IngestionLogResponse])
async def get_ingestion_status(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent ingestion run history."""
    logs = (
        db.query(IngestionLog)
        .order_by(IngestionLog.started_at.desc())
        .limit(limit)
        .all()
    )
    return [
        IngestionLogResponse(
            id=log.id,
            source_name=log.source_name,
            run_type=log.run_type,
            status=log.status,
            records_found=log.records_found or 0,
            records_inserted=log.records_inserted or 0,
            records_updated=log.records_updated or 0,
            records_skipped=log.records_skipped or 0,
            error_message=log.error_message,
            started_at=str(log.started_at) if log.started_at else None,
            completed_at=str(log.completed_at) if log.completed_at else None,
        )
        for log in logs
    ]


@router.get("/stats", response_model=IngestionStatsResponse)
async def get_ingestion_stats(db: Session = Depends(get_db)):
    """Get summary statistics of the legal database."""
    from sqlalchemy import func

    total = db.query(LawSection).filter_by(is_active=True).count()

    # By jurisdiction
    jurisdiction_counts = dict(
        db.query(LawSection.jurisdiction, func.count())
        .filter_by(is_active=True)
        .group_by(LawSection.jurisdiction)
        .all()
    )

    # By category
    category_counts = dict(
        db.query(LawSection.category, func.count())
        .filter_by(is_active=True)
        .group_by(LawSection.category)
        .all()
    )

    # By law_type
    type_counts = dict(
        db.query(LawSection.law_type, func.count())
        .filter_by(is_active=True)
        .group_by(LawSection.law_type)
        .all()
    )

    # By act (top 20)
    act_counts = (
        db.query(LawSection.act_name, func.count().label("count"))
        .filter_by(is_active=True)
        .group_by(LawSection.act_name)
        .order_by(func.count().desc())
        .limit(20)
        .all()
    )

    # Last ingestion
    last_log = db.query(IngestionLog).order_by(IngestionLog.started_at.desc()).first()
    last_ingestion = None
    if last_log:
        last_ingestion = IngestionLogResponse(
            id=last_log.id,
            source_name=last_log.source_name,
            run_type=last_log.run_type,
            status=last_log.status,
            records_found=last_log.records_found or 0,
            records_inserted=last_log.records_inserted or 0,
            records_updated=last_log.records_updated or 0,
            records_skipped=last_log.records_skipped or 0,
            error_message=last_log.error_message,
            started_at=str(last_log.started_at) if last_log.started_at else None,
            completed_at=str(last_log.completed_at) if last_log.completed_at else None,
        )

    return IngestionStatsResponse(
        total_laws=total,
        by_jurisdiction={k or "unknown": v for k, v in jurisdiction_counts.items()},
        by_category=category_counts,
        by_law_type={k or "unknown": v for k, v in type_counts.items()},
        by_act=[{"act_name": name, "count": count} for name, count in act_counts],
        last_ingestion=last_ingestion,
    )


@router.post("/export")
async def export_data(request: ExportRequest):
    """Export legal data to files (JSON, CSV, SQL, embeddings)."""
    from ingestion.exporter import DataExporter

    exporter = DataExporter()
    filters = {}
    if request.category:
        filters["category"] = request.category
    if request.jurisdiction:
        filters["jurisdiction"] = request.jurisdiction

    try:
        if request.format == "all":
            paths = exporter.export_all(**filters)
        elif request.format == "json":
            paths = {"json": exporter.export_json(**filters)}
        elif request.format == "csv":
            paths = {"csv": exporter.export_csv(**filters)}
        elif request.format == "sql":
            paths = {"sql": exporter.export_sql(**filters)}
        elif request.format == "embeddings":
            paths = {"embeddings": exporter.export_embeddings(**filters)}
        else:
            raise HTTPException(400, f"Invalid format: {request.format}")

        return {
            "status": "success",
            "format": request.format,
            "files": paths,
        }

    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(500, f"Export failed: {str(e)}")
