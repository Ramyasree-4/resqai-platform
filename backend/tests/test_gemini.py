"""
ResQAI – Gemini Service Tests
Tests for AI analysis, fallback classifier, and prompt building.
"""
import pytest
from unittest.mock import MagicMock, patch


# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_GEMINI_RESPONSE = {
    "classification": {
        "incidentType": "FLOOD",
        "subType": "Flash Flood",
        "confidence": 0.97,
    },
    "severity": {
        "score": 9,
        "band": "CRITICAL",
        "justification": "Large population affected with vulnerable groups trapped.",
    },
    "priority": {"score": 0.88, "reasoning": "Rapidly deteriorating life-safety situation."},
    "resourceRecommendations": [
        {"resourceType": "RESCUE_BOAT", "quantity": 5, "urgency": "IMMEDIATE", "reason": "Water rescue required"},
        {"resourceType": "MEDICAL_UNIT", "quantity": 2, "urgency": "HIGH", "reason": "Potential injuries"},
    ],
    "situationSummary": "A critical flash flood emergency is active in the Khandagiri area of Khurda district, affecting approximately 800 residents.",
    "reasoning": [
        "High number of affected people (800)",
        "Critical infrastructure loss (electricity)",
        "Vulnerable populations present (children, elderly)",
        "Rapidly rising water levels indicate active danger",
        "Location at historically high flood-risk zone",
    ],
    "immediateActions": [
        "Deploy rescue boats to Khandagiri area immediately",
        "Establish medical triage at DRM ground",
        "Issue district-wide flood alert broadcast",
    ],
    "risks": [
        "Secondary flooding from nearby drainage channels",
        "Electrocution risk from submerged electrical infrastructure",
    ],
    "duplicateLikelihood": 0.1,
    "dataQuality": "HIGH",
    "dataQualityNote": "",
}

EXPECTED_ANALYSIS_KEYS = {
    "classification", "severity", "priority", "resourceRecommendations",
    "situationSummary", "reasoning", "immediateActions",
}


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestPromptBuilding:
    """Prompt template tests — no API calls."""

    def test_incident_prompt_contains_key_data(self):
        from app.gemini.prompts import build_incident_analysis_prompt
        prompt = build_incident_analysis_prompt(
            incident_id="INC-2024-ABCD1234",
            incident_type="FLOOD",
            description="Water rising, families trapped",
            affected_people=800,
            district="Khurda",
            state="Odisha",
            latitude=20.2961,
            longitude=85.8245,
            reported_at="2024-01-15T10:30:00Z",
            urgency_level="CRITICAL",
        )
        assert "INC-2024-ABCD1234" in prompt
        assert "FLOOD" in prompt
        assert "800" in prompt
        assert "Khurda" in prompt
        assert "JSON" in prompt.upper()

    def test_duplicate_check_prompt(self):
        from app.gemini.prompts import build_duplicate_check_prompt
        prompt = build_duplicate_check_prompt("Flood in area A", "Flooding reported near area A")
        assert "Flood in area A" in prompt
        assert "JSON" in prompt.upper()

    def test_summary_prompt(self):
        from app.gemini.prompts import build_situation_summary_prompt
        prompt = build_situation_summary_prompt(
            classified_type="FLOOD",
            severity_score=9,
            severity_band="CRITICAL",
            affected_people=800,
            district="Khurda",
            state="Odisha",
            status="ASSIGNED",
            assigned_resources=["ODRAF Boat Unit 2"],
            description="Families trapped on rooftops",
        )
        assert "FLOOD" in prompt
        assert "800" in prompt
        assert "Khurda" in prompt


class TestFallbackClassifier:
    """Rule-based fallback when Gemini is unavailable."""

    def test_flood_keyword_classification(self):
        from app.gemini.service import _fallback_classify
        result = _fallback_classify(
            description="Water is rising, people drowning near the river",
            incident_type="OTHER",
            affected_people=100,
        )
        assert result["classification"]["incidentType"] == "FLOOD"

    def test_fire_keyword_classification(self):
        from app.gemini.service import _fallback_classify
        result = _fallback_classify(
            description="Building on fire, smoke everywhere",
            incident_type="OTHER",
            affected_people=50,
        )
        assert result["classification"]["incidentType"] == "FIRE"

    def test_high_population_severity(self):
        from app.gemini.service import _fallback_classify
        result = _fallback_classify("Generic emergency", "OTHER", 5000)
        assert result["severity"]["score"] >= 7
        assert result["severity"]["band"] in ("HIGH", "CRITICAL")

    def test_low_population_medium_severity(self):
        from app.gemini.service import _fallback_classify
        result = _fallback_classify("Small incident", "MEDICAL", 5)
        assert result["severity"]["score"] <= 6

    def test_fallback_flag(self):
        from app.gemini.service import _fallback_classify
        result = _fallback_classify("test", "OTHER", 10)
        assert result.get("_fallbackUsed") is True

    def test_fallback_has_required_keys(self):
        from app.gemini.service import _fallback_classify
        result = _fallback_classify("Emergency report", "FLOOD", 200)
        for key in EXPECTED_ANALYSIS_KEYS:
            assert key in result, f"Missing key: {key}"


class TestCircuitBreaker:
    """Circuit breaker state management."""

    def test_circuit_opens_after_threshold(self):
        from app.gemini.service import CircuitBreaker
        cb = CircuitBreaker(threshold=3, timeout=60)
        assert not cb.is_open
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open

    def test_circuit_resets_on_success(self):
        from app.gemini.service import CircuitBreaker
        cb = CircuitBreaker(threshold=3, timeout=60)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert not cb.is_open

    def test_circuit_half_opens_after_timeout(self):
        import time
        from app.gemini.service import CircuitBreaker
        cb = CircuitBreaker(threshold=1, timeout=1)
        cb.record_failure()
        assert cb.is_open
        time.sleep(1.1)
        assert not cb.is_open  # Timeout passed — half open


class TestBusinessRules:
    """Post-AI business rule overrides."""

    def test_fatalities_force_severity_8(self):
        from app.gemini.service import GeminiService
        svc = GeminiService.__new__(GeminiService)
        result = {
            "severity": {"score": 5, "band": "MEDIUM"},
            "situationSummary": "Minor incident",
        }
        updated = svc._apply_business_rules(result, fatalities=2, affected_people=10, incident_type="FLOOD")
        assert updated["severity"]["score"] >= 8

    def test_large_population_force_severity_8(self):
        from app.gemini.service import GeminiService
        svc = GeminiService.__new__(GeminiService)
        result = {"severity": {"score": 4, "band": "MEDIUM"}, "situationSummary": ""}
        updated = svc._apply_business_rules(result, fatalities=0, affected_people=15000, incident_type="FLOOD")
        assert updated["severity"]["score"] >= 8

    def test_score_capped_at_10(self):
        from app.gemini.service import GeminiService
        svc = GeminiService.__new__(GeminiService)
        result = {"severity": {"score": 9, "band": "CRITICAL"}, "situationSummary": "children trapped"}
        updated = svc._apply_business_rules(result, fatalities=5, affected_people=20000, incident_type="FLOOD")
        assert updated["severity"]["score"] == 10
