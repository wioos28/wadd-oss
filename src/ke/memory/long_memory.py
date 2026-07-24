"""Long-term Memory - Persistent, high-capacity storage."""

from __future__ import annotations

from datetime import datetime

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class LongTermMemory(BaseMemory):
    """Long-term memory for persistent knowledge.

    - High capacity (10000+ items)
    - No auto-expiry
    - Importance-based retention
    - Used for learned knowledge
    """

    def __init__(self, max_entries: int = 10000):
        super().__init__(MemoryType.LONG, max_entries=max_entries)

    def store(self, content: str, **kwargs) -> MemoryEntry:
        """Store with higher importance threshold."""
        kwargs.setdefault("importance", 0.5)
        return super().store(content, **kwargs)

    def consolidate(self, entry_id: str, importance_boost: float = 0.2) -> MemoryEntry | None:
        """Promote entry importance (consolidation)."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.importance = min(1.0, entry.importance + importance_boost)
            entry.access_count += 1
        return entry

    def get_by_importance(self, min_importance: float = 0.5) -> list[MemoryEntry]:
        """Get entries above importance threshold."""
        return sorted(
            [e for e in self._entries.values() if e.importance >= min_importance],
            key=lambda e: e.importance,
            reverse=True,
        )

    def forget_least_important(self, count: int = 10) -> int:
        """Remove least important entries. Returns count removed."""
        if len(self._entries) <= self.max_entries - count:
            return 0

        sorted_entries = sorted(
            self._entries.items(),
            key=lambda x: x[1].importance,
        )

        removed = 0
        for eid, _ in sorted_entries[:count]:
            if len(self._entries) > self.max_entries - count:
                del self._entries[eid]
                removed += 1
        return removed

    def search_by_tags(self, tags: list[str], limit: int = 10) -> list[MemoryEntry]:
        """Search entries by tags."""
        results = [
            e for e in self._entries.values()
            if set(tags) & set(e.tags)
        ]
        results.sort(key=lambda e: e.importance, reverse=True)
        return results[:limit]
