"""Domain interfaces - Abstract contracts for infrastructure implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ke.domain.models import (
    KnowledgeEntry,
    QueryResult,
    QueryMode,
    User,
    ChatMessage,
    MemoryEntry,
    MemoryType,
)


# ============================================================================
# Storage Interfaces
# ============================================================================

class VectorStoreInterface(ABC):
    """Abstract interface for vector storage."""

    @abstractmethod
    def add_entry(self, entry: KnowledgeEntry, embedding: list[float]) -> None:
        """Store a knowledge entry with its embedding."""
        ...

    @abstractmethod
    def add_batch(self, entries: list[KnowledgeEntry], embeddings: list[list[float]]) -> None:
        """Batch insert entries with embeddings."""
        ...

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict | None = None,
    ) -> list[dict]:
        """Search for similar entries by embedding."""
        ...

    @abstractmethod
    def get_entry(self, entry_id: str) -> dict | None:
        """Get a specific entry by ID."""
        ...

    @abstractmethod
    def delete_entry(self, entry_id: str) -> None:
        """Delete an entry from the vector store."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Get total number of entries."""
        ...


class MetadataStoreInterface(ABC):
    """Abstract interface for metadata storage."""

    @abstractmethod
    def add_entry(self, entry: KnowledgeEntry) -> None:
        """Store a knowledge entry."""
        ...

    @abstractmethod
    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """Get a knowledge entry by ID."""
        ...

    @abstractmethod
    def search_content(self, query: str, limit: int = 10) -> list[KnowledgeEntry]:
        """Search entries by content."""
        ...

    @abstractmethod
    def list_entries(
        self,
        source_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[KnowledgeEntry]:
        """List entries with optional filtering."""
        ...

    @abstractmethod
    def count_entries(self) -> int:
        """Count total entries."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the store."""
        ...


class CacheInterface(ABC):
    """Abstract interface for caching."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set a value in cache."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value from cache."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all entries from cache."""
        ...


# ============================================================================
# Service Interfaces
# ============================================================================

class EmbeddingServiceInterface(ABC):
    """Abstract interface for embedding generation."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        ...

    @abstractmethod
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        ...


class LLMServiceInterface(ABC):
    """Abstract interface for LLM interaction."""

    @abstractmethod
    def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Send chat completion request."""
        ...

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Complete a prompt."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        ...


class IngestorInterface(ABC):
    """Abstract interface for file ingestion."""

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """Check if this ingestor can handle the file."""
        ...

    @abstractmethod
    def ingest(self, file_path: str) -> list[KnowledgeEntry]:
        """Ingest a file and return knowledge entries."""
        ...


class AccountServiceInterface(ABC):
    """Abstract interface for user account management."""

    @abstractmethod
    def create_account(self, username: str, email: str, password: str) -> User:
        """Create a new user account."""
        ...

    @abstractmethod
    def authenticate(self, username: str, password: str) -> User | None:
        """Authenticate user with credentials."""
        ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        """Get user by ID."""
        ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        ...


class ChatHistoryInterface(ABC):
    """Abstract interface for chat history."""

    @abstractmethod
    def add_message(self, role: str, content: str, session_id: str) -> ChatMessage:
        """Add a message to chat history."""
        ...

    @abstractmethod
    def get_session_history(self, session_id: str) -> list[ChatMessage]:
        """Get messages from a session."""
        ...

    @abstractmethod
    def get_recent_messages(self, count: int = 10) -> list[ChatMessage]:
        """Get recent messages across all sessions."""
        ...


class MemoryStoreInterface(ABC):
    """Abstract interface for memory storage."""

    @abstractmethod
    def store(self, entry: MemoryEntry) -> None:
        """Store a memory entry."""
        ...

    @abstractmethod
    def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve a memory entry."""
        ...

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        """Search memory entries."""
        ...

    @abstractmethod
    def get_by_type(self, memory_type: MemoryType, limit: int = 100) -> list[MemoryEntry]:
        """Get entries by memory type."""
        ...
