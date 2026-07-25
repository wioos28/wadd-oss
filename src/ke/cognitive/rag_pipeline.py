"""RAG Pipeline - Retrieval-Augmented Generation with intent-aware search."""

from __future__ import annotations

from typing import Any

from ke.config import KeConfig
from ke.domain.models import QueryResult, QueryMode
from ke.cognitive.intent_detector import Intent, IntentType


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.

    Flow:
    1. Analyze intent to determine search strategy
    2. Retrieve relevant documents
    3. Re-rank and filter results
    4. Return context for generation
    """

    def __init__(self, config: KeConfig):
        self.config = config
        self._query_service = None

    @property
    def query_service(self):
        """Lazy-load query service."""
        if self._query_service is None:
            from ke.application.services import QueryService
            self._query_service = QueryService(self.config)
        return self._query_service

    async def retrieve(
        self,
        query: str,
        intent: Intent,
        memory_context: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> list[QueryResult]:
        """
        Retrieve relevant documents based on intent and query.

        Uses different strategies based on intent type:
        - QUESTION: Hybrid search (semantic + keyword)
        - CODE_REQUEST: Code similarity search
        - SEARCH_REQUEST: Semantic search
        - MEMORY_REQUEST: Memory search
        """
        # Determine search mode based on intent
        mode = self._get_search_mode(intent)

        # Enhance query with memory context
        enhanced_query = self._enhance_query(query, memory_context)

        # Execute search
        try:
            results = self.query_service.query(
                text=enhanced_query,
                mode=mode,
                limit=limit,
                min_score=0.2,  # Lower threshold for better recall
            )

            # Re-rank based on intent
            results = self._rerank_results(results, intent)

            return results

        except Exception as e:
            # Fallback to basic search
            try:
                return self.query_service.query(
                    text=query,
                    mode="hybrid",
                    limit=limit,
                    min_score=0.3,
                )
            except Exception:
                return []

    def _get_search_mode(self, intent: Intent) -> str:
        """Determine search mode based on intent type."""
        mode_mapping = {
            IntentType.QUESTION: "hybrid",
            IntentType.CODE_REQUEST: "code_similarity",
            IntentType.SEARCH_REQUEST: "semantic",
            IntentType.COMMAND: "keyword",
            IntentType.MEMORY_REQUEST: "semantic",
            IntentType.CONVERSATION: "hybrid",
        }
        return mode_mapping.get(intent.type, "hybrid")

    def _enhance_query(
        self,
        query: str,
        memory_context: dict[str, Any] | None,
    ) -> str:
        """Enhance query with context from memory."""
        if not memory_context:
            return query

        enhancements = []

        # Add recent conversation context
        if memory_context.get("short_term"):
            recent = memory_context["short_term"][-2:]
            for msg in recent:
                if msg.get("role") == "user":
                    content = msg.get("content", "")[:100]
                    if content:
                        enhancements.append(content)

        # Add relevant long-term memories
        if memory_context.get("long_term"):
            for mem in memory_context["long_term"][:2]:
                content = mem.get("content", "")[:100]
                if content:
                    enhancements.append(content)

        if enhancements:
            enhanced = f"{query} (context: {'; '.join(enhancements)})"
            return enhanced[:500]  # Limit length

        return query

    def _rerank_results(
        self,
        results: list[QueryResult],
        intent: Intent,
    ) -> list[QueryResult]:
        """Re-rank results based on intent and relevance."""
        if not results:
            return results

        # Boost scores based on intent
        for result in results:
            # Boost code results for code requests
            if intent.type == IntentType.CODE_REQUEST:
                if result.entry.source_type == "code":
                    result.score *= 1.2

            # Boost recent documents
            if result.entry.source_type in ["markdown", "text"]:
                result.score *= 1.1

            # Apply entity boosting
            if intent.entities:
                content_lower = result.entry.content.lower()
                for entity in intent.entities:
                    if entity.lower() in content_lower:
                        result.score *= 1.15

        # Sort by adjusted score
        results.sort(key=lambda r: r.score, reverse=True)

        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for result in results:
            if result.entry.id not in seen_ids:
                seen_ids.add(result.entry.id)
                unique_results.append(result)

        return unique_results

    def close(self) -> None:
        """Close the pipeline."""
        if self._query_service:
            self._query_service.close()
