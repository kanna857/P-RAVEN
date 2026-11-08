# RAVEN Architecture & System Design

**RAVEN** (Responsible Audio Verification & Evidence Navigator) is a specialized voice intelligence and evidence investigation platform designed for researchers, civic auditors, and investigative journalists.

---

## 1. End-to-End Pipeline Architecture

```mermaid
flowchart TD
    A[Multilingual Audio Input\nWAV / MP3 / Mic Stream] --> B[FastAPI Audio Ingestion\nSize & MIME Validation]
    B --> C[Gnani Prisma STT\nPOST https://api.vachana.ai/stt/v3\nX-API-Key-ID Header]
    C --> D[Timestamp-Linked Segmentation\nLanguage Identification & Confidence]
    D --> E[Claim Extraction Engine\nEvon 30B MoE or Heuristic Syntactic Scorer]
    E --> F[Epistemic Uncertainty Scoring\nHedge Word & Qualification Weighting]
    F --> G[Evidence Workspace Linking\nPrimary Gazettes, Audits & Records]
    G --> H[Human Analyst Adjudication\nSupported / Refuted / Inconclusive]
    H --> I[Investigation Report Dossier\nExport to Markdown & Structured JSON]
    I --> J[Gnani Timbre Neural TTS\nSpoken Voice Briefing in Indic Languages]
```

---

## 2. Component & Network Topology

```mermaid
flowchart LR
    subgraph Client["Next.js 14 Web Terminal (apps/web)"]
        UI["Editorial Interface\n(Tailwind + Geist/Inter)"]
        State["Zustand Global State\n(Audio Sync & Seeker)"]
        Studio["Transcript Studio & Audio Scrubber"]
        ClaimsView["Claim Adjudication & Evidence Drawer"]
    end

    subgraph Server["FastAPI Backend Service (apps/api)"]
        Router["FastAPI Application Router"]
        Security["JWT & Role Authorization"]
        DB[(SQLite / PostgreSQL)]
        Storage["Validated Audio Storage"]
    end

    subgraph GnaniAI["Gnani AI Vachana Cloud & Models"]
        Prisma["Prisma v3.0\nMultilingual Indic STT"]
        Timbre["Timbre v2.5\nNeural Speech Synthesis"]
        Evon["Evon 30B MoE\nOpen-Weight Reasoning (vLLM)"]
    end

    UI --> Router
    Router --> DB
    Router --> Storage
    Router --> Prisma
    Router --> Timbre
    Router --> Evon
```

---

## 3. Database Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ WORKSPACE_MEMBERSHIP : has
    WORKSPACE ||--o{ WORKSPACE_MEMBERSHIP : contains
    WORKSPACE ||--o{ INVESTIGATION : owns
    USER ||--o{ INVESTIGATION : authors
    INVESTIGATION ||--o{ AUDIO_ASSET : contains
    AUDIO_ASSET ||--o{ TRANSCRIPTION_JOB : processed_by
    TRANSCRIPTION_JOB ||--o{ TRANSCRIPT_SEGMENT : yields
    TRANSCRIPTION_JOB ||--o{ TRANSCRIPT_REVISION : tracks
    INVESTIGATION ||--o{ CLAIM : identifies
    TRANSCRIPT_SEGMENT ||--o{ CLAIM : sources
    CLAIM ||--o{ CLAIM_EVIDENCE_LINK : linked_to
    EVIDENCE_SOURCE ||--o{ CLAIM_EVIDENCE_LINK : provides
    CLAIM ||--o{ REVIEW_DECISION : adjudicated_by
    USER ||--o{ REVIEW_DECISION : executes
    INVESTIGATION ||--o{ REPORT : compiles
    USER ||--o{ AUDIT_EVENT : triggers
```

---

## 4. Key Design Tenets

1. **Epistemic Honesty:** A claim is **never** declared true or false automatically by an AI model. Spoken claims require corroboration against verified primary public records (court judgments, gazettes, certified laboratory tests).
2. **Audio-Text Synchronization:** Selecting any transcript segment instantly scrubs the persistent audio player to that exact millisecond offset.
3. **Transparent Fallbacks:** When the live Gnani API key is not configured, the system gracefully runs in high-fidelity demo mode with clear badges (`is_demo_fallback=True`), preventing broken experiences while never deceiving the user about live API invocation.
4. **Editorial Intelligence UX:** Styled with a restrained palette (`#101B2B` Midnight Navy, `#F6F5F1` Warm Off-White, `#242C35` Graphite, `#2A8C85` Muted Teal, and `#C89448` Restrained Amber) with zero generic gradient decoration.
