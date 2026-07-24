"""Project Memory - Project-specific knowledge and context."""

from __future__ import annotations

from typing import Any

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class ProjectMemory(BaseMemory):
    """Memory specific to a project.

    - Stores project context, decisions, conventions
    - Tracks file relationships
    - Used for project-aware assistance
    """

    def __init__(self, project_id: str, max_entries: int = 1000):
        super().__init__(MemoryType.PROJECT, max_entries=max_entries)
        self.project_id = project_id

    def store(self, content: str, **kwargs) -> MemoryEntry:
        """Store with project context."""
        kwargs.setdefault("metadata", {})
        kwargs["metadata"]["project_id"] = self.project_id
        return super().store(content, **kwargs)

    def store_decision(
        self,
        decision: str,
        rationale: str,
        alternatives: list[str] | None = None,
    ) -> MemoryEntry:
        """Store an architectural decision."""
        content = f"Decision: {decision}\nRationale: {rationale}"
        if alternatives:
            content += f"\nAlternatives considered: {', '.join(alternatives)}"

        return self.store(
            content=content,
            importance=0.8,
            tags=["decision", "architecture"],
            metadata={"type": "decision"},
        )

    def store_convention(self, name: str, description: str) -> MemoryEntry:
        """Store a project convention."""
        return self.store(
            content=f"Convention: {name} - {description}",
            importance=0.7,
            tags=["convention", name.lower()],
        )

    def store_file_context(
        self,
        file_path: str,
        purpose: str,
        dependencies: list[str] | None = None,
    ) -> MemoryEntry:
        """Store context about a project file."""
        return self.store(
            content=f"File: {file_path}\nPurpose: {purpose}",
            importance=0.6,
            tags=["file", file_path.split("/")[-1]],
            metadata={
                "file_path": file_path,
                "dependencies": dependencies or [],
            },
        )

    def get_decisions(self) -> list[MemoryEntry]:
        """Get all architectural decisions."""
        return [
            e for e in self._entries.values()
            if "decision" in e.tags
        ]

    def get_conventions(self) -> list[MemoryEntry]:
        """Get all project conventions."""
        return [
            e for e in self._entries.values()
            if "convention" in e.tags
        ]

    def get_file_context(self, file_path: str) -> MemoryEntry | None:
        """Get context for a specific file."""
        for entry in self._entries.values():
            if entry.metadata.get("file_path") == file_path:
                return entry
        return None

    def get_project_summary(self) -> str:
        """Generate a project context summary."""
        decisions = self.get_decisions()
        conventions = self.get_conventions()
        files = [e for e in self._entries.values() if "file" in e.tags]

        parts = [
            f"Project: {self.project_id}",
            f"Decisions: {len(decisions)}",
            f"Conventions: {len(conventions)}",
            f"Files tracked: {len(files)}",
            f"Total memories: {len(self._entries)}",
        ]

        return " | ".join(parts)
