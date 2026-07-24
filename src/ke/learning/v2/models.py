"""WCore X V2 - Data models for autonomous learning."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RelationType(str, Enum):
    """Knowledge graph relation types."""

    PARENT = "parent"
    CHILD = "child"
    RELATED = "related"
    DEPENDS_ON = "depends_on"
    ALTERNATIVE = "alternative"
    EXAMPLE = "example"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"


class KnowledgeNode(BaseModel):
    """A node in the knowledge graph."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept: str
    definition: str = ""
    summary: str = ""
    parent_id: str | None = None
    child_ids: list[str] = Field(default_factory=list)
    related_ids: list[str] = Field(default_factory=list)
    dependency_ids: list[str] = Field(default_factory=list)
    alternative_ids: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class Relation(BaseModel):
    """A relation between knowledge nodes."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QualityScore(BaseModel):
    """Quality score for a knowledge entry."""

    accuracy: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    freshness: float = Field(default=1.0, ge=0.0, le=1.0)
    source_reliability: float = Field(default=0.5, ge=0.0, le=1.0)
    difficulty: str = "beginner"
    coverage: float = Field(default=0.5, ge=0.0, le=1.0)

    @property
    def overall(self) -> float:
        """Calculate overall quality score."""
        return (
            self.accuracy * 0.3
            + self.confidence * 0.25
            + self.freshness * 0.15
            + self.source_reliability * 0.2
            + self.coverage * 0.1
        )


class LearningScore(BaseModel):
    """Learning progress score for a technology."""

    topic: str
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    level: str = "beginner"  # beginner | intermediate | advanced | expert
    entries_learned: int = 0
    exercises_completed: int = 0
    tests_passed: int = 0
    errors_learned: int = 0
    last_studied: datetime | None = None
    next_review: datetime | None = None


class SelfExam(BaseModel):
    """Self-generated exam for a topic."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    questions: list[dict[str, Any]] = Field(default_factory=list)
    answers: list[str] = Field(default_factory=list)
    score: float = 0.0
    passed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = None


class DreamReport(BaseModel):
    """Report from dream mode (idle learning)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    completed_at: datetime | None = None
    activities: list[str] = Field(default_factory=list)
    new_knowledge: int = 0
    updated_knowledge: int = 0
    removed_duplicates: int = 0
    contradictions_found: int = 0
    graph_nodes_added: int = 0
    graph_relations_added: int = 0
    embeddings_updated: int = 0
    next_actions: list[str] = Field(default_factory=list)


class ErrorMemory(BaseModel):
    """Error memory entry."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    error: str
    root_cause: str
    fix: str
    lessons: list[str] = Field(default_factory=list)
    prevention: list[str] = Field(default_factory=list)
    context: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class SelfReflection(BaseModel):
    """Self-reflection after learning session."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    weak_areas: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    study_plan: list[str] = Field(default_factory=list)
    questions_generated: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
