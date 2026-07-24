"""Metadata-based search (tags, source type, date)."""

from __future__ import annotations

from datetime import datetime, timedelta

from ke.core.models import KnowledgeEntry, QueryResult
from ke.storage.metadata import MetadataStore


class MetadataRetriever:
    """Search entries by metadata filters."""

    def __init__(self, metadata_store: MetadataStore):
        self.metadata_store = metadata_store

    def search_by_tags(
        self,
        tags: list[str],
        limit: int = 10,
    ) -> list[QueryResult]:
        """Search entries by tags."""
        entries = self.metadata_store.search_by_tags(tags, limit=limit)

        results = []
        for entry in entries:
            # Score based on tag overlap
            overlap = len(set(tags) & set(entry.tags))
            score = min(1.0, overlap / max(len(tags), 1))

            results.append(QueryResult(
                entry=entry,
                score=score,
                source_layer="metadata",
                retrieval_mode="metadata",
                explanation=f"Tag match: {overlap}/{len(tags)} tags",
            ))

        return results

    def search_by_source_type(
        self,
        source_type: str,
        limit: int = 10,
    ) -> list[QueryResult]:
        """Search entries by source type."""
        entries = self.metadata_store.list_entries(source_type=source_type, limit=limit)

        return [
            QueryResult(
                entry=entry,
                score=0.5,  # Default score for type-only filter
                source_layer="metadata",
                retrieval_mode="metadata",
                explanation=f"Source type: {source_type}",
            )
            for entry in entries
        ]

    def search_by_date(
        self,
        after: datetime | None = None,
        before: datetime | None = None,
        limit: int = 10,
    ) -> list[QueryResult]:
        """Search entries by date range."""
        # This is a simplified version - full impl would query SQLite with date filters
        entries = self.metadata_store.list_entries(limit=1000)

        filtered = []
        for entry in entries:
            if after and entry.created_at < after:
                continue
            if before and entry.created_at > before:
                continue
            filtered.append(entry)

        # Sort by date, most recent first
        filtered.sort(key=lambda e: e.created_at, reverse=True)

        return [
            QueryResult(
                entry=entry,
                score=0.5,
                source_layer="metadata",
                retrieval_mode="time",
                explanation=f"Created: {entry.created_at.isoformat()}",
            )
            for entry in filtered[:limit]
        ]

    def search_recent(self, hours: int = 24, limit: int = 10) -> list[QueryResult]:
        """Search for recently created/updated entries."""
        after = datetime.utcnow() - timedelta(hours=hours)
        return self.search_by_date(after=after, limit=limit)
