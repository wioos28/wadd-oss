"""Hybrid search combining semantic and keyword results."""

from __future__ import annotations

from ke.core.models import QueryResult
from ke.retrieval.keyword import KeywordRetriever
from ke.retrieval.semantic import SemanticRetriever


class HybridRetriever:
    """Combine semantic and keyword search with reciprocal rank fusion."""

    def __init__(self, semantic: SemanticRetriever, keyword: KeywordRetriever):
        self.semantic = semantic
        self.keyword = keyword

    def search(
        self,
        query: str,
        query_embedding: list[float],
        limit: int = 10,
        min_score: float = 0.0,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4,
    ) -> list[QueryResult]:
        """Search using both semantic and keyword approaches."""
        # Get results from both retrievers
        semantic_results = self.semantic.search(query_embedding, limit=limit * 2)
        keyword_results = self.keyword.search(query, limit=limit * 2)

        # Reciprocal rank fusion
        fused = self._reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            semantic_weight,
            keyword_weight,
        )

        # Filter and limit
        results = [r for r in fused if r.score >= min_score][:limit]

        return results

    def _reciprocal_rank_fusion(
        self,
        list_a: list[QueryResult],
        list_b: list[QueryResult],
        weight_a: float = 0.6,
        weight_b: float = 0.4,
        k: int = 60,
    ) -> list[QueryResult]:
        """Fuse two ranked lists using reciprocal rank fusion."""
        scores: dict[str, float] = {}
        entries: dict[str, QueryResult] = {}

        # Score from list A
        for rank, result in enumerate(list_a):
            rrf_score = weight_a / (k + rank + 1)
            scores[result.entry.id] = scores.get(result.entry.id, 0) + rrf_score
            entries[result.entry.id] = result

        # Score from list B
        for rank, result in enumerate(list_b):
            rrf_score = weight_b / (k + rank + 1)
            scores[result.entry.id] = scores.get(result.entry.id, 0) + rrf_score
            if result.entry.id not in entries:
                entries[result.entry.id] = result

        # Sort by fused score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        results = []
        for entry_id in sorted_ids:
            result = entries[entry_id]
            result.score = min(1.0, scores[entry_id] * 10)  # Normalize to 0-1
            result.retrieval_mode = "hybrid"
            result.explanation = f"Hybrid (semantic + keyword), fused score: {scores[entry_id]:.4f}"
            results.append(result)

        return results
