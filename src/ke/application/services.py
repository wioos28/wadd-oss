"""Application services - Business logic orchestration."""

from __future__ import annotations

from typing import Any

from ke.config import KeConfig
from ke.domain.models import (
    KnowledgeEntry,
    QueryResult,
    QueryMode,
    User,
    ChatMessage,
    MessageRole,
    MemoryEntry,
    MemoryType,
)


class KnowledgeService:
    """Service for knowledge management operations."""

    def __init__(self, config: KeConfig):
        self.config = config
        self._metadata_store = None
        self._vector_store = None
        self._embedding_model = None

    @property
    def metadata_store(self):
        if self._metadata_store is None:
            from ke.storage.metadata import MetadataStore
            self._metadata_store = MetadataStore(self.config.metadata_db_path())
        return self._metadata_store

    @property
    def vector_store(self):
        if self._vector_store is None:
            from ke.storage.vector import VectorStore
            self._vector_store = VectorStore(self.config.vector_db_path())
        return self._vector_store

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            from ke.embeddings.model import EmbeddingModel
            self._embedding_model = EmbeddingModel(
                model_name=self.config.embeddings.model_name,
                device=self.config.embeddings.device,
            )
        return self._embedding_model

    def add_entry(self, entry: KnowledgeEntry, embedding: list[float] | None = None) -> None:
        """Add a knowledge entry to all stores."""
        if embedding is None:
            embedding = self.embedding_model.embed(entry.content)

        self.metadata_store.add_entry(entry)
        self.vector_store.add_entry(entry, embedding)

    def add_entries(self, entries: list[KnowledgeEntry]) -> None:
        """Batch add knowledge entries."""
        if not entries:
            return

        texts = [e.content for e in entries]
        embeddings = self.embedding_model.embed_batch(texts)

        for entry in entries:
            self.metadata_store.add_entry(entry)

        self.vector_store.add_batch(entries, embeddings)

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """Get a knowledge entry by ID."""
        return self.metadata_store.get_entry(entry_id)

    def list_entries(
        self,
        source_type: str | None = None,
        limit: int = 100,
    ) -> list[KnowledgeEntry]:
        """List knowledge entries."""
        return self.metadata_store.list_entries(source_type=source_type, limit=limit)

    def count_entries(self) -> int:
        """Count total knowledge entries."""
        return self.metadata_store.count_entries()

    def close(self) -> None:
        """Close all resources."""
        if self._metadata_store:
            self._metadata_store.close()
        if self._vector_store:
            self._vector_store.close()


class QueryService:
    """Service for querying knowledge base."""

    def __init__(self, config: KeConfig):
        self.config = config
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            from ke.core.pipeline import QueryPipeline
            self._pipeline = QueryPipeline(self.config)
        return self._pipeline

    def query(
        self,
        text: str,
        mode: str | QueryMode = QueryMode.HYBRID,
        limit: int = 10,
        min_score: float | None = None,
        **kwargs: Any,
    ) -> list[QueryResult]:
        """Execute a query through the pipeline."""
        return self.pipeline.query(
            text=text,
            mode=mode,
            limit=limit,
            min_score=min_score,
            **kwargs,
        )

    def close(self) -> None:
        """Close the pipeline."""
        if self._pipeline:
            self._pipeline.close()


class IngestionService:
    """Service for file ingestion."""

    def __init__(self, config: KeConfig):
        self.config = config
        self._manager = None

    @property
    def manager(self):
        if self._manager is None:
            from ke.ingestion.manager import IngestionManager
            self._manager = IngestionManager(
                chunk_size=self.config.chunking.chunk_size,
                chunk_overlap=self.config.chunking.chunk_overlap,
            )
        return self._manager

    def ingest(self, path: str, recursive: bool = True) -> list[KnowledgeEntry]:
        """Ingest files and return knowledge entries."""
        from pathlib import Path

        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        results = self.manager.ingest(target, recursive=recursive)

        if isinstance(results, list):
            entries = []
            for r in results:
                entries.extend(r.entries)
            return entries
        else:
            return results.entries

    def ingest_file(self, file_path: str) -> list[KnowledgeEntry]:
        """Ingest a single file."""
        return self.ingest(file_path, recursive=False)


