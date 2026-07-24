"""Base memory class with common functionality."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ke.memory.models import MemoryEntry, MemoryQuery, MemoryType


class BaseMemory:
    """Base class for all memory types."""

    def __init__(self, memory_type: MemoryType, max_entries: int = 1000):
        self.memory_type = memory_type
        self.max_entries = max_entries
        self._entries: dict[str, MemoryEntry] = {}

    def store(
        self,
        content: str,
        summary: str = "",
        tags: list[str] | None = None,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
        source: str = "",
        ttl_seconds: int | None = None,
    ) -> MemoryEntry:
        """Store a new memory entry."""
        entry = MemoryEntry(
            content=content,
            summary=summary,
            memory_type=self.memory_type,
            tags=tags or [],
            importance=importance,
            metadata=metadata or {},
            source=source,
        )

        if ttl_seconds:
            entry.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        self._entries[entry.id] = entry
        self._enforce_limit()
        return entry

    def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve a memory entry by ID."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
        return entry

    def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search memory entries using keyword matching."""
        results = []
        query_words = set(query.text.lower().split())
        # Filter out common words
        stop_words = {"what", "is", "the", "a", "an", "how", "do", "you", "can", "i", "it", "in", "of", "and", "or", "to", "for", "my", "your"}
        query_words -= stop_words

        for entry in self._entries.values():
            if not query.include_expired and entry.is_expired:
                continue
            if query.min_importance > 0 and entry.importance < query.min_importance:
                continue
            if query.tags and not set(query.tags) & set(entry.tags):
                continue

            # Score based on keyword overlap
            content_lower = entry.content.lower()
            content_words = set(content_lower.split())
            tag_words = set(t.lower() for t in entry.tags)

            # Check for keyword matches
            matches = query_words & (content_words | tag_words)
            if matches:
                # Score: more matches = higher score
                score = len(matches) / max(len(query_words), 1)
                entry._search_score = score
                results.append(entry)

        results.sort(key=lambda e: getattr(e, '_search_score', 0) * e.importance, reverse=True)
        return results[:query.limit]

    def update(self, entry_id: str, **kwargs: Any) -> MemoryEntry | None:
        """Update a memory entry."""
        entry = self._entries.get(entry_id)
        if not entry:
            return None

        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)

        return entry

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False

    def clear(self) -> int:
        """Clear all entries. Returns count of cleared entries."""
        count = len(self._entries)
        self._entries.clear()
        return count

    def count(self) -> int:
        """Get number of entries."""
        return len(self._entries)

    def get_all(self) -> list[MemoryEntry]:
        """Get all entries."""
        return list(self._entries.values())

    def get_recent(self, limit: int = 10) -> list[MemoryEntry]:
        """Get most recent entries."""
        entries = sorted(
            self._entries.values(),
            key=lambda e: e.created_at,
            reverse=True,
        )
        return entries[:limit]

    def get_important(self, limit: int = 10) -> list[MemoryEntry]:
        """Get most important entries."""
        entries = sorted(
            self._entries.values(),
            key=lambda e: e.importance,
            reverse=True,
        )
        return entries[:limit]

    def _enforce_limit(self) -> None:
        """Remove oldest entries if over limit."""
        if len(self._entries) <= self.max_entries:
            return

        sorted_entries = sorted(
            self._entries.items(),
            key=lambda x: x[1].last_accessed,
        )

        to_remove = len(self._entries) - self.max_entries
        for entry_id, _ in sorted_entries[:to_remove]:
            del self._entries[entry_id]

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = datetime.utcnow()
        expired = [
            eid for eid, e in self._entries.items()
            if e.expires_at and e.expires_at < now
        ]
        for eid in expired:
            del self._entries[eid]
        return len(expired)
