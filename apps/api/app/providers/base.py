from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

class ProviderError(Exception):
    def __init__(self, message: str, status_code: int = 500, provider: str = "unknown", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.provider = provider
        self.details = details or {}

class ProviderAuthError(ProviderError):
    """Triggered on 401/403: Invalid or missing API key"""
    pass

class ProviderQuotaError(ProviderError):
    """Triggered on 429: Rate limit or credit exhaustion"""
    pass

class ProviderNetworkError(ProviderError):
    """Triggered on connection failure or timeout"""
    pass

class ProviderPayloadError(ProviderError):
    """Triggered on unsupported audio format, size exceeded, or invalid schema"""
    pass

@dataclass
class SegmentDTO:
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None
    speaker_label: str = "Speaker 1"
    language: Optional[str] = None
    order_index: int = 0

@dataclass
class TranscriptionResultDTO:
    transcript: str
    detected_language: str
    model_name: str
    provider: str
    segments: List[SegmentDTO]
    execution_time_ms: int
    raw_response: Dict[str, Any]
    is_demo_fallback: bool = False
    warning_message: Optional[str] = None

@dataclass
class TTSResultDTO:
    audio_bytes: bytes
    audio_format: str
    voice: str
    characters_processed: int
    execution_time_ms: int
    is_demo_fallback: bool = False

@dataclass
class ClaimExtractedDTO:
    claim_text: str
    category: str  # statistical, policy, event, quote, historical
    uncertainty_score: float  # 0.0 to 1.0
    segment_index: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    confidence: float = 0.85
    rationale: str = ""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    coreference_notes: str = ""
