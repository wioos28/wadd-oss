"""Self Learning - Self-questioning, self-exam, and reflection."""

from __future__ import annotations

import random
from datetime import UTC, datetime
from typing import Any

from ke.learning.v2.models import (
    ErrorMemory,
    KnowledgeNode,
    LearningScore,
    SelfExam,
    SelfReflection,
)


class SelfLearner:
    """Self-learning capabilities for WCore X."""

    def __init__(self):
        self._learning_scores: dict[str, LearningScore] = {}
        self._error_memory: list[ErrorMemory] = []
        self._exams: list[SelfExam] = []
        self._reflections: list[SelfReflection] = []

    def generate_questions(
        self, topic: str, content: str, count: int = 20
    ) -> list[dict[str, Any]]:
        """Generate self-questions about a topic."""
        questions = []

        # Generate different types of questions
        question_types = [
            self._generate_what_question,
            self._generate_why_question,
            self._generate_how_question,
            self._generate_when_question,
            self._generate_comparison_question,
            self._generate_exception_question,
            self._generate_optimization_question,
            self._generate_best_practice_question,
            self._generate_common_mistake_question,
            self._generate_real_world_question,
        ]

        for i in range(count):
            q_type = question_types[i % len(question_types)]
            question = q_type(topic, content)
            questions.append(question)

        return questions

    def _generate_what_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a 'what' question."""
        return {
            "type": "what",
            "question": f"What is {topic}?",
            "hint": f"Look for the definition and core concepts of {topic}",
        }

    def _generate_why_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a 'why' question."""
        return {
            "type": "why",
            "question": f"Why is {topic} important?",
            "hint": "Consider its use cases and benefits",
        }

    def _generate_how_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a 'how' question."""
        return {
            "type": "how",
            "question": f"How do you use {topic}?",
            "hint": "Provide step-by-step instructions",
        }

    def _generate_when_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a 'when' question."""
        return {
            "type": "when",
            "question": f"When should you use {topic}?",
            "hint": "Consider appropriate use cases",
        }

    def _generate_comparison_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a comparison question."""
        return {
            "type": "comparison",
            "question": f"What are the alternatives to {topic}?",
            "hint": "Compare different approaches",
        }

    def _generate_exception_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate an exception question."""
        return {
            "type": "exception",
            "question": f"What are the exceptions or edge cases for {topic}?",
            "hint": "Consider unusual scenarios",
        }

    def _generate_optimization_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate an optimization question."""
        return {
            "type": "optimization",
            "question": f"How can {topic} be optimized?",
            "hint": "Consider performance improvements",
        }

    def _generate_best_practice_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a best practice question."""
        return {
            "type": "best_practice",
            "question": f"What are the best practices for {topic}?",
            "hint": "Consider industry standards",
        }

    def _generate_common_mistake_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a common mistake question."""
        return {
            "type": "common_mistake",
            "question": f"What are common mistakes when using {topic}?",
            "hint": "Consider pitfalls and anti-patterns",
        }

    def _generate_real_world_question(self, topic: str, content: str) -> dict[str, Any]:
        """Generate a real-world application question."""
        return {
            "type": "real_world",
            "question": f"Give a real-world example of {topic} in action.",
            "hint": "Provide practical scenarios",
        }

    def create_exam(self, topic: str, content: str, question_count: int = 50) -> SelfExam:
        """Create a self-exam for a topic."""
        questions = []

        # Generate multiple choice questions
        for i in range(question_count):
            q_type = random.choice(["definition", "usage", "best_practice", "error"])

            if q_type == "definition":
                questions.append({
                    "type": "multiple_choice",
                    "question": f"Question {i+1}: What is the primary purpose of {topic}?",
                    "options": [
                        "To perform a specific function",
                        "To optimize performance",
                        "To handle errors",
                        "To manage memory",
                    ],
                    "correct": 0,
                })
            elif q_type == "usage":
                questions.append({
                    "type": "multiple_choice",
                    "question": f"Question {i+1}: When should you use {topic}?",
                    "options": [
                        "Always",
                        "Only when needed",
                        "Never",
                        "Only in production",
                    ],
                    "correct": 1,
                })
            elif q_type == "best_practice":
                questions.append({
                    "type": "multiple_choice",
                    "question": f"Question {i+1}: What is a best practice for {topic}?",
                    "options": [
                        "Use it everywhere",
                        "Follow documentation",
                        "Ignore warnings",
                        "Skip testing",
                    ],
                    "correct": 1,
                })
            else:
                questions.append({
                    "type": "multiple_choice",
                    "question": f"Question {i+1}: What is a common error with {topic}?",
                    "options": [
                        "Using it correctly",
                        "Not handling edge cases",
                        "Following best practices",
                        "Writing tests",
                    ],
                    "correct": 1,
                })

        return SelfExam(
            topic=topic,
            questions=questions,
            answers=[],
        )

    def grade_exam(self, exam: SelfExam, answers: list[int]) -> SelfExam:
        """Grade a self-exam."""
        correct = 0
        for i, answer in enumerate(answers):
            if i < len(exam.questions):
                if answer == exam.questions[i].get("correct"):
                    correct += 1

        exam.answers = [str(a) for a in answers]
        exam.score = (correct / max(len(exam.questions), 1)) * 100
        exam.passed = exam.score >= 95
        exam.completed_at = datetime.now(tz=UTC)

        return exam

    def learn_error(
        self,
        error: str,
        root_cause: str,
        fix: str,
        lessons: list[str] | None = None,
        prevention: list[str] | None = None,
        context: str = "",
    ) -> ErrorMemory:
        """Learn from an error."""
        error_memory = ErrorMemory(
            error=error,
            root_cause=root_cause,
            fix=fix,
            lessons=lessons or [],
            prevention=prevention or [],
            context=context,
        )

        self._error_memory.append(error_memory)
        return error_memory

    def reflect(
        self,
        topic: str,
        weak_areas: list[str],
        reasons: list[str],
    ) -> SelfReflection:
        """Generate self-reflection."""
        study_plan = []

        for area in weak_areas:
            study_plan.append(f"Review {area}")
            study_plan.append(f"Practice exercises on {area}")
            study_plan.append(f"Create examples for {area}")

        # Generate questions for self-testing
        questions = []
        for area in weak_areas:
            questions.append({
                "topic": area,
                "question": f"What did I struggle with in {area}?",
                "action": "Review and practice more",
            })

        reflection = SelfReflection(
            weak_areas=weak_areas,
            reasons=reasons,
            study_plan=study_plan,
            questions_generated=questions,
        )

        self._reflections.append(reflection)
        return reflection

    def update_learning_score(
        self,
        topic: str,
        score_delta: float = 1.0,
        entries_learned: int = 0,
        exercises_completed: int = 0,
        tests_passed: int = 0,
        errors_learned: int = 0,
    ) -> LearningScore:
        """Update learning score for a topic."""
        if topic not in self._learning_scores:
            self._learning_scores[topic] = LearningScore(topic=topic)

        score = self._learning_scores[topic]
        score.score = min(100.0, max(0.0, score.score + score_delta))
        score.entries_learned += entries_learned
        score.exercises_completed += exercises_completed
        score.tests_passed += tests_passed
        score.errors_learned += errors_learned
        score.last_studied = datetime.now(tz=UTC)

        # Update level based on score
        if score.score >= 90:
            score.level = "expert"
        elif score.score >= 70:
            score.level = "advanced"
        elif score.score >= 40:
            score.level = "intermediate"
        else:
            score.level = "beginner"

        return score

    def get_learning_scores(self) -> dict[str, LearningScore]:
        """Get all learning scores."""
        return self._learning_scores.copy()

    def get_error_memory(self) -> list[ErrorMemory]:
        """Get all error memories."""
        return self._error_memory.copy()

    def get_reflections(self) -> list[SelfReflection]:
        """Get all reflections."""
        return self._reflections.copy()

    def get_weak_areas(self) -> list[str]:
        """Get topics with low scores."""
        weak = []
        for topic, score in self._learning_scores.items():
            if score.score < 50:
                weak.append(topic)
        return weak

    def get_next_study_topics(self) -> list[str]:
        """Get topics to study next."""
        weak = self.get_weak_areas()
        if weak:
            return weak

        # If no weak areas, suggest new topics
        return ["Docker", "PostgreSQL", "React", "TypeScript"]
