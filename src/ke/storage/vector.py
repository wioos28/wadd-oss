"""ChromaDB vector store for embedding-based search."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings

from ke.core.models import KnowledgeEntry


class VectorStore:
    """ChromaDB-based vector storage for semantic search."""

    def __init__(self, db_path: Path | str, collection_name: str = "knowledge"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_entry(self, entry: KnowledgeEntry, embedding: list[float]) -> None:
        """Store a knowledge entry with its embedding."""
        self.collection.upsert(
            ids=[entry.id],
            embeddings=[embedding],
            documents=[entry.content],
            metadatas=[{
                "source_type": entry.source_type,
                "source_path": entry.source_path or "",
                "tags": ",".join(entry.tags),
                "created_at": entry.created_at.isoformat(),
            }],
        )

    def add_batch(
        self,
        entries: list[KnowledgeEntry],
        embeddings: list[list[float]],
    ) -> None:
        """Batch insert entries with embeddings."""
        if not entries:
            return
        self.collection.upsert(
            ids=[e.id for e in entries],
            embeddings=embeddings,
            documents=[e.content for e in entries],
            metadatas=[{
                "source_type": e.source_type,
                "source_path": e.source_path or "",
                "tags": ",".join(e.tags),
                "created_at": e.created_at.isoformat(),
            } for e in entries],
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict | None = None,
        where_document: dict | None = None,
    ) -> list[dict]:
        """Search for similar entries by embedding."""
        kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self.collection.count() or 1),
        }
        if where:
            kwargs["where"] = where
        if where_document:
            kwargs["where_document"] = where_document

        results = self.collection.query(**kwargs)
        return self._format_results(results)

    def get_entry(self, entry_id: str) -> dict | None:
        """Get a specific entry by ID."""
        results = self.collection.get(ids=[entry_id], include=["documents", "metadatas", "embeddings"])
        if not results["ids"]:
            return None
        return {
            "id": results["ids"][0],
            "document": results["documents"][0],
            "metadata": results["metadatas"][0],
            "embedding": results["embeddings"][0] if results["embeddings"] else None,
        }

    def delete_entry(self, entry_id: str) -> None:
        """Delete an entry from the vector store."""
        self.collection.delete(ids=[entry_id])

    def count(self) -> int:
        """Get total number of entries."""
        return self.collection.count()

    def _format_results(self, results: dict) -> list[dict]:
        """Format ChromaDB results into a clean list."""
        formatted = []
        if not results["ids"] or not results["ids"][0]:
            return formatted

        for i, doc_id in enumerate(results["ids"][0]):
            formatted.append({
                "id": doc_id,
                "document": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results.get("distances") else None,
            })
        return formatted

    def close(self) -> None:
        """Clean up resources."""
        # ChromaDB persistent client doesn't need explicit close
        pass
