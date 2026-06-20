"""
YAMA AI — Chat API Route
Handles conversational legal assistance with context awareness and multi-language support.
Uses IRAC framework for deep analysis when needed.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse, LawSectionResponse
from app.services.retrieval_engine.rag_pipeline import RAGPipeline
from app.services.ai_engine.chat_engine import get_chat_engine
from app.services.ai_engine.reasoning import IRACReasoningEngine
from app.services.language_processing.language_detector import get_language_detector
from app.services.language_processing.translator import get_translator
from app.services.language_processing.transliterator import get_transliterator

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_analyze(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Smart conversational legal assistant with multi-language support.
    - Handles greetings and casual messages
    - Provides concise legal analysis
    - Remembers conversation context for follow-ups
    - Supports Roman English (Hinglish/Tanglish/Kanglish) and other Indian languages
    """
    try:
        # Initialize language processing tools
        language_detector = get_language_detector()
        translator = get_translator()
        transliterator = get_transliterator()
        
        # Detect input language
        detected_language, script_type = language_detector.detect_language(request.message)
        
        # Determine response language
        response_language = request.response_language
        if response_language is None:
            # If input is Roman English, respond in Roman English
            if script_type == "roman_english":
                response_language = "roman_english"
            else:
                response_language = "english"
        
        # Convert input to English for processing
        message_for_analysis = request.message
        
        if detected_language != "english" and script_type == "native_script":
            # Translate native script to English
            message_for_analysis = translator.translate_to_english(
                request.message,
                detected_language
            )
        elif detected_language != "english" and script_type == "roman_english":
            # For Roman English, we'll keep it as-is for now since most LLMs handle it
            # But we could transliterate if needed
            message_for_analysis = request.message
        
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())

        # Check if session exists
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            session = ChatSession(session_id=session_id)
            db.add(session)
            db.commit()
            db.refresh(session)

        # Get conversation history for context
        history = []
        past_messages = (
            db.query(ChatMessage)
            .filter_by(session_id=session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
            .all()
        )
        for msg in reversed(past_messages):
            history.append({"role": msg.role, "content": msg.content})

        # Save user message (original language)
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.message,
        )
        db.add(user_msg)
        db.commit()

        # Smarter message classification for routing
        msg_lower = message_for_analysis.lower().strip()
        is_greeting = False
        greeting_words = ['hi', 'hello', 'hey', 'hlo', 'hii', 'namaste', 'good morning', 'good evening', 'greetings', 'thanks']
        if any(msg_lower == g or msg_lower.startswith(g + " ") for g in greeting_words) and len(msg_lower) < 25:
            is_greeting = True

        relevant_laws = []
        pipeline = None
        if not is_greeting:
            # Retrieve relevant laws using English message (limit to 5 for speed)
            pipeline = RAGPipeline(db)
            relevant_laws = pipeline.retrieve_relevant_laws(message_for_analysis, limit=5)

        # Get smart response from chat engine
        chat_engine = get_chat_engine(
            custom_api_key=request.custom_api_key,
            custom_model=request.custom_model
        )
        
        # Check for deep legal question indicators
        legal_keywords = ['law', 'legal', 'right', 'court', 'section', 'act', 'contract', 'agreement', 
                         'tenant', 'landlord', 'salary', 'wage', 'wrongful', 'damages', 'case']
        has_legal_keyword = any(word in msg_lower for word in legal_keywords)
        
        is_short_followup = len(history) > 0 and len(message_for_analysis) < 50
        is_simple_question = any(word in msg_lower for word in ['what', 'when', 'how', 'which', 'tell', 'explain', 'define']) and len(message_for_analysis) < 80
        
        # Treat very short words like 'hloo', 'hai', 'helo' as short generic queries to prevent heavy IRAC
        is_very_short_generic = len(msg_lower) < 15 and not has_legal_keyword
        
        # Use chat engine for greetings, short generic inputs, and simple questions
        is_llm_active = chat_engine.is_llm_enabled
        
        if is_greeting or is_very_short_generic or (is_short_followup and not has_legal_keyword) or (is_simple_question and not has_legal_keyword):
            response_text = chat_engine.get_response(
                message=message_for_analysis,
                retrieved_laws=relevant_laws,
                session_id=session_id,
                conversation_history=history,
                response_style=request.response_style,
                response_language=response_language,
            )
        else:
            # For actual legal situation analysis, use IRAC engine for proper analysis
            try:
                irac_engine = IRACReasoningEngine()
                is_llm_active = not irac_engine.is_standalone
                
                # Format laws for IRAC analysis
                laws_formatted = []
                for law in relevant_laws:
                    meta = law.get("metadata", {})
                    law_text = f"{meta.get('act_name', 'Unknown')}, Section {meta.get('section_number', 'N/A')}"
                    if meta.get('description'):
                        law_text += f": {meta.get('description')}"
                    laws_formatted.append(law_text)
                
                laws_text = "\n".join(laws_formatted) if laws_formatted else "No specific laws found"
                
                # Perform IRAC analysis
                response_text = irac_engine.analyze(
                    situation=message_for_analysis, 
                    retrieved_laws=laws_text, 
                    response_style=request.response_style, 
                    response_language=response_language
                )
            except Exception as e:
                # If IRAC fails, fallback to chat engine
                print(f"IRAC analysis failed: {e}, using fallback")
                response_text = chat_engine.get_response(
                    message=message_for_analysis,
                    retrieved_laws=relevant_laws,
                    session_id=session_id,
                    conversation_history=history,
                    response_style=request.response_style,
                    response_language=response_language,
                )

        # Convert response to target language if needed (only if LLM didn't handle it directly)
        final_response = response_text
        
        if not is_llm_active:
            if response_language == "roman_english" and detected_language != "english":
                # Translate to native script first, then transliterate to Roman
                if detected_language in ["hindi", "tamil", "telugu", "kannada"]:
                    native_response = translator.translate_from_english(
                        response_text,
                        detected_language
                    )
                    final_response = transliterator.transliterate_to_roman(
                        native_response,
                        detected_language
                    )
            elif response_language == "roman_english" and detected_language == "english":
                # If input was English but user wants Roman English response
                # Default to Hindi Roman English
                native_response = translator.translate_from_english(response_text, "hindi")
                final_response = transliterator.transliterate_to_roman(native_response, "hindi")
            elif response_language in ["hindi", "tamil", "telugu", "kannada"]:
                # Translate to native script
                final_response = translator.translate_from_english(
                    response_text,
                    response_language
                )

        # Save assistant response
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=final_response,
        )
        db.add(assistant_msg)
        db.commit()

        # Format relevant sections for API response
        relevant_sections = []
        if pipeline and relevant_laws:
            law_records = pipeline._resolve_db_records(relevant_laws)
            relevant_sections = [
                LawSectionResponse.model_validate(law) for law in law_records[:5]
            ]

        return ChatResponse(
            session_id=session_id,
            analysis=final_response,
            relevant_sections=relevant_sections,
            timestamp=datetime.now(timezone.utc),
            detected_input_language=detected_language,
            response_language=response_language,
        )

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR in chat_analyze: {str(e)}\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.delete("/{session_id}")
async def clear_chat(session_id: str, db: Session = Depends(get_db)):
    """Clear chat history for a session."""
    session = db.query(ChatSession).filter_by(session_id=session_id).first()
    if session:
        db.query(ChatMessage).filter_by(session_id=session.id).delete()
        db.commit()
        return {"status": "cleared", "session_id": session_id}
    return {"status": "not_found", "session_id": session_id}
