"""
ResQAI – Gemini AI Service
Handles all Gemini API interactions with retry logic,
circuit breaker, fallback classifier, and response validation.
"""
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from app.config import get_settings
from app.core.exceptions import (
    GeminiCircuitOpenError,
    GeminiError,
    GeminiTimeoutError,
)
from app.core.logging import get_logger
from app.gemini.prompts import (
    build_duplicate_check_prompt,
    build_incident_analysis_prompt,
    build_schema_correction_prompt,
    build_situation_report_prompt,
    build_situation_summary_prompt,
)
from app.models.enums import IncidentType, SeverityBand

logger = get_logger(__name__)
settings = get_settings()


# ── Circuit Breaker State ──────────────────────────────────────────────────────

class CircuitBreaker:
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self._failures = 0
        self._opened_at: Optional[float] = None

    @property
    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        if time.time() - self._opened_at > self.timeout:
            # Half-open: allow one probe
            self._opened_at = None
            self._failures = 0
            return False
        return True

    def record_failure(self):
        self._failures += 1
        if self._failures >= self.threshold:
            self._opened_at = time.time()
            logger.warning(
                "Gemini circuit breaker OPENED",
                failures=self._failures,
                threshold=self.threshold,
            )

    def record_success(self):
        self._failures = 0
        self._opened_at = None


_circuit_breaker = CircuitBreaker(
    threshold=settings.AI_CIRCUIT_BREAKER_THRESHOLD,
    timeout=settings.AI_CIRCUIT_BREAKER_TIMEOUT,
)


# ── Rule-Based Fallback Classifier ────────────────────────────────────────────

_KEYWORD_TYPE_MAP = {
    IncidentType.FLOOD: ["flood", "water", "drowning", "inundation", "submerged", "overflow"],
    IncidentType.FIRE: ["fire", "burning", "smoke", "blaze", "flames", "arson"],
    IncidentType.EARTHQUAKE: ["earthquake", "tremor", "seismic", "quake", "collapsed"],
    IncidentType.CYCLONE: ["cyclone", "hurricane", "storm", "typhoon", "wind", "gale"],
    IncidentType.LANDSLIDE: ["landslide", "mudslide", "debris", "slope", "rockfall"],
    IncidentType.MEDICAL: ["heart", "medical", "injury", "accident", "hospital", "unconscious"],
    IncidentType.INDUSTRIAL: ["factory", "chemical", "explosion", "gas leak", "industrial"],
}


