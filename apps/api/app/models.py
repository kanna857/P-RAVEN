import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst")  # analyst, senior_analyst, senior_researcher, admin, auditor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = relationship("WorkspaceMembership", back_populates="user", cascade="all, delete-orphan")
    investigations = relationship("Investigation", back_populates="author")
    audit_events = relationship("AuditEvent", back_populates="actor")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = relationship("WorkspaceMembership", back_populates="workspace", cascade="all, delete-orphan")
    investigations = relationship("Investigation", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMembership(Base):
    __tablename__ = "workspace_memberships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member, viewer
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="memberships")
    user = relationship("User", back_populates="memberships")


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # draft, active, under_review, closed, archived
    primary_language = Column(String(20), default="indic-auto")  # indic-auto, en-IN, hi-IN, ta-IN, etc.
    tags = Column(JSON, default=list)
    is_sample = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="investigations")
    author = relationship("User", back_populates="investigations")
    audio_assets = relationship("AudioAsset", back_populates="investigation", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="investigation", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="investigation", cascade="all, delete-orphan")


class AudioAsset(Base):
    __tablename__ = "audio_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    preprocessed_path = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    sha256_hash = Column(String(64), nullable=True)
    source_type = Column(String(50), default="upload")  # upload, microphone, sample
    highpass_80hz_applied = Column(Boolean, default=False)
    peak_normalized = Column(Boolean, default=False)
    waveform_data = Column(JSON, nullable=True)  # array of normalized float amplitudes for UI
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="audio_assets")
    transcription_jobs = relationship("TranscriptionJob", back_populates="audio_asset", cascade="all, delete-orphan")


class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    audio_asset_id = Column(String(36), ForeignKey("audio_assets.id"), nullable=False)
    provider = Column(String(50), default="gnani_prisma")  # gnani_prisma, demo_mock
    model_name = Column(String(100), default="prisma-v3.0")
    language_code = Column(String(20), default="indic-auto")
    detected_language = Column(String(20), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    wer_score = Column(Float, nullable=True)
    cer_score = Column(Float, nullable=True)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    audio_asset = relationship("AudioAsset", back_populates="transcription_jobs")
    segments = relationship("TranscriptSegment", back_populates="job", cascade="all, delete-orphan")
    revisions = relationship("TranscriptRevision", back_populates="job", cascade="all, delete-orphan")


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("transcription_jobs.id"), nullable=False)
    start_time = Column(Float, nullable=False)  # seconds
    end_time = Column(Float, nullable=False)    # seconds
    text = Column(Text, nullable=False)
    speaker_label = Column(String(50), default="Speaker 1")
    confidence = Column(Float, nullable=True)
    language = Column(String(20), nullable=True)
    order_index = Column(Integer, nullable=False)

    job = relationship("TranscriptionJob", back_populates="segments")
    claims = relationship("Claim", back_populates="transcript_segment")


class TranscriptRevision(Base):
    __tablename__ = "transcript_revisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("transcription_jobs.id"), nullable=False)
    editor_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    previous_text = Column(Text, nullable=False)
    new_text = Column(Text, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("TranscriptionJob", back_populates="revisions")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    segment_id = Column(String(36), ForeignKey("transcript_segments.id"), nullable=True)
    claim_text = Column(Text, nullable=False)
    category = Column(String(100), default="factual_assertion")  # statistical, policy, event, historical, quote
    extracted_by = Column(String(50), default="evon_reasoning")  # evon_reasoning, ollama, heuristic_extractor, analyst
    uncertainty_score = Column(Float, default=0.2)  # 0.0 to 1.0 (epistemic uncertainty)
    status = Column(String(50), default="unreviewed")  # unreviewed, verified_supported, refuted, inconclusive, context_missing
    review_stage = Column(String(50), default="unreviewed")  # unreviewed, primary_adjudicated, senior_approved, changes_requested
    senior_reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    senior_notes = Column(Text, nullable=True)
    senior_signed_at = Column(DateTime, nullable=True)
    entities = Column(JSON, default=list)  # extracted named entities (organizations, locations, amounts)
    coreference_notes = Column(Text, nullable=True)  # cross-sentence context resolution
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="claims")
    transcript_segment = relationship("TranscriptSegment", back_populates="claims")
    evidence_links = relationship("ClaimEvidenceLink", back_populates="claim", cascade="all, delete-orphan")
    review_decisions = relationship("ReviewDecision", back_populates="claim", cascade="all, delete-orphan")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_type = Column(String(50), default="web")  # web, government_gazette, official_data, court_record, archival
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=True)
    canonical_url = Column(String(1000), nullable=True)
    publisher = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    retrieval_date = Column(DateTime, default=datetime.utcnow)
    excerpt = Column(Text, nullable=True)
    reliability_tier = Column(String(50), default="primary_verified")  # primary_verified, secondary_reputable, unverified_claim
    provenance_sha256 = Column(String(64), nullable=True)
    text_fingerprint = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim_links = relationship("ClaimEvidenceLink", back_populates="evidence_source", cascade="all, delete-orphan")


class ClaimEvidenceLink(Base):
    __tablename__ = "claim_evidence_links"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False)
    evidence_id = Column(String(36), ForeignKey("evidence_sources.id"), nullable=False)
    relevance_rationale = Column(Text, nullable=True)
    supports_or_refutes = Column(String(50), default="supports")  # supports, refutes, contextualizes
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="evidence_links")
    evidence_source = relationship("EvidenceSource", back_populates="claim_links")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # supported, refuted, inconclusive, needs_context
    analyst_notes = Column(Text, nullable=False)
    confidence_rating = Column(Integer, default=4)  # 1-5 scale
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="review_decisions")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    methodology = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    verdict_summary = Column(JSON, nullable=True)
    approval_status = Column(String(50), default="draft")  # draft, under_senior_review, senior_approved, published
    approver_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    report_json = Column(JSON, nullable=True)
    audio_briefing_path = Column(String(500), nullable=True)  # Timbre-generated audio file path
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="reports")


class ProviderUsage(Base):
    __tablename__ = "provider_usages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider = Column(String(50), nullable=False)  # gnani_prisma, gnani_timbre, ollama_reasoning, evon_reasoning
    endpoint = Column(String(255), nullable=False)
    characters_or_seconds = Column(Float, nullable=False)
    estimated_units = Column(Float, default=0.0)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g. AUDIO_UPLOADED, TRANSCRIPTION_STARTED, CLAIM_REVIEWED, DUAL_REVIEW_APPROVED
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    actor = relationship("User", back_populates="audit_events")
