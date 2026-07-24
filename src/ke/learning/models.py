"""Learning models - Data structures for knowledge entries."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    """Knowledge difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SourceType(str, Enum):
    """Types of knowledge sources."""

    DOCUMENTATION = "documentation"
    GITHUB = "github"
    RESEARCH = "research"
    STANDARD = "standard"
    WIKIPEDIA = "wikipedia"
    STACKOVERFLOW = "stackoverflow"
    EXPERIENCE = "experience"
    UNKNOWN = "unknown"


class KnowledgeCategory(str, Enum):
    """Categories of knowledge."""

    CONCEPT = "concept"
    SYNTAX = "syntax"
    API = "api"
    PATTERN = "pattern"
    ALGORITHM = "algorithm"
    ERROR = "error"
    BEST_PRACTICE = "best_practice"
    ARCHITECTURE = "architecture"
    DEPENDENCY = "dependency"
    WORKFLOW = "workflow"
    UNKNOWN = "unknown"


class LearningSource(BaseModel):
    """Source of knowledge entry."""

    type: SourceType
    url: str = ""
    title: str = ""
    author: str = ""
    last_updated: datetime | None = None
    reliability_score: float = Field(default=0.5, ge=0.0, le=1.0)


class KnowledgeEntry(BaseModel):
    """A single knowledge entry in the knowledge base."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    summary: str
    explanation: str
    examples: list[str] = Field(default_factory=list)
    best_practices: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    difficulty: Difficulty = Difficulty.BEGINNER
    language: str = "en"
    category: KnowledgeCategory = KnowledgeCategory.UNKNOWN
    source: LearningSource = Field(default_factory=lambda: LearningSource(type=SourceType.UNKNOWN))
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    version: int = 1
    verified: bool = False
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class LearningReport(BaseModel):
    """Report generated after a learning session."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = None
    topics_learned: list[str] = Field(default_factory=list)
    files_processed: int = 0
    entries_created: int = 0
    entries_updated: int = 0
    examples_generated: int = 0
    errors_learned: int = 0
    projects_analyzed: int = 0
    tests_passed: int = 0
    coverage_percent: float = 0.0
    next_tasks: list[str] = Field(default_factory=list)
    knowledge_score: float = 0.0
    sources_used: list[LearningSource] = Field(default_factory=list)
    quality_issues: list[str] = Field(default_factory=list)


class LearningConfig(BaseModel):
    """Configuration for learning pipeline."""

    max_concurrent_fetches: int = 5
    min_reliability_score: float = 0.3
    auto_verify: bool = False
    store_raw_content: bool = False
    max_entry_length: int = 10000
    dedup_strategy: str = "exact"  # exact | semantic | skip
