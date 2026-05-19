"""
YAMA AI — Report/PDF Generation API Routes
Generate and export PDF reports.
"""

import os
import uuid
import json
from typing import List, Optional
from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import Report, Case, ReportType, Document

router = APIRouter(prefix="/reports", tags=["Reports"])

# Reports directory
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


# ============ SCHEMAS ============

class ReportCreate(BaseModel):
    case_uid: Optional[str] = None
    report_type: str = "case_summary"
    title: str
    include_documents: bool = True
    include_timeline: bool = True
    include_analysis: bool = True


class ReportResponse(BaseModel):
    id: int
    report_uid: str
    case_id: Optional[int]
    report_type: str
    title: str
    file_path: Optional[str]
    file_size: Optional[int]
    generated_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


# ============ PDF GENERATION ============

def generate_case_summary_pdf(case: Case, include_docs: bool, include_timeline: bool, include_analysis: bool) -> bytes:
    """Generate a PDF case summary report."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_CENTER,
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#6B21A8'),
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=16,
        )
        
        elements = []
        
        # Header
        elements.append(Paragraph("YAMA AI", ParagraphStyle('Header', fontSize=10, textColor=colors.grey, alignment=TA_CENTER)))
        elements.append(Paragraph("Legal Case Summary Report", ParagraphStyle('SubHeader', fontSize=12, textColor=colors.grey, alignment=TA_CENTER)))
        elements.append(Spacer(1, 20))
        
        # Title
        elements.append(Paragraph(case.title, title_style))
        elements.append(Spacer(1, 10))
        
        # Case Details Table
        case_data = [
            ["Case ID", case.case_uid[:8] + "..."],
            ["Status", case.status.value.upper() if case.status else "N/A"],
            ["Category", case.category or "N/A"],
            ["Priority", case.priority.upper() if case.priority else "N/A"],
            ["Created", case.created_at.strftime("%d %B %Y") if case.created_at else "N/A"],
        ]
        
        if case.client_name:
            case_data.append(["Client", case.client_name])
        if case.opponent_name:
            case_data.append(["Opponent", case.opponent_name])
        if case.court_name:
            case_data.append(["Court", case.court_name])
        if case.case_number:
            case_data.append(["Case Number", case.case_number])
        if case.next_hearing_date:
            case_data.append(["Next Hearing", case.next_hearing_date.strftime("%d %B %Y")])
        
        table = Table(case_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3E8FF')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Description
        if case.description:
            elements.append(Paragraph("Case Description", heading_style))
            elements.append(Paragraph(case.description, body_style))
        
        # AI Analysis
        if include_analysis and case.ai_summary:
            elements.append(Paragraph("AI Analysis Summary", heading_style))
            elements.append(Paragraph(case.ai_summary, body_style))
        
        if include_analysis and case.relevant_laws:
            elements.append(Paragraph("Relevant Laws", heading_style))
            elements.append(Paragraph(case.relevant_laws, body_style))
        
        if include_analysis and case.risk_assessment:
            elements.append(Paragraph("Risk Assessment", heading_style))
            elements.append(Paragraph(case.risk_assessment, body_style))
        
        # Timeline
        if include_timeline and case.events:
            elements.append(PageBreak())
            elements.append(Paragraph("Case Timeline", heading_style))
            
            for event in sorted(case.events, key=lambda x: x.event_date, reverse=True):
                event_text = f"<b>{event.event_date.strftime('%d %b %Y')}</b> - {event.title}"
                if event.description:
                    event_text += f"<br/>{event.description}"
                elements.append(Paragraph(event_text, body_style))
        
        # Documents
        if include_docs and case.documents:
            elements.append(Paragraph("Attached Documents", heading_style))
            
            doc_data = [["Document", "Type", "Uploaded"]]
            for doc in case.documents:
                doc_data.append([
                    doc.title or doc.original_filename,
                    doc.document_type.value if doc.document_type else "other",
                    doc.uploaded_at.strftime("%d %b %Y") if doc.uploaded_at else "N/A"
                ])
            
            doc_table = Table(doc_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            doc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6B21A8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ]))
            elements.append(doc_table)
        
        # Footer
        elements.append(Spacer(1, 40))
        elements.append(Paragraph(
            f"Generated by YAMA AI on {datetime.now().strftime('%d %B %Y at %H:%M')}",
            ParagraphStyle('Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        elements.append(Paragraph(
            "This report is for informational purposes only and does not constitute legal advice.",
            ParagraphStyle('Disclaimer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    except ImportError:
        # Fallback if reportlab is not installed
        return generate_simple_text_report(case)


def generate_simple_text_report(case: Case) -> bytes:
    """Generate a simple text report as fallback."""
    content = f"""
