"""Planner - Decompose tasks into executable steps."""

from __future__ import annotations

from typing import Any

from ke.reasoning.models import (
    ExecutionPlan,
    Intent,
    IntentType,
    PlanStep,
)


class TaskPlanner:
    """Break down user goals into structured execution plans."""

    # Default steps per intent type
    DEFAULT_STEPS: dict[IntentType, list[dict[str, str]]] = {
        IntentType.QUESTION: [
            {"description": "Parse and understand the question", "action": "parse_query"},
            {"description": "Identify key concepts and keywords", "action": "extract_concepts"},
            {"description": "Search knowledge base for relevant information", "action": "retrieve_knowledge"},
            {"description": "Synthesize answer from retrieved evidence", "action": "synthesize_answer"},
            {"description": "Verify answer consistency and completeness", "action": "verify_answer"},
        ],
        IntentType.SEARCH_REQUEST: [
            {"description": "Parse search query", "action": "parse_query"},
            {"description": "Extract search keywords and filters", "action": "extract_keywords"},
            {"description": "Execute multi-mode search", "action": "search_knowledge"},
            {"description": "Rank and filter results", "action": "rank_results"},
            {"description": "Format and present results", "action": "format_results"},
        ],
        IntentType.CODE_REQUEST: [
            {"description": "Understand code requirements", "action": "parse_requirements"},
            {"description": "Search for similar code patterns", "action": "search_code"},
            {"description": "Generate code solution", "action": "generate_code"},
            {"description": "Validate code syntax and logic", "action": "validate_code"},
            {"description": "Format code with explanation", "action": "format_output"},
        ],
        IntentType.TRAINING_REQUEST: [
            {"description": "Identify training topic and level", "action": "analyze_topic"},
            {"description": "Gather learning materials", "action": "gather_materials"},
            {"description": "Structure learning path", "action": "structure_path"},
            {"description": "Generate exercises and quizzes", "action": "generate_exercises"},
            {"description": "Create learning summary", "action": "create_summary"},
        ],
        IntentType.MEMORY_REQUEST: [
            {"description": "Parse memory query", "action": "parse_memory_query"},
            {"description": "Search memory and session history", "action": "search_memory"},
            {"description": "Retrieve relevant memories", "action": "retrieve_memories"},
            {"description": "Synthesize memory response", "action": "synthesize_memory"},
        ],
        IntentType.COMMAND: [
            {"description": "Parse command intent", "action": "parse_command"},
            {"description": "Validate command parameters", "action": "validate_params"},
            {"description": "Execute command", "action": "execute_command"},
            {"description": "Return execution result", "action": "return_result"},
        ],
    }

    def __init__(self, available_tools: list[str] | None = None):
        self.available_tools = available_tools or []

    def create_plan(
        self,
        intent: Intent,
        goal: str,
        context: dict[str, Any] | None = None,
    ) -> ExecutionPlan:
        """Create an execution plan from an intent and goal."""
        context = context or {}

        # Get default steps for this intent type
        step_defs = self.DEFAULT_STEPS.get(intent.type, self._default_unknown_steps())

        # Create plan steps
        steps = []
        for i, step_def in enumerate(step_defs):
            step = PlanStep(
                description=step_def["description"],
                action=step_def["action"],
                dependencies=[steps[-1].id] if steps else [],
            )
            steps.append(step)

        # Derive requirements from intent
        requirements = self._derive_requirements(intent, context)

        # Create execution plan
        plan = ExecutionPlan(
            goal=goal,
            requirements=requirements,
            available_tools=self.available_tools,
            steps=steps,
            expected_result=self._derive_expected_result(intent),
            verification_plan=self._derive_verification_plan(intent),
        )

        return plan

    def update_step_status(
        self,
        plan: ExecutionPlan,
        step_id: str,
        status: str,
        result: Any = None,
        error: str | None = None,
    ) -> ExecutionPlan:
        """Update the status of a plan step."""
        for step in plan.steps:
            if step.id == step_id:
                step.status = status
                step.result = result
                step.error = error
                break

        # Update plan status
        statuses = [s.status for s in plan.steps]
        if all(s == "completed" for s in statuses):
            plan.status = "completed"
        elif any(s == "failed" for s in statuses):
            plan.status = "failed"
        elif any(s == "in_progress" for s in statuses):
            plan.status = "executing"

        return plan

    def get_next_step(self, plan: ExecutionPlan) -> PlanStep | None:
        """Get the next step to execute based on dependencies."""
        for step in plan.steps:
            if step.status != "pending":
                continue

            # Check if all dependencies are completed
            deps_met = all(
                any(s.id == dep and s.status == "completed" for s in plan.steps)
                for dep in step.dependencies
            )

            if deps_met:
                return step

        return None

    def _derive_requirements(self, intent: Intent, context: dict[str, Any]) -> list[str]:
        """Derive requirements from intent and context."""
        requirements = []

        if intent.type == IntentType.QUESTION:
            requirements.append("Knowledge base access")
            requirements.append("Retrieval capability")
            if intent.keywords:
                requirements.append(f"Content related to: {', '.join(intent.keywords[:3])}")

        elif intent.type == IntentType.SEARCH_REQUEST:
            requirements.append("Search functionality")
            requirements.append("Result ranking")

        elif intent.type == IntentType.CODE_REQUEST:
            requirements.append("Code search")
            requirements.append("Code generation capability")

        elif intent.type == IntentType.MEMORY_REQUEST:
            requirements.append("Memory access")
            requirements.append("Session history")

        elif intent.type == IntentType.TRAINING_REQUEST:
            requirements.append("Knowledge materials")
            requirements.append("Exercise generation")

        return requirements

    def _derive_expected_result(self, intent: Intent) -> str:
        """Derive expected result description."""
        results = {
            IntentType.QUESTION: "A comprehensive answer with supporting evidence",
            IntentType.SEARCH_REQUEST: "Ranked list of relevant results",
            IntentType.CODE_REQUEST: "Code solution with explanation",
            IntentType.TRAINING_REQUEST: "Structured learning material",
            IntentType.MEMORY_REQUEST: "Relevant memory entries",
            IntentType.COMMAND: "Command execution result",
            IntentType.CONVERSATION: "Contextual response",
            IntentType.VISION_REQUEST: "Visual analysis result",
            IntentType.OCR_REQUEST: "Extracted text content",
            IntentType.API_REQUEST: "API response data",
            IntentType.PLUGIN_REQUEST: "Plugin operation result",
        }
        return results.get(intent.type, "Processed response")

    def _derive_verification_plan(self, intent: Intent) -> list[str]:
        """Derive verification steps."""
        base_verifications = [
            "Check logical consistency",
            "Verify confidence score meets threshold",
        ]

        if intent.type == IntentType.QUESTION:
            base_verifications.extend([
                "Verify all parts of question are addressed",
                "Check for conflicting information",
                "Ensure sources are cited",
            ])
        elif intent.type == IntentType.CODE_REQUEST:
            base_verifications.extend([
                "Verify code syntax correctness",
                "Check for common pitfalls",
            ])

        return base_verifications

    def _default_unknown_steps(self) -> list[dict[str, str]]:
        """Default steps for unknown intent types."""
        return [
            {"description": "Analyze input and determine approach", "action": "analyze_input"},
            {"description": "Gather relevant information", "action": "gather_info"},
            {"description": "Process and generate response", "action": "process_response"},
            {"description": "Verify response quality", "action": "verify_response"},
        ]
