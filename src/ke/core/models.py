"""Core models and data structures for the Knowledge Engine."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Confidence(BaseModel):
    """Confidence score for a knowledge entry or query result."""

    score: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    source: str = Field(description="Source of confidence: verified, user_memory, reasoning, assumption, search")
    explanation: str = Field(default="", description="Why this confidence level")


class NetworkState(BaseModel):
    """Current network connectivity state."""

    status: str = Field(description="offline, wifi, cellular, limited, poor")
    interfaces: list[str] = Field(default_factory=list, description="Active network interfaces")
    latency_ms: float | None = Field(default=None, description="Measured latency in ms")
    bandwidth_mbps: float | None = Field(default=None, description="Estimated bandwidth in Mbps")
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class Relationship(BaseModel):
    """A relationship between two knowledge entries."""

    source_id: str
    target_id: str
    relationship_type: str = Field(description="e.g., related_to, derived_from, contradicts, supports")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Strength of relationship")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeEntry(BaseModel):
    """A single piece of knowledge stored in the engine."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(description="The actual knowledge content")
    summary: str = Field(default="", description="AI-generated summary")
    tags: list[str] = Field(default_factory=list, description="Categorization tags")
    source_path: str | None = Field(default=None, description="Original file path if ingested")
    source_type: str = Field(default="manual", description="Source type: manual, pdf, docx, html, code, etc.")
    confidence: Confidence = Field(default_factory=lambda: Confidence(score=0.5, source="reasoning"))
    relationships: list[Relationship] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding_id: str | None = Field(default=None, description="Reference to vector store entry")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QueryResult(BaseModel):
    """A result from the query pipeline."""

    entry: KnowledgeEntry
    score: float = Field(ge=0.0, le=1.0, description="Relevance score")
    source_layer: str = Field(description="Which pipeline layer produced this: cache, metadata, vector, cloud, internet")
    retrieval_mode: str = Field(description="Which retrieval strategy found this: semantic, keyword, hybrid, etc.")
    explanation: str = Field(default="", description="Why this result matches")


class IngestionResult(BaseModel):
    """Result of ingesting a file or directory."""

    source_path: str
    chunks_created: int = 0
    entries: list[KnowledgeEntry] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    duration_ms: float = 0.0


class QueryMode(str, Enum):
    """Retrieval modes for querying."""

    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    CODE_SIMILARITY = "code_similarity"
    METADATA = "metadata"
    TIME = "time"
    RELATIONSHIP = "relationship"


class PipelineLayer(BaseModel):
    """Configuration for a query pipeline layer."""

    name: str
    enabled: bool = True
    priority: int = Field(ge=0, description="Lower number = checked first")
    requires_network: bool = False
