"""Reasoning Engine models - data structures for the reasoning pipeline."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Detected intent types from user input."""

    QUESTION = "question"
    COMMAND = "command"
    CONVERSATION = "conversation"
    VISION_REQUEST = "vision"
    OCR_REQUEST = "ocr"
    TRAINING_REQUEST = "training"
    SEARCH_REQUEST = "search"
    CODE_REQUEST = "code"
    MEMORY_REQUEST = "memory"
    API_REQUEST = "api"
    PLUGIN_REQUEST = "plugin"
    UNKNOWN = "unknown"


class Intent(BaseModel):
    """Detected intent from user input."""

    type: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    raw_input: str
    entities: dict[str, Any] = Field(default_factory=dict)
    keywords: list[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class PlanStep(BaseModel):
    """A single step in an execution plan."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    action: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    status: str = "pending"  # pending | in_progress | completed | failed | skipped
    result: Any = None
    error: str | None = None


class ExecutionPlan(BaseModel):
    """Complete execution plan for a task."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    goal: str
    requirements: list[str] = Field(default_factory=list)
    available_tools: list[str] = Field(default_factory=list)
    steps: list[PlanStep] = Field(default_factory=list)
    expected_result: str = ""
    verification_plan: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    status: str = "created"  # created | executing | completed | failed


class ReasoningChain(BaseModel):
    """A chain of reasoning steps."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    steps: list[ReasoningStep] = Field(default_factory=list)
    conclusion: str = ""
    confidence: float = 0.0
    sources: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReasoningStep(BaseModel):
    """A single step in the reasoning chain."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    thought: str
    evidence: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    step_type: str = "inference"  # inference | retrieval | calculation | synthesis


class VerificationResult(BaseModel):
    """Result of verifying an answer."""

    is_consistent: bool
    logical_errors: list[str] = Field(default_factory=list)
    conflicting_facts: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    duplicate_facts: list[str] = Field(default_factory=list)
    confidence_adjustment: float = 0.0
    recommendations: list[str] = Field(default_factory=list)


class ReflectionResult(BaseModel):
    """Result of reflecting on a completed task."""

    task_id: str
    answer_quality: float = Field(ge=0.0, le=1.0)
    lessons_learned: list[str] = Field(default_factory=list)
    summary: str = ""
    reusable_knowledge: list[str] = Field(default_factory=list)
    should_store: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConfidenceScore(BaseModel):
    """Confidence scoring for reasoning results."""

    overall: float = Field(ge=0.0, le=1.0)
    knowledge_quality: float = Field(ge=0.0, le=1.0)
    retrieval_score: float = Field(ge=0.0, le=1.0)
    evidence_count: float = 0.0
    reasoning_quality: float = Field(ge=0.0, le=1.0)
    factors: list[str] = Field(default_factory=list)


class ReasoningContext(BaseModel):
    """Context for the reasoning pipeline."""

    user_query: str
    intent: Intent | None = None
    plan: ExecutionPlan | None = None
    retrieved_entries: list[Any] = Field(default_factory=list)
    memory_entries: list[Any] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    session_id: str | None = None


class ReasoningResult(BaseModel):
    """Final result from the reasoning pipeline."""

    query: str
    answer: str
    reasoning_chain: ReasoningChain
    confidence: ConfidenceScore
    verification: VerificationResult | None = None
    reflection: ReflectionResult | None = None
    sources_used: list[str] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
