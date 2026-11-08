import re
import json
import httpx
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.providers.base import ClaimExtractedDTO, SegmentDTO
from app.providers.ollama_provider import OllamaProvider

logger = logging.getLogger("raven.providers.reasoning")

HEDGE_TERMS = {
    "allegedly": 0.45,
    "reported": 0.35,
    "reportedly": 0.40,
    "claims": 0.30,
    "claimed": 0.30,
    "might": 0.35,
    "could": 0.30,
    "perhaps": 0.40,
    "possibly": 0.45,
    "approx": 0.25,
    "approximately": 0.25,
    "rumored": 0.50,
    "purportedly": 0.45,
    "believed to": 0.35,
    "supposedly": 0.45,
}

STATISTICAL_PATTERNS = [
    r"\d+(\.\d+)?%",
    r"\b(percent|crore|lakh|million|billion|thousand|rupees|rs\.?|inr)\b",
    r"\b\d{1,4}\s*(wards|cases|deaths|liters|tonnes|km|kilometres)\b",
    r"\b(ninety|eighty|seventy|sixty|fifty|forty|thirty|twenty|hundred)\b"
]

POLICY_PATTERNS = [
    r"\b(allocated|approved|grant|ordinance|scheme|act|mandate|regulation|guidelines|commissioner|minister)\b"
]

