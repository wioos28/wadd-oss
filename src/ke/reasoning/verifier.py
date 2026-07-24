"""Verifier - Verify reasoning consistency and quality."""

from __future__ import annotations

import re
from typing import Any

from ke.reasoning.models import (
    ConfidenceScore,
    ReasoningChain,
    ReasoningStep,
    VerificationResult,
)


class Verifier:
    """Verify the quality and consistency of reasoning outputs."""

    def __init__(self, min_confidence: float = 0.5):
        self.min_confidence = min_confidence

    def verify(
        self,
        chain: ReasoningChain,
        query: str,
        answer: str,
    ) -> VerificationResult:
        """Verify the reasoning chain and answer."""
        logical_errors = self._check_logical_consistency(chain)
        conflicting = self._check_conflicting_facts(chain)
        missing = self._check_missing_information(chain, query)
        duplicates = self._check_duplicate_facts(chain)

        # Calculate confidence adjustment
        adjustment = 0.0
        if logical_errors:
            adjustment -= 0.2 * len(logical_errors)
        if conflicting:
            adjustment -= 0.15 * len(conflicting)
        if missing:
            adjustment -= 0.1 * len(missing)
        if duplicates:
            adjustment -= 0.05 * len(duplicates)

        # Determine consistency
        is_consistent = len(logical_errors) == 0 and len(conflicting) == 0

        # Generate recommendations
        recommendations = self._generate_recommendations(
            logical_errors, conflicting, missing, chain
        )

        return VerificationResult(
            is_consistent=is_consistent,
            logical_errors=logical_errors,
            conflicting_facts=conflicting,
            missing_info=missing,
            duplicate_facts=duplicates,
            confidence_adjustment=max(-0.5, adjustment),
            recommendations=recommendations,
        )

    def _check_logical_consistency(self, chain: ReasoningChain) -> list[str]:
        """Check for logical errors in the reasoning chain."""
        errors = []

        # Check for contradictory statements
        statements = [step.thought for step in chain.steps]

        # Simple contradiction patterns
        contradiction_patterns = [
            (r"\b(is|are|was|were)\b.*\b(not|never|no)\b", r"\b(is|are|was|were)\b.*(?!not|never|no)"),
        ]

        for i, stmt in enumerate(statements):
            for j, other in enumerate(statements):
                if i >= j:
                    continue
                # Check if statements directly contradict
                # This is a simplified check
                if self._statements_contradict(stmt, other):
                    errors.append(f"Potential contradiction between steps {i+1} and {j+1}")

        # Check confidence progression
        confidences = [step.confidence for step in chain.steps]
        if len(confidences) > 1:
            # Large confidence drops may indicate issues
            for i in range(1, len(confidences)):
                if confidences[i-1] - confidences[i] > 0.3:
                    errors.append(f"Large confidence drop between steps {i} and {i+1}")

        return errors

    def _check_conflicting_facts(self, chain: ReasoningChain) -> list[str]:
        """Check for conflicting facts in evidence."""
        conflicts = []

        # Collect all evidence
        all_evidence = []
        for step in chain.steps:
            all_evidence.extend(step.evidence)

        # Simple conflict detection
        # Look for negation patterns
        positive_facts = []
        negative_facts = []

        for evidence in all_evidence:
            if re.search(r"\b(not|never|no|isn't|aren't|wasn't|weren't)\b", evidence.lower()):
                negative_facts.append(evidence)
            else:
                positive_facts.append(evidence)

        # Check if same topic has both positive and negative
        # Simplified: just flag if we have many of both
        if len(positive_facts) > 2 and len(negative_facts) > 2:
            conflicts.append("Mixed positive and negative evidence detected")

        return conflicts

    def _check_missing_information(self, chain: ReasoningChain, query: str) -> list[str]:
        """Check for missing information needed to answer the query."""
        missing = []

        # Check if we have any evidence
        total_evidence = sum(len(step.evidence) for step in chain.steps)
        if total_evidence == 0:
            missing.append("No evidence retrieved to support answer")

        # Check if query is addressed
        query_words = set(query.lower().split())
        all_evidence_text = " ".join(
            e for step in chain.steps for e in step.evidence
        ).lower()

        # Check if key query terms appear in evidence
        key_terms = [w for w in query_words if len(w) > 3]
        missing_terms = [t for t in key_terms if t not in all_evidence_text]

        if len(missing_terms) > len(key_terms) * 0.5:
            missing.append(f"Key terms not found in evidence: {', '.join(missing_terms[:3])}")

        # Check for low confidence steps
        for i, step in enumerate(chain.steps):
            if step.confidence < 0.3:
                missing.append(f"Step {i+1} has very low confidence ({step.confidence:.2f})")

        return missing

    def _check_duplicate_facts(self, chain: ReasoningChain) -> list[str]:
        """Check for duplicate facts in the reasoning chain."""
        duplicates = []

        # Collect all evidence
        all_evidence = []
        for step in chain.steps:
            all_evidence.extend(step.evidence)

        # Check for exact duplicates
        seen = set()
        for evidence in all_evidence:
            normalized = evidence.strip().lower()
            if normalized in seen:
                duplicates.append(f"Duplicate fact: {evidence[:50]}...")
            seen.add(normalized)

        return duplicates

    def _statements_contradict(self, stmt1: str, stmt2: str) -> bool:
        """Check if two statements potentially contradict each other."""
        # Simplified contradiction check
        # Look for X vs not X patterns
        words1 = set(stmt1.lower().split())
        words2 = set(stmt2.lower().split())

        negations = {"not", "never", "no", "isn't", "aren't", "wasn't", "weren't", "won't", "can't"}

        has_neg1 = bool(words1 & negations)
        has_neg2 = bool(words2 & negations)

        # If one has negation and they share most other words
        if has_neg1 != has_neg2:
            shared = words1 & words2 - negations
            if len(shared) > min(len(words1), len(words2)) * 0.5:
                return True

        return False

    def _generate_recommendations(
        self,
        logical_errors: list[str],
        conflicting: list[str],
        missing: list[str],
        chain: ReasoningChain,
    ) -> list[str]:
        """Generate recommendations for improving the answer."""
        recommendations = []

        if logical_errors:
            recommendations.append("Review logical flow and remove contradictions")

        if conflicting:
            recommendations.append("Clarify conflicting information or present multiple perspectives")

        if missing:
            recommendations.append("Consider gathering additional evidence")

        if chain.confidence < self.min_confidence:
            recommendations.append("Overall confidence is low - consider expressing uncertainty")

        if len(chain.steps) < 3:
            recommendations.append("Reasoning chain is short - consider adding more analysis steps")

        return recommendations