class AuthService:
    """Service for user authentication."""

    def __init__(self, config: KeConfig):
        self.config = config
        self._store = None

    @property
    def store(self):
        if self._store is None:
            from ke.storage.accounts import AccountStore
            self._store = AccountStore(self.config.chromadb_cloud)
        return self._store

    def create_account(self, username: str, email: str, password: str) -> User:
        """Create a new user account."""
        account = self.store.create_account(username, email, password)
        return User(
            user_id=account.user_id,
            username=account.username,
            email=account.email,
            created_at=account.created_at,
        )

    def login(self, username: str, password: str) -> User | None:
        """Authenticate user with credentials."""
        account = self.store.authenticate(username, password)
        if not account:
            return None
        return User(
            user_id=account.user_id,
            username=account.username,
            email=account.email,
            created_at=account.created_at,
        )

    def get_user(self, user_id: str) -> User | None:
        """Get user by ID."""
        account = self.store.get_by_id(user_id)
        if not account:
            return None
        return User(
            user_id=account.user_id,
            username=account.username,
            email=account.email,
            created_at=account.created_at,
        )

    def list_users(self, limit: int = 100) -> list[User]:
        """List all users."""
        accounts = self.store.list_accounts(limit=limit)
        return [
            User(
                user_id=a.user_id,
                username=a.username,
                email=a.email,
                created_at=a.created_at,
            )
            for a in accounts
        ]


class ChatService:
    """Service for chat operations."""

    def __init__(self, config: KeConfig):
        self.config = config
        self._store = None

    @property
    def store(self):
        if self._store is None:
            from ke.storage.chat_history import ChatHistoryStore
            self._store = ChatHistoryStore(self.config.chromadb_cloud)
        return self._store

    def send_message(
        self,
        content: str,
        role: str = "user",
        session_id: str | None = None,
    ) -> ChatMessage:
        """Send a chat message."""
        msg = self.store.add_message(role, content, metadata={"session_id": session_id})
        return ChatMessage(
            message_id=msg.message_id,
            role=MessageRole(role),
            content=msg.content,
            session_id=msg.session_id,
            turn=msg.turn,
            timestamp=msg.timestamp,
        )

    def get_history(self, session_id: str | None = None) -> list[ChatMessage]:
        """Get chat history."""
        messages = self.store.get_session_history(session_id)
        return [
            ChatMessage(
                message_id=m.message_id,
                role=MessageRole(m.role),
                content=m.content,
                session_id=m.session_id,
                turn=m.turn,
                timestamp=m.timestamp,
            )
            for m in messages
        ]

    def get_recent(self, count: int = 10) -> list[ChatMessage]:
        """Get recent messages."""
        messages = self.store.get_recent_messages(count)
        return [
            ChatMessage(
                message_id=m.message_id,
                role=MessageRole(m.role),
                content=m.content,
                session_id=m.session_id,
                turn=m.turn,
                timestamp=m.timestamp,
            )
            for m in messages
        ]


class MemoryService:
    """Service for memory operations."""

    def __init__(self, config: KeConfig):
        self.config = config
        self._manager = None

    @property
    def manager(self):
        if self._manager is None:
            from ke.memory.memory_manager import MemoryManager
            self._manager = MemoryManager()
        return self._manager

    def store(
        self,
        content: str,
        memory_type: str = "working",
        tags: list[str] | None = None,
        importance: float = 0.5,
    ) -> MemoryEntry:
        """Store a memory entry."""
        mt = MemoryType(memory_type)
        entry = self.manager.store(content, mt, tags=tags or [], importance=importance)
        return MemoryEntry(
            id=entry.id,
            content=entry.content,
            summary=entry.summary,
            memory_type=mt,
            tags=entry.tags,
            importance=entry.importance,
            created_at=entry.created_at,
        )

    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        """Search memory entries."""
        from ke.memory.models import MemoryQuery

        mq = MemoryQuery(query=query, limit=limit)
        results = self.manager.search(mq)
        return [
            MemoryEntry(
                id=e.id,
                content=e.content,
                summary=e.summary,
                memory_type=MemoryType(e.memory_type.value),
                tags=e.tags,
                importance=e.importance,
                created_at=e.created_at,
            )
            for e in results
        ]

    def get_stats(self) -> dict[str, int]:
        """Get memory statistics."""
        return self.manager.get_stats()
