"""Base ingestor interface and chunking utilities."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path

from ke.core.models import KnowledgeEntry, IngestionResult


class Ingestor(ABC):
    """Base class for file format ingestors."""

    @abstractmethod
    def ingest(self, path: Path) -> IngestionResult:
        """Ingest a file and return knowledge entries."""

    @abstractmethod
    def can_handle(self, path: Path) -> bool:
        """Check if this ingestor can handle the given file."""


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text.strip()] if text.strip() else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind(".")
            last_newline = chunk.rfind("\n")
            break_point = max(last_period, last_newline)
            if break_point > chunk_size // 2:
                chunk = chunk[: break_point + 1]
                end = start + break_point + 1

        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def extract_metadata_from_path(path: Path) -> dict:
    """Extract metadata from file path."""
    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "parent_dir": str(path.parent),
        "file_size": path.stat().st_size if path.exists() else 0,
    }


def create_entries_from_chunks(
    chunks: list[str],
    source_path: Path,
    source_type: str,
    metadata: dict | None = None,
    tags: list[str] | None = None,
) -> list[KnowledgeEntry]:
    """Create KnowledgeEntry objects from text chunks."""
    entries = []
    base_metadata = extract_metadata_from_path(source_path)
    if metadata:
        base_metadata.update(metadata)

    for i, chunk in enumerate(chunks):
        entry = KnowledgeEntry(
            content=chunk,
            source_path=str(source_path),
            source_type=source_type,
            tags=tags or [],
            metadata={**base_metadata, "chunk_index": i, "total_chunks": len(chunks)},
        )
        entries.append(entry)

    return entries
