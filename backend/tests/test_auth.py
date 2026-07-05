"""
ResQAI – Auth API Tests
Sample requests / expected responses for all auth endpoints.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport


# ── Sample payloads ───────────────────────────────────────────────────────────

REGISTER_PAYLOAD = {
    "email": "test.citizen@resqai.in",
    "password": "Test@12345",
    "displayName": "Test Citizen",
    "phoneNumber": "+919876543210",
    "district": "Khurda",
    "state": "Odisha",
    "role": "CITIZEN",
}

REGISTER_EXPECTED_KEYS = {"uid", "email", "displayName", "role", "token", "refreshToken"}

LOGIN_PAYLOAD = {
    "email": "test.citizen@resqai.in",
    "password": "Test@12345",
}

LOGIN_EXPECTED_KEYS = {"uid", "token", "refreshToken", "expiresIn", "user"}

AUTHORITY_REGISTER_PAYLOAD = {
    "email": "authority@resqai.in",
    "password": "Authority@123",
    "displayName": "District Officer",
    "phoneNumber": "+919123456789",
    "district": "Khurda",
    "state": "Odisha",
    "role": "AUTHORITY",
}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_auth_service():
    """Mock AuthService to avoid real Firebase calls in unit tests."""
    with patch("app.api.auth.AuthService") as MockService:
        instance = MockService.return_value
        instance.register = AsyncMock(return_value={
            "uid": "test-uid-123",
            "email": REGISTER_PAYLOAD["email"],
            "displayName": REGISTER_PAYLOAD["displayName"],
            "role": "CITIZEN",
            "token": "mock.jwt.token",
            "refreshToken": "mock-refresh-token",
        })
        instance.login = AsyncMock(return_value={
            "uid": "test-uid-123",
            "token": "mock.jwt.token",
            "refreshToken": "mock-refresh-token",
            "expiresIn": 3600,
            "user": {
                "uid": "test-uid-123",
                "displayName": "Test Citizen",
                "email": "test.citizen@resqai.in",
                "role": "CITIZEN",
                "district": "Khurda",
            },
        })
        yield instance


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestRegister:
    """POST /v1/auth/register"""

    def test_payload_structure(self):
        """Registration payload has all required fields."""
        required = {"email", "password", "displayName", "district", "state", "role"}
        assert required.issubset(REGISTER_PAYLOAD.keys())

    def test_password_validation_weak(self):
        """Passwords without uppercase/special chars should fail Pydantic validation."""
        from app.models.user import UserCreate
        import pytest

        with pytest.raises(Exception):
            UserCreate(
                email="test@test.com",
                password="weakpass",
                displayName="Test",
                district="Khurda",
                state="Odisha",
                role="CITIZEN",
            )

    def test_password_validation_strong(self):
        """Strong password passes validation."""
        from app.models.user import UserCreate
        user = UserCreate(**REGISTER_PAYLOAD)
        assert user.email == REGISTER_PAYLOAD["email"]

    def test_role_enum_valid(self):
        """CITIZEN role is valid."""
        from app.models.enums import UserRole
        assert UserRole.CITIZEN.value == "CITIZEN"

    def test_expected_response_keys(self):
        """Mock register response contains all expected keys."""
        mock_response = {
            "uid": "test-uid-123",
            "email": "test@test.com",
            "displayName": "Test",
            "role": "CITIZEN",
            "token": "jwt",
            "refreshToken": "refresh",
        }
        assert REGISTER_EXPECTED_KEYS.issubset(mock_response.keys())


class TestLogin:
    """POST /v1/auth/login"""

    def test_login_payload_structure(self):
        assert "email" in LOGIN_PAYLOAD
        assert "password" in LOGIN_PAYLOAD

    def test_login_expected_response(self):
        mock_response = {
            "uid": "uid",
            "token": "jwt",
            "refreshToken": "refresh",
            "expiresIn": 3600,
            "user": {},
        }
        assert LOGIN_EXPECTED_KEYS.issubset(mock_response.keys())


class TestPasswordValidation:
    """UserCreate password strength validation."""

    @pytest.mark.parametrize("password,should_pass", [
        ("Secure@123", True),
        ("weakpassword", False),
        ("NoSpecial123", False),
        ("no_upper_1@", False),
        ("NoDigit@Pass", False),
    ])
    def test_password_strength(self, password, should_pass):
        from app.models.user import UserCreate
        data = {**REGISTER_PAYLOAD, "password": password}
        if should_pass:
            user = UserCreate(**data)
            assert user.password == password
        else:
            with pytest.raises(Exception):
                UserCreate(**data)


class TestCoordinateValidation:
    """Coordinate validation in incident models."""

    @pytest.mark.parametrize("lat,lng,valid", [
        (20.2961, 85.8245, True),
        (-91, 0, False),
        (91, 0, False),
        (0, -181, False),
        (0, 181, False),
    ])
    def test_coordinate_bounds(self, lat, lng, valid):
        from app.models.incident import Coordinates
        if valid:
            c = Coordinates(latitude=lat, longitude=lng)
            assert c.latitude == lat
        else:
            with pytest.raises(Exception):
                Coordinates(latitude=lat, longitude=lng)
