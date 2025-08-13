"""
Tests for the main middleware functionality.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from ayz_auth.middleware import (
    create_auth_dependency,
    verify_auth,
    verify_auth_optional,
)
from ayz_auth.models.context import StytchContext
from ayz_auth.utils.exceptions import (
    StytchAPIError,
    TokenExtractionError,
    TokenVerificationError,
)

# Test FastAPI app
app = FastAPI()


@app.get("/protected")
async def protected_route(user: StytchContext = Depends(verify_auth)):
    return {"member_id": user.member_id, "email": user.member_email}


@app.get("/optional")
async def optional_route(user: StytchContext = Depends(verify_auth_optional)):
    if user:
        return {"authenticated": True, "member_id": user.member_id}
    else:
        return {"authenticated": False}


# Custom auth dependency for testing
admin_auth = create_auth_dependency(required_claims=["admin"])


@app.get("/admin")
async def admin_route(user: StytchContext = Depends(admin_auth)):
    return {"message": "Admin access granted"}


client = TestClient(app)


class TestMiddleware:
    """Test cases for middleware functionality."""

    def create_mock_stytch_context(self, **kwargs):
        """Create a mock StytchContext for testing."""
        defaults = {
            "member_id": "member_123",
            "session_id": "session_456",
            "organization_id": "org_789",
            "session_started_at": datetime.now(timezone.utc) - timedelta(hours=1),
            "session_expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "session_last_accessed_at": datetime.now(timezone.utc),
            "member_email": "test@example.com",
            "member_name": "Test User",
            "session_custom_claims": {},
            "authentication_factors": ["password"],
            "raw_session_data": {},
        }
        defaults.update(kwargs)
        return StytchContext(**defaults)

    @patch("ayz_auth.middleware.stytch_verifier.verify_session_token")
    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_successful_authentication(self, mock_extract, mock_verify):
        """Test successful authentication flow."""
        # Setup mocks
        mock_extract.return_value = "valid_token_12345678901234567890"
        mock_context = self.create_mock_stytch_context()
        mock_verify.return_value = mock_context

        # Make request
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer valid_token_12345678901234567890"},
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == "member_123"
        assert data["email"] == "test@example.com"

        # Verify mocks were called
        mock_extract.assert_called_once()
        mock_verify.assert_called_once_with("valid_token_12345678901234567890")

    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_token_extraction_error(self, mock_extract):
        """Test handling of token extraction errors."""
        mock_extract.side_effect = TokenExtractionError(
            "Authorization header is required"
        )

        response = client.get("/protected")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "authentication_failed"
        assert data["detail"]["type"] == "token_extraction"
        assert "Authorization header is required" in data["detail"]["message"]

    @patch("ayz_auth.middleware.stytch_verifier.verify_session_token")
    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_token_verification_error(self, mock_extract, mock_verify):
        """Test handling of token verification errors."""
        mock_extract.return_value = "invalid_token_12345678901234567890"
        mock_verify.side_effect = TokenVerificationError(
            "Invalid or expired session token"
        )

        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid_token_12345678901234567890"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"] == "authentication_failed"
        assert data["detail"]["type"] == "token_verification"
        assert "Invalid or expired session token" in data["detail"]["message"]

    @patch("ayz_auth.middleware.stytch_verifier.verify_session_token")
    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_stytch_api_error(self, mock_extract, mock_verify):
        """Test handling of Stytch API errors."""
        mock_extract.return_value = "valid_token_12345678901234567890"
        mock_verify.side_effect = StytchAPIError("Stytch API is down")

        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer valid_token_12345678901234567890"},
        )

        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["error"] == "service_unavailable"
        assert data["detail"]["type"] == "stytch_api"
        assert "temporarily unavailable" in data["detail"]["message"]

    @patch("ayz_auth.middleware.stytch_verifier.verify_session_token")
    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_unexpected_error(self, mock_extract, mock_verify):
        """Test handling of unexpected errors."""
        mock_extract.return_value = "valid_token_12345678901234567890"
        mock_verify.side_effect = Exception("Unexpected error")

        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer valid_token_12345678901234567890"},
        )

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "internal_server_error"
        assert data["detail"]["type"] == "unknown"

    @patch("ayz_auth.middleware.stytch_verifier.verify_session_token")
    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_optional_auth_success(self, mock_extract, mock_verify):
        """Test optional authentication with valid token."""
        mock_extract.return_value = "valid_token_12345678901234567890"
        mock_context = self.create_mock_stytch_context()
        mock_verify.return_value = mock_context

        response = client.get(
            "/optional",
            headers={"Authorization": "Bearer valid_token_12345678901234567890"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["member_id"] == "member_123"

    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_optional_auth_failure(self, mock_extract):
        """Test optional authentication with invalid token."""
        mock_extract.side_effect = TokenExtractionError(
            "Authorization header is required"
        )

        response = client.get("/optional")

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False

    @patch("ayz_auth.middleware.stytch_verifier.verify_session_token")
    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_custom_auth_dependency_success(self, mock_extract, mock_verify):
        """Test custom auth dependency with required claims."""
        mock_extract.return_value = "valid_token_12345678901234567890"
        mock_context = self.create_mock_stytch_context(
            session_custom_claims={"admin": True, "role": "administrator"}
        )
        mock_verify.return_value = mock_context

        response = client.get(
            "/admin",
            headers={"Authorization": "Bearer valid_token_12345678901234567890"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Admin access granted"

    @patch("ayz_auth.middleware.stytch_verifier.verify_session_token")
    @patch("ayz_auth.middleware.extract_token_from_request")
    def test_custom_auth_dependency_missing_claims(self, mock_extract, mock_verify):
        """Test custom auth dependency with missing required claims."""
        mock_extract.return_value = "valid_token_12345678901234567890"
        mock_context = self.create_mock_stytch_context(
            session_custom_claims={"role": "user"}  # Missing "admin" claim
        )
        mock_verify.return_value = mock_context

        response = client.get(
            "/admin",
            headers={"Authorization": "Bearer valid_token_12345678901234567890"},
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"] == "insufficient_permissions"
        assert data["detail"]["type"] == "authorization"
        assert "admin" in data["detail"]["message"]

    def test_create_auth_dependency_with_factors(self):
        """Test creating auth dependency with required authentication factors."""
        mfa_auth = create_auth_dependency(required_factors=["mfa", "sms"])

        # This is a basic test to ensure the function returns a callable
        assert callable(mfa_auth)

        # The actual functionality would be tested in integration tests
        # since it requires a full FastAPI app setup


if __name__ == "__main__":
    pytest.main([__file__])
