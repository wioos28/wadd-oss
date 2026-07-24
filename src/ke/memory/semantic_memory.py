"""Semantic Memory - Facts, concepts, and general knowledge."""

from __future__ import annotations

from typing import Any

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class SemanticMemory(BaseMemory):
    """Memory of facts, concepts, and general knowledge.

    - Stores verified facts
    - Supports concept hierarchies
    - Used for "what is" knowledge
    """

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.SEMANTIC, max_entries=max_entries)

    def store_fact(
        self,
        fact: str,
        confidence: float = 0.8,
        source: str = "",
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """Store a verified fact."""
        return self.store(
            content=fact,
            importance=confidence,
            source=source,
            tags=(tags or []) + ["fact"],
        )

    def store_concept(
        self,
        name: str,
        definition: str,
        examples: list[str] | None = None,
        related: list[str] | None = None,
    ) -> MemoryEntry:
        """Store a concept with definition."""
        content = f"{name}: {definition}"
        if examples:
            content += f"\nExamples: {', '.join(examples[:3])}"

        return self.store(
            content=content,
            importance=0.7,
            tags=["concept", name.lower()],
            metadata={
                "concept_name": name,
                "examples": examples or [],
                "related_concepts": related or [],
            },
        )

    def get_by_concept(self, concept_name: str) -> list[MemoryEntry]:
        """Get entries related to a concept."""
        return [
            e for e in self._entries.values()
            if concept_name.lower() in [t.lower() for t in e.tags]
            or concept_name.lower() in e.content.lower()
        ]

    def get_facts(self, min_confidence: float = 0.5) -> list[MemoryEntry]:
        """Get verified facts above confidence threshold."""
        return sorted(
            [e for e in self._entries.values() if e.importance >= min_confidence],
            key=lambda e: e.importance,
            reverse=True,
        )

    def get_concepts(self) -> list[MemoryEntry]:
        """Get all concept entries."""
        return [
            e for e in self._entries.values()
            if "concept" in e.tags
        ]

    def verify_fact(self, entry_id: str, is_verified: bool) -> MemoryEntry | None:
        """Mark a fact as verified or unverified."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.metadata["verified"] = is_verified
            if is_verified:
                entry.importance = min(1.0, entry.importance + 0.1)
        return entry
