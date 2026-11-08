import time
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import ProviderUsage
from app.providers.gnani_speech import GnaniSpeechProvider
from app.providers.gnani_tts import GnaniTTSProvider
from app.providers.reasoning import ReasoningProvider
from app.schemas import ProviderStatusResponse, ProviderStatusItem

router = APIRouter(tags=["providers"])

@router.get("/providers/status", response_model=ProviderStatusResponse)
def get_providers_status(db: Session = Depends(get_db)):
    speech = GnaniSpeechProvider()
    tts = GnaniTTSProvider()
    reasoning = ReasoningProvider()

    prisma_status = "active_ready" if speech.is_configured() else "demo_fallback_ready"
    timbre_status = "active_ready" if tts.is_configured() else "demo_fallback_ready"
    evon_status = "active_ready" if reasoning.is_evon_configured() else "heuristic_fallback_ready"

    total_usages = db.query(ProviderUsage).count()

    return ProviderStatusResponse(
        status="operational",
        gnani_prisma=ProviderStatusItem(
            provider_name="Gnani AI Prisma (STT)",
            status=prisma_status,
            endpoint=speech.endpoint,
            model=settings.GNANI_PRISMA_MODEL,
            auth_configured=speech.is_configured(),
            details={
                "header": "X-API-Key-ID",
                "supported_languages": 10,
                "auto_detect": True,
                "mode": "Live Vachana API" if speech.is_configured() else "Sample Simulation Mode"
            }
        ),
        gnani_timbre=ProviderStatusItem(
            provider_name="Gnani AI Timbre (TTS)",
            status=timbre_status,
            endpoint=tts.endpoint,
            model=settings.GNANI_TIMBRE_MODEL,
            auth_configured=tts.is_configured(),
            details={
                "voices": ["Nalini", "Karan"],
                "streaming_sse": True,
                "mode": "Live Vachana API" if tts.is_configured() else "Sample Audio Preview Mode"
            }
        ),
        evon_reasoning=ProviderStatusItem(
            provider_name="Gnani Evon 30B / Reasoning Engine",
            status=evon_status,
            endpoint=settings.EVON_BASE_URL or "Local Syntactic & Uncertainty Heuristic Engine",
            model=settings.EVON_MODEL_NAME,
            auth_configured=reasoning.is_evon_configured(),
            details={
                "architecture": "Hybrid Mamba2-Transformer MoE (30B)",
                "deployment": "Self-hosted vLLM/SGLang (OpenAI API)" if reasoning.is_evon_configured() else "Deterministic Fact-Claim Heuristic Fallback",
                "open_weights": "gnani/gnani-evon-v3.3-30B-A3B"
            }
        ),
        total_calls_logged=total_usages,
        system_time=datetime.utcnow().isoformat()
    )

@router.post("/providers/test-connection")
async def test_provider_connection():
    """
    Smoke test pinging the official Gnani Vachana endpoint.
    Verifies DNS, connectivity, and response code without mutating data.
    """
    start = time.time()
    endpoint = f"{settings.GNANI_BASE_URL.rstrip('/')}/stt/v3"
    result = {
        "endpoint": endpoint,
        "reachable": False,
        "latency_ms": 0,
        "http_code": None,
        "message": ""
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(endpoint)
            result["latency_ms"] = int((time.time() - start) * 1000)
            result["reachable"] = True
            result["http_code"] = resp.status_code
            result["message"] = f"Endpoint responded with HTTP {resp.status_code}."
    except Exception as exc:
        result["latency_ms"] = int((time.time() - start) * 1000)
        result["message"] = f"Connection check: {str(exc)}"

    return result
