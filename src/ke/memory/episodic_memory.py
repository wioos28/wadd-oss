"""Episodic Memory - Event-based memory with temporal context."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class EpisodicMemory(BaseMemory):
    """Memory of specific events and experiences.

    - Stores events with timestamps
    - Supports temporal queries
    - Used for "what happened" recall
    """

    def __init__(self, max_entries: int = 500):
        super().__init__(MemoryType.EPISODIC, max_entries=max_entries)

    def store_episode(
        self,
        event: str,
        context: dict[str, Any] | None = None,
        importance: float = 0.6,
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """Store an episodic event."""
        return self.store(
            content=event,
            importance=importance,
            tags=(tags or []) + ["episode"],
            metadata={
                "event_time": datetime.now(tz=UTC).isoformat(),
                "context": context or {},
            },
        )

    def get_by_time_range(
        self,
        start: datetime,
        end: datetime,
    ) -> list[MemoryEntry]:
        """Get episodes within a time range."""
        results = []
        for entry in self._entries.values():
            event_time = entry.metadata.get("event_time")
            if event_time:
                try:
                    dt = datetime.fromisoformat(event_time)
                    if start <= dt <= end:
                        results.append(entry)
                except ValueError:
                    pass
        return sorted(results, key=lambda e: e.created_at)

    def get_recent_episodes(self, hours: int = 24) -> list[MemoryEntry]:
        """Get episodes from the last N hours."""
        cutoff = datetime.now(tz=UTC).timestamp() - (hours * 3600)
        results = []
        for entry in self._entries.values():
            if entry.created_at.timestamp() >= cutoff:
                results.append(entry)
        return sorted(results, key=lambda e: e.created_at, reverse=True)

    def get_by_context(self, context_key: str, context_value: Any) -> list[MemoryEntry]:
        """Get episodes matching a context value."""
        results = []
        for entry in self._entries.values():
            ctx = entry.metadata.get("context", {})
            if ctx.get(context_key) == context_value:
                results.append(entry)
        return results

    def get_timeline(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get episodes as a timeline."""
        entries = sorted(self._entries.values(), key=lambda e: e.created_at, reverse=True)
        return [
            {
                "id": e.id,
                "content": e.content[:200],
                "time": e.created_at.isoformat(),
                "importance": e.importance,
                "tags": e.tags,
            }
            for e in entries[:limit]
        ]
