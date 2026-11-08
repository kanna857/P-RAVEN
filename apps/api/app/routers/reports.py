import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Report, Investigation, Claim, ClaimEvidenceLink, EvidenceSource, AuditEvent
from app.schemas import ReportGenerateRequest, ReportResponse
from app.services.export_service import export_report_markdown
from app.routers.auth import get_current_user, User

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/generate", response_model=ReportResponse)
def generate_report(
    req: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == req.investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    claims = db.query(Claim).filter(Claim.investigation_id == inv.id).all()
    
    # Calculate claim breakdown
    supported = sum(1 for c in claims if c.status in ("verified_supported", "supported"))
    refuted = sum(1 for c in claims if c.status in ("refuted", "verified_refuted"))
    inconclusive = sum(1 for c in claims if c.status == "inconclusive")
    unreviewed = sum(1 for c in claims if c.status == "unreviewed")
    needs_context = sum(1 for c in claims if c.status == "needs_context")

    verdict_summary = {
        "total_claims": len(claims),
        "supported": supported,
        "refuted": refuted,
        "inconclusive": inconclusive,
        "unreviewed": unreviewed,
        "needs_context": needs_context,
        "completion_rate": round(((len(claims) - unreviewed) / max(1, len(claims))) * 100, 1)
    }

    # Generate summary if not explicitly provided
    if not req.executive_summary:
        summary = (
            f"Investigation into '{inv.title}' reviewed {len(claims)} spoken claims extracted from verified audio recordings. "
            f"Analyst review confirmed {supported} claim(s) supported by primary records, {refuted} claim(s) refuted by official evidence, "
            f"and {inconclusive} inconclusive statement(s). Findings indicate substantial public interest findings requiring documented corroboration."
        )
    else:
        summary = req.executive_summary

    report = Report(
        id=str(uuid.uuid4()),
        investigation_id=inv.id,
        title=req.title,
        executive_summary=summary,
        methodology=req.methodology or "Cross-reference of speech audio transcript with certified government gazettes, pollution audits, and regulatory disclosures.",
        limitations=req.limitations or "Hospital admission data and specific micro-level municipal contractor records remain subject to ongoing public information requests.",
        verdict_summary=verdict_summary
    )
    db.add(report)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="REPORT_GENERATED",
        resource_type="report",
        resource_id=report.id,
        details={"investigation_id": inv.id, "claims_total": len(claims)}
    )
    db.add(audit)
    db.commit()
    db.refresh(report)

    return ReportResponse(
        id=report.id,
        investigation_id=report.investigation_id,
        title=report.title,
        executive_summary=report.executive_summary,
        methodology=report.methodology,
        limitations=report.limitations,
        verdict_summary=report.verdict_summary,
        created_at=report.created_at
    )

@router.get("")
def list_reports(
    investigation_id: str = Query(...),
    db: Session = Depends(get_db)
):
    reports = db.query(Report).filter(Report.investigation_id == investigation_id).order_by(Report.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "investigation_id": r.investigation_id,
            "title": r.title,
            "executive_summary": r.executive_summary,
            "methodology": r.methodology,
            "limitations": r.limitations,
            "verdict_summary": r.verdict_summary,
            "audio_briefing_path": r.audio_briefing_path,
            "created_at": r.created_at
        }
        for r in reports
    ]

@router.get("/{id}/export")
def export_report(
    id: str,
    format: str = Query("markdown", regex="^(markdown|json)$"),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    inv = db.query(Investigation).filter(Investigation.id == report.investigation_id).first()
    claims = db.query(Claim).filter(Claim.investigation_id == report.investigation_id).all()

    if format == "markdown":
        md = export_report_markdown(report, inv.title if inv else "Investigation", claims, [])
        return Response(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="report_{report.id[:8]}.md"'}
        )
    else:
        data = {
            "report_id": report.id,
            "title": report.title,
            "investigation_title": inv.title if inv else "",
            "executive_summary": report.executive_summary,
            "methodology": report.methodology,
            "limitations": report.limitations,
            "verdict_summary": report.verdict_summary,
            "claims": [
                {
                    "id": c.id,
                    "text": c.claim_text,
                    "status": c.status,
                    "category": c.category,
                    "uncertainty_score": c.uncertainty_score
                }
                for c in claims
            ],
            "created_at": report.created_at.isoformat()
        }
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="report_{report.id[:8]}.json"'}
        )
