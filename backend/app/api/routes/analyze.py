"""
YAMA AI — Analysis API Route
Deep analysis endpoint for structured legal reasoning.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.schemas import AnalyzeRequest, LegalAnalysis, LawSectionResponse
from app.services.retrieval_engine.rag_pipeline import RAGPipeline
from app.core.constants import SAFETY_DISCLAIMER

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post("/", response_model=LegalAnalysis)
async def deep_analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Perform deep IRAC analysis on a legal situation.
    Returns structured analysis with fact summary, legal questions,
    relevant laws, interpretation, evidence guidance, and procedures.
    """
    try:
        pipeline = RAGPipeline(db)
        result = pipeline.analyze_situation(request.situation, request.category)

        relevant_sections = [
            LawSectionResponse.model_validate(law) for law in result["relevant_laws"]
        ]

        return LegalAnalysis(
            fact_summary=_extract_section(result["analysis"], "FACT SUMMARY"),
            legal_questions=_extract_list_section(result["analysis"], "LEGAL QUESTIONS"),
            relevant_laws=relevant_sections,
            legal_interpretation=_extract_section(result["analysis"], "LEGAL INTERPRETATION"),
            evidence_required=_extract_list_section(result["analysis"], "EVIDENCE COMMONLY REQUIRED"),
            possible_procedures=_extract_list_section(result["analysis"], "POSSIBLE LEGAL PROCEDURES"),
            disclaimer=SAFETY_DISCLAIMER.strip(),
            raw_analysis=result["analysis"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _extract_section(text: str, heading: str) -> str:
    """Extract a section from the markdown analysis by heading."""
    import re
    pattern = rf"##\s*[⚖️📋📖🔍📎🏛️⚠️]*\s*{heading}\s*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else f"Section '{heading}' not found in analysis."


def _extract_list_section(text: str, heading: str) -> list[str]:
    """Extract a list section from the markdown analysis."""
    section = _extract_section(text, heading)
    if "not found" in section:
        return [section]

    import re
    items = re.findall(r"[-•*\d.]\s*(.+)", section)
    return items if items else [section]