YAMA AI - Legal Case Summary Report
====================================

Case: {case.title}
Case ID: {case.case_uid}
Status: {case.status.value if case.status else 'N/A'}
Category: {case.category or 'N/A'}
Priority: {case.priority or 'N/A'}
Created: {case.created_at.strftime('%d %B %Y') if case.created_at else 'N/A'}

Description:
{case.description or 'No description provided.'}

AI Summary:
{case.ai_summary or 'No AI analysis available.'}

Relevant Laws:
{case.relevant_laws or 'Not analyzed.'}

---
Generated by YAMA AI on {datetime.now().strftime('%d %B %Y at %H:%M')}
This is for informational purposes only.
"""
    return content.encode('utf-8')


# ============ ROUTES ============

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    """Generate a new PDF report."""
    
    case = None
    if report_data.case_uid:
        case = db.query(Case).filter(Case.case_uid == report_data.case_uid).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
    
    report_uid = str(uuid.uuid4())
    
    # Generate PDF content
    if report_data.report_type == "case_summary" and case:
        pdf_content = generate_case_summary_pdf(
            case,
            report_data.include_documents,
            report_data.include_timeline,
            report_data.include_analysis
        )
        file_ext = ".pdf" if pdf_content[:4] == b'%PDF' else ".txt"
    else:
        pdf_content = b"Report type not supported yet."
        file_ext = ".txt"
    
    # Save file
    filename = f"{report_uid}{file_ext}"
    file_path = os.path.join(REPORTS_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(pdf_content)
    
    # Create report record
    report = Report(
        report_uid=report_uid,
        case_id=case.id if case else None,
        report_type=ReportType(report_data.report_type) if report_data.report_type in [e.value for e in ReportType] else ReportType.CASE_SUMMARY,
        title=report_data.title,
        file_path=file_path,
        file_size=len(pdf_content),
        content_json=json.dumps({
            "include_documents": report_data.include_documents,
            "include_timeline": report_data.include_timeline,
            "include_analysis": report_data.include_analysis,
        }),
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        "id": report.id,
        "report_uid": report.report_uid,
        "case_id": report.case_id,
        "report_type": report.report_type.value if report.report_type else "case_summary",
        "title": report.title,
        "file_path": report.file_path,
        "file_size": report.file_size,
        "generated_at": report.generated_at,
        "download_url": f"/api/v1/reports/{report.report_uid}/download",
    }


@router.get("", response_model=List[ReportResponse])
async def list_reports(
    case_uid: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List generated reports."""
    query = db.query(Report)
    
    if case_uid:
        case = db.query(Case).filter(Case.case_uid == case_uid).first()
        if case:
            query = query.filter(Report.case_id == case.id)
    
    reports = query.order_by(Report.generated_at.desc()).offset(offset).limit(limit).all()
    
    return [{
        "id": r.id,
        "report_uid": r.report_uid,
        "case_id": r.case_id,
        "report_type": r.report_type.value if r.report_type else "case_summary",
        "title": r.title,
        "file_path": r.file_path,
        "file_size": r.file_size,
        "generated_at": r.generated_at,
        "download_url": f"/api/v1/reports/{r.report_uid}/download",
    } for r in reports]


@router.get("/{report_uid}/download")
async def download_report(report_uid: str, db: Session = Depends(get_db)):
    """Download a generated report."""
    report = db.query(Report).filter(Report.report_uid == report_uid).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Determine media type
    media_type = "application/pdf" if report.file_path.endswith(".pdf") else "text/plain"
    filename = f"{report.title.replace(' ', '_')}.pdf" if media_type == "application/pdf" else f"{report.title.replace(' ', '_')}.txt"
    
    return FileResponse(
        report.file_path,
        media_type=media_type,
        filename=filename,
    )


@router.delete("/{report_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_uid: str, db: Session = Depends(get_db)):
    """Delete a report."""
    report = db.query(Report).filter(Report.report_uid == report_uid).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Delete file
    if report.file_path and os.path.exists(report.file_path):
        os.remove(report.file_path)
    
    db.delete(report)
    db.commit()
    return None
