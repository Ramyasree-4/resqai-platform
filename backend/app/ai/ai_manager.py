"""
ResQAI – AI Manager
Single entry point for all AI operations.

Workflow:
  1. LangSmith trace starts
  2. Call Mistral Large Latest (primary)
  3. On failure → retry up to 3 times
  4. Still failed → automatic switch to Gemini 1.5 Pro
  5. On Gemini failure → return rule-based fallback
  6. LangSmith trace ends

The rest of the application only calls AIManager.
It has NO knowledge of which model was used.
"""
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.core.logging import get_logger
from app.ai.mistral_service import get_mistral_service
from app.ai.gemini_service import get_gemini_fallback_service
from app.ai.fallback_manager import should_fallback_to_gemini, FallbackReason
from app.ai.langsmith_tracer import trace_ai_call
from app.ai.response_validator import build_fallback_standard_response
from app.ai.prompt_templates import (
    build_incident_analysis_prompt,
    build_extended_analysis_prompt,
    build_duplicate_check_prompt,
    build_situation_summary_prompt,
    build_situation_report_prompt,
)
from app.ai.json_parser import parse_llm_json

logger = get_logger(__name__)

# ── Model name constants ───────────────────────────────────────────────────────
MODEL_MISTRAL = "mistral-large-latest"
MODEL_GEMINI = "gemini-1.5-pro"
MODEL_FALLBACK = "rule-based-fallback"


def _convert_standard_to_extended(
    standard: Dict[str, Any],
    incident_type: str,
    affected_people: int,
    description: str,
) -> Dict[str, Any]:
    """
    Convert standard response format to the extended format
    expected by the existing Firestore schema (backward compatible).
    """
    severity_str = standard.get("severity", "MEDIUM")
    severity_score_map = {"LOW": 3, "MEDIUM": 5, "HIGH": 8, "CRITICAL": 9}
    severity_score = severity_score_map.get(severity_str, 5)

    disaster_type = standard.get("disaster_type", incident_type)
    confidence = float(standard.get("confidence", 0.5))
    reasoning_str = standard.get("reasoning", "")
    reasoning_list = (
        [r.strip() for r in reasoning_str.split(".") if r.strip()]
        if isinstance(reasoning_str, str) else
        [reasoning_str] if reasoning_str else []
    )[:5]

    resources = standard.get("recommended_resources", [])
    resource_recommendations = [
        {
            "resourceType": r if isinstance(r, str) else r.get("resourceType", "RESCUE_TEAM"),
            "quantity": 1,
            "urgency": "HIGH" if severity_str in ("CRITICAL", "HIGH") else "MEDIUM",
            "reason": f"Required for {disaster_type} response",
        }
        for r in resources
    ]

    return {
        # ── Standard format fields ──
        "disaster_type": disaster_type,
        "severity": severity_str,
        "priority": standard.get("priority", severity_str),
        "confidence": confidence,
        "summary": standard.get("summary", ""),
        "affected_population": standard.get("affected_population", str(affected_people)),
        "recommended_resources": resources,
        "medical_need": standard.get("medical_need", "UNKNOWN"),
        "shelter_need": standard.get("shelter_need", "UNKNOWN"),
        "reasoning": reasoning_str,
        # ── Extended / Firestore-compatible fields ──
        "classification": {
            "incidentType": disaster_type,
            "subType": "General",
            "confidence": confidence,
        },
        "severity_detail": {
            "score": severity_score,
            "band": severity_str,
            "justification": reasoning_str[:200] if reasoning_str else "",
        },
        "severity": {"score": severity_score, "band": severity_str, "justification": reasoning_str[:200]},
        "priority_detail": {
            "score": severity_score / 10.0,
            "reasoning": standard.get("priority", severity_str),
        },
        "priority": {"score": severity_score / 10.0, "reasoning": standard.get("priority", severity_str)},
        "resourceRecommendations": resource_recommendations,
        "situationSummary": standard.get("summary", ""),
        "reasoning_list": reasoning_list,
        "reasoning": reasoning_list,  # list format for Firestore schema
        "immediateActions": [
            f"Deploy {r} immediately" for r in resources[:3]
        ] or ["Dispatch nearest rescue unit"],
        "risks": [
            "Situation may deteriorate without prompt response",
            f"High affected population: {affected_people} people",
        ],
        "duplicateLikelihood": 0.1,
        "dataQuality": "HIGH" if confidence > 0.7 else "MEDIUM",
        "dataQualityNote": "",
        "_fallbackUsed": standard.get("_fallbackUsed", False),
        "_fallbackReason": standard.get("_fallbackReason", None),
    }


