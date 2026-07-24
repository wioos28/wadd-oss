"""Short-term Memory - Temporary storage with decay."""

from __future__ import annotations

from datetime import datetime, timedelta

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class ShortTermMemory(BaseMemory):
    """Short-term memory with time-based decay.

    - Medium capacity (100 items)
    - Decays over time (default 24h)
    - Used for recent context
    """

    def __init__(self, max_entries: int = 100, decay_hours: int = 24):
        super().__init__(MemoryType.SHORT, max_entries=max_entries)
        self.decay_hours = decay_hours

    def store(self, content: str, **kwargs) -> MemoryEntry:
        """Store with auto-expiry based on decay_hours."""
        kwargs.setdefault("ttl_seconds", self.decay_hours * 3600)
        return super().store(content, **kwargs)

    def get_fresh(self, max_age_hours: int | None = None) -> list[MemoryEntry]:
        """Get entries newer than max_age_hours."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours or self.decay_hours)
        return [
            e for e in self._entries.values()
            if e.created_at > cutoff
        ]

    def get_by_decay(self) -> list[MemoryEntry]:
        """Get entries sorted by decay (oldest first)."""
        now = datetime.utcnow()
        entries = []
        for e in self._entries.values():
            age_hours = (now - e.created_at).total_seconds() / 3600
            decay = max(0, 1.0 - (age_hours / self.decay_hours))
            entries.append((e, decay))
        entries.sort(key=lambda x: x[1], reverse=True)
        return [e for e, _ in entries]

    def decay(self) -> int:
        """Remove entries that have fully decayed. Returns count removed."""
        now = datetime.utcnow()
        decay_limit = now - timedelta(hours=self.decay_hours)
        expired = [
            eid for eid, e in self._entries.items()
            if e.created_at < decay_limit
        ]
        for eid in expired:
            del self._entries[eid]
        return len(expired)
