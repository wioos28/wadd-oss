"""Working Memory - Active, short-term processing memory."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class WorkingMemory(BaseMemory):
    """Active memory for current task processing.

    - Small capacity (7±2 items)
    - Auto-expires after task completion
    - High priority, low persistence
    """

    def __init__(self, max_items: int = 9):
        super().__init__(MemoryType.WORKING, max_entries=max_items)
        self._task_start: datetime | None = None

    def start_task(self, task_description: str) -> None:
        """Mark task start."""
        self._task_start = datetime.utcnow()
        self.store(
            content=f"Task started: {task_description}",
            summary=task_description[:100],
            importance=0.8,
            tags=["task_start"],
        )

    def add_thought(self, thought: str, importance: float = 0.6) -> MemoryEntry:
        """Add a thought to working memory."""
        return self.store(
            content=thought,
            importance=importance,
            tags=["thought"],
            ttl_seconds=3600,  # 1 hour
        )

    def add_context(self, key: str, value: Any) -> MemoryEntry:
        """Add contextual information."""
        return self.store(
            content=f"{key}: {value}",
            importance=0.7,
            tags=["context", key],
        )

    def get_task_context(self) -> list[MemoryEntry]:
        """Get all context related to current task."""
        return [
            e for e in self._entries.values()
            if "task_start" in e.tags or "context" in e.tags or "thought" in e.tags
        ]

    def end_task(self) -> list[MemoryEntry]:
        """End current task, return all entries for archival."""
        entries = list(self._entries.values())
        self._entries.clear()
        self._task_start = None
        return entries

    def is_full(self) -> bool:
        """Check if working memory is at capacity."""
        return len(self._entries) >= self.max_entries
