"""Keyword search via SQLite FTS."""

from __future__ import annotations

from ke.core.models import KnowledgeEntry, QueryResult
from ke.storage.metadata import MetadataStore


class KeywordRetriever:
    """Retrieve entries using keyword/full-text search."""

    def __init__(self, metadata_store: MetadataStore):
        self.metadata_store = metadata_store

    def search(self, query: str, limit: int = 10) -> list[QueryResult]:
        """Search for entries matching keywords."""
        entries = self.metadata_store.search_content(query, limit=limit)

        results = []
        for i, entry in enumerate(entries):
            # Score based on position (earlier = more relevant) and content match
            score = max(0.1, 1.0 - (i * 0.05))

            # Boost score if query appears in summary
            if query.lower() in entry.summary.lower():
                score = min(1.0, score + 0.2)

            results.append(QueryResult(
                entry=entry,
                score=score,
                source_layer="metadata",
                retrieval_mode="keyword",
                explanation=f"Keyword match for '{query}'",
            ))

        return results
