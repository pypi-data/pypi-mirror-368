"""
Example usage of the ayz-auth package.

This demonstrates how to integrate the authentication middleware into a FastAPI application.
"""

from typing import Optional

from fastapi import Depends, FastAPI

from ayz_auth import (
    StytchContext,
    create_auth_dependency,
    verify_auth,
    verify_auth_optional,
)

# Create FastAPI app
app = FastAPI(title="Example API with Stytch Authentication")

# Create custom auth dependencies
admin_auth = create_auth_dependency(required_claims=["admin"])
mfa_auth = create_auth_dependency(required_factors=["mfa"])


@app.get("/")
async def root():
    """Public endpoint - no authentication required."""
    return {
        "message": "Welcome to the API! Use /protected for authenticated endpoints."
    }


@app.get("/protected")
async def protected_route(user: StytchContext = Depends(verify_auth)):
    """Protected endpoint requiring authentication."""
    return {
        "message": f"Hello {user.member_email}!",
        "member_id": user.member_id,
        "organization_id": user.organization_id,
        "session_expires_at": user.session_expires_at.isoformat(),
    }


@app.get("/optional-auth")
async def optional_auth_route(
    user: Optional[StytchContext] = Depends(verify_auth_optional),
):
    """Endpoint that works with or without authentication."""
    if user:
        return {
            "authenticated": True,
            "message": f"Hello {user.member_email}!",
            "member_id": user.member_id,
        }
    else:
        return {
            "authenticated": False,
            "message": "Hello anonymous user!",
        }


@app.get("/admin")
async def admin_route(user: StytchContext = Depends(admin_auth)):
    """Admin-only endpoint requiring 'admin' claim."""
    return {
        "message": "Admin access granted!",
        "member_id": user.member_id,
        "admin_claims": user.session_custom_claims,
    }


@app.get("/secure")
async def secure_route(user: StytchContext = Depends(mfa_auth)):
    """Secure endpoint requiring MFA authentication."""
    return {
        "message": "MFA verified access granted!",
        "member_id": user.member_id,
        "auth_factors": user.authentication_factors,
    }


@app.get("/user-profile")
async def get_user_profile(user: StytchContext = Depends(verify_auth)):
    """
    Example of how to integrate with your own user system.

    The middleware provides Stytch session data, and you use the member_id
    to fetch your own user data from your database.
    """
    # In a real application, you would:
    # user_data = await get_user_by_stytch_member_id(user.member_id)
    #
    # For this example, we'll simulate it:
    simulated_user_data = {
        "user_id": "user_123",
        "name": "John Doe",
        "email": user.member_email,
        "roles": ["user", "editor"],
        "permissions": ["read", "write"],
        "preferences": {
            "theme": "dark",
            "notifications": True,
        },
    }

    return {
        "stytch_session": {
            "member_id": user.member_id,
            "organization_id": user.organization_id,
            "session_expires_at": user.session_expires_at.isoformat(),
        },
        "user_profile": simulated_user_data,
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting example API server...")
    print("Make sure to set these environment variables:")
    print("  STYTCH_PROJECT_ID=your_project_id")
    print("  STYTCH_SECRET=your_secret_key")
    print("  STYTCH_REDIS_URL=redis://localhost:6379  # optional")
    print()
    print("Example requests:")
    print("  GET /                    # Public endpoint")
    print("  GET /protected           # Requires: Authorization: Bearer <token>")
    print("  GET /optional-auth       # Works with or without auth")
    print("  GET /admin               # Requires 'admin' claim")
    print("  GET /secure              # Requires MFA")
    print("  GET /user-profile        # Shows integration pattern")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)
