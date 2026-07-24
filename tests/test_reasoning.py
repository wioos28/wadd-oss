"""Tests for the Reasoning Engine."""

import pytest

from ke.reasoning.confidence import ConfidenceScorer
from ke.reasoning.context import ContextBuilder
from ke.reasoning.intent import IntentEngine, IntentType
from ke.reasoning.models import (
    ConfidenceScore,
    ExecutionPlan,
    Intent,
    PlanStep,
    ReasoningChain,
    ReasoningContext,
    ReasoningResult,
    ReasoningStep,
    ReflectionResult,
    VerificationResult,
)
from ke.reasoning.planner import TaskPlanner
from ke.reasoning.prompt_builder import PromptBuilder
from ke.reasoning.reasoner import Reasoner
from ke.reasoning.reflection import Reflector
from ke.reasoning.verifier import Verifier


class TestIntentEngine:
    def setup_method(self):
        self.engine = IntentEngine()

    def test_detect_question(self):
        intent = self.engine.detect("What is machine learning?")
        assert intent.type == IntentType.QUESTION
        assert intent.confidence > 0.3

    def test_detect_command(self):
        intent = self.engine.detect("Run the tests")
        assert intent.type == IntentType.COMMAND

    def test_detect_search(self):
        intent = self.engine.detect("Find all Python files")
        assert intent.type == IntentType.SEARCH_REQUEST

    def test_detect_code(self):
        intent = self.engine.detect("Write a function to sort arrays")
        assert intent.type == IntentType.CODE_REQUEST

    def test_detect_memory(self):
        intent = self.engine.detect("Do you remember our last conversation?")
        assert intent.type == IntentType.MEMORY_REQUEST

    def test_detect_unknown(self):
        intent = self.engine.detect("asdklfjasdf")
        assert intent.type == IntentType.UNKNOWN
        assert intent.confidence < 0.5

    def test_entity_extraction(self):
        intent = self.engine.detect("Open the file /path/to/file.py")
        assert "file_paths" in intent.entities

    def test_batch_detection(self):
        intents = self.engine.detect_batch([
            "What is AI?",
            "Run the script",
            "Find files",
        ])
        assert len(intents) == 3
        assert intents[0].type == IntentType.QUESTION
        assert intents[1].type == IntentType.COMMAND
        assert intents[2].type == IntentType.SEARCH_REQUEST


class TestTaskPlanner:
    def setup_method(self):
        self.planner = TaskPlanner()

    def test_create_plan_for_question(self):
        intent = Intent(type=IntentType.QUESTION, confidence=0.8, raw_input="test")
        plan = self.planner.create_plan(intent, "What is AI?")
        assert plan.goal == "What is AI?"
        assert len(plan.steps) > 0
        assert plan.status == "created"

    def test_create_plan_for_search(self):
        intent = Intent(type=IntentType.SEARCH_REQUEST, confidence=0.8, raw_input="test")
        plan = self.planner.create_plan(intent, "Find Python files")
        assert len(plan.steps) >= 3

    def test_update_step_status(self):
        intent = Intent(type=IntentType.QUESTION, confidence=0.8, raw_input="test")
        plan = self.planner.create_plan(intent, "Test goal")
        first_step = plan.steps[0]

        plan = self.planner.update_step_status(plan, first_step.id, "completed")
        assert plan.steps[0].status == "completed"

    def test_get_next_step(self):
        intent = Intent(type=IntentType.QUESTION, confidence=0.8, raw_input="test")
        plan = self.planner.create_plan(intent, "Test goal")

        next_step = self.planner.get_next_step(plan)
        assert next_step is not None
        assert next_step.status == "pending"

        # Complete first step
        plan = self.planner.update_step_status(plan, plan.steps[0].id, "completed")
        next_step = self.planner.get_next_step(plan)
        assert next_step is not None


