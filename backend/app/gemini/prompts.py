"""
ResQAI – Gemini Prompt Templates
All prompts are versioned and centralized here.
"""
from typing import Any, Dict, List, Optional


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
    Build the primary Gemini incident analysis prompt.
    Returns a structured prompt requesting JSON output only.
    """
    return f"""You are ResQAI, an AI-powered disaster response analysis system for India.
Your role is to analyze emergency incident reports submitted by citizens during natural disasters
and provide structured, actionable intelligence to disaster management authorities.

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

=== REQUIRED JSON OUTPUT FORMAT ===
Return ONLY this JSON object, no other text:

{{
  "classification": {{
    "incidentType": "<FLOOD|CYCLONE|EARTHQUAKE|LANDSLIDE|FIRE|MEDICAL|INDUSTRIAL|DROUGHT|CIVIL_UNREST|OTHER>",
    "subType": "<specific sub-classification>",
    "confidence": <0.0-1.0>
  }},
  "severity": {{
    "score": <1-10>,
    "band": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "justification": "<one sentence why>"
  }},
  "priority": {{
    "score": <0.0-1.0>,
    "reasoning": "<one sentence>"
  }},
  "resourceRecommendations": [
    {{
      "resourceType": "<RESCUE_BOAT|AMBULANCE|FIRE_TRUCK|HELICOPTER|RESCUE_TEAM|MEDICAL_UNIT|POLICE_UNIT>",
      "quantity": <integer>,
      "urgency": "<IMMEDIATE|HIGH|MEDIUM|LOW>",
      "reason": "<why this resource is needed>"
    }}
  ],
  "situationSummary": "<2-3 sentence professional summary of the emergency>",
  "reasoning": [
    "<key factor 1 driving the severity rating>",
    "<key factor 2>",
    "<key factor 3>",
    "<key factor 4 if applicable>",
    "<key factor 5 if applicable>"
  ],
  "immediateActions": [
    "<action 1 authorities should take immediately>",
    "<action 2>",
    "<action 3>"
  ],
  "risks": [
    "<identified secondary risk 1>",
    "<identified secondary risk 2>"
  ],
  "duplicateLikelihood": <0.0-1.0>,
  "dataQuality": "<HIGH|MEDIUM|LOW>",
  "dataQualityNote": "<any concerns about completeness or reliability, or empty string>"
}}"""


def build_duplicate_check_prompt(description1: str, description2: str) -> str:
    """
    Prompt for checking if two incident descriptions describe the same event.
    Returns JSON with similarity score.
    """
    return f"""You are a disaster incident deduplication system.
Determine if these two emergency reports describe the same real-world event.

Report 1: {description1}

Report 2: {description2}

Respond ONLY with this JSON, no other text:
{{
  "areSameEvent": <true|false>,
  "confidence": <0.0-1.0>,
  "reasoning": "<one sentence explanation>"
}}"""


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
    """Prompt for refreshing the situation summary after status changes."""
    resources_str = ", ".join(assigned_resources) if assigned_resources else "None assigned yet"
    return f"""You are a professional disaster management report writer for the Government of India.

Generate a concise 2-3 sentence situation summary suitable for a formal situation report.
Use professional, factual language. Third person. Present tense for active incidents.

Incident Details:
- Type: {classified_type}
- Severity: {severity_score}/10 ({severity_band})
- Affected: {affected_people} people
- Location: {district}, {state}
- Current Status: {status}
- Deployed Resources: {resources_str}
- Original Report: {description}

Respond ONLY with the situation summary text. No JSON. No labels. Just the paragraph."""


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
    """Prompt for generating a formal government situation report."""
    import json
    return f"""You are a senior disaster management report writer for the Government of India.
Write a formal situation report in professional government style.

Period: {from_date} to {to_date}
Jurisdiction: {district}, {state}

Incident Statistics:
{json.dumps(incident_stats, indent=2)}

Response Metrics:
{json.dumps(response_metrics, indent=2)}

Resource Utilization:
{json.dumps(resource_metrics, indent=2)}

Top Critical Incidents:
{json.dumps(top_incidents, indent=2)}

Write a complete situation report with these sections:
1. Executive Summary (2 paragraphs)
2. Incident Overview (narrative from statistics)
3. Response Operations (what was done)
4. Resource Utilization (efficiency narrative)
5. Key Challenges
6. Recommendations for Next 24 Hours
7. Conclusion

Format: Professional government document.
Tone: Factual, measured, authoritative.
Length: 600-900 words."""


def build_schema_correction_prompt(original_response: str) -> str:
    """
    Fallback prompt when Gemini returns malformed JSON.
    Asks Gemini to fix its own output.
    """
    return f"""The following response from an AI system is not valid JSON or is missing required fields.
Fix it to match the required schema exactly.

Original response:
{original_response}

Return ONLY the corrected valid JSON object with all required fields filled in.
If a value is unknown, use a reasonable default (e.g., confidence: 0.5, score: 5).
Do not include any explanation or markdown."""