class ReasoningEngine:
    """
    Unified AI Reasoning & Epistemic Uncertainty Engine.
    Abstracts across:
      1. Local Ollama Models (Llama 3.2, Qwen 2.5, Mistral)
      2. Gnani Evon 30B (Open-weight MoE serving via OpenAI-compatible endpoints)
      3. Transparent Heuristic Fallback (clearly labeled)
    """

    def __init__(
        self,
        ollama_host: Optional[str] = None,
        ollama_model: Optional[str] = None,
        evon_base_url: Optional[str] = None,
        evon_api_key: Optional[str] = None
    ):
        self.ollama = OllamaProvider(host=ollama_host or settings.OLLAMA_HOST, model=ollama_model or settings.OLLAMA_MODEL)
        self.evon_base_url = (evon_base_url or settings.EVON_BASE_URL).rstrip("/") if (evon_base_url or settings.EVON_BASE_URL) else None
        self.evon_api_key = evon_api_key or settings.EVON_API_KEY
        self.evon_model_name = settings.EVON_MODEL_NAME

    def is_evon_configured(self) -> bool:
        return bool(self.evon_base_url and len(self.evon_base_url.strip()) > 5)

    async def get_active_provider_info(self) -> Dict[str, Any]:
        """Returns the status of all reasoning providers."""
        ollama_health = await self.ollama.check_health()
        evon_active = bool(self.evon_base_url and len(self.evon_base_url.strip()) > 5)

        active_name = "Heuristic Linguistic Extractor (Fallback)"
        if ollama_health["online"] and ollama_health["is_active_model_installed"]:
            active_name = f"Ollama Local ({self.ollama.model})"
        elif evon_active:
            active_name = f"Gnani Evon 30B ({self.evon_model_name})"

        return {
            "active_provider": active_name,
            "ollama": ollama_health,
            "evon": {
                "configured": evon_active,
                "endpoint": self.evon_base_url or "Not configured",
                "model": self.evon_model_name
            },
            "heuristic_fallback_available": True
        }

    async def extract_claims(self, segments: List[SegmentDTO]) -> Tuple[List[ClaimExtractedDTO], str]:
        """
        Extracts checkable claims through the highest priority active engine.
        Returns: (claims, engine_name)
        """
        # Priority 1: Ollama if online and model pulled
        try:
            ollama_health = await self.ollama.check_health()
            if ollama_health["online"] and ollama_health["is_active_model_installed"]:
                raw_claims = await self.ollama.extract_claims_and_entities(segments)
                claims = []
                for c in raw_claims:
                    seg_idx = c.get("segment_index")
                    start_t = None
                    end_t = None
                    if seg_idx is not None and 0 <= seg_idx < len(segments):
                        start_t = segments[seg_idx].start_time
                        end_t = segments[seg_idx].end_time

                    claims.append(ClaimExtractedDTO(
                        claim_text=c.get("claim_text", ""),
                        category=c.get("category", "factual_assertion"),
                        uncertainty_score=float(c.get("uncertainty_score", 0.2)),
                        segment_index=seg_idx,
                        start_time=start_t,
                        end_time=end_t,
                        confidence=0.92,
                        rationale=c.get("coreference_notes") or f"Ollama ({self.ollama.model}) contextual claim extraction."
                    ))
                if claims:
                    return claims, f"ollama_{self.ollama.model}"
        except Exception as exc:
            logger.warning(f"Ollama extraction failed, trying next provider: {exc}")

        # Priority 2: Gnani Evon 30B via OpenAI-compatible endpoint
        if self.evon_base_url:
            try:
                claims = await self._extract_via_evon_api(segments)
                if claims:
                    return claims, "gnani_evon_30b"
            except Exception as exc:
                logger.warning(f"Gnani Evon extraction failed: {exc}")

        # Priority 3: Transparent Heuristic Fallback
        claims = self._extract_via_heuristics(segments)
        return claims, "heuristic_syntactic_engine"

    async def _extract_via_evon_api(self, segments: List[SegmentDTO]) -> List[ClaimExtractedDTO]:
        url = f"{self.evon_base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.evon_api_key:
            headers["Authorization"] = f"Bearer {self.evon_api_key}"

        transcript_text = "\n".join([f"[{s.order_index}] {s.text}" for s in segments])

        prompt = (
            "You are a factual claim extraction system for investigative journalism and verification.\n"
            "Analyze the following transcript and extract distinct checkable factual claims.\n"
            "Respond ONLY with a JSON array of objects with keys: claim_text, category (statistical, policy, event, quote, historical), "
            "uncertainty_score (0.0 to 1.0), segment_index (integer matching the bracketed index), rationale (short reason).\n\n"
            f"Transcript:\n{transcript_text}"
        )

        payload = {
            "model": self.evon_model_name,
            "messages": [
                {"role": "system", "content": "You extract checkable claims for evidence verification. Always output pure valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            
            json_match = re.search(r"\[.*\]", raw_content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                claims = []
                for c in parsed:
                    seg_idx = c.get("segment_index")
                    start_t = None
                    end_t = None
                    if seg_idx is not None and 0 <= seg_idx < len(segments):
                        start_t = segments[seg_idx].start_time
                        end_t = segments[seg_idx].end_time

                    claims.append(ClaimExtractedDTO(
                        claim_text=c.get("claim_text", ""),
                        category=c.get("category", "factual_assertion"),
                        uncertainty_score=float(c.get("uncertainty_score", 0.2)),
                        segment_index=seg_idx,
                        start_time=start_t,
                        end_time=end_t,
                        confidence=0.9,
                        rationale=c.get("rationale", "Extracted by Gnani Evon 30B reasoning model.")
                    ))
                return claims

        return []

    def _extract_via_heuristics(self, segments: List[SegmentDTO]) -> List[ClaimExtractedDTO]:
        claims: List[ClaimExtractedDTO] = []

        for seg in segments:
            text = seg.text.strip()
            sentences = [s.strip() for s in re.split(r"[.!?]", text) if len(s.strip()) > 15]

            for sentence in sentences:
                is_claim = False
                category = "factual_assertion"
                rationale = []

                # Statistical markers
                for pattern in STATISTICAL_PATTERNS:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        is_claim = True
                        category = "statistical"
                        rationale.append("Quantifiable figures or financial allocation")
                        break

                # Policy markers
                if not is_claim:
                    for pattern in POLICY_PATTERNS:
                        if re.search(pattern, sentence, re.IGNORECASE):
                            is_claim = True
                            category = "policy"
                            rationale.append("Identified governance or statutory mandate")
                            break

                # Factual event assertion
                if not is_claim and len(sentence.split()) >= 6:
                    if re.search(r"\b(declared|revealed|denied|registered|reported|tested|found|occurred)\b", sentence, re.IGNORECASE):
                        is_claim = True
                        category = "event"
                        rationale.append("Verifiable historical or institutional assertion")

                if is_claim:
                    uncertainty = 0.15
                    for word, weight in HEDGE_TERMS.items():
                        if re.search(rf"\b{word}\b", sentence, re.IGNORECASE):
                            uncertainty = min(0.95, uncertainty + weight)
                            rationale.append(f"Hedge term '{word}' elevates uncertainty")

                    claims.append(ClaimExtractedDTO(
                        claim_text=sentence,
                        category=category,
                        uncertainty_score=round(uncertainty, 2),
                        segment_index=seg.order_index,
                        start_time=seg.start_time,
                        end_time=seg.end_time,
                        confidence=0.88,
                        rationale="; ".join(rationale) if rationale else "Heuristic syntactic fact extraction."
                    ))

        return claims

# Backward-compatibility alias
ReasoningProvider = ReasoningEngine
