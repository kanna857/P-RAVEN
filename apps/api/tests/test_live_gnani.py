import pytest
import os
from app.config import settings
from app.providers.gnani_speech import GnaniSpeechProvider
from app.providers.gnani_tts import GnaniTTSProvider

@pytest.mark.asyncio
async def test_gnani_speech_adapter_configuration():
    provider = GnaniSpeechProvider()
    assert provider.endpoint == f"{settings.GNANI_BASE_URL.rstrip('/')}/stt/v3"
    # Even without key, it should fallback safely with clear warning in demo mode
    result = await provider.transcribe(
        audio_bytes=b"RIFFsampleaudiobytes",
        filename="test.wav",
        language_code="indic-auto"
    )
    assert result.transcript != ""
    assert len(result.segments) > 0
    if not settings.GNANI_API_KEY:
        assert result.is_demo_fallback is True
        assert result.warning_message is not None

@pytest.mark.asyncio
async def test_gnani_tts_adapter_configuration():
    tts = GnaniTTSProvider()
    assert tts.endpoint == f"{settings.GNANI_BASE_URL.rstrip('/')}/api/v1/tts/inference"
    result = await tts.synthesize(
        text="Testing Gnani Timbre neural voice synthesis adapter.",
        voice="Nalini"
    )
    assert len(result.audio_bytes) > 0
    assert result.audio_format == "audio/wav"
