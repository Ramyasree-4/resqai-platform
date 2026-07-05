"""
ResQAI – Incident API Tests
Sample requests, model validation, and business logic tests.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone


# ── Sample Payloads ───────────────────────────────────────────────────────────

CREATE_INCIDENT_PAYLOAD = {
    "title": "Flood in residential area",
    "description": "Water level rising rapidly, approximately 200 families trapped on rooftops. Electricity cut off. Children and elderly need immediate help.",
    "incidentType": "FLOOD",
    "urgencyLevel": "CRITICAL",
    "affectedPeople": 800,
    "location": {
        "address": "Khandagiri area, Bhubaneswar",
        "district": "Khurda",
        "state": "Odisha",
        "pincode": "751030",
        "coordinates": {
            "latitude": 20.2961,
            "longitude": 85.8245,
        },
    },
}

SOS_PAYLOAD = {
    "coordinates": {
        "latitude": 20.2961,
        "longitude": 85.8245,
    },
    "description": "Trapped in flood water, 3rd floor",
    "phoneNumber": "+919876543210",
}

EXPECTED_CREATE_RESPONSE = {
    "incidentId": "INC-2024-XXXXXXXX",
    "status": "SUBMITTED",
    "message": "Report received. AI is analyzing your report.",
    "estimatedResponseTime": "30-45 minutes",
    "trackingUrl": "https://app.resqai.in/track/INC-2024-XXXXXXXX",
}

ASSIGN_PAYLOAD = {
    "authorityId": "authority-uid-001",
    "resourceIds": ["res-firestore-001", "res-firestore-002"],
}

ESCALATE_PAYLOAD = {
    "reason": "Incident scope exceeds district capacity. Requesting state-level support.",
    "escalateTo": "STATE_OFFICER",
}

STATUS_UPDATE_PAYLOAD = {
    "status": "IN_PROGRESS",
    "note": "ODRAF team dispatched, ETA 20 minutes",
}

AI_FEEDBACK_PAYLOAD = {
    "feedback": "ACCEPTED",
    "classificationCorrect": True,
    "severityAccurate": True,
    "recommendationsUseful": True,
    "comment": "Severity assessment was accurate",
}


# ── Model Validation Tests ────────────────────────────────────────────────────

class TestIncidentCreate:
    """IncidentCreate Pydantic model validation."""

    def test_valid_incident(self):
        from app.models.incident import IncidentCreate, IncidentLocation, Coordinates
        data = {**CREATE_INCIDENT_PAYLOAD}
        loc_data = data.pop("location")
        loc = IncidentLocation(
            address=loc_data["address"],
            district=loc_data["district"],
            state=loc_data["state"],
            pincode=loc_data["pincode"],
            coordinates=Coordinates(**loc_data["coordinates"]),
        )
        incident = IncidentCreate(**data, location=loc)
        assert incident.incidentType.value == "FLOOD"
        assert incident.affectedPeople == 800

    def test_description_too_short(self):
        from app.models.incident import IncidentCreate, IncidentLocation, Coordinates
        with pytest.raises(Exception):
            IncidentCreate(
                title="Test",
                description="Short",  # < 20 chars
                incidentType="FLOOD",
                urgencyLevel="HIGH",
                affectedPeople=100,
                location=IncidentLocation(
                    address="Test",
                    district="Khurda",
                    state="Odisha",
                    coordinates=Coordinates(latitude=20.0, longitude=85.0),
                ),
            )

    def test_affected_people_positive(self):
        """affectedPeople must be >= 1."""
        from app.models.incident import IncidentCreate, IncidentLocation, Coordinates
        with pytest.raises(Exception):
            IncidentCreate(
                title="Test incident title",
                description="A" * 25,
                incidentType="FLOOD",
                urgencyLevel="HIGH",
                affectedPeople=0,  # Invalid
                location=IncidentLocation(
                    address="Test",
                    district="Khurda",
                    state="Odisha",
                    coordinates=Coordinates(latitude=20.0, longitude=85.0),
                ),
            )

    def test_all_incident_types_valid(self):
        from app.models.enums import IncidentType
        valid_types = [
            "FLOOD", "CYCLONE", "EARTHQUAKE", "LANDSLIDE",
            "FIRE", "MEDICAL", "INDUSTRIAL", "DROUGHT", "CIVIL_UNREST", "OTHER",
        ]
        for t in valid_types:
            assert IncidentType(t).value == t


class TestSOSCreate:
    """SOSCreate model validation."""

    def test_valid_sos(self):
        from app.models.incident import SOSCreate, Coordinates
        sos = SOSCreate(
            coordinates=Coordinates(latitude=20.2961, longitude=85.8245),
            description="Trapped in flood",
            phoneNumber="+919876543210",
        )
        assert sos.coordinates.latitude == 20.2961

    def test_sos_minimal(self):
        """SOS with coordinates only — no description required."""
        from app.models.incident import SOSCreate, Coordinates
        sos = SOSCreate(coordinates=Coordinates(latitude=20.0, longitude=85.0))
        assert sos.description is None


# ── Priority Score Tests ──────────────────────────────────────────────────────

class TestPriorityScore:
    """Priority calculation unit tests."""

    def test_critical_incident_high_score(self):
        from app.utils.priority import compute_priority_score
        score = compute_priority_score(
            severity_score=9.0,
            affected_people=5000,
            reported_at=datetime.now(timezone.utc),
        )
        assert score > 0.6

    def test_low_incident_low_score(self):
        from app.utils.priority import compute_priority_score
        score = compute_priority_score(
            severity_score=2.0,
            affected_people=5,
            reported_at=datetime.now(timezone.utc),
        )
        assert score < 0.3

    def test_score_capped_at_one(self):
        from app.utils.priority import compute_priority_score
        score = compute_priority_score(
            severity_score=10.0,
            affected_people=100000,
            reported_at=datetime(2020, 1, 1, tzinfo=timezone.utc),  # Old incident
        )
        assert score <= 1.0

    def test_sla_mapping(self):
        from app.utils.priority import get_sla_minutes
        # These should match the defaults in .env.example
        assert get_sla_minutes("CRITICAL") == 30
        assert get_sla_minutes("HIGH") == 60
        assert get_sla_minutes("MEDIUM") == 120
        assert get_sla_minutes("LOW") == 240


# ── Geo Utilities Tests ───────────────────────────────────────────────────────

class TestGeoUtils:
    """Geospatial utility unit tests."""

    def test_haversine_same_point(self):
        from app.utils.geo import haversine_distance
        assert haversine_distance(20.0, 85.0, 20.0, 85.0) == 0.0

    def test_haversine_known_distance(self):
        """Bhubaneswar to Cuttack ≈ 27 km."""
        from app.utils.geo import haversine_distance
        dist = haversine_distance(20.2961, 85.8245, 20.4720, 85.8795)
        assert 20 < dist < 35  # approximate

    def test_geohash_encode(self):
        from app.utils.geo import encode_geohash
        gh = encode_geohash(20.2961, 85.8245, precision=6)
        assert isinstance(gh, str)
        assert len(gh) >= 5

    def test_validate_coordinates_india(self):
        from app.utils.geo import validate_coordinates
        valid, err = validate_coordinates(20.2961, 85.8245)
        assert valid is True

    def test_validate_coordinates_outside_india(self):
        from app.utils.geo import validate_coordinates
        valid, err = validate_coordinates(51.5, -0.1)  # London
        assert valid is False

    def test_arrival_estimate(self):
        from app.utils.geo import estimated_arrival_minutes
        mins = estimated_arrival_minutes(40.0, speed_kmh=40.0)
        assert mins == 60


# ── ID Generation Tests ───────────────────────────────────────────────────────

class TestIDGeneration:
    def test_incident_id_format(self):
        from app.utils.ids import generate_incident_id
        iid = generate_incident_id()
        assert iid.startswith("INC-")
        parts = iid.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 8

    def test_resource_id_format(self):
        from app.utils.ids import generate_resource_id
        rid = generate_resource_id()
        assert rid.startswith("RES-")

    def test_ids_are_unique(self):
        from app.utils.ids import generate_incident_id
        ids = {generate_incident_id() for _ in range(100)}
        assert len(ids) == 100
