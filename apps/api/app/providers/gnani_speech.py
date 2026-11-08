import os
import time
import httpx
import logging
from typing import Dict, Any, Optional, List
from app.config import settings
from app.providers.base import (
    TranscriptionResultDTO, SegmentDTO, ProviderAuthError, ProviderQuotaError,
    ProviderNetworkError, ProviderPayloadError, ProviderError
)

logger = logging.getLogger("raven.providers.gnani_speech")

# Supported Prisma v3.0 languages
SUPPORTED_LANGUAGES = {
    "indic-auto": "Automatic Indic Language Detection",
    "en-IN": "Indian English",
    "hi-IN": "Hindi",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "kn-IN": "Kannada",
    "mr-IN": "Marathi",
    "gu-IN": "Gujarati",
    "bn-IN": "Bengali",
    "pa-IN": "Punjabi",
    "ml-IN": "Malayalam",
}

class GnaniSpeechProvider:
    """
    Adapter for Gnani AI Prisma Speech-to-Text API.
    Endpoint: https://api.vachana.ai/stt/v3
    Header: X-API-Key-ID: <GNANI_API_KEY>
    Model: prisma-v3.0 (or prisma-v2.5)
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GNANI_API_KEY
        self.base_url = (base_url or settings.GNANI_BASE_URL).rstrip("/")
        self.endpoint = f"{self.base_url}/stt/v3"
        self.timeout = 60.0  # seconds

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        mime_type: str = "audio/wav",
        language_code: str = "indic-auto",
        model: str = "prisma-v3.0",
        output_style: str = "transcribe"
    ) -> TranscriptionResultDTO:
        """
        Submits audio to Gnani Prisma STT API.
        Falls back to demo simulation if API key is not configured and demo mode is allowed.
        """
        start_time = time.time()

        # Check configuration
        if not self.is_configured():
            if settings.DEMO_MODE_ALLOWED:
                logger.info("Gnani API key not configured. Generating realistic sample transcription.")
                return self._generate_sample_transcription(filename, language_code, model)
            else:
                raise ProviderAuthError(
                    "GNANI_API_KEY is not configured in backend environment variables.",
                    status_code=401,
                    provider="gnani_prisma"
                )

        headers = {
            "X-API-Key-ID": self.api_key,
        }

        files = {
            "audio_file": (filename, audio_bytes, mime_type)
        }

        data = {
            "model": model or settings.GNANI_PRISMA_MODEL,
            "language_code": language_code,
            "output_style": output_style
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.endpoint,
                    headers=headers,
                    files=files,
                    data=data
                )
                
                execution_time_ms = int((time.time() - start_time) * 1000)

                # Handle specific HTTP error codes
                if response.status_code == 401 or response.status_code == 403:
                    raise ProviderAuthError(
                        f"Gnani API authentication failed ({response.status_code}): {response.text}",
                        status_code=response.status_code,
                        provider="gnani_prisma",
                        details={"response": response.text}
                    )
                elif response.status_code == 429:
                    raise ProviderQuotaError(
                        "Gnani API rate limit reached or credits exhausted (HTTP 429).",
                        status_code=429,
                        provider="gnani_prisma",
                        details={"response": response.text}
                    )
                elif response.status_code >= 400 and response.status_code < 500:
                    raise ProviderPayloadError(
                        f"Invalid request sent to Gnani Prisma ({response.status_code}): {response.text}",
                        status_code=response.status_code,
                        provider="gnani_prisma",
                        details={"response": response.text}
                    )
                elif response.status_code >= 500:
                    raise ProviderError(
                        f"Gnani Prisma server error ({response.status_code}): {response.text}",
                        status_code=response.status_code,
                        provider="gnani_prisma",
                        details={"response": response.text}
                    )

                raw_json = response.json()
                return self._parse_gnani_response(raw_json, model, execution_time_ms)

        except httpx.TimeoutException as exc:
            raise ProviderNetworkError(
                f"Gnani Prisma request timed out after {self.timeout}s: {str(exc)}",
                status_code=504,
                provider="gnani_prisma"
            )
        except httpx.RequestError as exc:
            raise ProviderNetworkError(
                f"Gnani Prisma network connection failed: {str(exc)}",
                status_code=502,
                provider="gnani_prisma"
            )

    def _parse_gnani_response(self, raw_json: Dict[str, Any], model: str, execution_time_ms: int) -> TranscriptionResultDTO:
        """
        Parses Gnani API response payload into normalized DTO.
        Typical Gnani responses contain: transcript / text, detected_language, words/segments with timestamps.
        """
        transcript = (
            raw_json.get("transcript") or 
            raw_json.get("text") or 
            raw_json.get("data", {}).get("transcript") or 
            ""
        )
        detected_language = (
            raw_json.get("detected_language") or 
            raw_json.get("language") or 
            raw_json.get("language_code") or 
            "indic-auto"
        )

        segments: List[SegmentDTO] = []
        raw_segments = raw_json.get("segments") or raw_json.get("words") or raw_json.get("data", {}).get("segments") or []

        if raw_segments:
            for idx, item in enumerate(raw_segments):
                segments.append(
                    SegmentDTO(
                        start_time=float(item.get("start_time", item.get("start", 0.0))),
                        end_time=float(item.get("end_time", item.get("end", 0.0))),
                        text=item.get("text", item.get("word", "")),
                        confidence=float(item.get("confidence", 0.9)),
                        speaker_label=item.get("speaker", f"Speaker {item.get('speaker_id', 1)}"),
                        language=item.get("language", detected_language),
                        order_index=idx
                    )
                )
        else:
            # If no detailed segment timestamps returned by the model version, create sentence segments
            sentences = [s.strip() for s in transcript.split(".") if s.strip()]
            duration_per_sentence = 4.0
            for idx, sentence in enumerate(sentences):
                start = idx * duration_per_sentence
                end = start + duration_per_sentence
                segments.append(
                    SegmentDTO(
                        start_time=start,
                        end_time=end,
                        text=sentence + ".",
                        confidence=0.92,
                        speaker_label="Speaker 1",
                        language=detected_language,
                        order_index=idx
                    )
                )

        return TranscriptionResultDTO(
            transcript=transcript,
            detected_language=detected_language,
            model_name=model,
            provider="gnani_prisma",
            segments=segments,
            execution_time_ms=execution_time_ms,
            raw_response=raw_json,
            is_demo_fallback=False
        )

    def _generate_sample_transcription(self, filename: str, language_code: str, model: str) -> TranscriptionResultDTO:
        """
        High-fidelity realistic fallback for demonstration when no live API key is set.
        Explicitly marked with is_demo_fallback=True.
        """
        # Realistic investigative scenario: Municipal drinking water quality & pipeline fund claims (Bengaluru / Karnataka)
        sample_segments = [
            SegmentDTO(
                start_time=0.0,
                end_time=4.2,
                text="The municipal corporation declared that over ninety-four percent of all tested pipeline tap water in the eastern zone is completely potable.",
                confidence=0.96,
                speaker_label="Speaker 1 (Official)",
                language="en-IN",
                order_index=0
            ),
            SegmentDTO(
                start_time=4.3,
                end_time=9.8,
                text="However, independent laboratory samples collected from thirty-two wards in July revealed coliform bacterial contamination exceeding permissible BIS 10500 standards.",
                confidence=0.94,
                speaker_label="Speaker 2 (Investigator)",
                language="en-IN",
                order_index=1
            ),
            SegmentDTO(
                start_time=10.0,
                end_time=15.6,
                text="Officials allocated four hundred and twenty crore rupees under the 2025 water infrastructure modernization grant, yet only eighteen percent of pipeline replacements are physically complete.",
                confidence=0.91,
                speaker_label="Speaker 2 (Investigator)",
                language="en-IN",
                order_index=2
            ),
            SegmentDTO(
                start_time=15.9,
                end_time=21.4,
                text="ನಮ್ಮ ವರದಿಯ ಪ್ರಕಾರ, ಕಲುಷಿತ ನೀರಿನಿಂದಾಗಿ ಕಳೆದ ಮೂರು ತಿಂಗಳಲ್ಲಿ ಆರು ನೂರಕ್ಕೂ ಹೆಚ್ಚು ಪ್ರಕರಣಗಳು ದಾಖಲಾಗಿವೆ. (According to our report, over six hundred cases have been registered due to contaminated water over the last three months.)",
                confidence=0.93,
                speaker_label="Speaker 3 (Local Reporter)",
                language="kn-IN",
                order_index=3
            ),
            SegmentDTO(
                start_time=21.7,
                end_time=27.5,
                text="The municipal health commissioner denied any link between the pipeline repairs and reported gastrointestinal admissions in the peripheral hospitals.",
                confidence=0.89,
                speaker_label="Speaker 1 (Official)",
                language="en-IN",
                order_index=4
            )
        ]

        full_transcript = " ".join([s.text for s in sample_segments])

        return TranscriptionResultDTO(
            transcript=full_transcript,
            detected_language="en-IN / kn-IN (Code-Mixed)",
            model_name=f"{model} [DEMO-MODE-PREVIEW]",
            provider="gnani_prisma (Demo Fallback)",
            segments=sample_segments,
            execution_time_ms=480,
            raw_response={
                "status": "success",
                "mode": "demo_fallback",
                "message": "Generated using high-fidelity sample scenario. Add GNANI_API_KEY in .env to invoke live api.vachana.ai.",
                "total_segments": len(sample_segments),
                "words_count": len(full_transcript.split())
            },
            is_demo_fallback=True,
            warning_message="Running in Demo Mode: GNANI_API_KEY not configured. Transcription simulated from realistic evidence investigation data."
        )
