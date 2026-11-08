import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import Report, ProviderUsage, AuditEvent
from app.schemas import VoiceBriefingRequest
from app.providers.gnani_tts import GnaniTTSProvider
from app.routers.auth import get_current_user, User

router = APIRouter(prefix="/voice", tags=["voice"])

BRIEFINGS_DIR = os.path.join(settings.STORAGE_DIR, "briefings")
os.makedirs(BRIEFINGS_DIR, exist_ok=True)

@router.post("/briefing")
async def generate_voice_briefing(
    req: VoiceBriefingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.text or len(req.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Briefing text cannot be empty.")

    provider = GnaniTTSProvider()
    
    try:
        tts_result = await provider.synthesize(
            text=req.text,
            voice=req.voice or "Nalini",
            language=req.language or "en-IN",
            speed=req.speed or 1.0
        )

        briefing_id = str(uuid.uuid4())
        audio_filename = f"briefing_{briefing_id}.wav"
        file_path = os.path.join(BRIEFINGS_DIR, audio_filename)

        with open(file_path, "wb") as f:
            f.write(tts_result.audio_bytes)

        # Update report if linked
        if req.report_id:
            report = db.query(Report).filter(Report.id == req.report_id).first()
            if report:
                report.audio_briefing_path = file_path

        # Log Provider Usage
        usage = ProviderUsage(
            id=str(uuid.uuid4()),
            provider="gnani_timbre",
            endpoint="/api/v1/tts/inference",
            characters_or_seconds=len(req.text),
            estimated_units=round(len(req.text) * 0.001, 3),
            status_code=200,
            latency_ms=tts_result.execution_time_ms
        )
        db.add(usage)

        # Audit Event
        audit = AuditEvent(
            actor_id=current_user.id,
            action="VOICE_BRIEFING_GENERATED",
            resource_type="voice_briefing",
            resource_id=briefing_id,
            details={
                "voice": tts_result.voice,
                "characters": tts_result.characters_processed,
                "is_demo_fallback": tts_result.is_demo_fallback
            }
        )
        db.add(audit)
        db.commit()

        return {
            "briefing_id": briefing_id,
            "voice": tts_result.voice,
            "characters_processed": tts_result.characters_processed,
            "execution_time_ms": tts_result.execution_time_ms,
            "is_demo_fallback": tts_result.is_demo_fallback,
            "audio_url": f"/api/voice/{briefing_id}/audio"
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Voice briefing synthesis failed: {str(exc)}")

@router.get("/{briefing_id}/audio")
def get_briefing_audio(briefing_id: str):
    file_path = os.path.join(BRIEFINGS_DIR, f"briefing_{briefing_id}.wav")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(file_path, media_type="audio/wav", filename=f"briefing_{briefing_id[:8]}.wav")
