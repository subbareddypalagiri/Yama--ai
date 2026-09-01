"""
YAMA AI — Pydantic Request/Response Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ── Request Models ──

class ChatRequest(BaseModel):
    """User sends a situation description."""
    message: str = Field(..., min_length=1, max_length=5000, description="Describe your legal situation")
    session_id: Optional[str] = Field(None, description="Chat session ID for context")
    response_style: Literal["default", "roman_english"] = Field(
        "default",
        description="Reply style. Use 'roman_english' for Hinglish in Latin script.",
    )
    response_language: Optional[Literal["english", "hindi", "tamil", "telugu", "kannada", "roman_english"]] = Field(
        None,
        description="Desired response language. If None and input is Roman English, auto-detect. Otherwise defaults to English.",
    )
    input_language: Optional[Literal["auto", "hindi", "tamil", "telugu", "kannada", "english", "roman_english"]] = Field(
        "auto",
        description="Input language. 'auto' for auto-detection.",
    )
    custom_api_key: Optional[str] = Field(None, description="Optional custom API key from the user settings")
    custom_model: Optional[str] = Field(None, description="Optional custom model name from the user settings")


class AnalyzeRequest(BaseModel):
    """Deep analysis request with structured facts."""
    situation: str = Field(..., min_length=20, max_length=10000, description="Detailed situation description")
    category: Optional[str] = Field(None, description="Legal category hint (criminal, civil, etc.)")


class SituationRequest(BaseModel):
    """Primary endpoint — user describes a real-life situation."""
    situation: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Describe your legal situation in plain language",
        examples=["My landlord is refusing to return my security deposit after I vacated the property."],
    )
    category: Optional[str] = Field(
        None,
        description="Optional legal category hint: criminal, civil, constitutional, consumer, cyber, motor_vehicle, family, property, labour, tax",
    )


class LawSearchRequest(BaseModel):
    """Search laws by keyword."""
    query: str = Field(..., min_length=2, max_length=200)
    category: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)


# ── Response Models ──

class LawSectionResponse(BaseModel):
    id: int
    act_name: str
    section_number: str
    title: str
    description: str
    keywords: Optional[str]
    category: str
    punishment: Optional[str]
    old_law_reference: Optional[str]

    class Config:
        from_attributes = True


class SituationAnalysisResponse(BaseModel):
    """Structured response for /analyze-situation endpoint."""
    fact_summary: str = Field(..., description="Summary of key facts extracted from the situation")
    legal_questions: List[str] = Field(..., description="Identified legal issues")
    relevant_laws: List[LawSectionResponse] = Field(..., description="Applicable legal provisions")
    legal_interpretation: str = Field(..., description="How the laws may apply to the situation")
    evidence_required: List[str] = Field(..., description="Types of evidence courts typically consider")
    possible_procedures: List[str] = Field(..., description="Available legal processes and remedies")
    disclaimer: str = Field(..., description="Legal disclaimer")
    raw_analysis: str = Field(..., description="Full IRAC analysis in markdown format")
    engine_mode: str = Field(..., description="'llm' if powered by an LLM, 'standalone' if rule-based")
    laws_retrieved: int = Field(..., description="Number of legal provisions retrieved from the database")


class LegalAnalysis(BaseModel):
    """Structured legal analysis output."""
    fact_summary: str
    legal_questions: List[str]
    relevant_laws: List[LawSectionResponse]
    legal_interpretation: str
    evidence_required: List[str]
    possible_procedures: List[str]
    disclaimer: str
    raw_analysis: str  # Full markdown analysis from AI


class ChatResponse(BaseModel):
    """Chat endpoint response."""
    session_id: str
    analysis: str  # Full markdown response
    relevant_sections: List[LawSectionResponse]
    timestamp: datetime
    detected_input_language: Optional[str] = Field(None, description="Detected input language")
    response_language: Optional[str] = Field(None, description="Response language used")


class SearchResponse(BaseModel):
    """Law search results."""
    query: str
    results: List[LawSectionResponse]
    total: int


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    vector_store: str


# ── Intelligence Suite Models ──

class ScorecardRequest(BaseModel):
    situation: str = Field(..., min_length=5, max_length=10000, description="Detailed situation description")


class ScorecardResponse(BaseModel):
    win_probability: int = Field(..., ge=0, le=100, description="Estimated winning probability percentage")
    risk_level: Literal["Low", "Medium", "High", "Critical"] = Field(..., description="Overall legal risk level")
    primary_risk_factor: str = Field(..., description="Primary risk factor or loophole")
    evidence_booster_tips: List[str] = Field(..., description="Evidence tips under BSA 2023 to boost probability")
    applicable_bns_section: str = Field(..., description="Core BNS 2023 / IT Act section applicable")


class SimulationRequest(BaseModel):
    situation: str = Field(..., min_length=5, max_length=10000, description="Detailed situation description")


class PersonaSimulation(BaseModel):
    role: str = Field(..., description="Role e.g., Advocate YAMA (Counsel), Opponent Counsel, Presiding Judge")
    title: str = Field(..., description="Title or stance")
    arguments: List[str] = Field(..., description="Key legal points or observations")
    legal_citations: List[str] = Field(..., description="Cited laws or Supreme Court judgments")


class SimulationResponse(BaseModel):
    counsel_view: PersonaSimulation
    defense_view: PersonaSimulation
    judge_verdict: PersonaSimulation
    summary: str


class EstimatorRequest(BaseModel):
    situation: str = Field(..., min_length=5, max_length=10000, description="Detailed situation description")


class EstimatorResponse(BaseModel):
    case_type: str = Field(..., description="e.g., Cyber Crime / Criminal / Civil Dispute / Consumer")
    estimated_duration: str = Field(..., description="Expected timeline in court or authority")
    court_fee_stamp_duty: str = Field(..., description="Statutory court stamp duty or fee estimate")
    lawyer_fee_range: str = Field(..., description="Typical litigation fee range across courts")
    fast_track_remedy: str = Field(..., description="Alternative ₹0 fast-track resolution option e.g. Cyber portal / Lok Adalat")
    key_steps_count: int = Field(..., description="Number of legal stages involved")