class AIManager:
    """
    Unified AI orchestrator.

    Usage (from anywhere in the backend):
        ai = get_ai_manager()
        result = ai.analyze_incident(
            incident_id="INC-2024-...",
            incident_type="FLOOD",
            description="...",
            ...
        )
    """

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
        Main incident analysis entry point.
        Automatically handles Mistral → Gemini fallback with LangSmith tracing.
        Returns result in extended format compatible with existing Firestore schema.
        """
        start_total = time.perf_counter()
        reported_at = datetime.now(timezone.utc).isoformat()

        # Build the unified prompt (same for both models)
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

        standard_result = None
        model_used = MODEL_FALLBACK
        fallback_triggered = False
        fallback_reason = None
        total_retries = 0

        # ── Step 1: Try Mistral (Primary) ─────────────────────────────────
        mistral = get_mistral_service()

        with trace_ai_call(
            operation="analyze_incident",
            model=MODEL_MISTRAL,
            incident_id=incident_id,
            prompt=prompt,
            metadata={
                "district": district,
                "state": state,
                "incident_type": incident_type,
                "affected_people": affected_people,
                "urgency_level": urgency_level,
                "is_primary": True,
            },
        ) as trace:
            if mistral.is_available:
                logger.info(
                    "AI analysis started — trying Mistral",
                    incident_id=incident_id,
                    model=MODEL_MISTRAL,
                )
                standard_result, error, retries = mistral.analyze_incident(
                    prompt=prompt,
                    incident_id=incident_id,
                    trace=trace,
                )
                total_retries += retries

                if standard_result:
                    model_used = MODEL_MISTRAL
                    trace.set_response(str(standard_result))
                else:
                    # ── Step 2: Mistral failed → switch to Gemini ─────────
                    should_fallback, reason = should_fallback_to_gemini(error)
                    fallback_triggered = True
                    fallback_reason = reason.value
                    trace.set_fallback(reason.value)

                    logger.warning(
                        "Mistral failed — switching to Gemini",
                        incident_id=incident_id,
                        reason=reason.value,
                        error=error,
                    )
            else:
                # Mistral circuit open or unavailable
                fallback_triggered = True
                fallback_reason = FallbackReason.MISTRAL_NOT_AVAILABLE.value
                trace.set_fallback(fallback_reason)
                logger.warning(
                    "Mistral unavailable — switching directly to Gemini",
                    incident_id=incident_id,
                )

        # ── Step 3: Try Gemini (Fallback) ─────────────────────────────────
        if not standard_result:
            gemini = get_gemini_fallback_service()

            with trace_ai_call(
                operation="analyze_incident_gemini_fallback",
                model=MODEL_GEMINI,
                incident_id=incident_id,
                prompt=prompt,
                metadata={
                    "is_fallback": True,
                    "fallback_reason": fallback_reason,
                    "district": district,
                    "state": state,
                    "incident_type": incident_type,
                    "affected_people": affected_people,
                },
            ) as gemini_trace:
                if gemini.is_available:
                    standard_result, gemini_error = gemini.analyze_incident(
                        prompt=prompt,
                        incident_id=incident_id,
                        trace=gemini_trace,
                    )
                    if standard_result:
                        model_used = MODEL_GEMINI
                        standard_result["_fallbackUsed"] = True
                        standard_result["_fallbackReason"] = fallback_reason
                    else:
                        gemini_trace.set_error(gemini_error or "Unknown Gemini error")
                        logger.error(
                            "Gemini fallback also failed",
                            incident_id=incident_id,
                            error=gemini_error,
                        )
                else:
                    gemini_trace.set_error("Gemini not available")
                    logger.error("Gemini fallback not available", incident_id=incident_id)

        # ── Step 4: Rule-based last resort ────────────────────────────────
        if not standard_result:
            logger.error(
                "All AI models failed — using rule-based fallback",
                incident_id=incident_id,
            )
            standard_result = build_fallback_standard_response(
                description=description,
                incident_type=incident_type,
                affected_people=affected_people,
                reason=f"All models failed. Last fallback reason: {fallback_reason}",
            )
            model_used = MODEL_FALLBACK

        # ── Convert to extended format for Firestore ─────────────────────
        result = _convert_standard_to_extended(
            standard_result, incident_type, affected_people, description
        )

        # Inject metadata
        total_ms = round((time.perf_counter() - start_total) * 1000, 2)
        result["processingTimeMs"] = total_ms
        result["modelUsed"] = model_used
        result["totalRetries"] = total_retries
        result["fallbackTriggered"] = fallback_triggered
        result["fallbackReason"] = fallback_reason

        logger.info(
            "AI analysis pipeline complete",
            incident_id=incident_id,
            model_used=model_used,
            fallback=fallback_triggered,
            fallback_reason=fallback_reason,
            total_ms=total_ms,
            severity=result.get("severity", {}).get("band") if isinstance(result.get("severity"), dict) else result.get("severity"),
        )

        return result

    def check_duplicate(
        self,
        description1: str,
        description2: str,
        incident_id: Optional[str] = None,
    ) -> Tuple[bool, float, str]:
        """
        Check if two incident descriptions describe the same event.
        Returns (are_same, confidence, reasoning).
        """
        prompt = build_duplicate_check_prompt(description1, description2)

        with trace_ai_call(
            operation="duplicate_check",
            model=MODEL_MISTRAL,
            incident_id=incident_id,
            prompt=prompt,
        ) as trace:
            mistral = get_mistral_service()
            if mistral.is_available:
                result, error, _ = mistral.analyze_incident(prompt, incident_id, trace)
                if result:
                    return (
                        bool(result.get("areSameEvent", result.get("disaster_type") == "SAME")),
                        float(result.get("confidence", 0.0)),
                        str(result.get("reasoning", "")),
                    )

        # Fallback to Gemini
        with trace_ai_call(
            operation="duplicate_check_gemini",
            model=MODEL_GEMINI,
            incident_id=incident_id,
        ) as trace:
            gemini = get_gemini_fallback_service()
            if gemini.is_available:
                result, _ = gemini.analyze_incident(prompt, incident_id, trace)
                if result:
                    return (
                        bool(result.get("areSameEvent", False)),
                        float(result.get("confidence", 0.0)),
                        str(result.get("reasoning", "")),
                    )

        return False, 0.0, "Duplicate check unavailable"

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
        """Generate situation summary — tries Mistral then Gemini."""
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

        # Try Mistral
        mistral = get_mistral_service()
        if mistral.is_available:
            with trace_ai_call("situation_summary", MODEL_MISTRAL):
                raw, error, _ = mistral._call_with_retry(
                    [{"role": "user", "content": prompt}],
                    json_mode=False,
                )
                if raw and not error:
                    return raw.strip()

        # Try Gemini
        gemini = get_gemini_fallback_service()
        if gemini.is_available:
            with trace_ai_call("situation_summary_gemini", MODEL_GEMINI):
                text, _ = gemini.generate_text(prompt)
                if text:
                    return text

        return (
            f"Emergency incident in {district}, {state} affecting "
            f"{affected_people} people. Status: {status}."
        )

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
        """Generate full situation report — tries Mistral then Gemini."""
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

        mistral = get_mistral_service()
        if mistral.is_available:
            with trace_ai_call("situation_report", MODEL_MISTRAL):
                raw, error, _ = mistral._call_with_retry(
                    [{"role": "user", "content": prompt}],
                    json_mode=False,
                )
                if raw and not error:
                    return raw.strip()

        gemini = get_gemini_fallback_service()
        if gemini.is_available:
            with trace_ai_call("situation_report_gemini", MODEL_GEMINI):
                text, _ = gemini.generate_text(prompt)
                if text:
                    return text

        from app.core.exceptions import GeminiCircuitOpenError
        raise GeminiCircuitOpenError()


# ── Singleton ─────────────────────────────────────────────────────────────────
_ai_manager: Optional[AIManager] = None


def get_ai_manager() -> AIManager:
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
    return _ai_manager
