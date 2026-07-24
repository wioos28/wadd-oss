"""Relationship-based search using knowledge graph traversal."""

from __future__ import annotations

from ke.core.models import KnowledgeEntry, QueryResult
from ke.storage.metadata import MetadataStore


class RelationshipRetriever:
    """Search for entries related to a known entry via the knowledge graph."""

    def __init__(self, metadata_store: MetadataStore):
        self.metadata_store = metadata_store

    def search_from_entry(
        self,
        entry_id: str,
        max_depth: int = 2,
        limit: int = 10,
    ) -> list[QueryResult]:
        """Find entries related to the given entry via graph traversal."""
        visited = set()
        results = []
        self._traverse(entry_id, 0, max_depth, visited, results)
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def search_from_text(
        self,
        query: str,
        limit: int = 10,
    ) -> list[QueryResult]:
        """Find entries related to text by first finding matching entries."""
        # Find initial matches
        entries = self.metadata_store.search_content(query, limit=5)
        if not entries:
            return []

        # Traverse from each match
        all_results = []
        for entry in entries:
            related = self.search_from_entry(entry.id, max_depth=1, limit=limit)
            all_results.extend(related)

        # Dedupe and sort
        seen = set()
        unique_results = []
        for r in all_results:
            if r.entry.id not in seen:
                seen.add(r.entry.id)
                unique_results.append(r)

        unique_results.sort(key=lambda r: r.score, reverse=True)
        return unique_results[:limit]

    def _traverse(
        self,
        entry_id: str,
        depth: int,
        max_depth: int,
        visited: set[str],
        results: list[QueryResult],
    ) -> None:
        """BFS traversal of the knowledge graph."""
        if depth > max_depth or entry_id in visited:
            return

        visited.add(entry_id)
        relationships = self.metadata_store.get_relationships(entry_id)

        for rel in relationships:
            # Determine the target entry
            target_id = rel.target_id if rel.source_id == entry_id else rel.source_id
            if target_id in visited:
                continue

            # Get the target entry
            target_entry = self.metadata_store.get_entry(target_id)
            if target_entry is None:
                continue

            # Score based on relationship weight and depth
            score = rel.weight * (1.0 / (depth + 1))

            results.append(QueryResult(
                entry=target_entry,
                score=score,
                source_layer="metadata",
                retrieval_mode="relationship",
                explanation=f"Related via {rel.relationship_type} (depth={depth}, weight={rel.weight:.2f})",
            ))

            # Continue traversal
            self._traverse(target_id, depth + 1, max_depth, visited, results)
