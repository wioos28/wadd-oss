"""API Key Middleware - FastAPI middleware for authentication and rate limiting."""

from __future__ import annotations

import time
import hmac
import hashlib
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

from ke.auth.generator import verify_api_key
from ke.auth.store import APIKeyStore
from ke.auth.rate_limiter import (
    check_rate_limit_with_fallback,
    get_rate_limit_info,
    reset_rate_limit,
    RateLimiter,
)


# ============================================================================
# API Key Authentication
# ============================================================================

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyAuth:
    """API Key authentication dependency with Redis rate limiting."""

    def __init__(self, store: APIKeyStore | None = None):
        self.store = store or APIKeyStore()

    async def __call__(self, api_key: str = Security(API_KEY_HEADER)) -> dict:
        """Verify API key from request header."""
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing X-API-Key header",
            )

        # 1. Hash the incoming key (constant-time comparison)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # 2. Verify against database
        record = self.store.verify_key(key_hash)

        if not record:
            raise HTTPException(
                status_code=403,
                detail="Invalid or inactive API key",
            )

        # 3. Check rate limit via Redis (with in-memory fallback)
        rate_info = await check_rate_limit_with_fallback(key_hash)

        return {
            "key_id": record.id,
            "user_id": record.user_id,
            "name": record.name,
            "prefix": record.prefix,
            "rate_limit": rate_info,
        }


# ============================================================================
# Rate Limit Middleware (Redis-backed)
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests using Redis.

    Features:
    - Redis Sorted Set (zset) for sliding window
    - In-memory fallback when Redis unavailable
    - Atomic pipeline operations
    - Auto-cleanup with TTL
    """

    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60,
        key_func: Callable | None = None,
    ):
        super().__init__(app)
        self.rate_limiter = RateLimiter(max_requests, window_seconds)
        self.key_func = key_func or self._default_key_func

    def _default_key_func(self, request: Request) -> str:
        """Default key function using API key hash or client IP."""
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return hashlib.sha256(api_key.encode()).hexdigest()
        return request.client.host

    async def dispatch(self, request: Request, call_next):
        """Process request with Redis rate limiting."""
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/api/health", "/docs", "/openapi.json", "/"]:
            return await call_next(request)

        # Get rate limit key (API key hash or IP)
        key = self.key_func(request)

        try:
            # Try Redis rate limiting first
            rate_info = await check_rate_limit_with_fallback(key)

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset_in"])

            return response

        except HTTPException as e:
            # Rate limit exceeded (429)
            return Response(
                content=f'{{"detail": "{e.detail}"}}',
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "X-RateLimit-Limit": str(e.headers.get("X-RateLimit-Limit", "60")),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(e.headers.get("X-RateLimit-Reset", "60")),
                    "Retry-After": str(e.headers.get("Retry-After", "60")),
                },
            )
        except Exception as e:
            # Fallback to in-memory if Redis fails
            if not self.rate_limiter.is_allowed(key):
                reset_time = self.rate_limiter.get_reset_time(key)
                return Response(
                    content='{"detail": "Rate limit exceeded. Limit: 60 requests/minute."}',
                    status_code=429,
                    headers={
                        "Content-Type": "application/json",
                        "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time)),
                        "Retry-After": str(int(reset_time)),
                    },
                )

            response = await call_next(request)
            remaining = self.rate_limiter.get_remaining(key)
            reset_time = self.rate_limiter.get_reset_time(key)

            response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(reset_time))

            return response


# ============================================================================
# API Key Middleware (Combined Auth + Redis Rate Limit)
# ============================================================================

class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Combined middleware for API key authentication and Redis rate limiting.

    Flow:
    1. Check if path requires authentication
    2. Extract API key from X-API-Key header
    3. Hash the key using SHA-256
    4. Verify against database
    5. Check rate limit via Redis (sliding window)
    6. Add key info to request state
    """

    def __init__(
        self,
        app,
        store: APIKeyStore | None = None,
        protected_paths: list[str] | None = None,
        max_requests: int = 60,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.store = store or APIKeyStore()
        self.protected_paths = protected_paths or ["/api/"]
        self.rate_limiter = RateLimiter(max_requests, window_seconds)

    async def dispatch(self, request: Request, call_next):
        """Process request with API key authentication and Redis rate limiting."""
        # Check if path requires authentication
        path = request.url.path
        requires_auth = any(path.startswith(p) for p in self.protected_paths)

        # Skip auth for public routes
        public_paths = ["/api/auth/login", "/api/auth/register", "/api/health", "/"]
        if not requires_auth or path in public_paths:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return Response(
                content='{"detail": "Missing X-API-Key header"}',
                status_code=401,
                headers={"Content-Type": "application/json"},
            )

        # 1. Hash the key (SHA-256)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # 2. Verify against database
        record = self.store.verify_key(key_hash)

        if not record:
            return Response(
                content='{"detail": "Invalid or inactive API key"}',
                status_code=403,
                headers={"Content-Type": "application/json"},
            )

        # 3. Check rate limit via Redis (with fallback)
        try:
            rate_info = await check_rate_limit_with_fallback(key_hash)
        except HTTPException as e:
            return Response(
                content=f'{{"detail": "{e.detail}"}}',
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "X-RateLimit-Limit": str(e.headers.get("X-RateLimit-Limit", "60")),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(e.headers.get("Retry-After", "60")),
                },
            )
        except Exception:
            # Fallback to in-memory
            if not self.rate_limiter.is_allowed(key_hash):
                reset_time = self.rate_limiter.get_reset_time(key_hash)
                return Response(
                    content='{"detail": "Rate limit exceeded. Limit: 60 requests/minute."}',
                    status_code=429,
                    headers={
                        "Content-Type": "application/json",
                        "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time)),
                        "Retry-After": str(int(reset_time)),
                    },
                )
            rate_info = {
                "limit": self.rate_limiter.max_requests,
                "remaining": self.rate_limiter.get_remaining(key_hash),
                "reset_in": int(self.rate_limiter.get_reset_time(key_hash)),
            }

        # 4. Add key info to request state
        request.state.key_id = record.id
        request.state.user_id = record.user_id
        request.state.key_name = record.name
        request.state.rate_limit = rate_info

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset_in"])

        return response
