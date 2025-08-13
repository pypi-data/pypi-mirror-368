# ayz-auth

FastAPI middleware for Stytch B2B authentication with Redis caching.

## Overview

`ayz-auth` is a lightweight, production-ready authentication middleware for FastAPI applications using Stytch B2B authentication services. It provides session token verification with Redis caching for optimal performance and includes comprehensive error handling and logging.

## Features

- 🔐 **Stytch B2B Integration**: Seamless integration with Stytch B2B authentication
- ⚡ **Redis Caching**: Intelligent caching to reduce API calls and improve performance
- 🚀 **FastAPI Native**: Built specifically for FastAPI with proper dependency injection
- 📝 **Type Safe**: Full Pydantic models with type hints throughout
- 🛡️ **Security First**: Secure token handling with configurable logging levels
- 🔧 **Configurable**: Environment-based configuration with sensible defaults
- 📊 **Comprehensive Logging**: Structured logging with sensitive data protection
- 🧪 **Well Tested**: Comprehensive test suite with mocking support

## Installation

```bash
pip install ayz-auth
```

Or with UV:

```bash
uv add ayz-auth
```

## Quick Start

### 1. Environment Configuration

Create a `.env` file or set environment variables:

```bash
STYTCH_PROJECT_ID=your_project_id
STYTCH_SECRET=your_secret_key
STYTCH_ENV=test  # or "live" for production
# STYTCH_ORGANIZATION_ID=your_org_id  # optional, only needed for member search operations
REDIS_URL=redis://localhost:6379
```

### 2. Basic Usage

```python
from fastapi import FastAPI, Depends
from ayz_auth import verify_auth, StytchContext

app = FastAPI()

@app.get("/protected")
async def protected_route(user: StytchContext = Depends(verify_auth)):
    return {
        "message": f"Hello {user.member_email}",
        "member_id": user.member_id,
        "organization_id": user.organization_id
    }

@app.get("/user-info")
async def get_user_info(user: StytchContext = Depends(verify_auth)):
    return {
        "member_id": user.member_id,
        "email": user.member_email,
        "name": user.member_name,
        "organization_id": user.organization_id,
        "session_expires_at": user.session_expires_at,
        "authentication_factors": user.authentication_factors
    }
```

### 3. Optional Authentication

For endpoints that work with or without authentication:

```python
from typing import Optional
from ayz_auth import verify_auth_optional

@app.get("/optional-auth")
async def optional_route(user: Optional[StytchContext] = Depends(verify_auth_optional)):
    if user:
        return {"message": f"Hello {user.member_email}"}
    else:
        return {"message": "Hello anonymous user"}
```

### 4. Custom Authentication Requirements

Create custom dependencies with additional requirements:

```python
from ayz_auth import create_auth_dependency

# Require specific custom claims
admin_auth = create_auth_dependency(required_claims=["admin"])
moderator_auth = create_auth_dependency(required_claims=["moderator", "verified"])

# Require specific authentication factors
mfa_auth = create_auth_dependency(required_factors=["mfa"])

@app.get("/admin")
async def admin_route(user: StytchContext = Depends(admin_auth)):
    return {"message": "Admin access granted"}

@app.get("/sensitive")
async def sensitive_route(user: StytchContext = Depends(mfa_auth)):
    return {"message": "MFA verified access"}
```

## Configuration

All configuration is handled through environment variables with the `STYTCH_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `STYTCH_PROJECT_ID` | *required* | Your Stytch project ID |
| `STYTCH_SECRET` | *required* | Your Stytch secret key |
| `STYTCH_ENV` | `test` | Stytch environment (`test` or `live`) |
| `STYTCH_REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `STYTCH_REDIS_PASSWORD` | `None` | Redis password (if required) |
| `STYTCH_REDIS_DB` | `0` | Redis database number |
| `STYTCH_CACHE_TTL` | `300` | Cache TTL in seconds (5 minutes) |
| `STYTCH_CACHE_PREFIX` | `ayz_auth` | Redis key prefix |
| `STYTCH_LOG_LEVEL` | `INFO` | Logging level |
| `STYTCH_LOG_SENSITIVE_DATA` | `False` | Log sensitive data (never in production) |
| `STYTCH_REQUEST_TIMEOUT` | `10` | Request timeout in seconds |
| `STYTCH_MAX_RETRIES` | `3` | Maximum retry attempts |

## StytchContext Model

The `StytchContext` model contains all the essential session data from Stytch:

```python
class StytchContext(BaseModel):
    # Core identifiers
    member_id: str
    session_id: str
    organization_id: str
    
    # Session timing
    session_started_at: datetime
    session_expires_at: datetime
    session_last_accessed_at: datetime
    authenticated_at: datetime
    
    # Member information
    member_email: Optional[str]
    member_name: Optional[str]
    
    # Session metadata
    session_custom_claims: Dict[str, Any]
    authentication_factors: List[str]
    raw_session_data: Dict[str, Any]
    
    # Utility properties
    @property
    def is_expired(self) -> bool: ...
    
    @property
    def time_until_expiry(self) -> Optional[float]: ...
```

## Error Handling

The middleware provides structured error responses:

```python
# 401 Unauthorized - Missing or invalid token
{
    "error": "authentication_failed",
    "message": "Authorization header is required",
    "type": "token_extraction"
}

# 401 Unauthorized - Token verification failed
{
    "error": "authentication_failed", 
    "message": "Invalid or expired session token",
    "type": "token_verification"
}

# 503 Service Unavailable - Stytch API issues
{
    "error": "service_unavailable",
    "message": "Authentication service temporarily unavailable", 
    "type": "stytch_api"
}

# 403 Forbidden - Insufficient permissions (custom auth)
{
    "error": "insufficient_permissions",
    "message": "Missing required claims: ['admin']",
    "type": "authorization"
}

# 403 Forbidden - Insufficient authentication factors (custom auth)
{
    "error": "insufficient_authentication",
    "message": "Missing required authentication factors: ['mfa']",
    "type": "authorization"
}
```

## Caching Strategy

The middleware implements a two-tier verification system:

1. **Redis Cache Check**: Fast lookup of previously verified tokens
2. **Stytch API Fallback**: Fresh verification when cache misses

Cache entries automatically expire based on the session expiration time, ensuring security while maximizing performance.

## Integration with Your User System

Since the middleware only returns Stytch session data, you can easily integrate it with your existing user system:

```python
from your_app.models import User
from your_app.database import get_user_by_stytch_member_id

@app.get("/profile")
async def get_profile(stytch: StytchContext = Depends(verify_auth)):
    # Use the member_id to fetch your user data
    user = await get_user_by_stytch_member_id(stytch.member_id)
    
    if not user:
        raise HTTPException(404, "User not found")
    
    # Check permissions using your user model
    if "read_profile" not in user.permissions:
        raise HTTPException(403, "Insufficient permissions")
    
    return {
        "stytch_data": stytch.to_dict(),
        "user_data": user.to_dict()
    }
```

## Development

### Running Tests

```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest

# Run tests with coverage
pytest --cov=ayz_auth
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:

- GitHub Issues: [https://github.com/brandsoulmates/ayz-auth/issues](https://github.com/brandsoulmates/ayz-auth/issues)
- Documentation: [https://github.com/brandsoulmates/ayz-auth](https://github.com/brandsoulmates/ayz-auth)
