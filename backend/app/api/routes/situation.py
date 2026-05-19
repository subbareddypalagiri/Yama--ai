"""
YAMA AI — /analyze-situation API Route
Primary endpoint: accepts a user's real-life situation in plain language
and returns a structured IRAC legal analysis.
"""

import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.schemas import SituationRequest, SituationAnalysisResponse, LawSectionResponse
from app.services.retrieval_engine.rag_pipeline import RAGPipeline
from app.services.ai_engine.reasoning import get_reasoning_engine
from app.core.constants import SAFETY_DISCLAIMER

router = APIRouter(prefix="/analyze-situation", tags=["Situation Analysis"])


@router.post("", response_model=SituationAnalysisResponse)
async def analyze_situation(request: SituationRequest, db: Session = Depends(get_db)):
    """
    Analyze a legal situation described in plain language.

    Workflow:
    1. Receives user's situation text.
    2. Retrieves relevant Indian legal provisions via RAG (vector + keyword search).
    3. Runs IRAC reasoning engine (LLM-powered or standalone).
    4. Returns structured legal analysis with all IRAC sections.

    This endpoint NEVER declares guilt or innocence.
    It only presents possible legal interpretations supported by law.
    """
    try:
        # Run the full RAG pipeline
        pipeline = RAGPipeline(db)
        result = pipeline.analyze_situation(request.situation, request.category)

        analysis_text = result["analysis"]

        # Build structured response from the markdown analysis
        relevant_sections = [
            LawSectionResponse.model_validate(law)
            for law in result["relevant_laws"]
        ]

        engine = get_reasoning_engine()

        return SituationAnalysisResponse(
            fact_summary=_extract_section(analysis_text, "FACT SUMMARY"),
            legal_questions=_extract_list_section(analysis_text, "LEGAL QUESTIONS"),
            relevant_laws=relevant_sections,
            legal_interpretation=_extract_section(analysis_text, "LEGAL INTERPRETATION"),
            evidence_required=_extract_list_section(analysis_text, "EVIDENCE COMMONLY REQUIRED"),
            possible_procedures=_extract_list_section(analysis_text, "POSSIBLE LEGAL PROCEDURES"),
            disclaimer=SAFETY_DISCLAIMER.strip(),
            raw_analysis=analysis_text,
            engine_mode="standalone" if engine.is_standalone else "llm",
            laws_retrieved=result["retrieved_count"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Situation analysis failed: {str(e)}",
        )


# ── Helpers to parse IRAC markdown sections ──

def _extract_section(text: str, heading: str) -> str:
    """Extract a section from the IRAC markdown output by its heading."""
    # Match headings with or without emoji prefixes
    pattern = rf"##\s*[\U0001f000-\U0001ffff\u2600-\u27bf]*\s*{re.escape(heading)}\s*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: try without ## prefix
    pattern2 = rf"\*?\*?{re.escape(heading)}\*?\*?\s*\n(.*?)(?=\n\*?\*?[A-Z]|\n##|\Z)"
    match2 = re.search(pattern2, text, re.DOTALL | re.IGNORECASE)
    return match2.group(1).strip() if match2 else f"[{heading}: See raw_analysis for full details]"


def _extract_list_section(text: str, heading: str) -> list[str]:
    """Extract a bulleted/numbered list section from the IRAC markdown."""
    section = _extract_section(text, heading)
    if section.startswith("["):
        return [section]

    # Match lines starting with -, •, *, or digit.
    items = re.findall(r"[-•*]\s+(.+)", section)
    if not items:
        items = re.findall(r"\d+[.)]\s+(.+)", section)
    return items if items else [section]
