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


# ============================================================================
# API Key Authentication
# ============================================================================

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# --- RATE LIMIT CONFIGURATION ---
MAX_REQUESTS = 60      # Maximum 60 requests
WINDOW_SECONDS = 60    # Per 60 seconds (1 minute)

# Rate limit storage (in-memory, use Redis for production)
# Structure: { "key_hash": [timestamp_1, timestamp_2, ...] }
rate_limit_db: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(key_hash: str) -> int:
    """
    Check rate limit using sliding window algorithm.

    Args:
        key_hash: Hashed API key

    Returns:
        Number of remaining requests

    Raises:
        HTTPException: If rate limit exceeded (429)
    """
    current_time = time.time()

    # 1. Filter and keep only requests within the window
    active_requests = [
        timestamp for timestamp in rate_limit_db[key_hash]
        if current_time - timestamp < WINDOW_SECONDS
    ]
    rate_limit_db[key_hash] = active_requests

    # 2. Check if limit exceeded
    if len(active_requests) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests. Limit: 60 requests/minute.",
            headers={
                "X-RateLimit-Limit": str(MAX_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(WINDOW_SECONDS),
            }
        )

    # 3. Record this request
    rate_limit_db[key_hash].append(current_time)

    # 4. Calculate remaining requests
    remaining = MAX_REQUESTS - len(active_requests) - 1
    return remaining


class APIKeyAuth:
    """API Key authentication dependency with rate limiting."""

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

        # 3. Check rate limit BEFORE allowing request
        remaining_requests = check_rate_limit(key_hash)

        return {
            "key_id": record.id,
            "user_id": record.user_id,
            "name": record.name,
            "prefix": record.prefix,
            "rate_limit_remaining": remaining_requests,
        }


# ============================================================================
# Rate Limiter (Sliding Window Algorithm)
# ============================================================================

class RateLimiter:
    """
    Rate limiter using sliding window algorithm.

    Features:
    - Per-user/API-key rate limiting
    - Configurable limits
    - Sliding window for smooth limiting
    - Returns remaining requests and reset time
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
        """
        Check if request is allowed for the given key.

        Uses sliding window algorithm:
        1. Remove timestamps outside the window
        2. Check if count < max_requests
        3. If allowed, record the timestamp
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests (sliding window)
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
    """
    Middleware for rate limiting API requests.

    Uses sliding window algorithm:
    - Tracks timestamps of requests per key
    - Removes old timestamps outside the window
    - Rejects with 429 if limit exceeded
    - Adds X-RateLimit-* headers to responses
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
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/api/health", "/docs", "/openapi.json", "/"]:
            return await call_next(request)

        # Get rate limit key (API key hash or IP)
        key = self.key_func(request)

        # Check rate limit
        if not self.rate_limiter.is_allowed(key):
            remaining = self.rate_limiter.get_remaining(key)
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

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = self.rate_limiter.get_remaining(key)
        reset_time = self.rate_limiter.get_reset_time(key)

        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response


# ============================================================================
# API Key Middleware (Combined Auth + Rate Limit)
# ============================================================================

class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Combined middleware for API key authentication and rate limiting.

    Flow:
    1. Check if path requires authentication
    2. Extract API key from X-API-Key header
    3. Hash the key using SHA-256
    4. Verify against database
    5. Check rate limit (sliding window)
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
        """Process request with API key authentication and rate limiting."""
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

        # 3. Check rate limit (sliding window)
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

        # 4. Add key info to request state
        request.state.key_id = record.id
        request.state.user_id = record.user_id
        request.state.key_name = record.name

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.rate_limiter.get_remaining(key_hash)
        reset_time = self.rate_limiter.get_reset_time(key_hash)

        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response
