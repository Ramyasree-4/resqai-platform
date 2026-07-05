"""
ResQAI – Priority Score Calculator
Implements the composite priority algorithm from architecture doc 14.5.
"""
import math
from datetime import datetime, timezone
from typing import Optional


def compute_priority_score(
    severity_score: float,
    affected_people: int,
    reported_at: datetime,
    nearest_resource_km: Optional[float] = None,
    vulnerability_score: float = 5.0,
) -> float:
    """
    Compute composite priority score (0.0–1.0).

    Formula from architecture doc:
    priorityScore =
        (normalizedSeverity  × 0.40) +
        (timeDecayFactor     × 0.25) +
        (populationFactor    × 0.20) +
        (resourceProximity   × 0.10) +
        (vulnerabilityFactor × 0.05)
    """
    # 1. Normalized severity (0–1)
    normalized_severity = min(severity_score / 10.0, 1.0)

    # 2. Time decay factor — grows as incident waits without response
    now = datetime.now(timezone.utc)
    if reported_at.tzinfo is None:
        reported_at = reported_at.replace(tzinfo=timezone.utc)
    minutes_waiting = (now - reported_at).total_seconds() / 60.0
    time_decay = min(1.0, minutes_waiting / 120.0)  # Maxes at 120 minutes

    # 3. Population factor — log scale, capped at 10,000 for normalization
    if affected_people <= 0:
        population_factor = 0.0
    elif affected_people >= 10000:
        population_factor = 1.0
    else:
        population_factor = math.log(affected_people) / math.log(10000)

    # 4. Resource proximity factor
    if nearest_resource_km is None:
        resource_proximity = 0.5  # Unknown → neutral
    else:
        resource_proximity = max(0.0, 1.0 - (nearest_resource_km / 100.0))

    # 5. Vulnerability factor (0–1)
    vulnerability_factor = vulnerability_score / 10.0

    score = (
        normalized_severity  * 0.40
        + time_decay         * 0.25
        + population_factor  * 0.20
        + resource_proximity * 0.10
        + vulnerability_factor * 0.05
    )
    return round(min(score, 1.0), 4)


def get_sla_minutes(severity_band: str) -> int:
    """Return SLA response time in minutes for a severity band."""
    from app.config import get_settings
    s = get_settings()
    mapping = {
        "CRITICAL": s.SLA_CRITICAL_MINUTES,
        "HIGH":     s.SLA_HIGH_MINUTES,
        "MEDIUM":   s.SLA_MEDIUM_MINUTES,
        "LOW":      s.SLA_LOW_MINUTES,
    }
    return mapping.get(severity_band.upper(), s.SLA_MEDIUM_MINUTES)
