import re
import json
import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.providers.base import ClaimExtractedDTO, SegmentDTO

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

class ReasoningProvider:
    """
    Reasoning and claim extraction provider.
    Supports:
    1. Gnani Evon 30B (or compatible reasoning models) via OpenAI-compatible endpoints (vLLM / SGLang / Hosted).
    2. Transparent Heuristic Linguistic Extractor when no LLM endpoint is provided.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or settings.EVON_BASE_URL).rstrip("/") if (base_url or settings.EVON_BASE_URL) else None
        self.api_key = api_key or settings.EVON_API_KEY
        self.model_name = settings.EVON_MODEL_NAME

    def is_evon_configured(self) -> bool:
        return bool(self.base_url and len(self.base_url.strip()) > 5)

    async def extract_claims(self, segments: List[SegmentDTO]) -> List[ClaimExtractedDTO]:
        if self.is_evon_configured():
            try:
                return await self._extract_via_evon_api(segments)
            except Exception as e:
                logger.warning(f"Evon API call failed ({str(e)}), falling back to heuristic extractor.")

        return self._extract_via_heuristics(segments)

    async def _extract_via_evon_api(self, segments: List[SegmentDTO]) -> List[ClaimExtractedDTO]:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        transcript_text = "\n".join([f"[{s.order_index}] {s.text}" for s in segments])

        prompt = (
            "You are a factual claim extraction system for investigative journalism and verification.\n"
            "Analyze the following transcript and extract distinct checkable factual claims.\n"
            "Respond ONLY with a JSON array of objects with keys: claim_text, category (statistical, policy, event, quote, historical), "
            "uncertainty_score (0.0 to 1.0), segment_index (integer matching the bracketed index), rationale (short reason).\n\n"
            f"Transcript:\n{transcript_text}"
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You extract checkable claims for evidence verification. Always output pure valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            
            # Parse JSON block
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
                        rationale=c.get("rationale", "Extracted by Evon 30B reasoning model.")
                    ))
                return claims

        return self._extract_via_heuristics(segments)

    def _extract_via_heuristics(self, segments: List[SegmentDTO]) -> List[ClaimExtractedDTO]:
        claims: List[ClaimExtractedDTO] = []

        for seg in segments:
            text = seg.text.strip()
            # Split into sub-sentences
            sentences = [s.strip() for s in re.split(r"[.!?]", text) if len(s.strip()) > 15]

            for sentence in sentences:
                is_claim = False
                category = "factual_assertion"
                rationale = []

                # Check statistical markers
                for pattern in STATISTICAL_PATTERNS:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        is_claim = True
                        category = "statistical"
                        rationale.append("Contains quantifiable figures/amounts")
                        break

                # Check policy markers
                if not is_claim:
                    for pattern in POLICY_PATTERNS:
                        if re.search(pattern, sentence, re.IGNORECASE):
                            is_claim = True
                            category = "policy"
                            rationale.append("Identified governance or budgetary declaration")
                            break

                # General declarative factual claim
                if not is_claim and len(sentence.split()) >= 6:
                    # Look for verbs of assertion or action
                    if re.search(r"\b(declared|revealed|denied|registered|reported|tested|found|occurred)\b", sentence, re.IGNORECASE):
                        is_claim = True
                        category = "event"
                        rationale.append("Verifiable event or official assertion")

                if is_claim:
                    # Calculate uncertainty score based on hedge markers
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
                        rationale="; ".join(rationale) if rationale else "Syntactic assertion extracted for evidence verification."
                    ))

        return claims
