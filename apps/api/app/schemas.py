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
    channels: Optional[int] = 1
    source_type: str
    highpass_80hz_applied: Optional[bool] = False
    peak_normalized: Optional[bool] = False
    waveform_data: Optional[List[float]]
    created_at: datetime

    class Config:
        from_attributes = True

class AudioBenchmarkRequest(BaseModel):
    reference_text: str
    hypothesis_text: str

class AudioBenchmarkResponse(BaseModel):
    wer: float
    cer: float
    word_substitutions: int
    word_deletions: int
    word_insertions: int
    reference_word_count: int
    char_substitutions: int
    char_deletions: int
    char_insertions: int
    reference_char_count: int

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
    review_stage: Optional[str] = "unreviewed"
    senior_reviewer_id: Optional[str] = None
    senior_notes: Optional[str] = None
    senior_signed_at: Optional[datetime] = None
    entities: Optional[List[Dict[str, Any]]] = []
    coreference_notes: Optional[str] = None
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

class SeniorReviewRequest(BaseModel):
    decision: str = Field(..., description="senior_approved or changes_requested")
    senior_notes: str
    require_citations_verified: Optional[bool] = True

# --- Evidence & Crawling ---
class CrawlRequest(BaseModel):
    url: str
    claim_id: Optional[str] = None
    investigation_id: Optional[str] = None

class CrawlResponse(BaseModel):
    success: bool
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    canonical_url: Optional[str] = None
    excerpt: Optional[str] = None
    provenance_hash: Optional[str] = None
    reliability_tier: Optional[str] = "primary_verified"
    stance: Optional[str] = "contextualizes"
    confidence: Optional[float] = 0.5
    rationale: Optional[str] = None
    evidence_id: Optional[str] = None
    error: Optional[str] = None

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
    provenance_sha256: Optional[str] = None
    canonical_url: Optional[str] = None
    author: Optional[str] = None

class EvidenceResponse(BaseModel):
    id: str
    title: str
    url: Optional[str]
    canonical_url: Optional[str] = None
    publisher: Optional[str]
    author: Optional[str] = None
    publication_date: Optional[datetime]
    retrieval_date: datetime
    excerpt: Optional[str]
    reliability_tier: str
    provenance_sha256: Optional[str] = None
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

class ReportApprovalRequest(BaseModel):
    action: str = Field("approve", description="approve or request_revision")
    notes: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    investigation_id: str
    title: str
    executive_summary: str
    methodology: Optional[str]
    limitations: Optional[str]
    verdict_summary: Optional[Dict[str, Any]]
    approval_status: Optional[str] = "draft"
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    audio_briefing_path: Optional[str] = None
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

class OllamaStatusResponse(BaseModel):
    status: str  # online, offline, degraded
    endpoint: str
    active_model: str
    available_models: List[str]
    is_installed: bool
    inference_timeout_seconds: int
    system_compatibility: Dict[str, Any]
    error: Optional[str] = None

class ProviderStatusResponse(BaseModel):
    status: str
    gnani_prisma: ProviderStatusItem
    gnani_timbre: ProviderStatusItem
    evon_reasoning: ProviderStatusItem
    ollama: Optional[ProviderStatusItem] = None
    total_calls_logged: int
    system_time: str
