"""Reasoner - Generate reasoning chains from context and evidence."""

from __future__ import annotations

from typing import Any

from ke.reasoning.models import (
    ConfidenceScore,
    ExecutionPlan,
    Intent,
    ReasoningChain,
    ReasoningContext,
    ReasoningStep,
)


class Reasoner:
    """Generate structured reasoning chains from retrieved evidence."""

    def __init__(self, embedding_model: Any = None):
        self.embedding_model = embedding_model

    def reason(
        self,
        context: ReasoningContext,
        plan: ExecutionPlan | None = None,
    ) -> ReasoningChain:
        """Generate a reasoning chain from context."""
        steps: list[ReasoningStep] = []

        # Step 1: Analyze the query
        analysis_step = self._analyze_query(context)
        steps.append(analysis_step)

        # Step 2: Gather evidence from retrieved entries
        evidence_step = self._gather_evidence(context)
        steps.append(evidence_step)

        # Step 3: Cross-reference with memory
        memory_step = self._cross_reference_memory(context)
        steps.append(memory_step)

        # Step 4: Synthesize findings
        synthesis_step = self._synthesize_findings(context, steps)
        steps.append(synthesis_step)

        # Step 5: Generate conclusion
        conclusion_step = self._generate_conclusion(context, steps)
        steps.append(conclusion_step)

        # Calculate overall confidence
        confidence = self._calculate_chain_confidence(steps)

        # Build chain
        chain = ReasoningChain(
            steps=steps,
            conclusion=conclusion_step.thought,
            confidence=confidence,
            sources=self._extract_sources(context),
        )

        return chain

    def _analyze_query(self, context: ReasoningContext) -> ReasoningStep:
        """Analyze the user query to understand requirements."""
        query = context.user_query
        intent = context.intent

        thoughts = []
        evidence = []

        if intent:
            thoughts.append(f"Detected intent: {intent.type.value}")
            if intent.keywords:
                thoughts.append(f"Key concepts: {', '.join(intent.keywords[:5])}")
            if intent.entities:
                thoughts.append(f"Entities found: {list(intent.entities.keys())}")

        # Analyze query complexity
        word_count = len(query.split())
        if word_count < 5:
            thoughts.append("Simple query - direct answer likely sufficient")
        elif word_count < 20:
            thoughts.append("Moderate complexity - may need multi-step reasoning")
        else:
            thoughts.append("Complex query - comprehensive analysis needed")

        return ReasoningStep(
            thought=" | ".join(thoughts) if thoughts else "Analyzing query",
            evidence=evidence,
            confidence=0.7,
            step_type="inference",
        )

    def _gather_evidence(self, context: ReasoningContext) -> ReasoningStep:
        """Gather and evaluate evidence from retrieved entries."""
        entries = context.retrieved_entries
        thoughts = []
        evidence = []
        source_ids = []

        if not entries:
            thoughts.append("No relevant entries retrieved")
            return ReasoningStep(
                thought="No evidence found in knowledge base",
                evidence=[],
                confidence=0.2,
                step_type="retrieval",
            )

        thoughts.append(f"Found {len(entries)} relevant entries")

        # Analyze entry quality
        for entry in entries[:5]:  # Limit to top 5
            content = getattr(entry, "content", str(entry))
            entry_id = getattr(entry, "id", "unknown")
            source_ids.append(entry_id)

            # Truncate for evidence
            evidence_text = content[:200] + "..." if len(content) > 200 else content
            evidence.append(evidence_text)

        # Calculate evidence confidence
        confidence = min(1.0, len(entries) * 0.15)

        return ReasoningStep(
            thought=" | ".join(thoughts),
            evidence=evidence,
            source_ids=source_ids,
            confidence=confidence,
            step_type="retrieval",
        )

    def _cross_reference_memory(self, context: ReasoningContext) -> ReasoningStep:
        """Cross-reference with memory entries."""
        memories = context.memory_entries
        thoughts = []

        if not memories:
            thoughts.append("No relevant memories found")
            confidence = 0.3
        else:
            thoughts.append(f"Found {len(memories)} relevant memories")
            confidence = min(1.0, len(memories) * 0.2)

        return ReasoningStep(
            thought=" | ".join(thoughts),
            evidence=[],
            confidence=confidence,
            step_type="retrieval",
        )

    def _synthesize_findings(
        self,
        context: ReasoningContext,
        previous_steps: list[ReasoningStep],
    ) -> ReasoningStep:
        """Synthesize findings from previous reasoning steps."""
        all_evidence = []
        for step in previous_steps:
            all_evidence.extend(step.evidence)

        # Count evidence sources
        unique_sources = set()
        for step in previous_steps:
            unique_sources.update(step.source_ids)

        thoughts = [
            f"Synthesized {len(all_evidence)} pieces of evidence",
            f"From {len(unique_sources)} unique sources",
        ]

        # Analyze evidence consistency
        if len(all_evidence) > 1:
            thoughts.append("Multiple evidence points support the conclusion")
            confidence = 0.7
        elif len(all_evidence) == 1:
            thoughts.append("Single evidence source - limited confidence")
            confidence = 0.5
        else:
            thoughts.append("No direct evidence - relying on reasoning")
            confidence = 0.3

        return ReasoningStep(
            thought=" | ".join(thoughts),
            evidence=all_evidence[:10],  # Limit evidence
            source_ids=list(unique_sources),
            confidence=confidence,
            step_type="synthesis",
        )

    def _generate_conclusion(
        self,
        context: ReasoningContext,
        previous_steps: list[ReasoningStep],
    ) -> ReasoningStep:
        """Generate final conclusion from reasoning chain."""
        # Calculate average confidence from previous steps
        if previous_steps:
            avg_confidence = sum(s.confidence for s in previous_steps) / len(previous_steps)
        else:
            avg_confidence = 0.3

        # Build conclusion
        query = context.user_query
        evidence_count = sum(len(s.evidence) for s in previous_steps)

        thoughts = [
            f"Answering: {query[:100]}",
            f"Based on {evidence_count} evidence points",
            f"Overall confidence: {avg_confidence:.2f}",
        ]

        return ReasoningStep(
            thought=" | ".join(thoughts),
            evidence=[],
            confidence=avg_confidence,
            step_type="inference",
        )

    def _calculate_chain_confidence(self, steps: list[ReasoningStep]) -> float:
        """Calculate overall confidence for the reasoning chain."""
        if not steps:
            return 0.0

        # Weighted average with recency bias
        total_weight = 0.0
        weighted_sum = 0.0
        for i, step in enumerate(steps):
            weight = 1.0 + (i * 0.1)  # Later steps have more weight
            weighted_sum += step.confidence * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _extract_sources(self, context: ReasoningContext) -> list[str]:
        """Extract unique source IDs from context."""
        sources = set()
        for entry in context.retrieved_entries:
            entry_id = getattr(entry, "id", None)
            if entry_id:
                sources.add(entry_id)
        return list(sources)
