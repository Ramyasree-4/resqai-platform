"""
ResQAI – ID Generation Utilities
"""
import uuid
from datetime import datetime, timezone


def generate_incident_id() -> str:
    """Generate a human-readable incident display ID: INC-YYYY-XXXXXXXX"""
    year = datetime.now(timezone.utc).year
    suffix = uuid.uuid4().hex[:8].upper()
    return f"INC-{year}-{suffix}"


def generate_resource_id() -> str:
    """Generate a resource display ID: RES-XXXXXXXX"""
    suffix = uuid.uuid4().hex[:8].upper()
    return f"RES-{suffix}"


def generate_notification_id() -> str:
    """Generate a UUID-based notification ID."""
    return f"NOTIF-{uuid.uuid4().hex[:12].upper()}"


def generate_report_id() -> str:
    return f"RPT-{uuid.uuid4().hex[:10].upper()}"


def generate_audit_id() -> str:
    return f"AUDIT-{uuid.uuid4().hex[:10].upper()}"


def generate_uuid() -> str:
    return str(uuid.uuid4())
