"""
YAMA AI — Analysis API Route
Deep analysis endpoint for structured legal reasoning.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.schemas import (
    AnalyzeRequest, LegalAnalysis, LawSectionResponse,
    ScorecardRequest, ScorecardResponse,
    SimulationRequest, SimulationResponse,
    EstimatorRequest, EstimatorResponse
)
from app.services.retrieval_engine.rag_pipeline import RAGPipeline
from app.services.ai_engine.intelligence_suite import IntelligenceSuiteEngine
from app.core.constants import SAFETY_DISCLAIMER

router = APIRouter(prefix="/analyze", tags=["Analysis"])

# Singleton suite engine
_suite_engine = None

def get_suite_engine() -> IntelligenceSuiteEngine:
    global _suite_engine
    if _suite_engine is None:
        _suite_engine = IntelligenceSuiteEngine()
    return _suite_engine


@router.post("/scorecard", response_model=ScorecardResponse)
async def analyze_scorecard(request: ScorecardRequest):
    """Generate Live Win Probability & Risk Meter."""
    try:
        engine = get_suite_engine()
        return engine.generate_scorecard(request.situation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scorecard analysis failed: {str(e)}")


@router.post("/simulate", response_model=SimulationResponse)
async def analyze_simulate(request: SimulationRequest):
    """Generate 360° Courtroom Simulation (Counsel vs Defense vs Judge)."""
    try:
        engine = get_suite_engine()
        return engine.generate_simulation(request.situation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/estimator", response_model=EstimatorResponse)
async def analyze_estimator(request: EstimatorRequest):
    """Generate Litigation Timeline & Cost Estimator."""
    try:
        engine = get_suite_engine()
        return engine.generate_estimator(request.situation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Estimator analysis failed: {str(e)}")



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
