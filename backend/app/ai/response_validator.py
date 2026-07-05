"""
ResQAI – AI Response Validator
Validates and normalises the standard response format from both Mistral and Gemini.
Rejects malformed JSON and enforces schema compliance.
"""
import json
import re
from typing import Any, Dict, Optional, Tuple

from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Required fields in standard response ──────────────────────────────────────
REQUIRED_FIELDS = {
    "disaster_type", "severity", "priority", "confidence",
    "summary", "affected_population", "recommended_resources",
    "medical_need", "shelter_need", "reasoning",
}

VALID_DISASTER_TYPES = {
    "FLOOD", "CYCLONE", "EARTHQUAKE", "LANDSLIDE", "FIRE",
    "MEDICAL", "INDUSTRIAL", "DROUGHT", "CIVIL_UNREST", "OTHER",
}
VALID_SEVERITY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_PRIORITY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_YES_NO = {"YES", "NO", "UNKNOWN"}


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Strip markdown fences and extract raw JSON string from LLM output.
    Handles:
      - ```json ... ``` blocks
      - ``` ... ``` blocks
      - Plain JSON starting with {
    """
    text = text.strip()

    # Remove markdown fences
    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = [
            line for line in lines
            if not line.startswith("```")
        ]
        text = "\n".join(json_lines).strip()

    # Find first { and last } to extract JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return None


def parse_json_safe(raw: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Safely parse JSON string. Returns (parsed_dict, error_message).
    """
    extracted = extract_json_from_text(raw)
    if not extracted:
        return None, f"No JSON object found in response (length={len(raw)})"

    try:
        return json.loads(extracted), None
    except json.JSONDecodeError as e:
        return None, f"JSON parse error: {str(e)}"


def validate_standard_response(data: Dict[str, Any]) -> Tuple[bool, list]:
    """
    Validate standard response schema.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    if errors:
        return False, errors

    # Validate disaster_type
    dt = str(data.get("disaster_type", "")).upper()
    if dt not in VALID_DISASTER_TYPES:
        errors.append(f"Invalid disaster_type: '{dt}'. Must be one of {VALID_DISASTER_TYPES}")

    # Validate severity
    sev = str(data.get("severity", "")).upper()
    if sev not in VALID_SEVERITY:
        errors.append(f"Invalid severity: '{sev}'. Must be one of {VALID_SEVERITY}")

    # Validate priority
    pri = str(data.get("priority", "")).upper()
    if pri not in VALID_PRIORITY:
        errors.append(f"Invalid priority: '{pri}'. Must be one of {VALID_PRIORITY}")

    # Validate confidence
    conf = data.get("confidence")
    try:
        conf_float = float(conf)
        if not (0.0 <= conf_float <= 1.0):
            errors.append(f"confidence must be between 0.0 and 1.0, got {conf_float}")
    except (TypeError, ValueError):
        errors.append(f"confidence must be a float, got '{conf}'")

    # Validate summary is non-empty string
    if not isinstance(data.get("summary"), str) or not data["summary"].strip():
        errors.append("summary must be a non-empty string")

    # Validate recommended_resources is a list
    if not isinstance(data.get("recommended_resources"), list):
        errors.append("recommended_resources must be a list")

    # Validate medical_need and shelter_need
    for field in ("medical_need", "shelter_need"):
        val = str(data.get(field, "")).upper()
        if val not in VALID_YES_NO:
            errors.append(f"{field} must be YES, NO, or UNKNOWN (got '{val}')")

    return len(errors) == 0, errors


def normalise_standard_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalise values to expected formats (uppercase enums, float confidence, etc.)
    Mutates and returns the dict.
    """
    if "disaster_type" in data:
        data["disaster_type"] = str(data["disaster_type"]).upper()

    if "severity" in data:
        data["severity"] = str(data["severity"]).upper()

    if "priority" in data:
        data["priority"] = str(data["priority"]).upper()

    if "confidence" in data:
        try:
            data["confidence"] = round(float(data["confidence"]), 3)
        except (TypeError, ValueError):
            data["confidence"] = 0.5

    if "medical_need" in data:
        data["medical_need"] = str(data["medical_need"]).upper()

    if "shelter_need" in data:
        data["shelter_need"] = str(data["shelter_need"]).upper()

    if "recommended_resources" in data:
        if not isinstance(data["recommended_resources"], list):
            data["recommended_resources"] = []
        # Flatten any dict entries to string
        data["recommended_resources"] = [
            str(r.get("resourceType", r)) if isinstance(r, dict) else str(r)
            for r in data["recommended_resources"]
        ]

    # Ensure all strings are stripped
    for str_field in ("summary", "affected_population", "reasoning"):
        if field_val := data.get(str_field):
            data[str_field] = str(field_val).strip()

    return data


def build_fallback_standard_response(
    description: str,
    incident_type: str,
    affected_people: int,
    reason: str = "All AI models failed",
) -> Dict[str, Any]:
    """
    Build a rule-based standard response when all LLMs fail.
    Used as the absolute last resort.
    """
    # Simple severity heuristic
    if affected_people >= 5000:
        severity = priority = "CRITICAL"
        confidence = 0.4
    elif affected_people >= 500:
        severity = priority = "HIGH"
        confidence = 0.4
    elif affected_people >= 50:
        severity = priority = "MEDIUM"
        confidence = 0.35
    else:
        severity = priority = "LOW"
        confidence = 0.35

    # Keyword detection
    desc_lower = description.lower()
    medical_need = "YES" if any(w in desc_lower for w in ["injury", "injured", "hospital", "medical", "dead", "death"]) else "UNKNOWN"
    shelter_need = "YES" if any(w in desc_lower for w in ["homeless", "shelter", "displaced", "evacuate"]) else "UNKNOWN"

    return {
        "disaster_type": incident_type.upper() if incident_type.upper() in VALID_DISASTER_TYPES else "OTHER",
        "severity": severity,
        "priority": priority,
        "confidence": confidence,
        "summary": f"Emergency incident affecting approximately {affected_people} people. "
                   f"AI analysis unavailable — rule-based assessment applied.",
        "affected_population": f"Approximately {affected_people} people",
        "recommended_resources": ["RESCUE_TEAM", "MEDICAL_UNIT"],
        "medical_need": medical_need,
        "shelter_need": shelter_need,
        "reasoning": f"Rule-based fallback assessment. Reason: {reason}. "
                     f"Severity estimated from affected population count ({affected_people}).",
        "_fallbackUsed": True,
        "_fallbackReason": reason,
    }
