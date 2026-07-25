"""Mimo AI Trainer - Orchestrator for Meta-Learning system."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator
from dataclasses import dataclass

from ke.meta_learning.teacher import TeacherModel
from ke.meta_learning.student import StudentModel
from ke.meta_learning.feedback import FeedbackProcessor, LearningExperience


@dataclass
class TrainingConfig:
    """Configuration for training session."""
    teacher_provider: str = "anthropic"
    teacher_model: str | None = None
    student_provider: str = "openai"
    student_model: str | None = None
    dataset_name: str = "teknium/OpenHermes-2.5"
    max_lessons: int = 100
    batch_size: int = 1


class MimoAITrainer:
    """
    Mimo AI Trainer - Meta-Learning Orchestrator.

    Coordinates the learning process between:
    - Teacher (Mimo AI): Expert evaluation and feedback
    - Student (Wcore X): Learning and self-improvement

    Flow:
    1. Student reads learning material
    2. Student extracts understanding
    3. Teacher evaluates understanding
    4. Teacher provides feedback
    5. Student applies feedback
    6. System tracks learning progress
    """

    def __init__(self, config: TrainingConfig | None = None):
        self.config = config or TrainingConfig()

        # Initialize components
        self.teacher = TeacherModel(
            provider=self.config.teacher_provider,
            model=self.config.teacher_model,
        )
        self.student = StudentModel(
            provider=self.config.student_provider,
            model=self.config.student_model,
        )
        self.feedback_processor = FeedbackProcessor()

        # Learning history
        self.knowledge_base: list[str] = []
        self.lesson_count: int = 0

    async def train(
        self,
        dataset_name: str | None = None,
        max_lessons: int | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Run the meta-learning training loop.

        Yields events for monitoring:
        - {"type": "start", "data": {...}}
        - {"type": "lesson_start", "data": {...}}
        - {"type": "student_learning", "data": {...}}
        - {"type": "teacher_feedback", "data": {...}}
        - {"type": "lesson_complete", "data": {...}}
        - {"type": "progress", "data": {...}}
        - {"type": "complete", "data": {...}}
        """
        dataset_name = dataset_name or self.config.dataset_name
        max_lessons = max_lessons or self.config.max_lessons

        yield {"type": "start", "data": {
            "dataset": dataset_name,
            "max_lessons": max_lessons,
            "teacher": self.config.teacher_provider,
            "student": self.config.student_provider,
        }}

        try:
            # Load dataset with streaming
            from datasets import load_dataset

            dataset = load_dataset(dataset_name, split="train", streaming=True)

            async for data_row in self._async_iter(dataset):
                if self.lesson_count >= max_lessons:
                    break

                self.lesson_count += 1

                # Extract learning material
                material = self._extract_material(data_row)
                if not material:
                    continue

                yield {"type": "lesson_start", "data": {
                    "lesson": self.lesson_count,
                    "material_preview": material[:200],
                }}

                # Run learning cycle
                experience = await self._learn_one_lesson(material)

                yield {"type": "lesson_complete", "data": {
                    "lesson": self.lesson_count,
                    "score_before": experience.score_before,
                    "score_after": experience.score_after,
                    "learning_gain": experience.learning_gain,
                }}

                # Yield progress every 10 lessons
                if self.lesson_count % 10 == 0:
                    progress = self.feedback_processor.get_learning_progress()
                    yield {"type": "progress", "data": progress}

        except Exception as e:
            yield {"type": "error", "data": {"error": str(e)}}

        # Final report
        progress = self.feedback_processor.get_learning_progress()
        report = self.feedback_processor.generate_report()

        yield {"type": "complete", "data": {
            "total_lessons": self.lesson_count,
            "progress": progress,
            "report": report,
        }}

    async def _learn_one_lesson(self, material: str) -> LearningExperience:
        """Run one complete learning cycle."""

        # Step 1: Student learns the material
        student_response = await self.student.learn(
            material=material,
            existing_knowledge=self.knowledge_base[-10:],  # Last 10 concepts
        )

        # Step 2: Teacher evaluates
        teacher_feedback = await self.teacher.evaluate(
            original_data=material,
            student_understanding=student_response.understanding,
        )

        # Step 3: Student applies feedback
        improved = await self.student.apply_feedback(
            original_understanding=student_response.understanding,
            teacher_feedback=f"""
            Score: {teacher_feedback.score}
            Weaknesses: {', '.join(teacher_feedback.weaknesses)}
            Methodology: {teacher_feedback.methodology}
            """,
        )

        # Step 4: Process experience
        experience = self.feedback_processor.process_experience(
            lesson_id=self.lesson_count,
            original_data=material,
            student_response=student_response,
            teacher_feedback=teacher_feedback,
            improved_understanding=improved,
        )

        # Step 5: Update knowledge base
        for concept in student_response.key_concepts:
            if concept not in self.knowledge_base:
                self.knowledge_base.append(concept)

        # Keep knowledge base manageable
        if len(self.knowledge_base) > 100:
            self.knowledge_base = self.knowledge_base[-100:]

        return experience

    def _extract_material(self, data_row: Any) -> str | None:
        """Extract learning material from dataset row."""
        try:
            # Handle different dataset formats
            if "conversations" in data_row:
                conversations = data_row["conversations"]
                if isinstance(conversations, list):
                    # Extract user/assistant pairs
                    material_parts = []
                    for conv in conversations:
                        if isinstance(conv, dict):
                            role = conv.get("from", "")
                            content = conv.get("value", "")
                            if content:
                                material_parts.append(f"{role}: {content}")
                    return "\n".join(material_parts[:5])  # First 5 exchanges
                return str(conversations)

            elif "text" in data_row:
                return data_row["text"]

            elif "instruction" in data_row:
                instruction = data_row.get("instruction", "")
                input_text = data_row.get("input", "")
                output = data_row.get("output", "")
                return f"Instruction: {instruction}\nInput: {input_text}\nOutput: {output}"

            else:
                # Try to use the whole row
                return str(data_row)[:2000]

        except Exception:
            return None

    async def _async_iter(self, dataset: Any) -> AsyncGenerator[Any, None]:
        """Convert sync iterator to async."""
        for item in dataset:
            yield item
            await asyncio.sleep(0)  # Allow other tasks to run

    def get_report(self) -> str:
        """Get the learning progress report."""
        return self.feedback_processor.generate_report()

    def get_progress(self) -> dict[str, Any]:
        """Get learning progress metrics."""
        return self.feedback_processor.get_learning_progress()