class TestReasoner:
    def setup_method(self):
        self.reasoner = Reasoner()

    def test_reason_basic(self):
        context = ReasoningContext(
            user_query="What is Python?",
            retrieved_entries=[],
        )
        chain = self.reasoner.reason(context)
        assert chain is not None
        assert len(chain.steps) > 0
        assert chain.confidence >= 0.0

    def test_reason_with_evidence(self):
        # Create mock entries
        class MockEntry:
            def __init__(self, id: str, content: str):
                self.id = id
                self.content = content

        entries = [
            MockEntry("1", "Python is a programming language"),
            MockEntry("2", "Python is known for its simplicity"),
        ]

        context = ReasoningContext(
            user_query="What is Python?",
            retrieved_entries=entries,
        )
        chain = self.reasoner.reason(context)
        assert chain.confidence > 0.3
        assert len(chain.sources) > 0


class TestVerifier:
    def setup_method(self):
        self.verifier = Verifier()

    def test_verify_consistent(self):
        chain = ReasoningChain(
            steps=[
                ReasoningStep(thought="Test step", confidence=0.8),
            ],
            conclusion="Test conclusion",
            confidence=0.7,
        )
        result = self.verifier.verify(chain, "Test query", "Test answer")
        assert result.is_consistent is True

    def test_verify_with_low_confidence(self):
        chain = ReasoningChain(
            steps=[
                ReasoningStep(thought="Uncertain step", confidence=0.2),
            ],
            conclusion="Uncertain conclusion",
            confidence=0.2,
        )
        result = self.verifier.verify(chain, "Test query", "Test answer")
        assert result.confidence_adjustment < 0


class TestReflector:
    def setup_method(self):
        self.reflector = Reflector()

    def test_reflect_basic(self):
        result = ReasoningResult(
            query="Test query",
            answer="Test answer",
            reasoning_chain=ReasoningChain(
                steps=[ReasoningStep(thought="Step", confidence=0.7)],
                confidence=0.7,
            ),
            confidence=ConfidenceScore(
                overall=0.7,
                knowledge_quality=0.7,
                retrieval_score=0.7,
                evidence_count=3,
                reasoning_quality=0.7,
            ),
        )
        reflection = self.reflector.reflect(result)
        assert reflection.answer_quality >= 0.0
        assert reflection.summary != ""


class TestConfidenceScorer:
    def setup_method(self):
        self.scorer = ConfidenceScorer()

    def test_calculate_confidence(self):
        chain = ReasoningChain(
            steps=[
                ReasoningStep(thought="Step 1", evidence=["e1", "e2"], confidence=0.8),
                ReasoningStep(thought="Step 2", evidence=["e3"], confidence=0.7),
            ],
            confidence=0.75,
        )
        score = self.scorer.calculate(chain)
        assert 0.0 <= score.overall <= 1.0
        assert score.evidence_count > 0

    def test_adjust_confidence(self):
        adjusted = self.scorer.adjust_confidence(0.7, [-0.2, 0.1])
        assert adjusted == 0.6


class TestContextBuilder:
    def setup_method(self):
        self.builder = ContextBuilder()

    def test_build_context(self):
        context = self.builder.build(
            query="Test query",
            retrieved_entries=[],
        )
        assert context.user_query == "Test query"
        assert len(context.retrieved_entries) == 0

    def test_add_entries(self):
        self.builder.build(query="Test")
        self.builder.add_retrieved_entries(["entry1", "entry2"])
        context = self.builder.get_context()
        assert len(context.retrieved_entries) == 2

    def test_get_summary(self):
        self.builder.build(query="Test query")
        summary = self.builder.get_summary()
        assert summary["query"] == "Test query"


class TestPromptBuilder:
    def setup_method(self):
        self.builder = PromptBuilder()

    def test_build_reasoning_prompt(self):
        context = ReasoningContext(user_query="What is AI?")
        prompt = self.builder.build_reasoning_prompt(context)
        assert "What is AI?" in prompt
        assert "User Query" in prompt

    def test_build_verification_prompt(self):
        chain = ReasoningChain(
            steps=[ReasoningStep(thought="Test", confidence=0.7)],
            confidence=0.7,
        )
        prompt = self.builder.build_verification_prompt("Query", "Answer", chain)
        assert "Verify" in prompt

    def test_truncate_to_fit(self):
        long_prompt = "x" * 5000
        truncated = self.builder.truncate_to_fit(long_prompt, reserve=500)
        assert len(truncated) < 5000
        assert "truncated" in truncated
