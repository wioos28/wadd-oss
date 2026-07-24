"""Cloud sync provider interface and local mock implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ke.core.models import KnowledgeEntry


class CloudProvider(ABC):
    """Abstract base class for cloud sync providers."""

    @abstractmethod
    def push(self, entries: list[KnowledgeEntry]) -> int:
        """Push entries to cloud. Returns number of entries pushed."""

    @abstractmethod
    def pull(self, query: str | None = None, limit: int = 100) -> list[KnowledgeEntry]:
        """Pull entries from cloud, optionally filtered by query."""

    @abstractmethod
    def sync(self, local_entries: list[KnowledgeEntry]) -> tuple[list[KnowledgeEntry], list[KnowledgeEntry]]:
        """Bidirectional sync. Returns (to_pull, to_push)."""

    @abstractmethod
    def status(self) -> dict[str, Any]:
        """Get sync status information."""


class LocalSyncProvider(CloudProvider):
    """Local filesystem-based sync provider for development and offline use."""

    def __init__(self, sync_dir: Path | str):
        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self._entries_file = self.sync_dir / "entries.json"

    def push(self, entries: list[KnowledgeEntry]) -> int:
        """Push entries to local sync directory."""
        import json

        existing = self._load_entries()
        existing_ids = {e.id for e in existing}
        new_entries = [e for e in entries if e.id not in existing_ids]
        all_entries = existing + new_entries

        with open(self._entries_file, "w") as f:
            json.dump([e.model_dump(mode="json") for e in all_entries], f, indent=2)

        return len(new_entries)

    def pull(self, query: str | None = None, limit: int = 100) -> list[KnowledgeEntry]:
        """Pull entries from local sync directory."""
        entries = self._load_entries()
        if query:
            entries = [
                e for e in entries
                if query.lower() in e.content.lower() or query.lower() in e.summary.lower()
            ]
        return entries[:limit]

    def sync(self, local_entries: list[KnowledgeEntry]) -> tuple[list[KnowledgeEntry], list[KnowledgeEntry]]:
        """Compare local and remote, return what needs syncing."""
        remote_entries = self._load_entries()
        remote_ids = {e.id for e in remote_entries}
        local_ids = {e.id for e in local_entries}

        to_pull = [e for e in remote_entries if e.id not in local_ids]
        to_push = [e for e in local_entries if e.id not in remote_ids]

        return to_pull, to_push

    def status(self) -> dict[str, Any]:
        """Get sync status."""
        entries = self._load_entries()
        return {
            "provider": "local",
            "sync_dir": str(self.sync_dir),
            "entries_count": len(entries),
            "entries_file_exists": self._entries_file.exists(),
        }

    def _load_entries(self) -> list[KnowledgeEntry]:
        """Load entries from sync file."""
        import json

        if not self._entries_file.exists():
            return []

        with open(self._entries_file) as f:
            data = json.load(f)

        return [KnowledgeEntry(**item) for item in data]
