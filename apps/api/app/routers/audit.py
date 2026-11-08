from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import AuditEvent, ProviderUsage, User

router = APIRouter(tags=["audit"])

@router.get("/audit")
def get_audit_trail(
    limit: int = Query(50, le=200),
    action: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if action:
        query = query.filter(AuditEvent.action == action)

    events = query.order_by(AuditEvent.created_at.desc()).limit(limit).all()

    return [
        {
            "id": e.id,
            "actor_id": e.actor_id,
            "action": e.action,
            "resource_type": e.resource_type,
            "resource_id": e.resource_id,
            "details": e.details,
            "created_at": e.created_at
        }
        for e in events
    ]

@router.get("/usage")
def get_usage_metrics(db: Session = Depends(get_db)):
    usages = db.query(ProviderUsage).order_by(ProviderUsage.timestamp.desc()).limit(100).all()

    total_requests = len(usages)
    total_seconds_audio = sum(u.characters_or_seconds for u in usages if u.provider == "gnani_prisma")
    total_chars_tts = sum(u.characters_or_seconds for u in usages if u.provider == "gnani_timbre")
    avg_latency = (sum(u.latency_ms for u in usages) / max(1, total_requests)) if total_requests > 0 else 0

    return {
        "summary": {
            "total_requests": total_requests,
            "total_audio_seconds_processed": round(total_seconds_audio, 1),
            "total_tts_characters_synthesized": int(total_chars_tts),
            "average_latency_ms": round(avg_latency, 1),
            "currency": "INR / Estimated Units"
        },
        "recent_calls": [
            {
                "id": u.id,
                "provider": u.provider,
                "endpoint": u.endpoint,
                "quantity": u.characters_or_seconds,
                "units": u.estimated_units,
                "status_code": u.status_code,
                "latency_ms": u.latency_ms,
                "timestamp": u.timestamp
            }
            for u in usages[:20]
        ]
    }