def _fallback_classify(description: str, incident_type: str, affected_people: int) -> Dict[str, Any]:
    """Rule-based classifier activated when Gemini circuit is open."""
    desc_lower = description.lower()

    # Determine type from keywords
    classified_type = incident_type
    confidence = 0.6
    for itype, keywords in _KEYWORD_TYPE_MAP.items():
        if any(kw in desc_lower for kw in keywords):
            classified_type = itype.value
            confidence = 0.7
            break

    # Severity from population
    if affected_people >= 10000:
        severity_score, severity_band = 9, "CRITICAL"
    elif affected_people >= 1000:
        severity_score, severity_band = 8, "CRITICAL"
    elif affected_people >= 500:
        severity_score, severity_band = 7, "HIGH"
    elif affected_people >= 100:
        severity_score, severity_band = 6, "MEDIUM"
    elif affected_people >= 50:
        severity_score, severity_band = 5, "MEDIUM"
    else:
        severity_score, severity_band = 4, "MEDIUM"

    # Keyword boosters
    critical_words = ["death", "dead", "fatal", "trapped", "critical", "sinking"]
    if any(w in desc_lower for w in critical_words):
        severity_score = min(severity_score + 1, 10)
        severity_band = "CRITICAL" if severity_score >= 9 else "HIGH"

    return {
        "classification": {
            "incidentType": classified_type,
            "subType": "Unknown",
            "confidence": confidence,
        },
        "severity": {
            "score": severity_score,
            "band": severity_band,
            "justification": "Rule-based assessment (AI unavailable)",
        },
        "priority": {"score": severity_score / 10, "reasoning": "Based on severity score"},
        "resourceRecommendations": [
            {"resourceType": "RESCUE_TEAM", "quantity": max(1, affected_people // 100),
             "urgency": "HIGH", "reason": "Default rescue team dispatch"}
        ],
        "situationSummary": f"Emergency incident reported in the area affecting approximately {affected_people} people. AI analysis unavailable; rule-based triage applied.",
        "reasoning": [
            f"Affected population: {affected_people}",
            "Rule-based classification applied (AI service unavailable)",
        ],
        "immediateActions": ["Dispatch nearest available rescue unit", "Assess situation on arrival"],
        "risks": ["Situation may worsen without accurate AI assessment"],
        "duplicateLikelihood": 0.1,
        "dataQuality": "LOW",
        "dataQualityNote": "Rule-based fallback used — AI service unavailable",
        "_fallbackUsed": True,
    }


# ── Gemini Service ─────────────────────────────────────────────────────────────

class GeminiService:
    """Singleton service for all Gemini API interactions."""

    def __init__(self):
        # Use resolved key — supports both GOOGLE_API_KEY and GEMINI_API_KEY
        api_key = settings.resolved_gemini_key or settings.GEMINI_API_KEY
        genai.configure(api_key=api_key)
        self._pro_model = genai.GenerativeModel(settings.GEMINI_PRIMARY_MODEL)
        self._flash_model = genai.GenerativeModel(settings.GEMINI_FLASH_MODEL)
        logger.info(
            "GeminiService initialized",
            primary=settings.GEMINI_PRIMARY_MODEL,
            flash=settings.GEMINI_FLASH_MODEL,
        )

    def _generate_json(self, prompt: str, use_flash: bool = False) -> Dict[str, Any]:
        """
        Call Gemini and parse JSON response.
        Raises GeminiError on failure.
        """
        model = self._flash_model if use_flash else self._pro_model
        generation_config = genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=2048,
            top_p=0.9,
            candidate_count=1,
        )

        try:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={"timeout": settings.GEMINI_TIMEOUT_SECONDS},
            )
            raw_text = response.text.strip()
        except Exception as e:
            raise GeminiError(message=f"Gemini API call failed: {str(e)}")

        # Strip markdown fences if present
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            raw_text = "\n".join(
                line for line in lines
                if not line.startswith("```")
            ).strip()

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            raise GeminiError(message=f"Gemini returned non-JSON response: {raw_text[:200]}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(GeminiError),
        reraise=True,
    )
    def _generate_json_with_retry(
        self, prompt: str, use_flash: bool = False
    ) -> Dict[str, Any]:
        """Generate JSON with automatic retry on failure."""
        return self._generate_json(prompt, use_flash)

    def _validate_analysis_schema(self, data: Dict[str, Any]) -> bool:
        """Validate that the Gemini response has the required fields."""
        required = [
            "classification", "severity", "priority",
            "resourceRecommendations", "situationSummary",
            "reasoning", "immediateActions",
        ]
        if not all(k in data for k in required):
            return False
        if not (1 <= data["severity"].get("score", 0) <= 10):
            return False
        if not (0.0 <= data["classification"].get("confidence", -1) <= 1.0):
            return False
        return True

    def analyze_incident(
        self,
        incident_id: str,
        incident_type: str,
        description: str,
        affected_people: int,
        district: str,
        state: str,
        latitude: float,
        longitude: float,
        urgency_level: str,
        fatalities: int = 0,
        injuries: int = 0,
        active_district_incidents: int = 0,
        vulnerability_score: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Main incident analysis method.
        Returns structured AI analysis or fallback if Gemini unavailable.
        """
        start_time = time.time()

        # ── Circuit Breaker Check ────────────────────────────────────────
        if _circuit_breaker.is_open:
            logger.warning("Gemini circuit OPEN — using fallback classifier")
            result = _fallback_classify(description, incident_type, affected_people)
            result["processingTimeMs"] = int((time.time() - start_time) * 1000)
            return result

        reported_at = datetime.now(timezone.utc).isoformat()
        prompt = build_incident_analysis_prompt(
            incident_id=incident_id,
            incident_type=incident_type,
            description=description,
            affected_people=affected_people,
            district=district,
            state=state,
            latitude=latitude,
            longitude=longitude,
            reported_at=reported_at,
            urgency_level=urgency_level,
            fatalities=fatalities,
            injuries=injuries,
            active_district_incidents=active_district_incidents,
            vulnerability_score=vulnerability_score,
        )

        try:
            result = self._generate_json_with_retry(prompt, use_flash=False)

            # ── Schema validation + correction attempt ───────────────────
            if not self._validate_analysis_schema(result):
                logger.warning("Gemini schema invalid — attempting correction")
                correction_prompt = build_schema_correction_prompt(json.dumps(result))
                result = self._generate_json_with_retry(correction_prompt, use_flash=True)

            # ── Post-processing business rules ───────────────────────────
            result = self._apply_business_rules(result, fatalities, affected_people, incident_type)

            _circuit_breaker.record_success()
            processing_ms = int((time.time() - start_time) * 1000)
            result["processingTimeMs"] = processing_ms
            result["_fallbackUsed"] = False

            logger.info(
                "Gemini analysis complete",
                incident_id=incident_id,
                severity=result["severity"]["score"],
                processing_ms=processing_ms,
            )
            return result

        except GeminiError as e:
            _circuit_breaker.record_failure()
            logger.error(
                "Gemini analysis failed — activating fallback",
                incident_id=incident_id,
                error=str(e),
            )
            result = _fallback_classify(description, incident_type, affected_people)
            result["processingTimeMs"] = int((time.time() - start_time) * 1000)
            return result

    def _apply_business_rules(
        self,
        result: Dict[str, Any],
        fatalities: int,
        affected_people: int,
        incident_type: str,
    ) -> Dict[str, Any]:
        """Apply post-AI business rule overrides from architecture doc 14.4."""
        score = result["severity"]["score"]

        if fatalities and fatalities > 0:
            score = max(score, 8)
        if affected_people > 10000:
            score = max(score, 8)
        if incident_type == "EARTHQUAKE" and affected_people > 0:
            score = max(score, 7)

        desc = result.get("situationSummary", "").lower()
        if "children" in desc and "trapped" in desc:
            score = min(score + 1, 10)

        score = min(score, 10)
        result["severity"]["score"] = score

        # Recalculate band
        if score >= 9:
            result["severity"]["band"] = "CRITICAL"
        elif score >= 7:
            result["severity"]["band"] = "HIGH"
        elif score >= 4:
            result["severity"]["band"] = "MEDIUM"
        else:
            result["severity"]["band"] = "LOW"

        return result

    def check_duplicate(
        self, description1: str, description2: str
    ) -> Tuple[bool, float, str]:
        """
        Check if two descriptions describe the same event.
        Returns (are_same, confidence, reasoning).
        """
        if _circuit_breaker.is_open:
            return False, 0.0, "Circuit open — skipping duplicate check"

        try:
            prompt = build_duplicate_check_prompt(description1, description2)
            result = self._generate_json_with_retry(prompt, use_flash=True)
            _circuit_breaker.record_success()
            return (
                result.get("areSameEvent", False),
                float(result.get("confidence", 0.0)),
                result.get("reasoning", ""),
            )
        except Exception as e:
            _circuit_breaker.record_failure()
            logger.warning("Duplicate check failed", error=str(e))
            return False, 0.0, "Check failed"

    def generate_situation_summary(
        self,
        classified_type: str,
        severity_score: float,
        severity_band: str,
        affected_people: int,
        district: str,
        state: str,
        status: str,
        assigned_resources: List[str],
        description: str,
    ) -> str:
        """Generate or refresh a natural language situation summary."""
        if _circuit_breaker.is_open:
            return f"Emergency incident in {district}, {state} affecting {affected_people} people. Status: {status}."

        try:
            prompt = build_situation_summary_prompt(
                classified_type=classified_type,
                severity_score=severity_score,
                severity_band=severity_band,
                affected_people=affected_people,
                district=district,
                state=state,
                status=status,
                assigned_resources=assigned_resources,
                description=description,
            )
            model = self._flash_model
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3, max_output_tokens=256
                ),
            )
            _circuit_breaker.record_success()
            return response.text.strip()
        except Exception as e:
            _circuit_breaker.record_failure()
            logger.warning("Summary generation failed", error=str(e))
            return f"Emergency incident in {district}, {state} affecting {affected_people} people."

    def generate_situation_report(
        self,
        district: str,
        state: str,
        from_date: str,
        to_date: str,
        incident_stats: Dict[str, Any],
        response_metrics: Dict[str, Any],
        resource_metrics: Dict[str, Any],
        top_incidents: List[Dict[str, Any]],
    ) -> str:
        """Generate a full government-style situation report narrative."""
        if _circuit_breaker.is_open:
            raise GeminiCircuitOpenError()

        try:
            prompt = build_situation_report_prompt(
                district=district,
                state=state,
                from_date=from_date,
                to_date=to_date,
                incident_stats=incident_stats,
                response_metrics=response_metrics,
                resource_metrics=resource_metrics,
                top_incidents=top_incidents,
            )
            response = self._pro_model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3, max_output_tokens=2048
                ),
            )
            _circuit_breaker.record_success()
            return response.text.strip()
        except Exception as e:
            _circuit_breaker.record_failure()
            raise GeminiError(message=f"Report generation failed: {str(e)}")


# ── Singleton accessor ─────────────────────────────────────────────────────────
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
