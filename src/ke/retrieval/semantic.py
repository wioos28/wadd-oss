"""Semantic search via vector embeddings."""

from __future__ import annotations

from ke.core.models import KnowledgeEntry, QueryResult
from ke.storage.vector import VectorStore


class SemanticRetriever:
    """Retrieve entries using vector similarity search."""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[QueryResult]:
        """Search for entries similar to the query embedding."""
        raw_results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=limit,
        )

        results = []
        for raw in raw_results:
            distance = raw.get("distance")
            if distance is None:
                continue

            # Convert distance to similarity score (0-1)
            score = max(0.0, 1.0 - distance)

            if score < min_score:
                continue

            # Reconstruct entry from stored data
            entry = self._raw_to_entry(raw)
            results.append(QueryResult(
                entry=entry,
                score=score,
                source_layer="vector",
                retrieval_mode="semantic",
                explanation=f"Vector similarity: {score:.3f}",
            ))

        return results

    def _raw_to_entry(self, raw: dict) -> KnowledgeEntry:
        """Convert raw vector store result to KnowledgeEntry."""
        metadata = raw.get("metadata", {})
        return KnowledgeEntry(
            id=raw["id"],
            content=raw.get("document", ""),
            source_type=metadata.get("source_type", "unknown"),
            source_path=metadata.get("source_path") or None,
            tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
        )
