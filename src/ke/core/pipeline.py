"""Core pipeline implementing cascading knowledge retrieval."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ke.config import KeConfig
from ke.core.models import (
    Confidence,
    KnowledgeEntry,
    NetworkState,
    QueryMode,
    QueryResult,
)
from ke.embeddings.model import EmbeddingModel
from ke.retrieval.code_similarity import CodeSimilarityRetriever
from ke.retrieval.hybrid import HybridRetriever
from ke.retrieval.keyword import KeywordRetriever
from ke.retrieval.metadata_search import MetadataRetriever
from ke.retrieval.relationship import RelationshipRetriever
from ke.retrieval.semantic import SemanticRetriever
from ke.storage.cache import LocalCache
from ke.storage.metadata import MetadataStore
from ke.storage.vector import VectorStore


class QueryPipeline:
    """Cascading query pipeline that searches through multiple layers."""

    def __init__(self, config: KeConfig):
        self.config = config

        # Initialize storage
        self.metadata_store = MetadataStore(config.metadata_db_path())
        self.vector_store = VectorStore(config.vector_db_path())
        self.cache = LocalCache(config.cache_path())

        # Initialize embedding model (lazy loaded)
        self.embedding_model = EmbeddingModel(
            model_name=config.embeddings.model_name,
            device=config.embeddings.device,
        )

        # Initialize retrievers
        self.semantic = SemanticRetriever(self.vector_store)
        self.keyword = KeywordRetriever(self.metadata_store)
        self.hybrid = HybridRetriever(self.semantic, self.keyword)
        self.code_similarity = CodeSimilarityRetriever(self.metadata_store)
        self.metadata = MetadataRetriever(self.metadata_store)
        self.relationship = RelationshipRetriever(self.metadata_store)

        # Network state
        self._network_state: NetworkState | None = None

    def query(
        self,
        text: str,
        mode: QueryMode | str = QueryMode.HYBRID,
        limit: int = 10,
        min_score: float | None = None,
        **kwargs: Any,
    ) -> list[QueryResult]:
        """Execute a query through the pipeline."""
        if isinstance(mode, str):
            mode = QueryMode(mode)

        min_score = min_score or self.config.retrieval.min_score

        # Check cache first
        cache_key = f"query:{mode.value}:{text}:{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Get query embedding
        query_embedding = self.embedding_model.embed(text)

        # Execute based on mode
        results = self._execute_query(text, query_embedding, mode, limit, min_score, **kwargs)

        # Cache results
        self.cache.set(cache_key, results)

        return results

    def _execute_query(
        self,
        text: str,
        query_embedding: list[float],
        mode: QueryMode,
        limit: int,
        min_score: float,
        **kwargs: Any,
    ) -> list[QueryResult]:
        """Execute query with specific retrieval mode."""
        if mode == QueryMode.SEMANTIC:
            return self.semantic.search(query_embedding, limit=limit, min_score=min_score)

        elif mode == QueryMode.KEYWORD:
            return self.keyword.search(text, limit=limit)

        elif mode == QueryMode.HYBRID:
            return self.hybrid.search(
                text, query_embedding, limit=limit, min_score=min_score
            )

        elif mode == QueryMode.CODE_SIMILARITY:
            return self.code_similarity.search(text, limit=limit)

        elif mode == QueryMode.METADATA:
            tags = kwargs.get("tags", [])
            if tags:
                return self.metadata.search_by_tags(tags, limit=limit)
            source_type = kwargs.get("source_type")
            if source_type:
                return self.metadata.search_by_source_type(source_type, limit=limit)
            return self.metadata.search_recent(limit=limit)

        elif mode == QueryMode.TIME:
            hours = kwargs.get("hours", 24)
            return self.metadata.search_recent(hours=hours, limit=limit)

        elif mode == QueryMode.RELATIONSHIP:
            entry_id = kwargs.get("entry_id")
            if entry_id:
                return self.relationship.search_from_entry(entry_id, limit=limit)
            return self.relationship.search_from_text(text, limit=limit)

        return []

    def cascading_query(
        self,
        text: str,
        limit: int = 10,
        min_score: float | None = None,
        network_state: NetworkState | None = None,
    ) -> list[QueryResult]:
        """Execute a query through the full cascading pipeline."""
        min_score = min_score or self.config.retrieval.min_score
        query_embedding = self.embedding_model.embed(text)

        all_results: list[QueryResult] = []
        seen_ids: set[str] = set()

        # Layer 1: Cache (already handled in query method)

        # Layer 2: Local metadata DB (keyword search)
        keyword_results = self.keyword.search(text, limit=limit)
        for r in keyword_results:
            if r.entry.id not in seen_ids:
                seen_ids.add(r.entry.id)
                all_results.append(r)

        # Layer 3: Local vector DB (semantic search)
        semantic_results = self.semantic.search(query_embedding, limit=limit)
        for r in semantic_results:
            if r.entry.id not in seen_ids:
                seen_ids.add(r.entry.id)
                all_results.append(r)

        # Layer 4: Cloud (if enabled and online)
        if self.config.query.cloud_enabled:
            if network_state and network_state.status != "offline":
                # Cloud search would go here
                pass

        # Layer 5: Internet (if enabled and user approved)
        if self.config.query.internet_enabled:
            if network_state and network_state.status != "offline":
                if not self.config.query.internet_requires_permission:
                    # Internet search would go here
                    pass

        # Sort by score and return top results
        all_results.sort(key=lambda r: r.score, reverse=True)
        return [r for r in all_results if r.score >= min_score][:limit]

    def add_entry(self, entry: KnowledgeEntry, embedding: list[float] | None = None) -> None:
        """Add a knowledge entry to all stores."""
        # Generate embedding if not provided
        if embedding is None:
            embedding = self.embedding_model.embed(entry.content)

        # Store in metadata DB
        self.metadata_store.add_entry(entry)

        # Store in vector DB
        self.vector_store.add_entry(entry, embedding)

        # Update entry with embedding ID
        entry.embedding_id = entry.id
        self.metadata_store.add_entry(entry)

    def add_entries(self, entries: list[KnowledgeEntry]) -> None:
        """Batch add knowledge entries."""
        if not entries:
            return

        # Generate embeddings in batch
        texts = [e.content for e in entries]
        embeddings = self.embedding_model.embed_batch(texts)

        # Store in metadata DB
        for entry in entries:
            self.metadata_store.add_entry(entry)

        # Store in vector DB
        self.vector_store.add_batch(entries, embeddings)

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """Get a knowledge entry by ID."""
        return self.metadata_store.get_entry(entry_id)

    def delete_entry(self, entry_id: str) -> None:
        """Delete a knowledge entry from all stores."""
        self.metadata_store.delete_entry(entry_id) if hasattr(self.metadata_store, 'delete_entry') else None
        self.vector_store.delete_entry(entry_id)

    def count_entries(self) -> int:
        """Count total knowledge entries."""
        return self.metadata_store.count_entries()

    def close(self) -> None:
        """Close all resources."""
        self.metadata_store.close()
        self.vector_store.close()
        self.cache.close()

    def __enter__(self) -> QueryPipeline:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
