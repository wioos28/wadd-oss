"""Visual Memory - Image and visual data memory."""

from __future__ import annotations

from typing import Any

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class VisualMemory(BaseMemory):
    """Memory for images and visual data.

    - Stores image metadata and descriptions
    - Supports similarity search
    - Used for visual content recall
    """

    def __init__(self, max_entries: int = 500):
        super().__init__(MemoryType.VISUAL, max_entries=max_entries)

    def store_image(
        self,
        path: str,
        description: str,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        embedding_id: str | None = None,
    ) -> MemoryEntry:
        """Store image metadata and description."""
        return self.store(
            content=description,
            importance=0.5,
            tags=(tags or []) + ["image"],
            metadata={
                "image_path": path,
                "type": "image",
                **(metadata or {}),
            },
            source=path,
        )

    def store_screenshot(
        self,
        path: str,
        description: str,
        context: str = "",
    ) -> MemoryEntry:
        """Store a screenshot with context."""
        return self.store(
            content=f"Screenshot: {description}\nContext: {context}",
            importance=0.4,
            tags=["screenshot", "image"],
            metadata={
                "image_path": path,
                "type": "screenshot",
                "context": context,
            },
            source=path,
        )

    def store_diagram(
        self,
        path: str,
        description: str,
        diagram_type: str = "",
    ) -> MemoryEntry:
        """Store a diagram."""
        return self.store(
            content=f"Diagram ({diagram_type}): {description}",
            importance=0.6,
            tags=["diagram", "image", diagram_type] if diagram_type else ["diagram", "image"],
            metadata={
                "image_path": path,
                "type": "diagram",
                "diagram_type": diagram_type,
            },
            source=path,
        )

    def get_by_type(self, image_type: str) -> list[MemoryEntry]:
        """Get images by type (screenshot, diagram, etc.)."""
        return [
            e for e in self._entries.values()
            if e.metadata.get("type") == image_type
        ]

    def get_by_tags(self, tags: list[str]) -> list[MemoryEntry]:
        """Get images by tags."""
        return [
            e for e in self._entries.values()
            if set(tags) & set(e.tags)
        ]

    def search_by_description(self, query: str) -> list[MemoryEntry]:
        """Search images by description."""
        return [
            e for e in self._entries.values()
            if query.lower() in e.content.lower()
        ]

    def get_images_with_context(self) -> list[dict[str, Any]]:
        """Get all images with their context."""
        return [
            {
                "id": e.id,
                "path": e.metadata.get("image_path"),
                "description": e.content[:200],
                "type": e.metadata.get("type"),
                "tags": e.tags,
            }
            for e in self._entries.values()
        ]
