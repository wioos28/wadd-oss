"""Reflection - Post-task learning and quality evaluation."""

from __future__ import annotations

from typing import Any

from ke.reasoning.models import (
    ConfidenceScore,
    ReasoningChain,
    ReasoningResult,
    ReflectionResult,
)


class Reflector:
    """Evaluate completed tasks and extract reusable knowledge."""

    def __init__(self, min_quality_threshold: float = 0.5):
        self.min_quality_threshold = min_quality_threshold

    def reflect(
        self,
        result: ReasoningResult,
        task_id: str | None = None,
    ) -> ReflectionResult:
        """Reflect on a completed reasoning task."""
        # Evaluate answer quality
        quality = self._evaluate_quality(result)

        # Extract lessons learned
        lessons = self._extract_lessons(result)

        # Generate summary
        summary = self._generate_summary(result)

        # Extract reusable knowledge
        reusable = self._extract_reusable_knowledge(result)

        # Determine if we should store
        should_store = quality >= self.min_quality_threshold

        return ReflectionResult(
            task_id=task_id or result.reasoning_chain.id,
            answer_quality=quality,
            lessons_learned=lessons,
            summary=summary,
            reusable_knowledge=reusable,
            should_store=should_store,
            metadata={
                "confidence": result.confidence.overall,
                "evidence_count": result.confidence.evidence_count,
                "sources_used": len(result.sources_used),
            },
        )

    def _evaluate_quality(self, result: ReasoningResult) -> float:
        """Evaluate the quality of the reasoning result."""
        scores = []

        # Confidence score
        scores.append(result.confidence.overall)

        # Evidence count (more evidence = better, up to a point)
        evidence_score = min(1.0, result.confidence.evidence_count / 5)
        scores.append(evidence_score)

        # Reasoning chain length (more steps = more thorough)
        chain_length = len(result.reasoning_chain.steps)
        chain_score = min(1.0, chain_length / 5)
        scores.append(chain_score)

        # Source diversity
        source_score = min(1.0, len(result.sources_used) / 3)
        scores.append(source_score)

        # Verification passed
        if result.verification:
            verification_score = 1.0 if result.verification.is_consistent else 0.5
            scores.append(verification_score)

        # Weighted average
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights[:len(scores)])

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _extract_lessons(self, result: ReasoningResult) -> list[str]:
        """Extract lessons learned from the reasoning process."""
        lessons = []

        # High confidence = good retrieval
        if result.confidence.retrieval_score > 0.8:
            lessons.append("Retrieval was highly effective for this type of query")

        # Low confidence = needs improvement
        if result.confidence.overall < 0.5:
            lessons.append("Low confidence - consider different retrieval strategy")

        # Many sources used
        if len(result.sources_used) > 5:
            lessons.append("Multiple sources provided comprehensive coverage")

        # Verification issues
        if result.verification and result.verification.logical_errors:
            lessons.append("Logical consistency check found issues - improve reasoning")

        if result.verification and result.verification.missing_info:
            lessons.append("Missing information detected - may need additional retrieval")

        # Chain length insight
        if len(result.reasoning_chain.steps) > 7:
            lessons.append("Complex reasoning chain - consider simplification")

        return lessons

    def _generate_summary(self, result: ReasoningResult) -> str:
        """Generate a summary of the reasoning result."""
        query = result.query[:100]
        confidence = result.confidence.overall
        evidence = result.confidence.evidence_count

        summary_parts = [
            f"Query: {query}",
            f"Confidence: {confidence:.2f}",
            f"Evidence used: {evidence} items",
            f"Sources: {len(result.sources_used)}",
        ]

        if result.verification:
            status = "consistent" if result.verification.is_consistent else "inconsistent"
            summary_parts.append(f"Verification: {status}")

        return " | ".join(summary_parts)

    def _extract_reusable_knowledge(self, result: ReasoningResult) -> list[str]:
        """Extract knowledge that can be reused in future tasks."""
        knowledge = []

        # High-quality answers are reusable
        if result.confidence.overall > 0.7:
            knowledge.append(f"High-confidence answer pattern for: {result.query[:50]}")

        # Effective source combinations
        if len(result.sources_used) > 2:
            knowledge.append(f"Effective source combination: {', '.join(result.sources_used[:3])}")

        # Reasoning patterns
        for step in result.reasoning_chain.steps:
            if step.confidence > 0.8 and step.step_type == "synthesis":
                knowledge.append(f"Effective synthesis pattern: {step.thought[:100]}")

        return knowledge[:5]  # Limit

    def should_store(self, result: ReasoningResult) -> bool:
        """Determine if this result should be stored for future use."""
        # Store high-confidence results
        if result.confidence.overall >= 0.7:
            return True

        # Store results with many sources
        if len(result.sources_used) >= 3:
            return True

        # Store results that pass verification
        if result.verification and result.verification.is_consistent:
            if result.confidence.overall >= 0.5:
                return True

        return False
