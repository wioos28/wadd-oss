"""Infrastructure storage implementations - Concrete implementations of domain interfaces."""

from __future__ import annotations

from typing import Any

from ke.config import KeConfig, ChromaDBCloudConfig
from ke.domain.models import KnowledgeEntry
from ke.domain.interfaces import (
    VectorStoreInterface,
    MetadataStoreInterface,
    CacheInterface,
)


class SQLiteMetadataStore(MetadataStoreInterface):
    """SQLite-based metadata storage implementation."""

    def __init__(self, db_path: str | None = None):
        from ke.storage.metadata import MetadataStore
        self._store = MetadataStore(db_path) if db_path else MetadataStore()

    def add_entry(self, entry: KnowledgeEntry) -> None:
        self._store.add_entry(entry)

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        return self._store.get_entry(entry_id)

    def search_content(self, query: str, limit: int = 10) -> list[KnowledgeEntry]:
        return self._store.search_content(query, limit)

    def list_entries(
        self,
        source_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[KnowledgeEntry]:
        return self._store.list_entries(source_type=source_type, limit=limit, offset=offset)

    def count_entries(self) -> int:
        return self._store.count_entries()

    def close(self) -> None:
        self._store.close()


class ChromaVectorStore(VectorStoreInterface):
    """ChromaDB local vector storage implementation."""

    def __init__(self, db_path: str | None = None, collection_name: str = "knowledge"):
        from ke.storage.vector import VectorStore
        self._store = VectorStore(db_path, collection_name) if db_path else VectorStore(collection_name)

    def add_entry(self, entry: KnowledgeEntry, embedding: list[float]) -> None:
        self._store.add_entry(entry, embedding)

    def add_batch(self, entries: list[KnowledgeEntry], embeddings: list[list[float]]) -> None:
        self._store.add_batch(entries, embeddings)

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict | None = None,
    ) -> list[dict]:
        return self._store.search(query_embedding, n_results, where)

    def get_entry(self, entry_id: str) -> dict | None:
        return self._store.get_entry(entry_id)

    def delete_entry(self, entry_id: str) -> None:
        self._store.delete_entry(entry_id)

    def count(self) -> int:
        return self._store.count()


class ShelveCache(CacheInterface):
    """Python shelve-based cache implementation."""

    def __init__(self, cache_path: str | None = None):
        from ke.storage.cache import LocalCache
        self._cache = LocalCache(cache_path) if cache_path else LocalCache()

    def get(self, key: str) -> Any | None:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache.set(key, value)

    def delete(self, key: str) -> None:
        self._cache.delete(key)

    def clear(self) -> None:
        self._cache.clear()


class ChromaCloudStore:
    """ChromaDB Cloud vector storage implementation."""

    def __init__(self, config: ChromaDBCloudConfig):
        from ke.storage.cloud import CloudVectorStore
        self._store = CloudVectorStore(config)

    def add_entry(self, entry: KnowledgeEntry, embedding: list[float]) -> None:
        self._store.add_entry(entry, embedding)

    def add_batch(self, entries: list[KnowledgeEntry], embeddings: list[list[float]]) -> None:
        self._store.add_batch(entries, embeddings)

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict | None = None,
    ) -> list[dict]:
        return self._store.search(query_embedding, n_results, where)

    def count(self) -> int:
        return self._store.count()


class CloudAccountStore:
    """ChromaDB Cloud user account storage implementation."""

    def __init__(self, config: ChromaDBCloudConfig):
        from ke.storage.accounts import AccountStore
        self._store = AccountStore(config)

    def create_account(self, username: str, email: str, password: str):
        return self._store.create_account(username, email, password)

    def authenticate(self, username: str, password: str):
        return self._store.authenticate(username, password)

    def get_by_id(self, user_id: str):
        return self._store.get_by_id(user_id)

    def get_by_username(self, username: str):
        return self._store.get_by_username(username)

    def list_accounts(self, limit: int = 100):
        return self._store.list_accounts(limit)

    def count(self) -> int:
        return self._store.count()


class CloudChatHistoryStore:
    """ChromaDB Cloud chat history storage implementation."""

    def __init__(self, config: ChromaDBCloudConfig):
        from ke.storage.chat_history import ChatHistoryStore
        self._store = ChatHistoryStore(config)

    def add_message(self, role: str, content: str, session_id: str | None = None):
        return self._store.add_message(role, content, metadata={"session_id": session_id})

    def get_session_history(self, session_id: str):
        return self._store.get_session_history(session_id)

    def get_recent_messages(self, count: int = 10):
        return self._store.get_recent_messages(count)

    def count(self) -> int:
        return self._store.count()
