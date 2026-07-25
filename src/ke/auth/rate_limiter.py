"""Redis Rate Limiter - Production-ready rate limiting using Redis Sorted Sets."""

from __future__ import annotations

import time
import os
from typing import Optional

import redis.asyncio as aioredis
from fastapi import HTTPException


# ============================================================================
# Configuration
# ============================================================================

# Redis connection URL (configure via environment variable)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Rate limit settings
MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


# ============================================================================
# Redis Client (Singleton)
# ============================================================================

_redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    """Get or create Redis client (singleton pattern)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    return _redis_client


async def close_redis_client():
    """Close Redis client connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# ============================================================================
# Rate Limiter using Redis Sorted Set (Sliding Window)
# ============================================================================

async def check_rate_limit_redis(
    key_hash: str,
    max_requests: int = MAX_REQUESTS,
    window_seconds: int = WINDOW_SECONDS,
) -> dict:
    """
    Check rate limit using Redis Sorted Set (Sliding Window Algorithm).

    Algorithm:
    1. Remove timestamps older than window (zremrangebyscore)
    2. Count remaining requests in window (zcard)
    3. Add current request timestamp (zadd)
    4. Set TTL for auto-cleanup (expire)

    Args:
        key_hash: API key hash (unique identifier)
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds

    Returns:
        dict with limit, remaining, reset_in

    Raises:
        HTTPException: If rate limit exceeded (429)
    """
    current_time = time.time()
    clear_before = current_time - window_seconds
    redis_key = f"rate_limit:{key_hash}"

    try:
        client = await get_redis_client()

        # Use Redis Pipeline for atomic operations (reduces RTT)
        async with client.pipeline(transaction=True) as pipe:
            # Step 1: Remove old timestamps outside the window
            pipe.zremrangebyscore(redis_key, 0, clear_before)

            # Step 2: Count remaining requests in window
            pipe.zcard(redis_key)

            # Step 3: Add current request timestamp
            # Use unique member to avoid duplicates
            member = f"{current_time}:{id(pipe)}"
            pipe.zadd(redis_key, {member: current_time})

            # Step 4: Set TTL for auto-cleanup (prevents memory leaks)
            pipe.expire(redis_key, window_seconds)

            # Execute all commands atomically
            results = await pipe.execute()

        # Get request count (from zcard result)
        request_count = results[1]

        # Check if limit exceeded
        if request_count >= max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests. Limit: 60 requests/minute.",
                headers={
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(window_seconds),
                    "Retry-After": str(window_seconds),
                },
            )

        remaining = max(0, max_requests - request_count - 1)

        return {
            "limit": max_requests,
            "remaining": remaining,
            "reset_in": window_seconds,
        }

    except HTTPException:
        raise
    except Exception as e:
        # If Redis is unavailable, fail open (allow request)
        # In production, you might want to fail closed instead
        print(f"Redis rate limit error: {e}")
        return {
            "limit": max_requests,
            "remaining": max_requests - 1,
            "reset_in": window_seconds,
        }


async def get_rate_limit_info(key_hash: str) -> dict:
    """
    Get current rate limit info without incrementing counter.

    Useful for checking limits without consuming a request.
    """
    current_time = time.time()
    clear_before = current_time - WINDOW_SECONDS
    redis_key = f"rate_limit:{key_hash}"

    try:
        client = await get_redis_client()

        # Remove old timestamps
        await client.zremrangebyscore(redis_key, 0, clear_before)

        # Count remaining requests
        request_count = await client.zcard(redis_key)

        remaining = max(0, MAX_REQUESTS - request_count)

        # Calculate reset time
        reset_in = WINDOW_SECONDS
        if request_count > 0:
            oldest = await client.zrange(redis_key, 0, 0, withscores=True)
            if oldest:
                reset_in = int(oldest[0][1] + WINDOW_SECONDS - current_time)

        return {
            "limit": MAX_REQUESTS,
            "remaining": remaining,
            "reset_in": max(0, reset_in),
            "used": request_count,
        }

    except Exception as e:
        print(f"Redis rate limit info error: {e}")
        return {
            "limit": MAX_REQUESTS,
            "remaining": MAX_REQUESTS,
            "reset_in": 0,
            "used": 0,
        }


async def reset_rate_limit(key_hash: str) -> bool:
    """
    Reset rate limit for a key.

    Useful for admin operations or when upgrading plans.
    """
    redis_key = f"rate_limit:{key_hash}"

    try:
        client = await get_redis_client()
        await client.delete(redis_key)
        return True
    except Exception as e:
        print(f"Redis rate limit reset error: {e}")
        return False


# ============================================================================
# Fallback to In-Memory (when Redis unavailable)
# ============================================================================

class InMemoryRateLimiter:
    """Fallback in-memory rate limiter when Redis is unavailable."""

    def __init__(
        self,
        max_requests: int = MAX_REQUESTS,
        window_seconds: int = WINDOW_SECONDS,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> tuple[bool, dict]:
        """Check if request is allowed."""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Clean old requests
        if key not in self._requests:
            self._requests[key] = []

        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        # Check limit
        if len(self._requests[key]) >= self.max_requests:
            return False, {
                "limit": self.max_requests,
                "remaining": 0,
                "reset_in": self.window_seconds,
            }

        # Record this request
        self._requests[key].append(current_time)

        remaining = max(0, self.max_requests - len(self._requests[key]))
        return True, {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset_in": self.window_seconds,
        }


# Global fallback instance
_fallback_limiter = InMemoryRateLimiter()


async def check_rate_limit_with_fallback(key_hash: str) -> dict:
    """
    Check rate limit with Redis primary and in-memory fallback.

    This provides resilience if Redis is temporarily unavailable.
    """
    try:
        return await check_rate_limit_redis(key_hash)
    except Exception:
        # Fallback to in-memory
        allowed, info = _fallback_limiter.is_allowed(key_hash)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests. Limit: 60 requests/minute.",
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset_in"]),
                    "Retry-After": str(info["reset_in"]),
                },
            )
        return info
