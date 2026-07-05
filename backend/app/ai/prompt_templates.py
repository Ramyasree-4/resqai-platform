"""
ResQAI – Unified Prompt Templates
Single source of truth for all AI prompts.
Both Mistral and Gemini receive identical prompts.
"""
from typing import Any, Dict, List


# ── Standard response schema (required from BOTH models) ──────────────────────
STANDARD_RESPONSE_SCHEMA = {
    "disaster_type": "string  — FLOOD|CYCLONE|EARTHQUAKE|LANDSLIDE|FIRE|MEDICAL|INDUSTRIAL|DROUGHT|CIVIL_UNREST|OTHER",
    "severity": "string  — LOW|MEDIUM|HIGH|CRITICAL",
    "priority": "string  — LOW|MEDIUM|HIGH|CRITICAL",
    "confidence": "float  — 0.0 to 1.0",
    "summary": "string  — 2-3 sentence professional summary",
    "affected_population": "string  — estimated affected people description",
    "recommended_resources": "array  — list of resource type strings",
    "medical_need": "string  — YES|NO|UNKNOWN",
    "shelter_need": "string  — YES|NO|UNKNOWN",
    "reasoning": "string  — explanation of severity and priority assessment",
}


def build_incident_analysis_prompt(
    incident_id: str,
    incident_type: str,
    description: str,
    affected_people: int,
    district: str,
    state: str,
    latitude: float,
    longitude: float,
    reported_at: str,
    urgency_level: str,
    fatalities: int = 0,
    injuries: int = 0,
    active_district_incidents: int = 0,
    vulnerability_score: float = 5.0,
) -> str:
    """
    Unified incident analysis prompt.
    Used by BOTH Mistral and Gemini — identical content, same schema.
    """
    return f"""You are ResQAI, an AI-powered disaster response analysis system for India.
Analyze emergency incident reports and provide structured, actionable intelligence
to disaster management authorities.

CRITICAL RULES:
- Respond ONLY with valid JSON. No markdown, no explanation, no code fences.
- Be conservative with severity — when uncertain, rate HIGHER to protect lives.
- Prioritize human life above all other factors.

=== INCIDENT DATA ===
Incident ID: {incident_id}
Report Type: {incident_type}
Description: {description}
People Affected: {affected_people}
Fatalities (reported): {fatalities}
Injuries (reported): {injuries}
Location: {district}, {state}, India
GPS Coordinates: {latitude}, {longitude}
Reported At: {reported_at}
User Urgency: {urgency_level}

=== CONTEXT DATA ===
Active Incidents in District (last 2 hours): {active_district_incidents}
Historical Vulnerability Score: {vulnerability_score}/10

=== REQUIRED JSON OUTPUT ===
Return ONLY this exact JSON structure — no other text:

{{
  "disaster_type": "<FLOOD|CYCLONE|EARTHQUAKE|LANDSLIDE|FIRE|MEDICAL|INDUSTRIAL|DROUGHT|CIVIL_UNREST|OTHER>",
  "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "priority": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "confidence": <0.0 to 1.0>,
  "summary": "<2-3 sentence professional summary of the emergency>",
  "affected_population": "<description of affected population and scale>",
  "recommended_resources": ["<resource1>", "<resource2>", "<resource3>"],
  "medical_need": "<YES|NO|UNKNOWN>",
  "shelter_need": "<YES|NO|UNKNOWN>",
  "reasoning": "<detailed explanation of severity and priority assessment>"
}}"""


