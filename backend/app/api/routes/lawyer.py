"""
YAMA AI — Your Lawyer API Route
Personal lawyer mode: context-aware, profile-based legal advice.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.db.models import ChatSession, ChatMessage
from app.services.retrieval_engine.rag_pipeline import RAGPipeline
from app.services.ai_engine.chat_engine import get_chat_engine

router = APIRouter(prefix="/lawyer", tags=["Lawyer"])


# ── Request / Response schemas ────────────────────────────────────────────────

class ClientProfile(BaseModel):
    name: str
    state: str
    concern: str


class LawyerRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: Optional[str] = "quick"          # quick | deep | rights | document
    lawyer_context: Optional[str] = None
    client_profile: Optional[ClientProfile] = None


class LawyerResponse(BaseModel):
    analysis: str
    session_id: str
    mode: str
    relevant_sections: list = []
    timestamp: str


# ── System prompts per mode ───────────────────────────────────────────────────

MODE_PROMPTS = {
    "quick": """You are a trusted personal lawyer in India. Give a DIRECT, CONCISE answer in 3-5 sentences.
Always mention the specific law section (e.g. IPC/BNS section, CrPC/BNSS section).
Speak like a friend who happens to be a lawyer — warm, clear, no jargon unless necessary.""",

    "deep": """You are a senior advocate in India. Provide a FULL legal analysis using the IRAC framework:
1. ISSUE — What is the core legal question?
2. RULE — Cite specific sections (BNS/IPC, BNSS/CrPC, Constitution, relevant state law, case precedents)
3. APPLICATION — How do these laws apply to this specific situation?
4. CONCLUSION — What are their options, recommended next steps, and realistic outcomes?
Be thorough, cite real Indian laws, and mention landmark Supreme Court/High Court cases if relevant.""",

    "rights": """You are a legal rights advisor in India. Focus SPECIFICALLY on:
- What fundamental/legal rights the person has in this situation
- Which constitutional articles protect them (Part III, Directive Principles)
- What remedies are available (writ petitions, FIR, consumer forum, labour court, etc.)
- What documents/evidence they should preserve
Empower them with knowledge of their rights.""",

    "document": """You are a legal drafter in India. Help the person with:
- Drafting legal notices (Section 80 CPC, demand notices, etc.)
- FIR / police complaint templates
- Consumer complaint drafts
- Simple agreement templates
- Application formats (RTI, stay orders, etc.)
Always include the correct format, required details, and where to send/file it.""",
}


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=LawyerResponse)
async def personal_lawyer(request: LawyerRequest, db: Session = Depends(get_db)):
    """
    Personal lawyer endpoint — context-aware with client profile.
    Wraps the chat engine with a lawyer persona and mode-specific system prompts.
    """
    try:
        # Build enriched message with client context
        profile = request.client_profile
        mode = request.mode or "quick"
        mode_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["quick"])

        if profile:
            context_prefix = (
                f"CLIENT PROFILE:\n"
                f"- Name: {profile.name}\n"
                f"- State: {profile.state} (apply {profile.state} state laws where relevant)\n"
                f"- Primary concern area: {profile.concern}\n\n"
                f"LAWYER MODE: {mode.upper()}\n"
                f"{mode_prompt}\n\n"
                f"CLIENT QUESTION: {request.message}"
            )
        else:
            context_prefix = (
                f"LAWYER MODE: {mode.upper()}\n"
                f"{mode_prompt}\n\n"
                f"CLIENT QUESTION: {request.message}"
            )

        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            session = ChatSession(session_id=session_id)
            db.add(session)
            db.commit()
            db.refresh(session)

        # Get conversation history
        history = []
        past_messages = (
            db.query(ChatMessage)
            .filter_by(session_id=session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(8)
            .all()
        )
        for msg in reversed(past_messages):
            history.append({"role": msg.role, "content": msg.content})

        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.message,
        )
        db.add(user_msg)
        db.commit()

        # Retrieve relevant laws from RAG
        pipeline = RAGPipeline(db)
        relevant_laws = pipeline.retrieve_relevant_laws(request.message, limit=5)

        # Build law context for prompt
        law_context = ""
        if relevant_laws:
            law_context = "\n\nRELEVANT LAWS FROM DATABASE:\n"
            for law in relevant_laws[:5]:
                law_context += f"- {law.get('act_name', '')}, Section {law.get('section_number', '')}: {law.get('title', '')}\n"
                if law.get('description'):
                    law_context += f"  {law['description'][:200]}...\n"

        full_prompt = context_prefix + law_context

        # Get AI response
        chat_engine = get_chat_engine()
        response_text = await chat_engine.generate_response(
            message=full_prompt,
            history=history,
            relevant_laws=relevant_laws,
            response_style="default",
        )

        # Save assistant response
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=response_text,
        )
        db.add(assistant_msg)
        db.commit()

        # Format relevant sections for frontend
        relevant_sections = [
            {
                "act_name": law.get("act_name", ""),
                "section_number": law.get("section_number", ""),
                "title": law.get("title", ""),
                "category": law.get("category", "general"),
            }
            for law in relevant_laws[:5]
        ]

        return LawyerResponse(
            analysis=response_text,
            session_id=session_id,
            mode=mode,
            relevant_sections=relevant_sections,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Lawyer engine error: {str(exc)}")
