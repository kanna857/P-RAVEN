import os
import uuid
import wave
import io
import math
import struct
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.config import settings
from app.models import AudioAsset, TranscriptionJob, TranscriptSegment, ProviderUsage, AuditEvent, Investigation
from app.schemas import AudioAssetResponse, TranscribeRequest, TranscriptResponse
from app.providers.gnani_speech import GnaniSpeechProvider, SUPPORTED_LANGUAGES
from app.services.audio_service import compute_sha256, extract_waveform_and_meta
from app.routers.auth import get_current_user, User

router = APIRouter(tags=["audio"])

@router.post("/audio/upload", response_model=AudioAssetResponse)
async def upload_audio(
    file: UploadFile = File(...),
    investigation_id: str = Form(...),
    source_type: str = Form("upload"),  # upload or microphone
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    # Read audio content with size limit check
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB")

    # Secure filename
    asset_id = str(uuid.uuid4())
    safe_filename = f"{asset_id}_{os.path.basename(file.filename or 'recording.wav')}"
    saved_path = os.path.join(settings.STORAGE_DIR, safe_filename)

    with open(saved_path, "wb") as f:
        f.write(content)

    sha256 = compute_sha256(saved_path)
    mime_type = file.content_type or "audio/wav"
    duration, sample_rate, channels, waveform = extract_waveform_and_meta(saved_path, mime_type)

    audio_asset = AudioAsset(
        id=asset_id,
        investigation_id=investigation_id,
        filename=file.filename or "recording.wav",
        file_path=saved_path,
        mime_type=mime_type,
        size_bytes=len(content),
        duration_seconds=duration,
        sample_rate=sample_rate,
        channels=channels,
        sha256_hash=sha256,
        source_type=source_type,
        waveform_data=waveform
    )
    db.add(audio_asset)

    audit = AuditEvent(
        actor_id=current_user.id,
        action="AUDIO_UPLOADED",
        resource_type="audio_asset",
        resource_id=asset_id,
        details={
            "filename": audio_asset.filename,
            "size_bytes": audio_asset.size_bytes,
            "duration": duration,
            "source_type": source_type
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(audio_asset)

    return AudioAssetResponse(
        id=audio_asset.id,
        investigation_id=audio_asset.investigation_id,
        filename=audio_asset.filename,
        mime_type=audio_asset.mime_type,
        size_bytes=audio_asset.size_bytes,
        duration_seconds=audio_asset.duration_seconds,
        sample_rate=audio_asset.sample_rate,
        source_type=audio_asset.source_type,
        waveform_data=audio_asset.waveform_data,
        created_at=audio_asset.created_at
    )

@router.post("/audio/transcribe")
async def transcribe_audio(
    req: TranscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    audio_asset = db.query(AudioAsset).filter(AudioAsset.id == req.audio_asset_id).first()
    if not audio_asset:
        raise HTTPException(status_code=404, detail="Audio asset not found")

    # Read binary content
    file_bytes = b""
    if os.path.exists(audio_asset.file_path):
        with open(audio_asset.file_path, "rb") as f:
            file_bytes = f.read()
    else:
        # If running in sample mode without a physical file on disk
        file_bytes = b"RIFFsampleaudiobytes"

    # Initialize Gnani Prisma Provider
    provider = GnaniSpeechProvider()
    
    # Create Job record
    job_id = str(uuid.uuid4())
    job = TranscriptionJob(
        id=job_id,
        audio_asset_id=audio_asset.id,
        provider="gnani_prisma",
        model_name=req.model or "prisma-v3.0",
        language_code=req.language_code or "indic-auto",
        status="processing"
    )
    db.add(job)
    db.commit()

    try:
        # Call Gnani STT API (or sample fallback if key unset)
        result = await provider.transcribe(
            audio_bytes=file_bytes,
            filename=audio_asset.filename,
            mime_type=audio_asset.mime_type,
            language_code=req.language_code or "indic-auto",
            model=req.model or "prisma-v3.0",
            output_style=req.output_style or "transcribe"
        )

        job.status = "completed"
        job.detected_language = result.detected_language
        job.execution_time_ms = result.execution_time_ms
        job.raw_response = result.raw_response
        job.completed_at = datetime.utcnow()

        # Save segments
        db_segments = []
        for s in result.segments:
            seg = TranscriptSegment(
                id=str(uuid.uuid4()),
                job_id=job.id,
                start_time=s.start_time,
                end_time=s.end_time,
                text=s.text,
                speaker_label=s.speaker_label,
                confidence=s.confidence,
                language=s.language or result.detected_language,
                order_index=s.order_index
            )
            db.add(seg)
            db_segments.append(seg)

        # Log Provider Usage
        usage = ProviderUsage(
            id=str(uuid.uuid4()),
            provider="gnani_prisma",
            endpoint="/stt/v3",
            characters_or_seconds=audio_asset.duration_seconds or 10.0,
            estimated_units=round((audio_asset.duration_seconds or 10.0) * 0.015, 3),
            status_code=200,
            latency_ms=result.execution_time_ms
        )
        db.add(usage)

        # Audit Event
        audit = AuditEvent(
            actor_id=current_user.id,
            action="TRANSCRIPTION_COMPLETED",
            resource_type="transcription_job",
            resource_id=job.id,
            details={
                "provider": result.provider,
                "detected_language": result.detected_language,
                "segments_count": len(result.segments),
                "is_demo_fallback": result.is_demo_fallback
            }
        )
        db.add(audit)
        db.commit()

        return {
            "job_id": job.id,
            "status": "completed",
            "detected_language": result.detected_language,
            "model_name": result.model_name,
            "execution_time_ms": result.execution_time_ms,
            "is_demo_fallback": result.is_demo_fallback,
            "warning_message": result.warning_message,
            "segments_count": len(db_segments)
        }

    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(exc)}")

@router.get("/jobs/{id}")
def get_job_status(id: str, db: Session = Depends(get_db)):
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "audio_asset_id": job.audio_asset_id,
        "status": job.status,
        "provider": job.provider,
        "model_name": job.model_name,
        "detected_language": job.detected_language,
        "error_message": job.error_message,
        "execution_time_ms": job.execution_time_ms,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }

@router.get("/audio/{id}/file")
def get_audio_file(id: str, db: Session = Depends(get_db)):
    audio_asset = db.query(AudioAsset).filter(AudioAsset.id == id).first()
    if not audio_asset:
        raise HTTPException(status_code=404, detail="Audio asset not found")

    if os.path.exists(audio_asset.file_path):
        return FileResponse(
            audio_asset.file_path,
            media_type=audio_asset.mime_type,
            filename=audio_asset.filename
        )

    # If physical file does not exist on disk, synthesize an audio tone on the fly for playback
    sample_rate = 16000
    duration = audio_asset.duration_seconds or 10.0
    num_samples = int(sample_rate * min(duration, 30.0))
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 320.0 + 80.0 * math.sin(t * 1.5)
            val = int(12000.0 * math.sin(2.0 * math.pi * freq * t))
            wav_file.writeframes(struct.pack("<h", val))

    return Response(content=buffer.getvalue(), media_type="audio/wav")
