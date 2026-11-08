# Gnani AI Official Integration Guide

This document details the exact integration specifications for **Gnani AI** models within the RAVEN platform for the **Great Indian AI Internship Challenge 2026**.

---

## 1. Gnani Prisma Speech-to-Text (STT)

* **Official Developer Platform:** Gnani Vachana (`https://api.vachana.ai`)
* **Endpoint:** `POST https://api.vachana.ai/stt/v3`
* **Authentication Header:**
  ```http
  X-API-Key-ID: <GNANI_API_KEY>
  ```
* **Payload Type:** `multipart/form-data`
* **Form Parameters:**
  * `audio_file`: Binary audio payload (`audio/wav`, `audio/mpeg`, `audio/webm`)
  * `model`: `prisma-v3.0` (Default) or `prisma-v2.5`
  * `language_code`: `indic-auto` (Auto language identification) or specific language tag:
    * `en-IN` — Indian English
    * `hi-IN` — Hindi
    * `kn-IN` — Kannada
    * `ta-IN` — Tamil
    * `te-IN` — Telugu
    * `mr-IN` — Marathi
    * `gu-IN` — Gujarati
    * `bn-IN` — Bengali
    * `ml-IN` — Malayalam
    * `pa-IN` — Punjabi
  * `output_style`: `transcribe`, `verbatim`, `codemix`, or `transliterate`

### Response Schema Normalized by RAVEN
```json
{
  "transcript": "Full decoded transcript string...",
  "detected_language": "indic-auto",
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 4.2,
      "text": "Segment text...",
      "confidence": 0.94,
      "speaker_label": "Speaker 1"
    }
  ],
  "execution_time_ms": 1120
}
```

---

## 2. Gnani Timbre Text-to-Speech (TTS)

* **Endpoint:** `POST https://api.vachana.ai/api/v1/tts/inference`
* **Authentication Header:**
  ```http
  Content-Type: application/json
  X-API-Key-ID: <GNANI_API_KEY>
  ```
* **Request JSON Payload:**
  ```json
  {
    "text": "Executive briefing text to synthesize...",
    "voice": "Nalini",
    "model": "timbre-v2.5",
    "language": "en-IN",
    "speed": 1.0,
    "audio_config": {
      "container": "wav",
      "encoding": "linear_pcm",
      "num_channels": 1,
      "sample_rate": 24000,
      "sample_width": 2
    }
  }
  ```
* **Response:** Binary audio stream (`audio/wav`).

---

## 3. Gnani Evon 30B (Reasoning Model)

* **Architecture:** Hybrid Mamba2-Transformer Mixture-of-Experts (MoE) with 30 billion total parameters (~3.5 billion active parameters per token) and 128K context window.
* **Weights Repository:** Hosted openly on Hugging Face at [`gnani/gnani-evon-v3.3-30B-A3B`](https://huggingface.co/gnani/gnani-evon-v3.3-30B-A3B) under Apache 2.0.
* **Serving:** Self-hosted using vLLM or SGLang running an OpenAI-compatible endpoint:
  ```bash
  python3 -m sglang.launch_server --model-path "gnani/gnani-evon-v3.3-30B-A3B" --port 30000
  ```
* **Heuristic Fallback:** If `EVON_BASE_URL` is omitted, RAVEN utilizes a deterministic syntactic claim extraction and epistemic uncertainty hedge analyzer, avoiding unverified LLM hallucinations.

---

## 4. Error Codes & Resiliency Handling

| HTTP Code | Exception Triggered | Platform Behavior |
|:---|:---|:---|
| **401 / 403** | `ProviderAuthError` | Alerts analyst of invalid `GNANI_API_KEY`; offers demo simulation mode. |
| **429** | `ProviderQuotaError` | Backoff retry notification with usage quota exhaustion notice. |
| **504 / Timeout** | `ProviderNetworkError` | Network timeout threshold set to 60s for STT; retry options displayed. |
| **400 / 413** | `ProviderPayloadError` | Rejects payload exceeding 50MB before dispatching network request. |
