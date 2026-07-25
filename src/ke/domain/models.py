"""Unified domain models - single source of truth for all business entities."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# ============================================================================
# Core Knowledge Models
# ============================================================================

class KnowledgeEntry(BaseModel):
    """Single knowledge unit stored in the system."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    source_type: str = "text"
    source_path: str | None = None
    confidence: float = 1.0
    relationships: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class QueryMode(str, Enum):
    """Query retrieval modes."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    CODE_SIMILARITY = "code_similarity"
    METADATA = "metadata"
    TIME = "time"
    RELATIONSHIP = "relationship"


class QueryResult(BaseModel):
    """Query result with scoring and metadata."""
    entry: KnowledgeEntry
    score: float
    source_layer: str = ""
    retrieval_mode: str = ""
    explanation: str = ""


class IngestionResult(BaseModel):
    """Result of file ingestion."""
    entries: list[KnowledgeEntry] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    source_path: str = ""


# ============================================================================
# Relationship Models
# ============================================================================

class RelationshipType(str, Enum):
    """Types of knowledge relationships."""
    RELATED_TO = "related_to"
    DERIVED_FROM = "derived_from"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"


class Relationship(BaseModel):
    """Relationship between two knowledge entries."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Confidence Models
# ============================================================================

class Confidence(BaseModel):
    """Confidence score with explanation."""
    score: float = Field(ge=0.0, le=1.0)
    source: str = ""
    explanation: str = ""


# ============================================================================
# Network Models
# ============================================================================

class NetworkState(BaseModel):
    """Network connectivity state."""
    status: str = "unknown"  # online, offline, degraded
    interfaces: list[str] = Field(default_factory=list)
    latency_ms: float | None = None
    last_checked: datetime = Field(default_factory=lambda: datetime.now())


# ============================================================================
# User Models
# ============================================================================

class User(BaseModel):
    """User account."""
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: str
    password_hash: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Chat Models
# ============================================================================

class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message."""
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str
    session_id: str = ""
    turn: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Memory Models
# ============================================================================

class MemoryType(str, Enum):
    """Types of memory."""
    WORKING = "working"
    SHORT = "short"
    LONG = "long"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    CONVERSATION = "conversation"
    PROJECT = "project"
    VISUAL = "visual"


class MemoryEntry(BaseModel):
    """Memory entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    summary: str = ""
    memory_type: MemoryType
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(ge=0.0, le=1.0, default=0.5)
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=lambda: datetime.now())
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    expires_at: datetime | None = None
    source: str = ""
    embedding_id: str | None = None
