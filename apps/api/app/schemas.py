from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: Optional[str] = "analyst"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Investigation ---
class InvestigationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    primary_language: Optional[str] = "indic-auto"
    tags: Optional[List[str]] = []
    workspace_id: Optional[str] = None

class InvestigationResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    primary_language: str
    tags: List[str]
    is_sample: bool
    created_at: datetime
    updated_at: datetime
    author_id: str
    workspace_id: str
    audio_assets_count: Optional[int] = 0
    claims_count: Optional[int] = 0

    class Config:
        from_attributes = True

# --- Audio & Transcription ---
class AudioAssetResponse(BaseModel):
    id: str
    investigation_id: str
    filename: str
    mime_type: str
    size_bytes: int
    duration_seconds: Optional[float]
    sample_rate: Optional[int]
    source_type: str
    waveform_data: Optional[List[float]]
    created_at: datetime

    class Config:
        from_attributes = True

class TranscribeRequest(BaseModel):
    audio_asset_id: str
    language_code: Optional[str] = "indic-auto"
    model: Optional[str] = "prisma-v3.0"
    output_style: Optional[str] = "transcribe"

class SegmentResponse(BaseModel):
    id: str
    job_id: str
    start_time: float
    end_time: float
    text: str
    speaker_label: str
    confidence: Optional[float]
    language: Optional[str]
    order_index: int

    class Config:
        from_attributes = True

class TranscriptResponse(BaseModel):
    id: str
    audio_asset_id: str
    provider: str
    model_name: str
    language_code: str
    detected_language: Optional[str]
    status: str
    execution_time_ms: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    segments: List[SegmentResponse]
    full_text: Optional[str] = ""

    class Config:
        from_attributes = True

class SegmentUpdateRequest(BaseModel):
    text: str
    speaker_label: Optional[str] = None
    reason: Optional[str] = "Manual analyst correction"

# --- Claims ---
class ClaimExtractRequest(BaseModel):
    investigation_id: str
    job_id: Optional[str] = None

class ClaimResponse(BaseModel):
    id: str
    investigation_id: str
    segment_id: Optional[str]
    claim_text: str
    category: str
    extracted_by: str
    uncertainty_score: float
    status: str
    order_index: int
    created_at: datetime
    updated_at: datetime
    evidence_count: Optional[int] = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    class Config:
        from_attributes = True

class ClaimReviewRequest(BaseModel):
    decision: str = Field(..., description="supported, refuted, inconclusive, needs_context")
    analyst_notes: str
    confidence_rating: Optional[int] = 4

# --- Evidence ---
class EvidenceCreateRequest(BaseModel):
    claim_id: str
    title: str
    url: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[datetime] = None
    excerpt: Optional[str] = None
    reliability_tier: Optional[str] = "primary_verified"
    supports_or_refutes: Optional[str] = "supports"
    relevance_rationale: Optional[str] = None
    source_type: Optional[str] = "web"

class EvidenceResponse(BaseModel):
    id: str
    title: str
    url: Optional[str]
    publisher: Optional[str]
    publication_date: Optional[datetime]
    retrieval_date: datetime
    excerpt: Optional[str]
    reliability_tier: str
    source_type: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Reports ---
class ReportGenerateRequest(BaseModel):
    investigation_id: str
    title: str
    executive_summary: Optional[str] = None
    methodology: Optional[str] = None
    limitations: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    investigation_id: str
    title: str
    executive_summary: str
    methodology: Optional[str]
    limitations: Optional[str]
    verdict_summary: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Voice Briefing ---
class VoiceBriefingRequest(BaseModel):
    report_id: Optional[str] = None
    investigation_id: Optional[str] = None
    text: str
    voice: Optional[str] = "Nalini"
    language: Optional[str] = "en-IN"
    speed: Optional[float] = 1.0

# --- Providers Status ---
class ProviderStatusItem(BaseModel):
    provider_name: str
    status: str  # active_ready, demo_fallback_ready, error, unconfigured
    endpoint: str
    model: str
    auth_configured: bool
    details: Dict[str, Any]

class ProviderStatusResponse(BaseModel):
    status: str
    gnani_prisma: ProviderStatusItem
    gnani_timbre: ProviderStatusItem
    evon_reasoning: ProviderStatusItem
    total_calls_logged: int
    system_time: str
