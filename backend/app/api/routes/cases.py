"""
YAMA AI — Case Management API Routes
CRUD operations for legal cases.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import uuid

from app.db.database import get_db
from app.db.models import Case, CaseEvent, CaseStatus

router = APIRouter(prefix="/cases", tags=["Cases"])


# ============ SCHEMAS ============

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = None
    priority: str = "medium"
    client_name: Optional[str] = None
    opponent_name: Optional[str] = None
    court_name: Optional[str] = None
    case_number: Optional[str] = None
    next_hearing_date: Optional[datetime] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    client_name: Optional[str] = None
    opponent_name: Optional[str] = None
    court_name: Optional[str] = None
    case_number: Optional[str] = None
    next_hearing_date: Optional[datetime] = None
    ai_summary: Optional[str] = None
    relevant_laws: Optional[str] = None
    risk_assessment: Optional[str] = None


class CaseEventCreate(BaseModel):
    event_type: str = Field(..., pattern="^(note|hearing|document|milestone)$")
    title: str
    description: Optional[str] = None
    event_date: datetime


class CaseResponse(BaseModel):
    id: int
    case_uid: str
    title: str
    description: Optional[str]
    category: Optional[str]
    status: str
    priority: str
    client_name: Optional[str]
    opponent_name: Optional[str]
    court_name: Optional[str]
    case_number: Optional[str]
    next_hearing_date: Optional[datetime]
    ai_summary: Optional[str]
    relevant_laws: Optional[str]
    risk_assessment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    document_count: int = 0
    event_count: int = 0

    class Config:
        from_attributes = True


class CaseEventResponse(BaseModel):
    id: int
    event_type: str
    title: str
    description: Optional[str]
    event_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============ ROUTES ============

@router.get("", response_model=List[CaseResponse])
async def list_cases(
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all cases with optional filters."""
    query = db.query(Case)
    
    if status:
        query = query.filter(Case.status == CaseStatus(status))
    if category:
        query = query.filter(Case.category == category)
    if search:
        query = query.filter(
            Case.title.ilike(f"%{search}%") | 
            Case.description.ilike(f"%{search}%")
        )
    
    cases = query.order_by(Case.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for case in cases:
        case_dict = {
            "id": case.id,
            "case_uid": case.case_uid,
            "title": case.title,
            "description": case.description,
            "category": case.category,
            "status": case.status.value if case.status else "draft",
            "priority": case.priority,
            "client_name": case.client_name,
            "opponent_name": case.opponent_name,
            "court_name": case.court_name,
            "case_number": case.case_number,
            "next_hearing_date": case.next_hearing_date,
            "ai_summary": case.ai_summary,
            "relevant_laws": case.relevant_laws,
            "risk_assessment": case.risk_assessment,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
            "document_count": len(case.documents) if case.documents else 0,
            "event_count": len(case.events) if case.events else 0,
        }
        result.append(case_dict)
    
    return result


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    """Create a new case."""
    case = Case(
        case_uid=str(uuid.uuid4()),
        title=case_data.title,
        description=case_data.description,
        category=case_data.category,
        priority=case_data.priority,
        client_name=case_data.client_name,
        opponent_name=case_data.opponent_name,
        court_name=case_data.court_name,
        case_number=case_data.case_number,
        next_hearing_date=case_data.next_hearing_date,
        status=CaseStatus.DRAFT,
    )
    
    db.add(case)
    db.commit()
    db.refresh(case)
    
    return {
        "id": case.id,
        "case_uid": case.case_uid,
        "title": case.title,
        "description": case.description,
        "category": case.category,
        "status": case.status.value,
        "priority": case.priority,
        "client_name": case.client_name,
        "opponent_name": case.opponent_name,
        "court_name": case.court_name,
        "case_number": case.case_number,
        "next_hearing_date": case.next_hearing_date,
        "ai_summary": case.ai_summary,
        "relevant_laws": case.relevant_laws,
        "risk_assessment": case.risk_assessment,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "document_count": 0,
        "event_count": 0,
    }


@router.get("/{case_uid}", response_model=CaseResponse)
async def get_case(case_uid: str, db: Session = Depends(get_db)):
    """Get a specific case by UID."""
    case = db.query(Case).filter(Case.case_uid == case_uid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {
        "id": case.id,
        "case_uid": case.case_uid,
        "title": case.title,
        "description": case.description,
        "category": case.category,
        "status": case.status.value if case.status else "draft",
        "priority": case.priority,
        "client_name": case.client_name,
        "opponent_name": case.opponent_name,
        "court_name": case.court_name,
        "case_number": case.case_number,
        "next_hearing_date": case.next_hearing_date,
        "ai_summary": case.ai_summary,
        "relevant_laws": case.relevant_laws,
        "risk_assessment": case.risk_assessment,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "document_count": len(case.documents) if case.documents else 0,
        "event_count": len(case.events) if case.events else 0,
    }


@router.patch("/{case_uid}", response_model=CaseResponse)
async def update_case(case_uid: str, case_data: CaseUpdate, db: Session = Depends(get_db)):
    """Update a case."""
    case = db.query(Case).filter(Case.case_uid == case_uid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    update_data = case_data.model_dump(exclude_unset=True)
    
    if "status" in update_data:
        update_data["status"] = CaseStatus(update_data["status"])
    
    for field, value in update_data.items():
        setattr(case, field, value)
    
    db.commit()
    db.refresh(case)
    
    return {
        "id": case.id,
        "case_uid": case.case_uid,
        "title": case.title,
        "description": case.description,
        "category": case.category,
        "status": case.status.value if case.status else "draft",
        "priority": case.priority,
        "client_name": case.client_name,
        "opponent_name": case.opponent_name,
        "court_name": case.court_name,
        "case_number": case.case_number,
        "next_hearing_date": case.next_hearing_date,
        "ai_summary": case.ai_summary,
        "relevant_laws": case.relevant_laws,
        "risk_assessment": case.risk_assessment,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "document_count": len(case.documents) if case.documents else 0,
        "event_count": len(case.events) if case.events else 0,
    }


@router.delete("/{case_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_uid: str, db: Session = Depends(get_db)):
    """Delete a case."""
    case = db.query(Case).filter(Case.case_uid == case_uid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db.delete(case)
    db.commit()
    return None


# ============ CASE EVENTS ============

@router.get("/{case_uid}/events", response_model=List[CaseEventResponse])
async def list_case_events(case_uid: str, db: Session = Depends(get_db)):
    """Get all events for a case."""
    case = db.query(Case).filter(Case.case_uid == case_uid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case.events


@router.post("/{case_uid}/events", response_model=CaseEventResponse, status_code=status.HTTP_201_CREATED)
async def create_case_event(case_uid: str, event_data: CaseEventCreate, db: Session = Depends(get_db)):
    """Add an event to a case timeline."""
    case = db.query(Case).filter(Case.case_uid == case_uid).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    event = CaseEvent(
        case_id=case.id,
        event_type=event_data.event_type,
        title=event_data.title,
        description=event_data.description,
        event_date=event_data.event_date,
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event
