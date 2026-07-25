"""Status router - System status and health checks."""

from __future__ import annotations

from fastapi import APIRouter

from ke.config import load_config

router = APIRouter()


@router.get("/status")
async def get_status():
    """Get system status."""
    from ke.storage.metadata import MetadataStore
    from ke.storage.vector import VectorStore
    from ke.core.network import NetworkDetector

    config = load_config()

    # Network status
    detector = NetworkDetector()
    network = detector.detect()

    # Storage status
    with MetadataStore(config.metadata_db_path()) as store:
        entry_count = store.count_entries()

    with VectorStore(config.vector_db_path()) as vec:
        vector_count = vec.count()

    return {
        "entries": entry_count,
        "vectors": vector_count,
        "cloud": entry_count,  # Same as local for now
        "network": network.status,
        "latency_ms": network.latency_ms,
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
