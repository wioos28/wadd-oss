"""Reasoning Pipeline - Orchestrate the full reasoning process."""

from __future__ import annotations

import time
from typing import Any

from ke.reasoning.confidence import ConfidenceScorer
from ke.reasoning.context import ContextBuilder
from ke.reasoning.intent import IntentEngine
from ke.reasoning.models import (
    ConfidenceScore,
    ExecutionPlan,
    Intent,
    ReasoningChain,
    ReasoningContext,
    ReasoningResult,
    ReflectionResult,
    VerificationResult,
)
from ke.reasoning.planner import TaskPlanner
from ke.reasoning.prompt_builder import PromptBuilder
from ke.reasoning.reasoner import Reasoner
from ke.reasoning.reflection import Reflector
from ke.reasoning.verifier import Verifier


class ReasoningPipeline:
    """Full reasoning pipeline that processes queries through all stages."""

    def __init__(
        self,
        knowledge_pipeline: Any = None,
        embedding_model: Any = None,
        min_confidence: float = 0.5,
    ):
        # Core components
        self.intent_engine = IntentEngine()
        self.planner = TaskPlanner()
        self.context_builder = ContextBuilder()
        self.reasoner = Reasoner(embedding_model)
        self.verifier = Verifier(min_confidence=min_confidence)
        self.reflector = Reflector(min_quality_threshold=min_confidence)
        self.confidence_scorer = ConfidenceScorer(min_confidence=min_confidence)
        self.prompt_builder = PromptBuilder()

        # External dependencies
        self.knowledge_pipeline = knowledge_pipeline
        self.embedding_model = embedding_model

    def reason(
        self,
        query: str,
        context: ReasoningContext | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        session_id: str | None = None,
    ) -> ReasoningResult:
        """Execute the full reasoning pipeline."""
        start_time = time.time()

        # Step 1: Detect intent
        intent = self.intent_engine.detect(query)

        # Step 2: Build context
        if context is None:
            context = self._build_context(query, intent, session_id)
        else:
            context.intent = intent

        # Step 3: Create execution plan
        plan = self.planner.create_plan(intent, query)

        # Step 4: Execute reasoning
        chain = self._execute_reasoning(context, plan)

        # Step 5: Verify result
        answer = chain.conclusion
        verification = self.verifier.verify(chain, query, answer)

        # Adjust confidence based on verification
        if verification:
            adjusted_confidence = self.confidence_scorer.adjust_confidence(
                chain.confidence,
                [verification.confidence_adjustment],
            )
            chain.confidence = adjusted_confidence

        # Step 6: Calculate final confidence
        confidence = self.confidence_scorer.calculate(chain)

        # Step 7: Reflect on the result
        result = ReasoningResult(
            query=query,
            answer=answer,
            reasoning_chain=chain,
            confidence=confidence,
            verification=verification,
            sources_used=chain.sources,
        )

        reflection = self.reflector.reflect(result)
        result.reflection = reflection

        # Calculate processing time
        result.processing_time_ms = (time.time() - start_time) * 1000

        return result

    def plan(
        self,
        query: str,
        context: ReasoningContext | None = None,
    ) -> ExecutionPlan:
        """Create an execution plan without full reasoning."""
        intent = self.intent_engine.detect(query)
        return self.planner.create_plan(intent, query)

    def verify(
        self,
        query: str,
        answer: str,
        chain: ReasoningChain,
    ) -> VerificationResult:
        """Verify a specific answer."""
        return self.verifier.verify(chain, query, answer)

    def reflect(
        self,
        result: ReasoningResult,
        task_id: str | None = None,
    ) -> ReflectionResult:
        """Reflect on a reasoning result."""
        return self.reflector.reflect(result, task_id)

    def confidence(
        self,
        chain: ReasoningChain,
        retrieval_score: float = 0.0,
        knowledge_quality: float = 0.0,
    ) -> ConfidenceScore:
        """Calculate confidence for a reasoning chain."""
        return self.confidence_scorer.calculate(chain, retrieval_score, knowledge_quality)

    def detect_intent(self, text: str) -> Intent:
        """Detect intent from user input."""
        return self.intent_engine.detect(text)

    def _build_context(
        self,
        query: str,
        intent: Intent,
        session_id: str | None = None,
    ) -> ReasoningContext:
        """Build reasoning context from query."""
        if self.knowledge_pipeline:
            return self.context_builder.build_from_pipeline(
                query, self.knowledge_pipeline, intent
            )
        else:
            return self.context_builder.build(
                query=query,
                intent=intent,
                session_id=session_id,
            )

    def _execute_reasoning(
        self,
        context: ReasoningContext,
        plan: ExecutionPlan,
    ) -> ReasoningChain:
        """Execute the reasoning process."""
        # Use the reasoner to generate a reasoning chain
        chain = self.reasoner.reason(context, plan)

        return chain

    def process_with_callback(
        self,
        query: str,
        on_intent: Any = None,
        on_plan: Any = None,
        on_reasoning: Any = None,
        on_verification: Any = None,
        on_reflection: Any = None,
        **kwargs: Any,
    ) -> ReasoningResult:
        """Process a query with callbacks at each stage."""
        # Intent detection
        intent = self.intent_engine.detect(query)
        if on_intent:
            on_intent(intent)

        # Context building
        context = self._build_context(query, intent)

        # Planning
        plan = self.planner.create_plan(intent, query)
        if on_plan:
            on_plan(plan)

        # Reasoning
        chain = self._execute_reasoning(context, plan)
        if on_reasoning:
            on_reasoning(chain)

        # Verification
        verification = self.verifier.verify(chain, query, chain.conclusion)
        if on_verification:
            on_verification(verification)

        # Calculate confidence
        confidence = self.confidence_scorer.calculate(chain)

        # Build result
        result = ReasoningResult(
            query=query,
            answer=chain.conclusion,
            reasoning_chain=chain,
            confidence=confidence,
            verification=verification,
            sources_used=chain.sources,
        )

        # Reflection
        reflection = self.reflector.reflect(result)
        result.reflection = reflection
        if on_reflection:
            on_reflection(reflection)

        return result
