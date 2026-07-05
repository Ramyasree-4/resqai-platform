"""
ResQAI – AI Manager Unit Tests
Tests for: json_parser, response_validator, fallback_manager,
           prompt_templates, mistral circuit breaker, AI manager pipeline.
No real API calls — all external services are mocked.
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

# ── Set env vars before any app import ───────────────────────────────────────
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("FIREBASE_STORAGE_BUCKET", "test.appspot.com")
os.environ.setdefault("FIREBASE_WEB_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-minimum-32-characters-long!!")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
os.environ.setdefault("MISTRAL_API_KEY", "")  # Empty — disables Mistral
os.environ.setdefault("GOOGLE_API_KEY", "")   # Empty — disables Gemini


# ═══════════════════════════════════════════════════════════════
# JSON PARSER TESTS
# ═══════════════════════════════════════════════════════════════

class TestJsonParser:
    """Tests for app.ai.json_parser"""

    def test_parse_plain_json(self):
        from app.ai.json_parser import parse_llm_json
        raw = '{"disaster_type": "FLOOD", "severity": "HIGH"}'
        result, error = parse_llm_json(raw)
        assert error is None
        assert result["disaster_type"] == "FLOOD"

    def test_parse_markdown_json(self):
        from app.ai.json_parser import parse_llm_json
        raw = '```json\n{"disaster_type": "FIRE"}\n```'
        result, error = parse_llm_json(raw)
        assert error is None
        assert result["disaster_type"] == "FIRE"

    def test_parse_json_with_preamble(self):
        from app.ai.json_parser import parse_llm_json
        raw = 'Here is my analysis:\n{"disaster_type": "FLOOD", "severity": "CRITICAL"}'
        result, error = parse_llm_json(raw)
        assert error is None
        assert result["severity"] == "CRITICAL"

    def test_parse_trailing_comma(self):
        from app.ai.json_parser import parse_llm_json
        raw = '{"disaster_type": "FLOOD", "severity": "HIGH",}'
        result, error = parse_llm_json(raw)
        assert result is not None, f"Should handle trailing comma, got error: {error}"

    def test_parse_empty_returns_error(self):
        from app.ai.json_parser import parse_llm_json
        result, error = parse_llm_json("")
        assert result is None
        assert error is not None

    def test_parse_plain_text_returns_error(self):
        from app.ai.json_parser import parse_llm_json
        result, error = parse_llm_json("I cannot analyze this incident.")
        assert result is None
        assert error is not None

    def test_strip_markdown_backtick_only(self):
        from app.ai.json_parser import parse_llm_json
        raw = '```\n{"key": "val"}\n```'
        result, error = parse_llm_json(raw)
        assert error is None
        assert result["key"] == "val"

    def test_safe_float(self):
        from app.ai.json_parser import safe_float
        assert safe_float("0.95") == 0.95
        assert safe_float(None) == 0.0
        assert safe_float("bad") == 0.0
        assert safe_float(1) == 1.0

    def test_safe_list(self):
        from app.ai.json_parser import safe_list
        assert safe_list([1, 2]) == [1, 2]
        assert safe_list(None) == []
        assert safe_list("item") == ["item"]


# ═══════════════════════════════════════════════════════════════
# RESPONSE VALIDATOR TESTS
# ═══════════════════════════════════════════════════════════════

class TestResponseValidator:
    """Tests for app.ai.response_validator"""

    def _valid_response(self):
        return {
            "disaster_type": "FLOOD",
            "severity": "HIGH",
            "priority": "HIGH",
            "confidence": 0.92,
            "summary": "A critical flood emergency is active.",
            "affected_population": "Approximately 800 people affected",
            "recommended_resources": ["RESCUE_BOAT", "MEDICAL_UNIT"],
            "medical_need": "YES",
            "shelter_need": "YES",
            "reasoning": "High severity due to large affected population.",
        }

    def test_valid_response_passes(self):
        from app.ai.response_validator import validate_standard_response
        is_valid, errors = validate_standard_response(self._valid_response())
        assert is_valid is True
        assert errors == []

    def test_missing_field_fails(self):
        from app.ai.response_validator import validate_standard_response
        data = self._valid_response()
        del data["summary"]
        is_valid, errors = validate_standard_response(data)
        assert is_valid is False
        assert any("summary" in e for e in errors)

    def test_invalid_disaster_type_fails(self):
        from app.ai.response_validator import validate_standard_response
        data = self._valid_response()
        data["disaster_type"] = "TSUNAMI"
        is_valid, errors = validate_standard_response(data)
        assert is_valid is False

    def test_confidence_out_of_range_fails(self):
        from app.ai.response_validator import validate_standard_response
        data = self._valid_response()
        data["confidence"] = 1.5
        is_valid, errors = validate_standard_response(data)
        assert is_valid is False

    def test_normalise_uppercase_enums(self):
        from app.ai.response_validator import normalise_standard_response
        data = {
            "disaster_type": "flood",
            "severity": "high",
            "priority": "medium",
            "confidence": "0.8",
            "summary": "  test  ",
            "affected_population": "100",
            "recommended_resources": [],
            "medical_need": "yes",
            "shelter_need": "no",
            "reasoning": "test",
        }
        result = normalise_standard_response(data)
        assert result["disaster_type"] == "FLOOD"
        assert result["severity"] == "HIGH"
        assert result["medical_need"] == "YES"
        assert result["confidence"] == 0.8
        assert result["summary"] == "test"

    def test_fallback_response_is_valid(self):
        from app.ai.response_validator import (
            build_fallback_standard_response,
            validate_standard_response,
        )
        fallback = build_fallback_standard_response(
            description="water rising rapidly near the river",
            incident_type="FLOOD",
            affected_people=500,
            reason="All AI models failed",
        )
        is_valid, errors = validate_standard_response(fallback)
        assert is_valid is True, f"Fallback should be valid: {errors}"

    def test_fallback_severity_scaling(self):
        from app.ai.response_validator import build_fallback_standard_response
        critical = build_fallback_standard_response("test", "FLOOD", 10000)
        assert critical["severity"] == "CRITICAL"
        low = build_fallback_standard_response("test", "FLOOD", 5)
        assert low["severity"] == "LOW"

    def test_extract_json_finds_object(self):
        from app.ai.response_validator import extract_json_from_text
        text = 'Here is the result: {"key": "val"} extra text'
        extracted = extract_json_from_text(text)
        assert extracted is not None
        assert '"key"' in extracted


# ═══════════════════════════════════════════════════════════════
# FALLBACK MANAGER TESTS
# ═══════════════════════════════════════════════════════════════

class TestFallbackManager:
    """Tests for app.ai.fallback_manager"""

    def test_rate_limit_triggers_fallback(self):
        from app.ai.fallback_manager import should_fallback_to_gemini, FallbackReason
        should, reason = should_fallback_to_gemini("Error 429: rate_limit exceeded")
        assert should is True
        assert reason == FallbackReason.MISTRAL_RATE_LIMIT

    def test_timeout_triggers_fallback(self):
        from app.ai.fallback_manager import should_fallback_to_gemini, FallbackReason
        should, reason = should_fallback_to_gemini("Request timed out after 30s")
        assert should is True
        assert reason == FallbackReason.MISTRAL_TIMEOUT

    def test_server_error_triggers_fallback(self):
        from app.ai.fallback_manager import should_fallback_to_gemini, FallbackReason
        should, reason = should_fallback_to_gemini("HTTP 503 Service Unavailable")
        assert should is True
        assert reason == FallbackReason.MISTRAL_SERVER_ERROR

    def test_invalid_json_triggers_fallback(self):
        from app.ai.fallback_manager import should_fallback_to_gemini, FallbackReason
        should, reason = should_fallback_to_gemini("JSON parse error: unexpected token")
        assert should is True
        assert reason == FallbackReason.MISTRAL_INVALID_JSON

    def test_circuit_open_triggers_fallback(self):
        from app.ai.fallback_manager import should_fallback_to_gemini, FallbackReason
        should, reason = should_fallback_to_gemini("Mistral unavailable: circuit_open")
        assert should is True
        assert reason == FallbackReason.MISTRAL_CIRCUIT_OPEN

    def test_empty_error_triggers_fallback(self):
        from app.ai.fallback_manager import should_fallback_to_gemini
        should, _ = should_fallback_to_gemini(None)
        assert should is True

    def test_unknown_error_still_triggers_fallback(self):
        from app.ai.fallback_manager import should_fallback_to_gemini
        should, _ = should_fallback_to_gemini("some unexpected error occurred")
        assert should is True


# ═══════════════════════════════════════════════════════════════
# PROMPT TEMPLATES TESTS
# ═══════════════════════════════════════════════════════════════

class TestPromptTemplates:
    """Tests for app.ai.prompt_templates"""

    def test_incident_prompt_contains_all_data(self):
        from app.ai.prompt_templates import build_incident_analysis_prompt
        prompt = build_incident_analysis_prompt(
            incident_id="INC-2024-TEST0001",
            incident_type="FLOOD",
            description="Water rising rapidly, 200 families trapped",
            affected_people=800,
            district="Khurda",
            state="Odisha",
            latitude=20.2961,
            longitude=85.8245,
            reported_at="2024-01-15T10:30:00Z",
            urgency_level="CRITICAL",
            fatalities=2,
            injuries=15,
            active_district_incidents=3,
            vulnerability_score=7.5,
        )
        assert "INC-2024-TEST0001" in prompt
        assert "FLOOD" in prompt
        assert "800" in prompt
        assert "Khurda" in prompt
        assert "Odisha" in prompt
        assert "20.2961" in prompt
        assert "disaster_type" in prompt
        assert "severity" in prompt
        assert "confidence" in prompt

    def test_duplicate_check_prompt(self):
        from app.ai.prompt_templates import build_duplicate_check_prompt
        prompt = build_duplicate_check_prompt(
            "Flood in Khandagiri area",
            "Flooding reported near Khandagiri",
        )
        assert "Flood in Khandagiri area" in prompt
        assert "areSameEvent" in prompt
        assert "confidence" in prompt

    def test_schema_correction_prompt(self):
        from app.ai.prompt_templates import build_schema_correction_prompt
        prompt = build_schema_correction_prompt('{"bad": "json"}')
        assert '{"bad": "json"}' in prompt
        assert "disaster_type" in prompt

    def test_situation_summary_prompt(self):
        from app.ai.prompt_templates import build_situation_summary_prompt
        prompt = build_situation_summary_prompt(
            classified_type="FLOOD",
            severity_score=8.5,
            severity_band="CRITICAL",
            affected_people=800,
            district="Khurda",
            state="Odisha",
            status="ASSIGNED",
            assigned_resources=["ODRAF Boat Unit 2"],
            description="Families trapped on rooftops",
        )
        assert "FLOOD" in prompt
        assert "Khurda" in prompt
        assert "ODRAF Boat Unit 2" in prompt


# ═══════════════════════════════════════════════════════════════
# MISTRAL CIRCUIT BREAKER TESTS
# ═══════════════════════════════════════════════════════════════

class TestMistralCircuitBreaker:
    """Tests for MistralCircuitBreaker in app.ai.mistral_service"""

    def test_circuit_starts_closed(self):
        from app.ai.mistral_service import MistralCircuitBreaker
        cb = MistralCircuitBreaker(threshold=3, reset_timeout=60)
        assert cb.is_open is False

    def test_circuit_opens_after_threshold(self):
        from app.ai.mistral_service import MistralCircuitBreaker
        cb = MistralCircuitBreaker(threshold=3, reset_timeout=60)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open is False  # Not yet at threshold
        cb.record_failure()
        assert cb.is_open is True

    def test_circuit_closes_on_success(self):
        from app.ai.mistral_service import MistralCircuitBreaker
        cb = MistralCircuitBreaker(threshold=2, reset_timeout=60)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open is True
        cb.record_success()
        assert cb.is_open is False

    def test_circuit_half_opens_after_timeout(self):
        import time
        from app.ai.mistral_service import MistralCircuitBreaker
        cb = MistralCircuitBreaker(threshold=1, reset_timeout=1)
        cb.record_failure()
        assert cb.is_open is True
        time.sleep(1.1)
        assert cb.is_open is False  # Timeout expired → half-open

    def test_circuit_resets_failure_count_on_success(self):
        from app.ai.mistral_service import MistralCircuitBreaker
        cb = MistralCircuitBreaker(threshold=5, reset_timeout=60)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb._failures == 0


# ═══════════════════════════════════════════════════════════════
# AI MANAGER PIPELINE TESTS (mocked)
# ═══════════════════════════════════════════════════════════════

class TestAIManagerPipeline:
    """
    Tests for app.ai.ai_manager — all external calls mocked.
    Verifies the Mistral→Gemini→Fallback pipeline logic.
    """

    SAMPLE_STANDARD_RESULT = {
        "disaster_type": "FLOOD",
        "severity": "CRITICAL",
        "priority": "CRITICAL",
        "confidence": 0.97,
        "summary": "Critical flood in Khurda district affecting 800 people.",
        "affected_population": "800 people",
        "recommended_resources": ["RESCUE_BOAT", "MEDICAL_UNIT"],
        "medical_need": "YES",
        "shelter_need": "YES",
        "reasoning": "Large population affected with vulnerable groups trapped.",
        "_fallbackUsed": False,
    }

    def test_mistral_success_returns_result(self):
        """When Mistral succeeds, result is returned and Gemini is NOT called."""
        with patch("app.ai.ai_manager.get_mistral_service") as mock_mistral_factory, \
             patch("app.ai.ai_manager.get_gemini_fallback_service") as mock_gemini_factory:

            mock_mistral = MagicMock()
            mock_mistral.is_available = True
            mock_mistral.analyze_incident.return_value = (
                self.SAMPLE_STANDARD_RESULT.copy(), None, 0
            )
            mock_mistral_factory.return_value = mock_mistral

            mock_gemini = MagicMock()
            mock_gemini.is_available = True
            mock_gemini_factory.return_value = mock_gemini

            from app.ai.ai_manager import AIManager
            manager = AIManager()
            result = manager.analyze_incident(
                incident_id="INC-2024-TEST0001",
                incident_type="FLOOD",
                description="Water rising, families trapped",
                affected_people=800,
                district="Khurda",
                state="Odisha",
                latitude=20.29,
                longitude=85.82,
                urgency_level="CRITICAL",
            )

            # Mistral called
            mock_mistral.analyze_incident.assert_called_once()
            # Gemini NOT called
            mock_gemini.analyze_incident.assert_not_called()
            # Result contains expected fields
            assert result["modelUsed"] == "mistral-large-latest"
            assert result["fallbackTriggered"] is False
            assert "processingTimeMs" in result

    def test_mistral_failure_triggers_gemini_fallback(self):
        """When Mistral fails, Gemini is called automatically."""
        with patch("app.ai.ai_manager.get_mistral_service") as mock_mistral_factory, \
             patch("app.ai.ai_manager.get_gemini_fallback_service") as mock_gemini_factory:

            mock_mistral = MagicMock()
            mock_mistral.is_available = True
            mock_mistral.analyze_incident.return_value = (
                None, "HTTP 503 Service Unavailable", 3
            )
            mock_mistral_factory.return_value = mock_mistral

            mock_gemini = MagicMock()
            mock_gemini.is_available = True
            gemini_result = self.SAMPLE_STANDARD_RESULT.copy()
            gemini_result["_fallbackUsed"] = True
            mock_gemini.analyze_incident.return_value = (gemini_result, None)
            mock_gemini_factory.return_value = mock_gemini

            from app.ai.ai_manager import AIManager
            manager = AIManager()
            result = manager.analyze_incident(
                incident_id="INC-2024-TEST0002",
                incident_type="FIRE",
                description="Building on fire, people trapped",
                affected_people=50,
                district="Puri",
                state="Odisha",
                latitude=19.81,
                longitude=85.83,
                urgency_level="HIGH",
            )

            mock_mistral.analyze_incident.assert_called_once()
            mock_gemini.analyze_incident.assert_called_once()
            assert result["modelUsed"] == "gemini-1.5-pro"
            assert result["fallbackTriggered"] is True

    def test_both_models_fail_returns_rule_based_fallback(self):
        """When both Mistral and Gemini fail, rule-based fallback is returned."""
        with patch("app.ai.ai_manager.get_mistral_service") as mock_mf, \
             patch("app.ai.ai_manager.get_gemini_fallback_service") as mock_gf:

            mock_mistral = MagicMock()
            mock_mistral.is_available = True
            mock_mistral.analyze_incident.return_value = (None, "timeout", 3)
            mock_mf.return_value = mock_mistral

            mock_gemini = MagicMock()
            mock_gemini.is_available = True
            mock_gemini.analyze_incident.return_value = (None, "Gemini error")
            mock_gf.return_value = mock_gemini

            from app.ai.ai_manager import AIManager
            manager = AIManager()
            result = manager.analyze_incident(
                incident_id="INC-2024-TEST0003",
                incident_type="EARTHQUAKE",
                description="Building collapsed, people buried under rubble",
                affected_people=200,
                district="Bhubaneswar",
                state="Odisha",
                latitude=20.29,
                longitude=85.82,
                urgency_level="CRITICAL",
            )

            assert result["modelUsed"] == "rule-based-fallback"
            assert result["fallbackTriggered"] is True
            # Result must still be a valid, usable response
            assert "processingTimeMs" in result

    def test_mistral_unavailable_goes_directly_to_gemini(self):
        """When Mistral circuit is open, Gemini is called without retrying Mistral."""
        with patch("app.ai.ai_manager.get_mistral_service") as mock_mf, \
             patch("app.ai.ai_manager.get_gemini_fallback_service") as mock_gf:

            mock_mistral = MagicMock()
            mock_mistral.is_available = False  # Circuit open
            mock_mf.return_value = mock_mistral

            mock_gemini = MagicMock()
            mock_gemini.is_available = True
            gemini_result = self.SAMPLE_STANDARD_RESULT.copy()
            gemini_result["_fallbackUsed"] = True
            mock_gemini.analyze_incident.return_value = (gemini_result, None)
            mock_gf.return_value = mock_gemini

            from app.ai.ai_manager import AIManager
            manager = AIManager()
            result = manager.analyze_incident(
                incident_id="INC-2024-TEST0004",
                incident_type="CYCLONE",
                description="Cyclone approaching, evacuation needed",
                affected_people=5000,
                district="Jagatsinghpur",
                state="Odisha",
                latitude=20.26,
                longitude=86.17,
                urgency_level="CRITICAL",
            )

            mock_mistral.analyze_incident.assert_not_called()
            mock_gemini.analyze_incident.assert_called_once()
            assert result["fallbackTriggered"] is True

    def test_result_always_has_standard_fields(self):
        """Result always contains required fields regardless of which model was used."""
        with patch("app.ai.ai_manager.get_mistral_service") as mock_mf, \
             patch("app.ai.ai_manager.get_gemini_fallback_service") as mock_gf:

            # Both fail
            mock_m = MagicMock()
            mock_m.is_available = True
            mock_m.analyze_incident.return_value = (None, "error", 0)
            mock_mf.return_value = mock_m

            mock_g = MagicMock()
            mock_g.is_available = False
            mock_gf.return_value = mock_g

            from app.ai.ai_manager import AIManager
            manager = AIManager()
            result = manager.analyze_incident(
                incident_id="INC-TEST",
                incident_type="FLOOD",
                description="A " * 20,
                affected_people=10,
                district="Test",
                state="Test",
                latitude=20.0,
                longitude=85.0,
                urgency_level="LOW",
            )

            required = [
                "processingTimeMs", "modelUsed", "fallbackTriggered",
                "situationSummary", "reasoning", "resourceRecommendations",
            ]
            for field in required:
                assert field in result, f"Missing required field: {field}"


# ═══════════════════════════════════════════════════════════════
# CONVERT STANDARD → EXTENDED FORMAT TESTS
# ═══════════════════════════════════════════════════════════════

class TestConvertStandardToExtended:
    """Tests for _convert_standard_to_extended in ai_manager"""

    def test_severity_band_mapping(self):
        from app.ai.ai_manager import _convert_standard_to_extended
        result = _convert_standard_to_extended(
            {"disaster_type": "FLOOD", "severity": "CRITICAL", "priority": "CRITICAL",
             "confidence": 0.9, "summary": "test", "affected_population": "100",
             "recommended_resources": [], "medical_need": "YES", "shelter_need": "NO",
             "reasoning": "test"},
            "FLOOD", 100, "test"
        )
        assert isinstance(result["severity"], dict)
        assert result["severity"]["band"] == "CRITICAL"
        assert result["severity"]["score"] == 9

    def test_resource_list_converted(self):
        from app.ai.ai_manager import _convert_standard_to_extended
        result = _convert_standard_to_extended(
            {"disaster_type": "FIRE", "severity": "HIGH", "priority": "HIGH",
             "confidence": 0.8, "summary": "fire", "affected_population": "50",
             "recommended_resources": ["FIRE_TRUCK", "AMBULANCE"],
             "medical_need": "YES", "shelter_need": "NO", "reasoning": "fire detected"},
            "FIRE", 50, "fire"
        )
        recs = result["resourceRecommendations"]
        types = [r["resourceType"] for r in recs]
        assert "FIRE_TRUCK" in types
        assert "AMBULANCE" in types
