"""API Key Management Router - Endpoints for managing API keys."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ke.config import load_config
from ke.auth.generator import generate_api_key
from ke.auth.store import APIKeyStore

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class CreateKeyRequest(BaseModel):
    name: str
    expires_in_days: Optional[int] = None


class CreateKeyResponse(BaseModel):
    key_id: str
    api_key: str
    name: str
    prefix: str
    created_at: str
    expires_at: str | None
    message: str


class KeyInfo(BaseModel):
    key_id: str
    name: str
    prefix: str
    is_active: bool
    created_at: str
    last_used_at: str | None
    expires_at: str | None


class DeactivateKeyRequest(BaseModel):
    key_id: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/generate", response_model=CreateKeyResponse)
async def generate_api_key_endpoint(
    request: CreateKeyRequest,
    user_id: str = "default",  # In production, get from auth
):
    """Generate a new API key."""
    store = APIKeyStore()

    # Generate key pair
    key_pair = generate_api_key(prefix="wc_live_")

    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)

    # Store in database
    record = store.create_key(
        user_id=user_id,
        key_hash=key_pair.key_hash,
        name=request.name,
        prefix=key_pair.prefix,
        expires_at=expires_at,
    )

    return CreateKeyResponse(
        key_id=record.id,
        api_key=key_pair.raw_key,
        name=request.name,
        prefix=key_pair.prefix,
        created_at=record.created_at.isoformat(),
        expires_at=record.expires_at.isoformat() if record.expires_at else None,
        message="API Key created successfully. Save it now - you won't be able to see it again!",
    )


@router.get("/list")
async def list_api_keys(
    user_id: str = "default",
):
    """List all API keys for a user."""
    store = APIKeyStore()
    records = store.list_user_keys(user_id)

    return [
        KeyInfo(
            key_id=r.id,
            name=r.name,
            prefix=r.prefix,
            is_active=r.is_active,
            created_at=r.created_at.isoformat(),
            last_used_at=r.last_used_at.isoformat() if r.last_used_at else None,
            expires_at=r.expires_at.isoformat() if r.expires_at else None,
        )
        for r in records
    ]


@router.get("/{key_id}")
async def get_api_key(key_id: str):
    """Get API key details (without the actual key)."""
    store = APIKeyStore()
    record = store.get_key(key_id)

    if not record:
        raise HTTPException(status_code=404, detail="API key not found")

    return KeyInfo(
        key_id=record.id,
        name=record.name,
        prefix=record.prefix,
        is_active=record.is_active,
        created_at=record.created_at.isoformat(),
        last_used_at=record.last_used_at.isoformat() if record.last_used_at else None,
        expires_at=record.expires_at.isoformat() if record.expires_at else None,
    )


@router.post("/{key_id}/deactivate")
async def deactivate_api_key(key_id: str):
    """Deactivate an API key."""
    store = APIKeyStore()

    if not store.deactivate_key(key_id):
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key deactivated successfully"}


@router.post("/{key_id}/activate")
async def activate_api_key(key_id: str):
    """Activate an API key."""
    store = APIKeyStore()

    if not store.activate_key(key_id):
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key activated successfully"}


@router.delete("/{key_id}")
async def delete_api_key(key_id: str):
    """Permanently delete an API key."""
    store = APIKeyStore()

    if not store.delete_key(key_id):
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key deleted successfully"}


@router.get("/stats/usage")
async def get_api_key_stats(
    user_id: str = "default",
):
    """Get API key usage statistics."""
    store = APIKeyStore()
    records = store.list_user_keys(user_id)

    total_keys = len(records)
    active_keys = sum(1 for r in records if r.is_active)
    inactive_keys = total_keys - active_keys

    # Find most recently used key
    last_used = max(
        (r.last_used_at for r in records if r.last_used_at),
        default=None,
    )

    return {
        "total_keys": total_keys,
        "active_keys": active_keys,
        "inactive_keys": inactive_keys,
        "last_used": last_used.isoformat() if last_used else None,
    }
