import io
import time
import wave
import math
import struct
import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings
from app.providers.base import (
    TTSResultDTO, ProviderAuthError, ProviderQuotaError,
    ProviderNetworkError, ProviderPayloadError, ProviderError
)

logger = logging.getLogger("raven.providers.gnani_tts")

class GnaniTTSProvider:
    """
    Adapter for Gnani AI Timbre Text-to-Speech API.
    Endpoint: https://api.vachana.ai/api/v1/tts/inference
    Header: X-API-Key-ID: <GNANI_API_KEY>
    Model: timbre-v2.5 (or timbre-v3.0)
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GNANI_API_KEY
        self.base_url = (base_url or settings.GNANI_BASE_URL).rstrip("/")
        self.endpoint = f"{self.base_url}/api/v1/tts/inference"
        self.timeout = 45.0

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def synthesize(
        self,
        text: str,
        voice: str = "Nalini",
        language: str = "en-IN",
        model: str = "timbre-v2.5",
        speed: float = 1.0
    ) -> TTSResultDTO:
        start_time = time.time()

        if not self.is_configured():
            if settings.DEMO_MODE_ALLOWED:
                logger.info("Gnani API key not configured for Timbre. Generating demonstration audio tone.")
                return self._generate_sample_audio(text, voice)
            else:
                raise ProviderAuthError(
                    "GNANI_API_KEY is not configured in backend environment variables.",
                    status_code=401,
                    provider="gnani_timbre"
                )

        headers = {
            "Content-Type": "application/json",
            "X-API-Key-ID": self.api_key,
        }

        payload = {
            "text": text,
            "voice": voice,
            "model": model or settings.GNANI_TIMBRE_MODEL,
            "language": language,
            "speed": speed,
            "audio_config": {
                "container": "wav",
                "encoding": "linear_pcm",
                "num_channels": 1,
                "sample_rate": 24000,
                "sample_width": 2
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.endpoint,
                    headers=headers,
                    json=payload
                )

                execution_time_ms = int((time.time() - start_time) * 1000)

                if response.status_code == 401 or response.status_code == 403:
                    raise ProviderAuthError(
                        f"Gnani Timbre API authentication failed ({response.status_code}): {response.text}",
                        status_code=response.status_code,
                        provider="gnani_timbre"
                    )
                elif response.status_code == 429:
                    raise ProviderQuotaError(
                        "Gnani Timbre rate limit reached or credits exhausted (HTTP 429).",
                        status_code=429,
                        provider="gnani_timbre"
                    )
                elif response.status_code >= 400:
                    raise ProviderError(
                        f"Gnani Timbre API error ({response.status_code}): {response.text}",
                        status_code=response.status_code,
                        provider="gnani_timbre"
                    )

                audio_content = response.content
                return TTSResultDTO(
                    audio_bytes=audio_content,
                    audio_format="audio/wav",
                    voice=voice,
                    characters_processed=len(text),
                    execution_time_ms=execution_time_ms,
                    is_demo_fallback=False
                )

        except httpx.TimeoutException as exc:
            raise ProviderNetworkError(
                f"Gnani Timbre request timed out: {str(exc)}",
                status_code=504,
                provider="gnani_timbre"
            )
        except httpx.RequestError as exc:
            raise ProviderNetworkError(
                f"Gnani Timbre network error: {str(exc)}",
                status_code=502,
                provider="gnani_timbre"
            )

    def _generate_sample_audio(self, text: str, voice: str) -> TTSResultDTO:
        """
        Creates a clean 2-second WAV chime for sample playback demonstration.
        """
        sample_rate = 24000
        duration = 2.0  # seconds
        num_samples = int(sample_rate * duration)
        
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            # Generate pleasant two-tone chime (440Hz -> 660Hz)
            for i in range(num_samples):
                t = i / sample_rate
                freq = 440.0 if t < 1.0 else 660.0
                envelope = math.exp(-2.5 * (t % 1.0))  # decay
                sample_val = int(32767.0 * 0.3 * envelope * math.sin(2.0 * math.pi * freq * t))
                wav_file.writeframes(struct.pack("<h", sample_val))

        return TTSResultDTO(
            audio_bytes=buffer.getvalue(),
            audio_format="audio/wav",
            voice=f"{voice} (Synthesized Sample Preview)",
            characters_processed=len(text),
            execution_time_ms=55,
            is_demo_fallback=True
        )
