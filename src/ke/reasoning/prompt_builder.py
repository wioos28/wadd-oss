"""Prompt Builder - Construct prompts for reasoning components."""

from __future__ import annotations

from typing import Any

from ke.reasoning.models import (
    ExecutionPlan,
    Intent,
    IntentType,
    PlanStep,
    ReasoningChain,
    ReasoningContext,
)


class PromptBuilder:
    """Build prompts for various reasoning operations."""

    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length

    def build_reasoning_prompt(
        self,
        context: ReasoningContext,
        plan: ExecutionPlan | None = None,
    ) -> str:
        """Build a prompt for the reasoning step."""
        parts = []

        # System context
        parts.append("You are a knowledge-reasoning AI assistant.")
        parts.append("Analyze the query and evidence to provide a well-reasoned answer.")
        parts.append("")

        # Query
        parts.append(f"## User Query\n{context.user_query}")

        # Intent
        if context.intent:
            parts.append(f"\n## Detected Intent\nType: {context.intent.type.value}")
            if context.intent.keywords:
                parts.append(f"Keywords: {', '.join(context.intent.keywords[:5])}")

        # Retrieved evidence
        if context.retrieved_entries:
            parts.append("\n## Retrieved Evidence")
            for i, entry in enumerate(context.retrieved_entries[:5], 1):
                content = getattr(entry, "content", str(entry))
                entry_id = getattr(entry, "id", f"entry_{i}")
                truncated = content[:300] + "..." if len(content) > 300 else content
                parts.append(f"\n### Evidence {i} (ID: {entry_id})\n{truncated}")

        # Memory context
        if context.memory_entries:
            parts.append("\n## Relevant Memories")
            for i, mem in enumerate(context.memory_entries[:3], 1):
                content = getattr(mem, "content", str(mem))
                truncated = content[:200] + "..." if len(content) > 200 else content
                parts.append(f"\n### Memory {i}\n{truncated}")

        # Plan steps
        if plan:
            parts.append("\n## Execution Plan")
            parts.append(f"Goal: {plan.goal}")
            parts.append("Steps:")
            for step in plan.steps:
                status_icon = "✓" if step.status == "completed" else "○"
                parts.append(f"  {status_icon} {step.description}")

        # Instructions
        parts.append("\n## Instructions")
        parts.append("1. Analyze the query and evidence carefully")
        parts.append("2. Identify key facts and relationships")
        parts.append("3. Synthesize a comprehensive answer")
        parts.append("4. Note any uncertainties or gaps")
        parts.append("5. Provide confidence level for your answer")

        return "\n".join(parts)

    def build_verification_prompt(
        self,
        query: str,
        answer: str,
        chain: ReasoningChain,
    ) -> str:
        """Build a prompt for verification."""
        parts = []

        parts.append("Verify the following answer for consistency and completeness.")
        parts.append("")

        parts.append(f"## Original Query\n{query}")

        parts.append(f"\n## Proposed Answer\n{answer}")

        parts.append("\n## Reasoning Chain")
        for i, step in enumerate(chain.steps, 1):
            parts.append(f"\n### Step {i}: {step.step_type}")
            parts.append(f"Thought: {step.thought}")
            if step.evidence:
                parts.append(f"Evidence: {len(step.evidence)} items")
            parts.append(f"Confidence: {step.confidence:.2f}")

        parts.append("\n## Verification Checklist")
        parts.append("- [ ] Answer directly addresses the query")
        parts.append("- [ ] All claims are supported by evidence")
        parts.append("- [ ] No logical contradictions")
        parts.append("- [ ] No conflicting information")
        parts.append("- [ ] Confidence level is appropriate")

        parts.append("\nProvide your verification result with:")
        parts.append("1. Is the answer consistent? (yes/no)")
        parts.append("2. Any logical errors found")
        parts.append("3. Any conflicting facts")
        parts.append("4. Any missing information")
        parts.append("5. Confidence adjustment recommendation")

        return "\n".join(parts)

    def build_reflection_prompt(
        self,
        query: str,
        answer: str,
        chain: ReasoningChain,
    ) -> str:
        """Build a prompt for reflection."""
        parts = []

        parts.append("Reflect on this completed reasoning task.")
        parts.append("")

        parts.append(f"## Query\n{query}")
        parts.append(f"\n## Answer\n{answer}")

        parts.append("\n## Reasoning Summary")
        parts.append(f"Steps completed: {len(chain.steps)}")
        parts.append(f"Overall confidence: {chain.confidence:.2f}")
        parts.append(f"Sources used: {len(chain.sources)}")

        parts.append("\n## Reflection Questions")
        parts.append("1. What worked well in this reasoning process?")
        parts.append("2. What could be improved?")
        parts.append("3. What lessons can be applied to future tasks?")
        parts.append("4. Is this knowledge reusable?")
        parts.append("5. Should this be stored for future reference?")

        return "\n".join(parts)

    def build_intent_detection_prompt(self, text: str) -> str:
        """Build a prompt for intent detection."""
        parts = []

        parts.append("Classify the user's intent from the following input.")
        parts.append("")
        parts.append(f"## User Input\n{text}")
        parts.append("")
        parts.append("## Intent Categories")
        parts.append("- question: Asking for information")
        parts.append("- command: Requesting an action")
        parts.append("- search: Looking for specific content")
        parts.append("- code: Requesting code or code help")
        parts.append("- memory: Asking about past interactions")
        parts.append("- training: Wanting to learn or practice")
        parts.append("- conversation: General discussion")
        parts.append("- other: Doesn't fit other categories")
        parts.append("")
        parts.append("Provide:")
        parts.append("1. Intent type")
        parts.append("2. Confidence score (0-1)")
        parts.append("3. Key keywords detected")

        return "\n".join(parts)

    def build_plan_prompt(
        self,
        intent: Intent,
        goal: str,
        available_tools: list[str],
    ) -> str:
        """Build a prompt for plan generation."""
        parts = []

        parts.append("Create an execution plan for the following task.")
        parts.append("")
        parts.append(f"## Goal\n{goal}")
        parts.append(f"\n## Detected Intent\n{intent.type.value}")
        if intent.keywords:
            parts.append(f"Keywords: {', '.join(intent.keywords)}")
        parts.append(f"\n## Available Tools\n{', '.join(available_tools) if available_tools else 'None specified'}")
        parts.append("")
        parts.append("## Plan Requirements")
        parts.append("1. Break the goal into clear, actionable steps")
        parts.append("2. Specify inputs and outputs for each step")
        parts.append("3. Define dependencies between steps")
        parts.append("4. Plan for verification")

        return "\n".join(parts)

    def truncate_to_fit(self, prompt: str, reserve: int = 500) -> str:
        """Truncate prompt to fit within token limits."""
        max_length = self.max_context_length - reserve
        if len(prompt) <= max_length:
            return prompt

        # Truncate and add indicator
        return prompt[:max_length] + "\n\n[Context truncated for length]"