def build_extended_analysis_prompt(
    incident_id: str,
    incident_type: str,
    description: str,
    affected_people: int,
    district: str,
    state: str,
    latitude: float,
    longitude: float,
    reported_at: str,
    urgency_level: str,
    fatalities: int = 0,
    injuries: int = 0,
    active_district_incidents: int = 0,
    vulnerability_score: float = 5.0,
) -> str:
    """
    Extended analysis prompt — returned alongside standard format
    for backward compatibility with existing Firestore schema.
    """
    return f"""You are ResQAI, an AI-powered disaster response analysis system for India.

CRITICAL RULES:
- Respond ONLY with valid JSON. No markdown, no explanation, no code fences.
- Be conservative with severity — when uncertain, rate HIGHER.

=== INCIDENT DATA ===
Incident ID: {incident_id}
Report Type: {incident_type}
Description: {description}
People Affected: {affected_people}
Fatalities: {fatalities} | Injuries: {injuries}
Location: {district}, {state}, India
GPS: {latitude}, {longitude}
Reported At: {reported_at}
User Urgency: {urgency_level}
Active District Incidents: {active_district_incidents}
Vulnerability Score: {vulnerability_score}/10

Return ONLY this JSON:
{{
  "disaster_type": "<FLOOD|CYCLONE|EARTHQUAKE|LANDSLIDE|FIRE|MEDICAL|INDUSTRIAL|DROUGHT|CIVIL_UNREST|OTHER>",
  "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "priority": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "confidence": <0.0-1.0>,
  "summary": "<2-3 sentence summary>",
  "affected_population": "<affected population description>",
  "recommended_resources": ["<resource_type_1>", "<resource_type_2>"],
  "medical_need": "<YES|NO|UNKNOWN>",
  "shelter_need": "<YES|NO|UNKNOWN>",
  "reasoning": "<why this severity and priority>",
  "classification": {{
    "incidentType": "<disaster_type>",
    "subType": "<sub-classification>",
    "confidence": <0.0-1.0>
  }},
  "severity_detail": {{
    "score": <1-10>,
    "band": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "justification": "<one sentence>"
  }},
  "priority_detail": {{
    "score": <0.0-1.0>,
    "reasoning": "<one sentence>"
  }},
  "resourceRecommendations": [
    {{
      "resourceType": "<RESCUE_BOAT|AMBULANCE|FIRE_TRUCK|HELICOPTER|RESCUE_TEAM|MEDICAL_UNIT|POLICE_UNIT>",
      "quantity": <integer>,
      "urgency": "<IMMEDIATE|HIGH|MEDIUM|LOW>",
      "reason": "<why>"
    }}
  ],
  "situationSummary": "<2-3 sentence professional summary>",
  "reasoning_list": ["<reason 1>", "<reason 2>", "<reason 3>"],
  "immediateActions": ["<action 1>", "<action 2>", "<action 3>"],
  "risks": ["<risk 1>", "<risk 2>"],
  "duplicateLikelihood": <0.0-1.0>,
  "dataQuality": "<HIGH|MEDIUM|LOW>",
  "dataQualityNote": "<concerns or empty string>"
}}"""


def build_duplicate_check_prompt(description1: str, description2: str) -> str:
    return f"""Determine if these two emergency reports describe the same real-world event.

Report 1: {description1}

Report 2: {description2}

Respond ONLY with this JSON:
{{
  "areSameEvent": <true|false>,
  "confidence": <0.0-1.0>,
  "reasoning": "<one sentence explanation>"
}}"""


def build_schema_correction_prompt(original_response: str) -> str:
    return f"""The following AI response is invalid JSON or missing required fields.
Fix it to match the required schema exactly.

Original response:
{original_response}

Return ONLY the corrected valid JSON with all required fields:
{{
  "disaster_type": "...",
  "severity": "MEDIUM",
  "priority": "MEDIUM",
  "confidence": 0.5,
  "summary": "...",
  "affected_population": "...",
  "recommended_resources": [],
  "medical_need": "UNKNOWN",
  "shelter_need": "UNKNOWN",
  "reasoning": "..."
}}
No explanation. No markdown."""


def build_situation_summary_prompt(
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
    resources_str = ", ".join(assigned_resources) if assigned_resources else "None assigned yet"
    return f"""You are a professional disaster management report writer for the Government of India.

Generate a concise 2-3 sentence situation summary for a formal situation report.
Use professional, factual language. Third person. Present tense for active incidents.

Incident Details:
- Type: {classified_type}
- Severity: {severity_score}/10 ({severity_band})
- Affected: {affected_people} people
- Location: {district}, {state}
- Status: {status}
- Deployed Resources: {resources_str}
- Report: {description}

Respond ONLY with the situation summary text. No JSON. No labels."""


def build_situation_report_prompt(
    district: str,
    state: str,
    from_date: str,
    to_date: str,
    incident_stats: Dict[str, Any],
    response_metrics: Dict[str, Any],
    resource_metrics: Dict[str, Any],
    top_incidents: List[Dict[str, Any]],
) -> str:
    import json
    return f"""You are a senior disaster management report writer for the Government of India.
Write a formal situation report in professional government style.

Period: {from_date} to {to_date}
Jurisdiction: {district}, {state}

Incident Statistics: {json.dumps(incident_stats, indent=2)}
Response Metrics: {json.dumps(response_metrics, indent=2)}
Resource Utilization: {json.dumps(resource_metrics, indent=2)}
Top Critical Incidents: {json.dumps(top_incidents, indent=2)}

Write a complete situation report with:
1. Executive Summary (2 paragraphs)
2. Incident Overview
3. Response Operations
4. Resource Utilization
5. Key Challenges
6. Recommendations for Next 24 Hours
7. Conclusion

Format: Professional government document. 600-900 words."""
