import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import (
    Claim, TranscriptSegment, TranscriptionJob, AudioAsset,
    Investigation, ReviewDecision, ClaimEvidenceLink, AuditEvent
)
from app.schemas import ClaimExtractRequest, ClaimResponse, ClaimReviewRequest
from app.providers.reasoning import ReasoningProvider
from app.providers.base import SegmentDTO
from app.routers.auth import get_current_user, User

router = APIRouter(prefix="/claims", tags=["claims"])

@router.post("/extract")
async def extract_claims_endpoint(
    req: ClaimExtractRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == req.investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    # Locate segments
    if req.job_id:
        job = db.query(TranscriptionJob).filter(TranscriptionJob.id == req.job_id).first()
    else:
        # Find latest job associated with investigation
        job = (
            db.query(TranscriptionJob)
            .join(AudioAsset, AudioAsset.id == TranscriptionJob.audio_asset_id)
            .filter(AudioAsset.investigation_id == req.investigation_id)
            .order_by(TranscriptionJob.created_at.desc())
            .first()
        )

    if not job:
        raise HTTPException(status_code=400, detail="No completed transcription job found for this investigation.")

    segments = db.query(TranscriptSegment).filter(TranscriptSegment.job_id == job.id).order_by(TranscriptSegment.order_index.asc()).all()
    if not segments:
        raise HTTPException(status_code=400, detail="No transcript segments found to extract claims from.")

    # Convert to DTOs
    dto_segments = [
        SegmentDTO(
            start_time=s.start_time,
            end_time=s.end_time,
            text=s.text,
            confidence=s.confidence,
            speaker_label=s.speaker_label,
            language=s.language,
            order_index=s.order_index
        )
        for s in segments
    ]

    reasoning = ReasoningProvider()
    extracted = await reasoning.extract_claims(dto_segments)

    # Persist extracted claims into database
    created_claims = []
    for idx, c in enumerate(extracted):
        # Match segment id if index matches
        segment_id = None
        if c.segment_index is not None and 0 <= c.segment_index < len(segments):
            segment_id = segments[c.segment_index].id

        claim_record = Claim(
            id=str(uuid.uuid4()),
            investigation_id=inv.id,
            segment_id=segment_id,
            claim_text=c.claim_text,
            category=c.category,
            extracted_by="evon_reasoning" if reasoning.is_evon_configured() else "linguistic_extractor",
            uncertainty_score=c.uncertainty_score,
            status="unreviewed",
            order_index=idx
        )
        db.add(claim_record)
        created_claims.append(claim_record)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="CLAIMS_EXTRACTED",
        resource_type="investigation",
        resource_id=inv.id,
        details={"claims_count": len(created_claims), "method": "evon_or_linguistic"}
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Successfully extracted {len(created_claims)} checkable claims.",
        "claims_count": len(created_claims),
        "claims": [
            {
                "id": c.id,
                "claim_text": c.claim_text,
                "category": c.category,
                "uncertainty_score": c.uncertainty_score,
                "status": c.status,
                "order_index": c.order_index
            }
            for c in created_claims
        ]
    }

@router.get("")
def list_claims(
    investigation_id: str = Query(...),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Claim).filter(Claim.investigation_id == investigation_id)
    if status and status != "all":
        query = query.filter(Claim.status == status)

    claims = query.order_by(Claim.order_index.asc()).all()

    result = []
    for c in claims:
        # Check segment times
        start_time = None
        end_time = None
        if c.transcript_segment:
            start_time = c.transcript_segment.start_time
            end_time = c.transcript_segment.end_time

        ev_count = db.query(ClaimEvidenceLink).filter(ClaimEvidenceLink.claim_id == c.id).count()

        result.append(
            ClaimResponse(
                id=c.id,
                investigation_id=c.investigation_id,
                segment_id=c.segment_id,
                claim_text=c.claim_text,
                category=c.category,
                extracted_by=c.extracted_by,
                uncertainty_score=c.uncertainty_score,
                status=c.status,
                order_index=c.order_index,
                created_at=c.created_at,
                updated_at=c.updated_at,
                evidence_count=ev_count,
                start_time=start_time,
                end_time=end_time
            )
        )

    return result

@router.patch("/{id}/review")
def review_claim(
    id: str,
    req: ClaimReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.status = req.decision
    claim.updated_at = datetime.utcnow()

    # Create ReviewDecision record
    review = ReviewDecision(
        id=str(uuid.uuid4()),
        claim_id=claim.id,
        reviewer_id=current_user.id,
        decision=req.decision,
        analyst_notes=req.analyst_notes,
        confidence_rating=req.confidence_rating or 4
    )
    db.add(review)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="CLAIM_REVIEWED",
        resource_type="claim",
        resource_id=claim.id,
        details={"decision": req.decision, "confidence": req.confidence_rating}
    )
    db.add(audit)
    db.commit()

    return {
        "id": claim.id,
        "status": claim.status,
        "review_id": review.id,
        "decision": review.decision,
        "analyst_notes": review.analyst_notes,
        "confidence_rating": review.confidence_rating,
        "reviewed_at": review.reviewed_at
    }
