from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.models import TranscriptionJob, TranscriptSegment, TranscriptRevision, AudioAsset, AuditEvent
from app.schemas import TranscriptResponse, SegmentResponse, SegmentUpdateRequest
from app.services.export_service import export_segments_srt, export_segments_txt, export_segments_json
from app.routers.auth import get_current_user, User

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

@router.get("/{id}")
def get_transcript(id: str, db: Session = Depends(get_db)):
    # Try finding job by id, or by audio_asset_id, or find latest job for investigation
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == id).first()
    if not job:
        job = db.query(TranscriptionJob).filter(TranscriptionJob.audio_asset_id == id).order_by(TranscriptionJob.created_at.desc()).first()
    
    if not job:
        # Check if id is investigation_id
        audio = db.query(AudioAsset).filter(AudioAsset.investigation_id == id).first()
        if audio:
            job = db.query(TranscriptionJob).filter(TranscriptionJob.audio_asset_id == audio.id).order_by(TranscriptionJob.created_at.desc()).first()

    if not job:
        raise HTTPException(status_code=404, detail="Transcript or job not found")

    segments = db.query(TranscriptSegment).filter(TranscriptSegment.job_id == job.id).order_by(TranscriptSegment.start_time.asc()).all()
    full_text = " ".join([s.text for s in segments])

    return {
        "id": job.id,
        "audio_asset_id": job.audio_asset_id,
        "provider": job.provider,
        "model_name": job.model_name,
        "language_code": job.language_code,
        "detected_language": job.detected_language,
        "status": job.status,
        "execution_time_ms": job.execution_time_ms,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "full_text": full_text,
        "segments": [
            {
                "id": s.id,
                "job_id": s.job_id,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "text": s.text,
                "speaker_label": s.speaker_label,
                "confidence": s.confidence,
                "language": s.language,
                "order_index": s.order_index
            }
            for s in segments
        ]
    }

@router.patch("/{job_id}/segments/{segment_id}")
def update_segment(
    job_id: str,
    segment_id: str,
    req: SegmentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    seg = db.query(TranscriptSegment).filter(
        TranscriptSegment.id == segment_id,
        TranscriptSegment.job_id == job_id
    ).first()

    if not seg:
        raise HTTPException(status_code=404, detail="Transcript segment not found")

    previous_text = seg.text
    seg.text = req.text
    if req.speaker_label:
        seg.speaker_label = req.speaker_label

    # Save Revision Record
    revision = TranscriptRevision(
        id=str(uuid.uuid4()),
        job_id=job_id,
        editor_user_id=current_user.id,
        previous_text=previous_text,
        new_text=req.text,
        reason=req.reason
    )
    db.add(revision)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="SEGMENT_CORRECTED",
        resource_type="transcript_segment",
        resource_id=segment_id,
        details={"reason": req.reason, "order_index": seg.order_index}
    )
    db.add(audit)
    db.commit()

    return {
        "id": seg.id,
        "job_id": seg.job_id,
        "start_time": seg.start_time,
        "end_time": seg.end_time,
        "text": seg.text,
        "speaker_label": seg.speaker_label,
        "confidence": 1.0,  # human verified
        "language": seg.language,
        "order_index": seg.order_index
    }

@router.get("/{id}/export")
def export_transcript(
    id: str,
    format: str = Query("srt", regex="^(srt|txt|json)$"),
    db: Session = Depends(get_db)
):
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == id).first()
    if not job:
        job = db.query(TranscriptionJob).filter(TranscriptionJob.audio_asset_id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Transcript job not found")

    segments = db.query(TranscriptSegment).filter(TranscriptSegment.job_id == job.id).order_by(TranscriptSegment.start_time.asc()).all()

    if format == "srt":
        content = export_segments_srt(segments)
        media_type = "application/x-subrip"
        filename = f"transcript_{job.id[:8]}.srt"
    elif format == "txt":
        content = export_segments_txt(segments)
        media_type = "text/plain"
        filename = f"transcript_{job.id[:8]}.txt"
    else:
        content = export_segments_json(segments)
        media_type = "application/json"
        filename = f"transcript_{job.id[:8]}.json"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
