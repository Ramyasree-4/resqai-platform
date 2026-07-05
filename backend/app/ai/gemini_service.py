"""
ResQAI – Gemini AI Service (Fallback LLM)
"""
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure .env is loaded regardless of CWD
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv(Path(__file__).parent.parent.parent / ".env", override=False)
except ImportError:
    pass

from app.core.logging import get_logger
from app.ai.json_parser import parse_llm_json
from app.ai.response_validator import (
    validate_standard_response,
    normalise_standard_response,
)

logger = get_logger(__name__)

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))

def _is_real_gemini_key(val: str) -> bool:
    if not val:
        return False
    lower = val.lower()
    return not any(lower.startswith(p) for p in ("your-", "change-", "test"))


class GeminiFallbackService:
    """
    Gemini 1.5 Pro as fallback LLM.
    Called automatically by AIManager when Mistral fails.
    Uses the same prompt and returns the same standard response format.
    """

    def __init__(self):
        if not GEMINI_API_KEY or not _is_real_gemini_key(GEMINI_API_KEY):
            logger.warning("GOOGLE_API_KEY not set or is a placeholder — Gemini fallback disabled")
            self._model = None
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            self._model = genai.GenerativeModel(GEMINI_MODEL)
            self._genai = genai
            logger.info("GeminiFallbackService initialized", model=GEMINI_MODEL)
        except ImportError:
            logger.warning("google-generativeai not installed — Gemini fallback disabled")
            self._model = None
        except Exception as e:
            logger.error("Gemini init failed", error=str(e))
            self._model = None

    @property
    def is_available(self) -> bool:
        return self._model is not None

    def analyze_incident(
        self,
        prompt: str,
        incident_id: Optional[str] = None,
        trace=None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Analyze an incident using Gemini 1.5 Pro.
        Returns (result_dict, error_message).
        """
        if not self.is_available:
            return None, "Gemini fallback not available (check GOOGLE_API_KEY)"

        try:
            generation_config = self._genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048,
                top_p=0.9,
                candidate_count=1,
            )

            response = self._model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={"timeout": GEMINI_TIMEOUT},
            )

            if not response or not response.text:
                return None, "Empty response from Gemini"

            raw_text = response.text.strip()

            if trace:
                trace.set_response(raw_text)

            # Parse JSON
            parsed, parse_error = parse_llm_json(raw_text)
            if parse_error or not parsed:
                logger.warning("Gemini JSON parse failed", error=parse_error)
                return None, f"Gemini JSON invalid: {parse_error}"

            # Normalise and validate
            normalised = normalise_standard_response(parsed)
            is_valid, errors = validate_standard_response(normalised)

            if not is_valid:
                logger.warning("Gemini schema invalid", errors=errors)
                # Attempt self-correction
                corrected = self._attempt_gemini_correction(raw_text)
                if corrected:
                    return corrected, None
                return None, f"Gemini schema invalid: {errors}"

            logger.info(
                "Gemini fallback analysis complete",
                incident_id=incident_id,
                severity=normalised.get("severity"),
                confidence=normalised.get("confidence"),
                model=GEMINI_MODEL,
            )
            return normalised, None

        except Exception as e:
            error_str = str(e)
            logger.error("Gemini fallback failed", error=error_str, incident_id=incident_id)
            return None, f"Gemini error: {error_str}"

    def _attempt_gemini_correction(self, bad_response: str) -> Optional[Dict[str, Any]]:
        """Ask Gemini to self-correct invalid JSON."""
        from app.ai.prompt_templates import build_schema_correction_prompt
        try:
            correction_prompt = build_schema_correction_prompt(bad_response)
            response = self._model.generate_content(
                correction_prompt,
                generation_config=self._genai.GenerationConfig(
                    temperature=0.0, max_output_tokens=1024
                ),
            )
            if not response or not response.text:
                return None
            parsed, error = parse_llm_json(response.text)
            if error or not parsed:
                return None
            normalised = normalise_standard_response(parsed)
            is_valid, _ = validate_standard_response(normalised)
            return normalised if is_valid else None
        except Exception:
            return None

    def generate_text(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate free-form text (for situation summaries, reports).
        Returns (text, error).
        """
        if not self.is_available:
            return None, "Gemini not available"
        try:
            response = self._model.generate_content(
                prompt,
                generation_config=self._genai.GenerationConfig(
                    temperature=0.3, max_output_tokens=2048
                ),
            )
            return response.text.strip() if response and response.text else None, None
        except Exception as e:
            return None, str(e)


# ── Singleton ─────────────────────────────────────────────────────────────────
_gemini_fallback: Optional[GeminiFallbackService] = None


def get_gemini_fallback_service() -> GeminiFallbackService:
    global _gemini_fallback
    if _gemini_fallback is None:
        _gemini_fallback = GeminiFallbackService()
    return _gemini_fallback


def reset_gemini_fallback_service() -> None:
    global _gemini_fallback
    _gemini_fallback = None
