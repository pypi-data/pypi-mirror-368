"""
Stytch B2B session token verification.

Handles verification of session tokens with the Stytch B2B API, including
caching, error handling, and session data extraction.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import stytch

from ..cache.redis_client import redis_client
from ..models.context import StytchContext
from ..utils.config import settings
from ..utils.exceptions import StytchAPIError, TokenVerificationError
from ..utils.logger import logger


class StytchVerifier:
    """
    Handles Stytch B2B session token verification with Redis caching.

    Provides a two-tier verification system:
    1. Check Redis cache for previously verified tokens
    2. Fall back to Stytch API for fresh verification
    """

    def __init__(self) -> None:
        self._client: Optional[stytch.B2BClient] = None

    def _get_client(self) -> stytch.B2BClient:
        """
        Get or create Stytch B2B client.

        Returns:
            Configured Stytch B2B client

        Raises:
            StytchAPIError: If client cannot be configured
        """
        if self._client is None:
            try:
                # These should be validated as non-None by the model_validator
                assert settings.project_id is not None, "project_id must be set"
                assert settings.secret is not None, "secret must be set"

                # Log configuration details for debugging (safe for production)
                logger.error("🔧 [STYTCH DEBUG] Initializing Stytch B2B client with:")
                logger.error(
                    f"🔧 [STYTCH DEBUG] - project_id: {'LIVE' if settings.project_id and settings.project_id.startswith('project-live-') else 'TEST' if settings.project_id and settings.project_id.startswith('project-test-') else 'UNKNOWN'}"
                )
                logger.error(f"🔧 [STYTCH DEBUG] - environment: {settings.environment}")
                logger.error(
                    f"🔧 [STYTCH DEBUG] - secret: {'LIVE' if settings.secret and settings.secret.startswith('secret-live-') else 'TEST' if settings.secret and settings.secret.startswith('secret-test-') else 'UNKNOWN'}"
                )

                self._client = stytch.B2BClient(
                    project_id=settings.project_id,
                    secret=settings.secret,
                    environment=settings.environment,
                )
                logger.error(
                    "🔧 [STYTCH DEBUG] ✅ Stytch B2B client initialized successfully"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Stytch client: {str(e)}")
                raise StytchAPIError(f"Stytch client initialization failed: {str(e)}")

        return self._client

    def _hash_token(self, token: str) -> str:
        """
        Create a hash of the token for cache key generation.

        Args:
            token: Session token to hash

        Returns:
            SHA256 hash of the token
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def verify_session_token(self, token: str) -> StytchContext:
        """
        Verify session token with caching support.

        Args:
            token: Stytch session token to verify

        Returns:
            StytchContext with session data

        Raises:
            TokenVerificationError: If token verification fails
            StytchAPIError: If Stytch API is unreachable
        """
        token_hash = self._hash_token(token)

        # Try cache first
        cached_result = await self._get_cached_verification(token_hash)
        if cached_result:
            return self._build_context_from_cache(cached_result)

        # Fall back to Stytch API
        session_data = await self._verify_with_stytch_api(token)

        # Cache the result
        await self._cache_verification_result(token_hash, session_data)

        return self._build_context_from_stytch_data(session_data)

    async def _get_cached_verification(
        self, token_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached verification result.

        Args:
            token_hash: Hash of the token to look up

        Returns:
            Cached verification data if found and valid
        """
        try:
            cached_data = await redis_client.get_cached_verification(token_hash)
            if cached_data:
                # Check if cached session is still valid
                expires_at_str = cached_data.get("session_expires_at")
                if not expires_at_str or not isinstance(expires_at_str, str):
                    return None
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now(timezone.utc) < expires_at:
                    logger.debug("Using cached verification result")
                    return cached_data
                else:
                    logger.debug("Cached session expired, removing from cache")
                    await redis_client.delete_cached_verification(token_hash)

            return None

        except Exception as e:
            logger.warning(f"Cache lookup failed: {str(e)}")
            return None

    async def _verify_with_stytch_api(self, token: str) -> Dict[str, Any]:
        """
        Verify token directly with Stytch B2B API.

        Args:
            token: Session token to verify

        Returns:
            Raw session data from Stytch API

        Raises:
            TokenVerificationError: If token is invalid
            StytchAPIError: If API call fails

        Note:
            This method contains extensive debug logging (marked with 🔍 [DEBUG])
            to help diagnose response parsing issues. This logging should be
            removed or reduced in a future release once the parsing issues
            are fully resolved.
        """
        try:
            client = self._get_client()

            logger.debug("Verifying token with Stytch API")
            logger.debug(
                f"🔍 [DEBUG] Starting Stytch API verification (token: {token[:8]}...)"
            )
            response = client.sessions.authenticate(session_token=token)

            # Enhanced debug logging for response analysis
            logger.debug(f"🔍 [DEBUG] Response type: {type(response)}")
            logger.debug(f"🔍 [DEBUG] Response class: {response.__class__}")
            logger.debug(
                f"🔍 [DEBUG] Response status_code: {getattr(response, 'status_code', 'N/A')}"
            )
            logger.debug(
                f"🔍 [DEBUG] Response has json method: {hasattr(response, 'json')}"
            )
            logger.debug(
                f"🔍 [DEBUG] Response has __dict__: {hasattr(response, '__dict__')}"
            )
            logger.debug(
                f"🔍 [DEBUG] Response has member_session attr: {hasattr(response, 'member_session')}"
            )
            logger.debug(
                f"🔍 [DEBUG] Response has member attr: {hasattr(response, 'member')}"
            )
            logger.debug(
                f"🔍 [DEBUG] Response isinstance str: {isinstance(response, str)}"
            )
            logger.debug(
                f"🔍 [DEBUG] Response isinstance dict: {isinstance(response, dict)}"
            )

            # Log response attributes for debugging
            if hasattr(response, "__dict__"):
                logger.debug(
                    f"🔍 [DEBUG] Response __dict__ keys: {list(response.__dict__.keys())}"
                )

            # Log first 300 chars of string representation
            response_str_preview = str(response)[:300]
            logger.debug(f"🔍 [DEBUG] Response str preview: {response_str_preview}")
            logger.debug(
                f"🔍 [DEBUG] Response str starts with {{: {str(response).startswith('{')}"
            )
            logger.debug(
                f"🔍 [DEBUG] Response str ends with }}: {str(response).endswith('}')}"
            )

            if hasattr(response, "status_code") and response.status_code != 200:
                logger.warning(
                    f"Stytch API returned error: {response.status_code}",
                    extra={
                        "response": (
                            response.json()
                            if hasattr(response, "json")
                            else str(response)
                        )
                    },
                )
                raise TokenVerificationError(
                    "Invalid or expired session token", token_hint=token[:8] + "..."
                )

            # Handle different response formats from Stytch SDK
            session_data = None
            parsing_path = "unknown"

            # First, try to convert response to string to check if it's JSON
            response_str = str(response)
            logger.debug(
                f"🔍 [DEBUG] Response string representation: {response_str[:200]}..."
            )

            if hasattr(response, "json") and callable(response.json):
                # Response is an HTTP response object
                parsing_path = "http_response_json_method"
                logger.debug(f"🔍 [DEBUG] Attempting parsing path: {parsing_path}")
                try:
                    session_data = response.json()
                    logger.debug("🔍 [DEBUG] ✅ Successfully called .json() method")
                    logger.debug(
                        f"🔍 [DEBUG] .json() returned type: {type(session_data)}"
                    )

                    # Check if .json() returned a string instead of parsed data
                    if isinstance(session_data, str):
                        logger.debug(
                            "🔍 [DEBUG] .json() returned string, parsing as JSON"
                        )
                        session_data = json.loads(session_data)
                        logger.debug(
                            "🔍 [DEBUG] ✅ Successfully parsed JSON string from .json() method"
                        )
                        logger.debug(
                            f"🔍 [DEBUG] Final parsed data type: {type(session_data)}"
                        )
                    else:
                        logger.debug("🔍 [DEBUG] .json() returned parsed data directly")

                except Exception as e:
                    logger.error(
                        f"🔍 [DEBUG] ❌ Failed to parse using .json() method: {e}"
                    )
                    session_data = None
            elif isinstance(response, dict):
                # Response is already a dictionary
                parsing_path = "already_dict"
                logger.debug(f"🔍 [DEBUG] Attempting parsing path: {parsing_path}")
                session_data = response
                logger.debug("🔍 [DEBUG] ✅ Response is already a dictionary")
                logger.debug(f"🔍 [DEBUG] Dict keys: {list(session_data.keys())}")
            elif hasattr(response, "member_session") and hasattr(response, "member"):
                # Modern Stytch response object with direct attributes
                parsing_path = "stytch_object_direct_attrs"
                logger.debug(f"🔍 [DEBUG] Attempting parsing path: {parsing_path}")
                member_session = getattr(response, "member_session", {})
                member = getattr(response, "member", {})
                organization = getattr(response, "organization", {})

                logger.debug(f"🔍 [DEBUG] member_session type: {type(member_session)}")
                logger.debug(f"🔍 [DEBUG] member type: {type(member)}")
                logger.debug(f"🔍 [DEBUG] organization type: {type(organization)}")

                # Convert objects to dicts if they're not already
                if hasattr(member_session, "__dict__"):
                    member_session = member_session.__dict__
                    logger.debug("🔍 [DEBUG] Converted member_session to dict")
                if hasattr(member, "__dict__"):
                    member = member.__dict__
                    logger.debug("🔍 [DEBUG] Converted member to dict")
                if hasattr(organization, "__dict__"):
                    organization = organization.__dict__
                    logger.debug("🔍 [DEBUG] Converted organization to dict")

                session_data = {
                    "status_code": getattr(response, "status_code", 200),
                    "request_id": getattr(response, "request_id", ""),
                    "member_session": member_session,
                    "member": member,
                    "organization": organization,
                    "session_token": getattr(response, "session_token", ""),
                    "session_jwt": getattr(response, "session_jwt", ""),
                }
                logger.debug(
                    "🔍 [DEBUG] ✅ Converted Stytch response object to dict using direct attributes"
                )
                logger.debug(
                    f"🔍 [DEBUG] Final session_data keys: {list(session_data.keys())}"
                )
            elif response_str.startswith("{") and response_str.endswith("}"):
                # Response looks like JSON - try to parse it
                parsing_path = "json_string_from_str_repr"
                logger.debug(f"🔍 [DEBUG] Attempting parsing path: {parsing_path}")
                logger.debug(f"🔍 [DEBUG] JSON string length: {len(response_str)}")
                try:
                    session_data = json.loads(response_str)
                    logger.debug(
                        "🔍 [DEBUG] ✅ Parsed response as JSON string from string representation"
                    )
                    logger.debug(f"🔍 [DEBUG] Parsed data type: {type(session_data)}")
                    logger.debug(
                        f"🔍 [DEBUG] Parsed data keys: {list(session_data.keys()) if isinstance(session_data, dict) else 'N/A'}"
                    )
                except json.JSONDecodeError as e:
                    logger.error(
                        f"🔍 [DEBUG] ❌ Failed to parse JSON string response: {e}"
                    )
                    logger.error(
                        f"🔍 [DEBUG] Raw response content: {response_str[:500]}..."
                    )
                    raise StytchAPIError(
                        "Invalid JSON response from Stytch API",
                        api_response={"error": f"JSON parse error: {str(e)}"},
                    )
            elif isinstance(response, str):
                # Response is a JSON string - parse it
                parsing_path = "direct_string_instance"
                logger.debug(f"🔍 [DEBUG] Attempting parsing path: {parsing_path}")
                logger.debug(f"🔍 [DEBUG] String length: {len(response)}")
                try:
                    session_data = json.loads(response)
                    logger.debug("🔍 [DEBUG] ✅ Parsed response as JSON string")
                    logger.debug(f"🔍 [DEBUG] Parsed data type: {type(session_data)}")
                    logger.debug(
                        f"🔍 [DEBUG] Parsed data keys: {list(session_data.keys()) if isinstance(session_data, dict) else 'N/A'}"
                    )
                except json.JSONDecodeError as e:
                    logger.error(
                        f"🔍 [DEBUG] ❌ Failed to parse JSON string response: {e}"
                    )
                    logger.error(
                        f"🔍 [DEBUG] Raw response content: {response[:500]}..."
                    )
                    raise StytchAPIError(
                        "Invalid JSON response from Stytch API",
                        api_response={"error": f"JSON parse error: {str(e)}"},
                    )
            elif hasattr(response, "__dict__"):
                # Response is a Stytch response object - convert to dict
                parsing_path = "generic_object_dict"
                logger.debug(f"🔍 [DEBUG] Attempting parsing path: {parsing_path}")
                session_data = response.__dict__
                logger.debug(
                    "🔍 [DEBUG] ✅ Converted response object to dict using __dict__"
                )
                logger.debug(f"🔍 [DEBUG] Dict keys: {list(session_data.keys())}")
            else:
                # Response is some other format - try to get its attributes
                parsing_path = "fallback_vars"
                logger.debug(f"🔍 [DEBUG] Attempting parsing path: {parsing_path}")
                logger.warning(
                    f"🔍 [DEBUG] ⚠️ Unexpected response format: {type(response)}"
                )
                logger.debug(f"🔍 [DEBUG] Response content: {response_str[:200]}...")
                session_data = vars(response) if hasattr(response, "__dict__") else {}
                logger.debug(f"🔍 [DEBUG] Fallback session_data: {session_data}")

            # Final validation and logging
            logger.debug("🔍 [DEBUG] Final parsing result:")
            logger.debug(f"🔍 [DEBUG] - Parsing path used: {parsing_path}")
            logger.debug(f"🔍 [DEBUG] - Session data type: {type(session_data)}")
            logger.debug(f"🔍 [DEBUG] - Session data is None: {session_data is None}")

            # Validate we have the expected data structure
            if not isinstance(session_data, dict):
                logger.error(
                    "🔍 [DEBUG] ❌ VALIDATION FAILED: Session data is not a dict"
                )
                logger.error(f"🔍 [DEBUG] - Session data type: {type(session_data)}")
                logger.error(
                    f"🔍 [DEBUG] - Session data content: {str(session_data)[:200]}..."
                )
                logger.error(f"🔍 [DEBUG] - Parsing path used: {parsing_path}")
                logger.error(f"🔍 [DEBUG] - Original response type: {type(response)}")
                logger.error(
                    f"🔍 [DEBUG] - Original response class: {response.__class__}"
                )
                raise StytchAPIError(
                    "Invalid response format from Stytch API",
                    api_response={"error": f"Expected dict, got {type(session_data)}"},
                )

            logger.debug("🔍 [DEBUG] ✅ Session data validation passed - type is dict")
            logger.debug(f"🔍 [DEBUG] Session data keys: {list(session_data.keys())}")

            # Check for required fields in the response
            # Stytch B2B API returns member_session instead of separate member/session
            if "member_session" not in session_data or "member" not in session_data:
                logger.error(
                    "🔍 [DEBUG] ❌ FIELD VALIDATION FAILED: Missing required fields"
                )
                logger.error(
                    f"🔍 [DEBUG] - Available keys: {list(session_data.keys())}"
                )
                logger.error(
                    f"🔍 [DEBUG] - Has member_session: {'member_session' in session_data}"
                )
                logger.error(f"🔍 [DEBUG] - Has member: {'member' in session_data}")
                logger.error(f"🔍 [DEBUG] - Parsing path used: {parsing_path}")
                raise StytchAPIError(
                    "Invalid session data format from Stytch API",
                    api_response={"error": "Missing member_session or member data"},
                )

            logger.debug("🔍 [DEBUG] ✅ Required fields validation passed")
            logger.info("Token verified successfully with Stytch API")
            logger.debug(
                f"🔍 [DEBUG] 🎉 Complete success - returning session data with {len(session_data)} keys"
            )
            return session_data

        except TokenVerificationError:
            # Re-raise token verification errors as-is
            raise

        except Exception as e:
            # Log configuration details when API calls fail to help diagnose environment issues
            logger.error("🔧 [STYTCH DEBUG] API verification failed - Current config:")
            logger.error(
                f"🔧 [STYTCH DEBUG] - Environment setting: {settings.environment}"
            )
            logger.error(
                f"🔧 [STYTCH DEBUG] - Project type: {'LIVE' if settings.project_id and settings.project_id.startswith('project-live-') else 'TEST' if settings.project_id and settings.project_id.startswith('project-test-') else 'UNKNOWN'}"
            )
            logger.error(f"Stytch API verification failed: {str(e)}", exc_info=True)
            raise StytchAPIError(
                f"Failed to verify token with Stytch: {str(e)}",
                api_response={"error": str(e)},
            )

    async def _cache_verification_result(
        self, token_hash: str, session_data: Dict[str, Any]
    ) -> None:
        """
        Cache verification result for future use.

        Args:
            token_hash: Hash of the verified token
            session_data: Session data from Stytch API
        """
        try:
            # Extract essential data for caching
            # Handle both dict and object formats from Stytch SDK
            member_data = session_data.get("member", {})
            session_data_inner = session_data.get("member_session", {})
            organization_data = session_data.get("organization", {})

            # Helper function to safely get attribute from object or dict
            def safe_get(obj: Any, attr: str, default: Any = None) -> Any:
                if hasattr(obj, attr):
                    return getattr(obj, attr)
                elif isinstance(obj, dict):
                    return obj.get(attr, default)
                return default

            # Normalize authentication factors for caching
            raw_auth_factors = safe_get(
                session_data_inner, "authentication_factors", []
            )
            normalized_factors = []
            for factor in raw_auth_factors:
                if isinstance(factor, dict):
                    factor_type = factor.get("type", "unknown")
                    normalized_factors.append(factor_type)
                elif isinstance(factor, str):
                    normalized_factors.append(factor)
                else:
                    normalized_factors.append(str(factor))

            cache_data = {
                "member_id": safe_get(member_data, "member_id")
                or safe_get(session_data_inner, "member_id"),
                "session_id": safe_get(session_data_inner, "member_session_id"),
                "organization_id": safe_get(organization_data, "organization_id")
                or safe_get(session_data_inner, "organization_id"),
                "session_started_at": safe_get(session_data_inner, "started_at"),
                "session_expires_at": safe_get(session_data_inner, "expires_at"),
                "session_last_accessed_at": safe_get(
                    session_data_inner, "last_accessed_at"
                ),
                "member_email": safe_get(member_data, "email_address"),
                "member_name": safe_get(member_data, "name"),
                "session_custom_claims": safe_get(
                    session_data_inner, "custom_claims", {}
                ),
                "authentication_factors": normalized_factors,
                "raw_session_data": session_data,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }

            await redis_client.cache_verification_result(token_hash, cache_data)

        except Exception as e:
            logger.warning(f"Failed to cache verification result: {str(e)}")
            # Don't raise - caching failures should be non-fatal

    def _build_context_from_cache(self, cached_data: Dict[str, Any]) -> StytchContext:
        """
        Build StytchContext from cached verification data.

        Args:
            cached_data: Cached session data

        Returns:
            StytchContext instance
        """
        # Handle datetime fields safely
        started_at = cached_data.get("session_started_at")
        expires_at = cached_data.get("session_expires_at")
        last_accessed_at = cached_data.get("session_last_accessed_at")

        return StytchContext(
            member_id=cached_data["member_id"],
            session_id=cached_data["session_id"],
            organization_id=cached_data["organization_id"],
            session_started_at=(
                datetime.fromisoformat(started_at)
                if started_at
                else datetime.now(timezone.utc)
            ),
            session_expires_at=(
                datetime.fromisoformat(expires_at)
                if expires_at
                else datetime.now(timezone.utc)
            ),
            session_last_accessed_at=(
                datetime.fromisoformat(last_accessed_at)
                if last_accessed_at
                else datetime.now(timezone.utc)
            ),
            member_email=cached_data.get("member_email"),
            member_name=cached_data.get("member_name"),
            session_custom_claims=cached_data.get("session_custom_claims", {}),
            authentication_factors=cached_data.get("authentication_factors", []),
            raw_session_data=cached_data.get("raw_session_data", {}),
        )

    def _build_context_from_stytch_data(
        self, session_data: Dict[str, Any]
    ) -> StytchContext:
        """
        Build StytchContext from fresh Stytch API response.

        Args:
            session_data: Raw session data from Stytch API

        Returns:
            StytchContext instance
        """
        # Handle both dict and object formats from Stytch SDK
        member = session_data.get("member", {})
        session = session_data.get("member_session", {})
        organization = session_data.get("organization", {})

        # Helper function to safely get attribute from object or dict
        def safe_get(obj: Any, attr: str, default: Any = None) -> Any:
            if hasattr(obj, attr):
                return getattr(obj, attr)
            elif isinstance(obj, dict):
                return obj.get(attr, default)
            return default

        # Helper function to normalize authentication factors
        def normalize_auth_factors(factors: Any) -> List[str]:
            """Convert authentication factors to list of strings."""
            if not factors:
                return []

            normalized = []
            for factor in factors:
                if isinstance(factor, dict):
                    # Extract the type from the dict or use a fallback
                    factor_type = factor.get("type", "unknown")
                    normalized.append(factor_type)
                    logger.debug(
                        f"🔍 [DEBUG] Normalized auth factor dict to string: {factor_type}"
                    )
                elif isinstance(factor, str):
                    # Already a string, keep as-is
                    normalized.append(factor)
                else:
                    # Fallback for unexpected types
                    normalized.append(str(factor))
                    logger.debug(
                        f"🔍 [DEBUG] Converted auth factor to string: {str(factor)}"
                    )

            logger.debug(f"🔍 [DEBUG] Final normalized auth factors: {normalized}")
            return normalized

        # Handle datetime fields safely
        started_at = safe_get(session, "started_at")
        expires_at = safe_get(session, "expires_at")
        last_accessed_at = safe_get(session, "last_accessed_at")

        # Get and normalize authentication factors
        raw_auth_factors = safe_get(session, "authentication_factors", [])
        logger.debug(f"🔍 [DEBUG] Raw auth factors: {raw_auth_factors}")
        logger.debug(f"🔍 [DEBUG] Raw auth factors type: {type(raw_auth_factors)}")
        if raw_auth_factors:
            logger.debug(
                f"🔍 [DEBUG] First auth factor type: {type(raw_auth_factors[0])}"
            )
            logger.debug(f"🔍 [DEBUG] First auth factor content: {raw_auth_factors[0]}")
        normalized_auth_factors = normalize_auth_factors(raw_auth_factors)

        return StytchContext(
            member_id=safe_get(member, "member_id") or safe_get(session, "member_id"),
            session_id=safe_get(session, "member_session_id"),
            organization_id=safe_get(organization, "organization_id")
            or safe_get(session, "organization_id"),
            session_started_at=(
                datetime.fromisoformat(started_at)
                if started_at
                else datetime.now(timezone.utc)
            ),
            session_expires_at=(
                datetime.fromisoformat(expires_at)
                if expires_at
                else datetime.now(timezone.utc)
            ),
            session_last_accessed_at=(
                datetime.fromisoformat(last_accessed_at)
                if last_accessed_at
                else datetime.now(timezone.utc)
            ),
            member_email=safe_get(member, "email_address"),
            member_name=safe_get(member, "name"),
            session_custom_claims=safe_get(session, "custom_claims", {}),
            authentication_factors=normalized_auth_factors,
            raw_session_data=session_data,
        )

    async def get_member_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a member's details by their email address.
        This is needed to resolve an email to a Stytch member ID, which is used
        to add a user to a project in the soulmates-file-management service.
        """
        logger.info(f"Attempting to get member by email: {email}")

        if not settings.organization_id:
            raise StytchAPIError(
                "Organization ID is required for member search operations. "
                "Please set STYTCH_ORGANIZATION_ID environment variable."
            )

        try:
            client = self._get_client()
            # Note: This requires the organization ID to be set in the config.
            # This is a temporary solution until a more robust user management
            # service is in place.
            response = client.organizations.members.search(
                organization_ids=[settings.organization_id],
                query={
                    "operator": "AND",
                    "operands": [
                        {"filter_name": "member_emails", "filter_value": [email]}
                    ],
                },
            )

            response_json: Dict[str, Any] = {}
            try:
                if hasattr(response, "json"):
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        response_json = json_data
            except Exception:
                pass  # Keep response_json as empty dict

            if response.status_code != 200:
                logger.warning(
                    f"Stytch API returned error when searching for member: {response.status_code}",
                    extra={"response": response_json},
                )
                raise StytchAPIError(
                    f"Stytch API error ({response.status_code})",
                    api_response=response_json,
                )

            # Ensure response_json is a dictionary (should already be guaranteed by above logic)

            members = response_json.get("members", [])
            if members:
                logger.info(f"Found member for email: {email}")
                return members[0]

            logger.info(f"Member not found for email: {email}")
            return None

        except StytchAPIError as e:
            logger.error(
                f"Stytch API search for member failed: {e.message}",
                extra={"api_response": e.details.get("api_response")},
            )
            raise  # Re-raise the exception to be handled by the endpoint
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during Stytch member search: {str(e)}",
                exc_info=True,
            )
            raise StytchAPIError(f"An unexpected error occurred: {str(e)}")


# Global verifier instance
stytch_verifier = StytchVerifier()
