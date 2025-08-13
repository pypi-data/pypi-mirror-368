"""
Redis cache client for token verification caching.

Provides async Redis operations for caching Stytch token verification results
to improve performance and reduce API calls.
"""

import json
from typing import Any, Dict, Optional

import redis.asyncio as redis

from ..utils.config import settings
from ..utils.exceptions import CacheError
from ..utils.logger import logger


class RedisClient:
    """
    Async Redis client for caching authentication tokens and session data.

    Handles connection management, serialization, and error handling for
    Redis cache operations.
    """

    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None

    async def _get_client(self) -> redis.Redis:
        """
        Get or create Redis client with connection pooling.

        Returns:
            Configured Redis client instance

        Raises:
            CacheError: If Redis connection cannot be established
        """
        if self._client is None:
            try:
                # Create Redis connection pool
                self._connection_pool = redis.ConnectionPool.from_url(
                    settings.redis_url,
                    password=settings.redis_password,
                    db=settings.redis_db,
                    decode_responses=True,
                    max_connections=10,
                    retry_on_timeout=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )

                self._client = redis.Redis(connection_pool=self._connection_pool)

                # Test connection
                await self._client.ping()
                logger.info("Redis connection established successfully")

            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}", exc_info=True)
                raise CacheError(f"Redis connection failed: {str(e)}", "connect")

        return self._client

    def _make_key(self, token_hash: str) -> str:
        """
        Create a cache key for a token.

        Args:
            token_hash: Hash of the session token

        Returns:
            Formatted cache key with prefix
        """
        return f"{settings.cache_prefix}:token:{token_hash}"

    async def get_cached_verification(
        self, token_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached token verification result.

        Args:
            token_hash: Hash of the session token to look up

        Returns:
            Cached verification data if found, None otherwise

        Raises:
            CacheError: If cache operation fails
        """
        try:
            client = await self._get_client()
            cache_key = self._make_key(token_hash)

            cached_data = await client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for token hash: {token_hash[:8]}...")
                parsed_data: Dict[str, Any] = json.loads(cached_data)
                return parsed_data

            logger.debug(f"Cache miss for token hash: {token_hash[:8]}...")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode cached data: {str(e)}")
            # Delete corrupted cache entry
            await self.delete_cached_verification(token_hash)
            return None

        except Exception as e:
            logger.warning(f"Cache get operation failed: {str(e)}")
            # Don't raise - cache failures should be non-fatal
            return None

    async def cache_verification_result(
        self, token_hash: str, verification_data: Dict[str, Any]
    ) -> bool:
        """
        Cache token verification result.

        Args:
            token_hash: Hash of the session token
            verification_data: Verification result to cache

        Returns:
            True if caching succeeded, False otherwise

        Raises:
            CacheError: If cache operation fails critically
        """
        try:
            client = await self._get_client()
            cache_key = self._make_key(token_hash)

            # Serialize data
            serialized_data = json.dumps(verification_data, default=str)

            # Set with TTL
            await client.setex(cache_key, settings.cache_ttl, serialized_data)

            logger.debug(
                f"Cached verification result for token hash: {token_hash[:8]}...",
                extra={"ttl": settings.cache_ttl},
            )
            return True

        except Exception as e:
            logger.warning(f"Cache set operation failed: {str(e)}")
            # Don't raise - cache failures should be non-fatal
            return False

    async def delete_cached_verification(self, token_hash: str) -> bool:
        """
        Delete cached token verification result.

        Args:
            token_hash: Hash of the session token to delete

        Returns:
            True if deletion succeeded, False otherwise
        """
        try:
            client = await self._get_client()
            cache_key = self._make_key(token_hash)

            result = await client.delete(cache_key)
            logger.debug(
                f"Deleted cached verification for token hash: {token_hash[:8]}..."
            )
            return bool(result)

        except Exception as e:
            logger.warning(f"Cache delete operation failed: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        Check if Redis is healthy and responsive.

        Returns:
            True if Redis is healthy, False otherwise
        """
        try:
            client = await self._get_client()
            await client.ping()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection and cleanup resources."""
        if self._client:
            await self._client.close()
            self._client = None

        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None

        logger.info("Redis connection closed")


# Global Redis client instance
redis_client = RedisClient()
