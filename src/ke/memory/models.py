"""Memory models - data structures for the memory system."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memory in the system."""

    WORKING = "working"
    SHORT = "short"
    LONG = "long"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    CONVERSATION = "conversation"
    PROJECT = "project"
    VISUAL = "visual"


class MemoryEntry(BaseModel):
    """A single memory entry."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    summary: str = ""
    memory_type: MemoryType
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    source: str = ""
    embedding_id: str | None = None

    @property
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class MemoryQuery(BaseModel):
    """Query for searching memory."""

    text: str
    memory_types: list[MemoryType] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    limit: int = 10
    min_importance: float = 0.0
    include_expired: bool = False


class MemoryStats(BaseModel):
    """Statistics about the memory system."""

    total_entries: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    avg_importance: float = 0.0
    oldest_entry: datetime | None = None
    newest_entry: datetime | None = None
