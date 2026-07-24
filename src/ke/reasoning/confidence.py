"""Confidence scoring for reasoning results."""

from __future__ import annotations

from typing import Any

from ke.reasoning.models import ConfidenceScore, ReasoningChain, ReasoningStep


class ConfidenceScorer:
    """Calculate confidence scores for reasoning results."""

    # Weights for different confidence factors
    WEIGHTS = {
        "knowledge_quality": 0.25,
        "retrieval_score": 0.25,
        "evidence_count": 0.20,
        "reasoning_quality": 0.30,
    }

    def __init__(self, min_confidence: float = 0.3):
        self.min_confidence = min_confidence

    def calculate(
        self,
        chain: ReasoningChain,
        retrieval_score: float = 0.0,
        knowledge_quality: float = 0.0,
    ) -> ConfidenceScore:
        """Calculate overall confidence score."""
        # Calculate individual factors
        knowledge_q = self._assess_knowledge_quality(chain, knowledge_quality)
        retrieval_s = self._assess_retrieval_score(retrieval_score)
        evidence_c = self._assess_evidence_count(chain)
        reasoning_q = self._assess_reasoning_quality(chain)

        # Weighted overall score
        overall = (
            knowledge_q * self.WEIGHTS["knowledge_quality"]
            + retrieval_s * self.WEIGHTS["retrieval_score"]
            + evidence_c * self.WEIGHTS["evidence_count"]
            + reasoning_q * self.WEIGHTS["reasoning_quality"]
        )

        # Ensure minimum confidence
        overall = max(self.min_confidence, min(1.0, overall))

        # Generate factor explanations
        factors = self._generate_factors(
            knowledge_q, retrieval_s, evidence_c, reasoning_q
        )

        return ConfidenceScore(
            overall=overall,
            knowledge_quality=knowledge_q,
            retrieval_score=retrieval_s,
            evidence_count=evidence_c,
            reasoning_quality=reasoning_q,
            factors=factors,
        )

    def _assess_knowledge_quality(
        self, chain: ReasoningChain, provided_score: float
    ) -> float:
        """Assess the quality of knowledge used."""
        if provided_score > 0:
            return provided_score

        # Base assessment on chain confidence
        if chain.confidence > 0.8:
            return 0.9
        elif chain.confidence > 0.6:
            return 0.7
        elif chain.confidence > 0.4:
            return 0.5
        return 0.3

    def _assess_retrieval_score(self, provided_score: float) -> float:
        """Assess retrieval quality."""
        if provided_score > 0:
            return min(1.0, provided_score)

        # Default based on whether we have sources
        return 0.5

    def _assess_evidence_count(self, chain: ReasoningChain) -> float:
        """Assess confidence based on evidence count."""
        total_evidence = sum(len(step.evidence) for step in chain.steps)

        if total_evidence >= 10:
            return 1.0
        elif total_evidence >= 5:
            return 0.8
        elif total_evidence >= 3:
            return 0.6
        elif total_evidence >= 1:
            return 0.4
        return 0.2

    def _assess_reasoning_quality(self, chain: ReasoningChain) -> float:
        """Assess the quality of the reasoning process."""
        if not chain.steps:
            return 0.2

        # Check step progression
        confidences = [step.confidence for step in chain.steps]

        # Good reasoning has stable or improving confidence
        if len(confidences) > 1:
            trend = confidences[-1] - confidences[0]
            if trend > 0:
                # Confidence improved
                base_score = 0.7
            elif trend > -0.2:
                # Stable
                base_score = 0.6
            else:
                # Declining - may indicate issues
                base_score = 0.4
        else:
            base_score = 0.5

        # Bonus for multiple step types
        step_types = set(step.step_type for step in chain.steps)
        if len(step_types) >= 3:
            base_score = min(1.0, base_score + 0.1)

        # Penalty for very short chains
        if len(chain.steps) < 3:
            base_score = max(0.3, base_score - 0.1)

        return base_score

    def _generate_factors(
        self,
        knowledge_q: float,
        retrieval_s: float,
        evidence_c: float,
        reasoning_q: float,
    ) -> list[str]:
        """Generate human-readable factor explanations."""
        factors = []

        if knowledge_q > 0.7:
            factors.append("High-quality knowledge sources")
        elif knowledge_q < 0.4:
            factors.append("Knowledge quality is low")

        if retrieval_s > 0.7:
            factors.append("Effective retrieval")
        elif retrieval_s < 0.4:
            factors.append("Retrieval quality is limited")

        if evidence_c > 0.7:
            factors.append("Strong evidence base")
        elif evidence_c < 0.4:
            factors.append("Limited evidence available")

        if reasoning_q > 0.7:
            factors.append("Solid reasoning process")
        elif reasoning_q < 0.4:
            factors.append("Reasoning quality needs improvement")

        return factors

    def adjust_confidence(
        self,
        base_confidence: float,
        adjustments: list[float],
    ) -> float:
        """Apply adjustments to a base confidence score."""
        adjusted = base_confidence
        for adj in adjustments:
            adjusted += adj
        return max(0.0, min(1.0, adjusted))
