import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from app.providers.base import ClaimExtractedDTO, SegmentDTO

logger = logging.getLogger("raven.providers.ollama")

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
RECOMMENDED_LIGHTWEIGHT_MODELS = [
    "llama3.2:1b",
    "llama3.2:3b",
    "qwen2.5:1.5b",
    "qwen2.5:3b",
    "mistral:latest",
    "llama3.1:8b"
]

class OllamaProvider:
    """
    Ollama Local Reasoning Engine Provider.
    Interfaces with locally running Ollama instance for contextual claim extraction,
    numerical analysis, named entity recognition, and epistemic uncertainty evaluation.
    """

    def __init__(self, host: Optional[str] = None, model: str = "llama3.2:3b", timeout: float = 45.0):
        self.host = (host or DEFAULT_OLLAMA_HOST).rstrip("/")
        self.model = model
        self.timeout = timeout

    async def check_health(self) -> Dict[str, Any]:
        """
        Pings Ollama server and lists installed models.
        Never pretends a model is installed if Ollama is unreachable.
        """
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.host}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    installed_models = [m.get("name", "") for m in data.get("models", [])]
                    is_active_model_installed = any(self.model in m for m in installed_models)
                    return {
                        "online": True,
                        "host": self.host,
                        "active_model": self.model,
                        "is_active_model_installed": is_active_model_installed,
                        "installed_models": installed_models,
                        "recommended_lightweight": RECOMMENDED_LIGHTWEIGHT_MODELS
                    }
        except Exception as exc:
            logger.debug(f"Ollama server not reachable: {exc}")

        return {
            "online": False,
            "host": self.host,
            "active_model": self.model,
            "is_active_model_installed": False,
            "installed_models": [],
            "recommended_lightweight": RECOMMENDED_LIGHTWEIGHT_MODELS,
            "message": "Ollama service offline or not running at host. Local heuristic fallback active."
        }

    async def extract_claims_and_entities(self, segments: List[SegmentDTO]) -> List[Dict[str, Any]]:
        """
        Extracts structured factual claims, numerical figures, entities, and uncertainty using Ollama.
        Forces JSON format schema.
        """
        health = await self.check_health()
        if not health["online"] or not health["is_active_model_installed"]:
            raise RuntimeError(
                f"Ollama reasoning model '{self.model}' is not currently available at {self.host}."
            )

        transcript_body = "\n".join([f"[{s.order_index}] {s.text}" for s in segments])

        system_prompt = (
            "You are RAVEN's factual claim extraction and epistemic uncertainty engine.\n"
            "Analyze the transcript and extract discrete checkable factual claims.\n"
            "Identify statistical/numerical figures, government policies, verifiable events, and named entities.\n"
            "Strictly distinguish opinions/rhetoric from factual claims.\n"
            "Output MUST be a JSON object with a single key 'claims' containing an array of claim objects.\n"
            "Each object must have:\n"
            "  - claim_text (str): checkable statement\n"
            "  - category (str): 'statistical', 'policy', 'event', 'quote', or 'historical'\n"
            "  - is_opinion (bool): false if factual assertion\n"
            "  - segment_index (int): index matching [order_index]\n"
            "  - uncertainty_score (float 0.0 to 1.0): linguistic epistemic uncertainty\n"
            "  - entities (list of str): named organizations, places, programs\n"
            "  - coreference_notes (str): context resolved across sentences\n"
            "  - evidence_questions (list of str): specific questions to investigate\n"
        )

        user_prompt = f"Transcript Segments:\n{transcript_body}\n\nExtract all verifiable claims in pure JSON format."

        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.host}/api/generate", json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama generation failed ({resp.status_code}): {resp.text}")

            result_json = resp.json()
            raw_response = result_json.get("response", "{}")

            parsed = json.loads(raw_response)
            claims_list = parsed.get("claims", [])
            if isinstance(parsed, list):
                claims_list = parsed

            return claims_list
