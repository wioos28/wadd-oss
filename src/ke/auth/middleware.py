"""API Key Middleware - FastAPI middleware for authentication and rate limiting."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

from ke.auth.generator import verify_api_key
from ke.auth.store import APIKeyStore


# ============================================================================
# API Key Authentication
# ============================================================================

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyAuth:
    """API Key authentication dependency."""

    def __init__(self, store: APIKeyStore | None = None):
        self.store = store or APIKeyStore()

    async def __call__(self, api_key: str = Security(API_KEY_HEADER)) -> dict:
        """Verify API key from request header."""
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="Missing X-API-Key header",
            )

        # Hash the incoming key
        import hashlib
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Verify against database
        record = self.store.verify_key(key_hash)

        if not record:
            raise HTTPException(
                status_code=403,
                detail="Invalid or inactive API key",
            )

        return {
            "key_id": record.id,
            "user_id": record.user_id,
            "name": record.name,
            "prefix": record.prefix,
        }


# ============================================================================
# Rate Limiter
# ============================================================================

class RateLimiter:
    """
    Rate limiter using sliding window algorithm.

    Features:
    - Per-user rate limiting
    - Configurable limits
    - Sliding window for smooth limiting
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        # Check limit
        if len(self._requests[key]) >= self.max_requests:
            return False

        # Record this request
        self._requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the key."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        return max(0, self.max_requests - len(self._requests[key]))

    def get_reset_time(self, key: str) -> float:
        """Get time until rate limit resets (in seconds)."""
        if not self._requests[key]:
            return 0

        oldest = min(self._requests[key])
        reset_time = oldest + self.window_seconds - time.time()
        return max(0, reset_time)

    def reset(self, key: str):
        """Reset rate limit for a key."""
        self._requests[key] = []


# ============================================================================
# Rate Limit Middleware
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""

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
        """Default key function using API key or IP."""
        api_key = request.headers.get("X-API-Key")
        if api_key:
            import hashlib
            return hashlib.sha256(api_key.encode()).hexdigest()
        return request.client.host

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/api/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get rate limit key
        key = self.key_func(request)

        # Check rate limit
        if not self.rate_limiter.is_allowed(key):
            remaining = self.rate_limiter.get_remaining(key)
            reset_time = self.rate_limiter.get_reset_time(key)

            return Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(int(reset_time)),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.rate_limiter.get_remaining(key)
        reset_time = self.rate_limiter.get_reset_time(key)

        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response


# ============================================================================
# API Key Middleware
# ============================================================================

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware for API key authentication on protected routes."""

    def __init__(
        self,
        app,
        store: APIKeyStore | None = None,
        protected_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.store = store or APIKeyStore()
        self.protected_paths = protected_paths or ["/api/"]

    async def dispatch(self, request: Request, call_next):
        """Process request with API key authentication."""
        # Check if path requires authentication
        path = request.url.path
        requires_auth = any(path.startswith(p) for p in self.protected_paths)

        # Skip auth for public routes
        if not requires_auth or path in ["/api/auth/login", "/api/auth/register", "/api/health"]:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return Response(
                content='{"detail": "Missing X-API-Key header"}',
                status_code=401,
                headers={"Content-Type": "application/json"},
            )

        # Verify API key
        import hashlib
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        record = self.store.verify_key(key_hash)

        if not record:
            return Response(
                content='{"detail": "Invalid or inactive API key"}',
                status_code=403,
                headers={"Content-Type": "application/json"},
            )

        # Add key info to request state
        request.state.key_id = record.id
        request.state.user_id = record.user_id
        request.state.key_name = record.name

        return await call_next(request)
