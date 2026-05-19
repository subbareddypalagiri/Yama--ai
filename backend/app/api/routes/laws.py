"""
YAMA AI — Laws API Route
Search, browse, and explore Indian legal provisions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.db.database import get_db
from app.db.models import LawSection
from app.models.schemas import LawSectionResponse, SearchResponse
from app.services.retrieval_engine.rag_pipeline import RAGPipeline

router = APIRouter(prefix="/laws", tags=["Laws"])


@router.get("/search", response_model=SearchResponse)
async def search_laws(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Search legal provisions by keyword or semantic similarity."""
    try:
        pipeline = RAGPipeline(db)
        results = pipeline.search_laws(q, category, limit)

        return SearchResponse(
            query=q,
            results=[LawSectionResponse.model_validate(r) for r in results],
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/sections/{act_name}", response_model=list[LawSectionResponse])
async def get_sections_by_act(
    act_name: str,
    db: Session = Depends(get_db),
):
    """Get all sections of a specific act."""
    results = (
        db.query(LawSection)
        .filter(LawSection.act_name.ilike(f"%{act_name}%"))
        .order_by(LawSection.section_number)
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail=f"No sections found for act: {act_name}")

    return [LawSectionResponse.model_validate(r) for r in results]


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all available legal categories."""
    from app.db.models import LegalCategory
    categories = db.query(LegalCategory).all()
    return [{"id": c.id, "name": c.name, "slug": c.slug, "description": c.description} for c in categories]


@router.get("/acts")
async def get_acts(db: Session = Depends(get_db)):
    """Get all available acts."""
    acts = db.query(LawSection.act_name).distinct().order_by(LawSection.act_name).all()
    return [{"act_name": a[0]} for a in acts]


@router.get("/{law_id}", response_model=LawSectionResponse)
async def get_law_by_id(
    law_id: int,
    db: Session = Depends(get_db),
):
    """Get details of a specific law section by ID."""
    law = db.query(LawSection).filter_by(id=law_id).first()
    if not law:
        raise HTTPException(status_code=404, detail=f"Law section with ID {law_id} not found")
    return LawSectionResponse.model_validate(law)
