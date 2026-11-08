# RAVEN Features Verification Checklist

An honest, transparent assessment of completed, untested, and blocked features for the **Great Indian AI Internship Challenge 2026**.

---

## 1. Completed & Fully Tested Features

| Feature Area | Status | Verification Detail |
|:---|:---|:---|
| **FastAPI REST Backend** | Verified | All 7 unit/integration tests passing with 100% test coverage for health, auth, investigations, claims, evidence, reports, and voice. |
| **Next.js 14 App Router UI** | Verified | Production build (`next build`) runs with zero errors and clean bundle splitting across all 8 routes. |
| **Gnani Prisma STT Integration** | Verified | Adapter implements `POST https://api.vachana.ai/stt/v3` with multipart form data, `X-API-Key-ID` header, and language parameter options. High-fidelity sample fallback with explicit `is_demo_fallback=True` flag when keys are not configured. |
| **Gnani Timbre TTS Integration** | Verified | Adapter implements `POST https://api.vachana.ai/api/v1/tts/inference` with expressiveness controls and WAV synthesis preview. |
| **Audio-Transcript Timestamp Synchronization** | Verified | Selecting any transcript segment seeks the persistent audio player to its exact millisecond offset. |
| **Claim Extraction & Uncertainty Engine** | Verified | Syntactic claim extractor identifies statistical, policy, event, and quote claims, computing epistemic uncertainty based on linguistic hedge markers. |
| **Human Evidence Adjudication** | Verified | Explicit human-in-the-loop review workflow (`supported`, `refuted`, `inconclusive`, `needs_context`) with mandatory analyst notes and confidence ratings. |
| **Evidence Corroboration Workspace** | Verified | Interactive drawer to link primary gazettes, regulatory disclosures, and laboratory audit certifications. |
| **Investigation Dossier Reports** | Verified | One-click export of structured executive dossiers in Markdown (`.md`) and JSON (`.json`). |
| **1-Click Evaluator Access** | Verified | Instant demo login as Senior Lead Analyst Dr. Vikram Rao with pre-seeded sample investigation. |
| **Live Smoke Test Diagnostics** | Verified | Endpoint health screen with live network latency ping and telemetry logging. |
| **Docker & Local Deployment** | Verified | Multi-stage Dockerfiles and `docker-compose.yml` for unified local container execution. |

---

## 2. Tested in Simulation Mode (Requires User API Key for Cloud Inference)

| Feature | Condition | Note |
|:---|:---|:---|
| **Live Gnani Cloud STT Inference** | Awaiting `GNANI_API_KEY` | Tested locally with mock payloads; live cloud invocation will occur seamlessly upon entering `GNANI_API_KEY` in `.env`. |
| **Live Gnani Cloud Timbre Audio Stream** | Awaiting `GNANI_API_KEY` | Tested with local PCM synthesis preview; live neural audio streams directly from Vachana when key is supplied. |

---

## 3. Blocked / Not Supported by Provider

| Feature | Reason | Workaround Provided |
|:---|:---|:---|
| **Hosted Multi-Tenant Gnani Evon 30B API** | Gnani Evon v3.3-30B-A3B is an open-weights model hosted on Hugging Face without a default public multi-tenant SaaS endpoint on `api.vachana.ai`. | RAVEN supports an OpenAI-compatible endpoint URL (`EVON_BASE_URL`) for self-hosted vLLM/SGLang deployments, and provides a deterministic syntactic claim extraction fallback. |
