"""
YAMA AI — Database Models (SQLAlchemy ORM)
PostgreSQL schema for structured legal data.
"""

import uuid
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, Enum, Float
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# ============ ENUMS ============

class CaseStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DocumentType(enum.Enum):
    COMPLAINT = "complaint"
    FIR = "fir"
    EVIDENCE = "evidence"
    CONTRACT = "contract"
    COURT_ORDER = "court_order"
    LEGAL_NOTICE = "legal_notice"
    AFFIDAVIT = "affidavit"
    OTHER = "other"


class ReportType(enum.Enum):
    CASE_SUMMARY = "case_summary"
    LEGAL_ANALYSIS = "legal_analysis"
    CHAT_EXPORT = "chat_export"
    DOCUMENT_ANALYSIS = "document_analysis"


# ============ CASE MANAGEMENT ============

class Case(Base):
    """Stores user legal cases/matters for tracking."""

    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_uid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)  # criminal, civil, family, etc.
    status = Column(Enum(CaseStatus), default=CaseStatus.DRAFT, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Parties involved
    client_name = Column(String(300), nullable=True)
    opponent_name = Column(String(300), nullable=True)
    
    # Court details (if applicable)
    court_name = Column(String(300), nullable=True)
    case_number = Column(String(100), nullable=True)
    next_hearing_date = Column(DateTime(timezone=True), nullable=True)
    
    # AI Analysis summary
    ai_summary = Column(Text, nullable=True)
    relevant_laws = Column(Text, nullable=True)  # JSON array of law references
    risk_assessment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    events = relationship("CaseEvent", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")
    chat_sessions = relationship("CaseChatSession", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case {self.case_uid}: {self.title}>"


class CaseEvent(Base):
    """Timeline events for a case."""

    __tablename__ = "case_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # note, hearing, document, milestone
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="events")


class CaseChatSession(Base):
    """Links chat sessions to cases."""

    __tablename__ = "case_chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="chat_sessions")


# ============ DOCUMENT MANAGEMENT ============

class Document(Base):
    """Stores uploaded documents for cases."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_uid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)  # nullable for standalone docs
    
    # File info
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    mime_type = Column(String(100), nullable=True)
    
    # Document metadata
    document_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Extracted content
    extracted_text = Column(Text, nullable=True)
    ocr_processed = Column(Boolean, default=False)
    
    # AI Analysis
    ai_analysis = Column(Text, nullable=True)
    detected_entities = Column(Text, nullable=True)  # JSON - names, dates, amounts
    relevant_laws = Column(Text, nullable=True)  # JSON array
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)

    case = relationship("Case", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.doc_uid}: {self.original_filename}>"


# ============ REPORT/PDF GENERATION ============

class Report(Base):
    """Generated PDF reports."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_uid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    
    # Report info
    report_type = Column(Enum(ReportType), nullable=False)
    title = Column(String(500), nullable=False)
    
    # Generated file
    file_path = Column(String(1000), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Content (stored for regeneration)
    content_json = Column(Text, nullable=True)  # JSON structure of report content
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    case = relationship("Case", back_populates="reports")

    def __repr__(self):
        return f"<Report {self.report_uid}: {self.title}>"


# ============ EXISTING MODELS ============


class LawSection(Base):
    """Stores individual sections/provisions of Indian laws."""

    __tablename__ = "law_sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    act_name = Column(String(500), nullable=False, index=True)
    section_number = Column(String(50), nullable=False)
    title = Column(String(1000), nullable=False)
    description = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # comma-separated keywords
    category = Column(String(100), nullable=False, index=True)
    punishment = Column(Text, nullable=True)
    old_law_reference = Column(String(500), nullable=True)  # e.g., "IPC Section 302"

    # --- Ingestion-system fields ---
    jurisdiction = Column(String(50), nullable=True, default="central")  # central / state
    state_name = Column(String(200), nullable=True)
    law_type = Column(String(100), nullable=True)  # act / rule / amendment / article / notification / judgment
    source_url = Column(String(2000), nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)  # SHA-256 for change detection

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_act_section", "act_name", "section_number", unique=True),
    )

    def __repr__(self):
        return f"<LawSection {self.act_name} - Section {self.section_number}>"


class LegalCategory(Base):
    """Categories of law for classification."""

    __tablename__ = "legal_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<LegalCategory {self.name}>"


class ChatSession(Base):
    """Stores user chat sessions for context."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Stores individual messages in a chat session."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class IngestionLog(Base):
    """Tracks each ingestion/crawl run for auditing and deduplication."""

    __tablename__ = "ingestion_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(200), nullable=False, index=True)  # e.g., "india_code", "sci_judgments"
    run_type = Column(String(50), nullable=False)  # full / incremental
    status = Column(String(50), nullable=False, default="running")  # running / completed / failed
    records_found = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<IngestionLog {self.source_name} [{self.status}]>"
