"""API Key Generator - Secure key generation with hashing."""

from __future__ import annotations

import secrets
import hashlib
from dataclasses import dataclass
from datetime import datetime


@dataclass
class APIKeyPair:
    """API Key pair containing raw key and hash."""
    raw_key: str
    key_hash: str
    prefix: str
    created_at: datetime


def generate_api_key(
    prefix: str = "wc_live_",
    entropy: int = 32,
) -> APIKeyPair:
    """
    Generate a secure API key pair.

    Args:
        prefix: Key prefix for identification (e.g., "wc_live_", "wc_test_")
        entropy: Number of random bytes (32 = 256 bits of entropy)

    Returns:
        APIKeyPair with raw_key (shown once) and key_hash (stored in DB)

    Security Notes:
        - raw_key should ONLY be shown to the user ONCE
        - key_hash is what gets stored in the database
        - Uses secrets.token_hex() for cryptographically secure randomness
    """
    # Generate cryptographically secure random bytes
    random_bytes = secrets.token_hex(entropy)

    # Create the full raw key with prefix
    raw_key = f"{prefix}{random_bytes}"

    # Hash the key for storage (never store raw key!)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    return APIKeyPair(
        raw_key=raw_key,
        key_hash=key_hash,
        prefix=prefix,
        created_at=datetime.utcnow(),
    )


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """
    Verify an API key against its stored hash.

    Args:
        raw_key: The raw API key from the request
        stored_hash: The hash stored in the database

    Returns:
        True if the key matches the hash
    """
    # Hash the incoming key
    incoming_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    # Compare hashes (constant-time comparison to prevent timing attacks)
    return secrets.compare_digest(incoming_hash, stored_hash)


def hash_api_key(raw_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_test_key() -> APIKeyPair:
    """Generate a test API key with wc_test_ prefix."""
    return generate_api_key(prefix="wc_test_")


def generate_live_key() -> APIKeyPair:
    """Generate a live API key with wc_live_ prefix."""
    return generate_api_key(prefix="wc_live_")


def get_key_prefix(raw_key: str) -> str | None:
    """Extract the prefix from a raw API key."""
    if "_" in raw_key:
        parts = raw_key.split("_", 2)
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}_"
    return None
