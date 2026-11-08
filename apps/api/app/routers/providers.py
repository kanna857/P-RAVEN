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
from app.providers.ollama_provider import OllamaProvider
from app.schemas import ProviderStatusResponse, ProviderStatusItem, OllamaStatusResponse

router = APIRouter(tags=["providers"])

@router.get("/providers/status", response_model=ProviderStatusResponse)
def get_providers_status(db: Session = Depends(get_db)):
    speech = GnaniSpeechProvider()
    tts = GnaniTTSProvider()
    reasoning = ReasoningProvider()
    ollama = OllamaProvider(host=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)

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
        ollama=ProviderStatusItem(
            provider_name="Ollama Local LLM Provider",
            status="active_ready" if getattr(reasoning, "_ollama_available", False) else "standby_or_offline",
            endpoint=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            auth_configured=True,
            details={
                "host": settings.OLLAMA_BASE_URL,
                "active_model": settings.OLLAMA_MODEL,
                "timeout_seconds": settings.OLLAMA_TIMEOUT_SECONDS,
                "suitable_for_8gb_ram": True,
                "recommended_lightweight": ["llama3.2:1b", "llama3.2:3b", "qwen2.5:1.5b"]
            }
        ),
        total_calls_logged=total_usages,
        system_time=datetime.utcnow().isoformat()
    )

@router.get("/providers/ollama/status", response_model=OllamaStatusResponse)
async def get_ollama_status():
    """
    Direct model discovery and health check against local Ollama instance.
    Never pretends a model is installed when it is not.
    """
    ollama = OllamaProvider(host=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
    health = await ollama.check_health()

    if health.get("online"):
        return OllamaStatusResponse(
            status="online",
            endpoint=ollama.host,
            active_model=ollama.model,
            available_models=health.get("installed_models", []),
            is_installed=health.get("is_active_model_installed", False),
            inference_timeout_seconds=int(ollama.timeout),
            system_compatibility={
                "8gb_ram_ready": True,
                "recommended_models": health.get("recommended_lightweight", []),
                "supports_structured_json": True
            }
        )
    else:
        return OllamaStatusResponse(
            status="offline",
            endpoint=ollama.host,
            active_model=ollama.model,
            available_models=[],
            is_installed=False,
            inference_timeout_seconds=int(ollama.timeout),
            system_compatibility={
                "8gb_ram_ready": True,
                "recommended_models": health.get("recommended_lightweight", []),
                "supports_structured_json": True
            },
            error=health.get("error", "Ollama daemon unreachable on localhost:11434")
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
