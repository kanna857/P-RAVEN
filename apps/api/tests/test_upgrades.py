import pytest
import os
import wave
import struct
from app.services.audio_processor import convert_to_16k_mono_pcm, calculate_wer_cer
from app.crawler.safety import validate_url_safety
from app.providers.ollama_provider import OllamaProvider
from app.providers.reasoning import ReasoningEngine
from app.providers.base import SegmentDTO

def test_wer_cer_calculation_exact():
    reference = "the quick brown fox jumps over the lazy dog"
    hypothesis = "the fast brown fox jumps over lazy dog"
    
    result = calculate_wer_cer(reference, hypothesis)
    assert result["wer"] > 0.0
    assert result["cer"] > 0.0
    assert result["reference_word_count"] == 9
    assert result["hypothesis_word_count"] == 8
    # "quick" -> "fast" is 1 substitution, "the" before lazy is 1 deletion
    assert result["substitutions"] == 1
    assert result["deletions"] == 1

def test_wer_cer_identical_text():
    text = "Bengaluru civic body allocates 1200 crore for stormwater drains"
    result = calculate_wer_cer(text, text)
    assert result["wer"] == 0.0
    assert result["cer"] == 0.0
    assert result["accuracy_percent"] == 100.0

def test_anti_ssrf_validator_blocks_internal_and_cloud_metadata():
    # Loopback
    is_safe, reason = validate_url_safety("http://127.0.0.1:8000/secret")
    assert not is_safe

    is_safe, reason = validate_url_safety("http://localhost/admin")
    assert not is_safe

    # RFC 1918 Private ranges
    assert not validate_url_safety("http://192.168.1.10/router")[0]
    assert not validate_url_safety("http://10.0.0.5/internal")[0]
    assert not validate_url_safety("http://172.16.50.2/api")[0]

    # Cloud metadata (AWS/GCP/Azure)
    assert not validate_url_safety("http://169.254.169.254/latest/meta-data")[0]

    # Non-HTTP schemes
    assert not validate_url_safety("file:///etc/passwd")[0]
    assert not validate_url_safety("ftp://ftp.internal.org/data")[0]

def test_anti_ssrf_validator_allows_permitted_public_domains():
    is_safe, reason = validate_url_safety("https://en.wikipedia.org/wiki/Bengaluru")
    assert is_safe

def test_audio_processor_wav_conversion(tmp_path):
    # Generate 1 second synthetic stereo 44.1kHz WAV
    raw_wav_path = str(tmp_path / "synthetic_stereo.wav")
    out_wav_path = str(tmp_path / "processed_mono_16k.wav")

    sample_rate = 44100
    with wave.open(raw_wav_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        # 100 samples
        data = []
        for i in range(100):
            data.append(struct.pack("<hh", 1000, 1000))
        w.writeframes(b"".join(data))

    meta = convert_to_16k_mono_pcm(
        input_path=raw_wav_path,
        output_path=out_wav_path,
        target_sample_rate=16000,
        apply_highpass_80hz=True,
        apply_peak_normalization=True
    )

    assert os.path.exists(out_wav_path)
    assert meta["channels"] == 1
    assert meta["sample_rate"] == 16000

    # Verify output WAV properties
    with wave.open(out_wav_path, "rb") as out_w:
        assert out_w.getnchannels() == 1
        assert out_w.getframerate() == 16000
        assert out_w.getsampwidth() == 2

@pytest.mark.asyncio
async def test_ollama_provider_health_when_offline():
    # Query non-existent port to test graceful offline reporting
    provider = OllamaProvider(host="http://localhost:59999", model="llama3.2:1b", timeout=2.0)
    health = await provider.check_health()
    assert health["online"] is False
    assert health["active_model"] == "llama3.2:1b"
    assert health["is_active_model_installed"] is False

@pytest.mark.asyncio
async def test_reasoning_engine_extracts_structured_claims():
    engine = ReasoningEngine()
    test_segments = [
        SegmentDTO(
            start_time=0.0,
            end_time=4.5,
            text="The state allocated 450 crore rupees for hospital construction across 12 districts.",
            speaker_label="Speaker 1",
            order_index=0
        ),
        SegmentDTO(
            start_time=4.5,
            end_time=9.0,
            text="In my personal opinion this policy is completely wonderful and everyone loves it.",
            speaker_label="Speaker 1",
            order_index=1
        )
    ]

    claims, engine_name = await engine.extract_claims(test_segments)
    assert len(claims) >= 1
    assert "heuristic" in engine_name or "ollama" in engine_name or "evon" in engine_name
    
    # Statistical claim should be captured
    stat_claim = next((c for c in claims if "450" in c.claim_text or "hospital" in c.claim_text), None)
    assert stat_claim is not None
    assert stat_claim.category in ("statistical", "policy", "factual_assertion")
    assert 0.0 <= stat_claim.uncertainty_score <= 1.0
