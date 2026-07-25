"""Feedback Processor - Process and integrate learning feedback."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass
from datetime import datetime

from ke.meta_learning.teacher import TeacherFeedback
from ke.meta_learning.student import StudentResponse


@dataclass
class LearningExperience:
    """A complete learning experience record."""
    lesson_id: int
    original_data: str
    student_response: StudentResponse
    teacher_feedback: TeacherFeedback
    improved_understanding: str
    score_before: float
    score_after: float
    learning_gain: float
    timestamp: datetime
    metadata: dict[str, Any] | None = None


class FeedbackProcessor:
    """
    Process and integrate learning feedback.

    Responsibilities:
    1. Calculate learning gains
    2. Identify patterns in feedback
    3. Generate learning reports
    4. Track progress over time
    """

    def __init__(self):
        self.experiences: list[LearningExperience] = []
        self.total_score_before: float = 0.0
        self.total_score_after: float = 0.0

    def process_experience(
        self,
        lesson_id: int,
        original_data: str,
        student_response: StudentResponse,
        teacher_feedback: TeacherFeedback,
        improved_understanding: str,
    ) -> LearningExperience:
        """
        Process a complete learning experience.

        Returns:
            LearningExperience with calculated metrics
        """
        score_before = student_response.confidence
        score_after = teacher_feedback.score
        learning_gain = score_after - score_before

        experience = LearningExperience(
            lesson_id=lesson_id,
            original_data=original_data[:500],  # Truncate for storage
            student_response=student_response,
            teacher_feedback=teacher_feedback,
            improved_understanding=improved_understanding[:500],
            score_before=score_before,
            score_after=score_after,
            learning_gain=learning_gain,
            timestamp=datetime.now(),
        )

        self.experiences.append(experience)
        self.total_score_before += score_before
        self.total_score_after += score_after

        return experience

    def get_learning_progress(self) -> dict[str, Any]:
        """Get overall learning progress."""
        if not self.experiences:
            return {
                "total_lessons": 0,
                "average_score_before": 0,
                "average_score_after": 0,
                "average_learning_gain": 0,
                "improvement_rate": 0,
            }

        total_lessons = len(self.experiences)
        avg_before = self.total_score_before / total_lessons
        avg_after = self.total_score_after / total_lessons
        avg_gain = avg_after - avg_before
        improvement_rate = (avg_gain / max(avg_before, 0.01)) * 100

        return {
            "total_lessons": total_lessons,
            "average_score_before": round(avg_before, 3),
            "average_score_after": round(avg_after, 3),
            "average_learning_gain": round(avg_gain, 3),
            "improvement_rate": round(improvement_rate, 1),
        }

    def get_weak_areas(self) -> list[str]:
        """Identify areas where the student consistently struggles."""
        weakness_count: dict[str, int] = {}

        for exp in self.experiences:
            for weakness in exp.teacher_feedback.weaknesses:
                # Simplify weakness to key phrase
                key = weakness.lower()[:50]
                weakness_count[key] = weakness_count.get(key, 0) + 1

        # Sort by frequency
        sorted_weaknesses = sorted(
            weakness_count.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [w[0] for w in sorted_weaknesses[:5]]

    def get_strong_areas(self) -> list[str]:
        """Identify areas where the student excels."""
        strength_count: dict[str, int] = {}

        for exp in self.experiences:
            for strength in exp.teacher_feedback.strengths:
                key = strength.lower()[:50]
                strength_count[key] = strength_count.get(key, 0) + 1

        sorted_strengths = sorted(
            strength_count.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [s[0] for s in sorted_strengths[:5]]

    def get_methodology_patterns(self) -> list[str]:
        """Extract common methodology patterns from feedback."""
        methodologies = []

        for exp in self.experiences:
            if exp.teacher_feedback.methodology:
                methodologies.append(exp.teacher_feedback.methodology[:200])

        return methodologies[-5:]  # Last 5 methodologies

    def generate_report(self) -> str:
        """Generate a learning progress report."""
        progress = self.get_learning_progress()
        weak_areas = self.get_weak_areas()
        strong_areas = self.get_strong_areas()

        report = f"""# Wcore X Learning Report

## Progress Summary
- Total Lessons: {progress['total_lessons']}
- Average Score Before: {progress['average_score_before']:.1%}
- Average Score After: {progress['average_score_after']:.1%}
- Learning Gain: {progress['average_learning_gain']:.1%}
- Improvement Rate: {progress['improvement_rate']:.1f}%

## Strong Areas
"""
        for area in strong_areas:
            report += f"- {area}\n"

        report += "\n## Weak Areas (Focus for Improvement)\n"
        for area in weak_areas:
            report += f"- {area}\n"

        report += "\n## Recent Methodology Insights\n"
        for method in self.get_methodology_patterns():
            report += f"- {method}\n"

        return report

    def to_dict(self) -> dict[str, Any]:
        """Convert processor state to dictionary for persistence."""
        return {
            "total_lessons": len(self.experiences),
            "total_score_before": self.total_score_before,
            "total_score_after": self.total_score_after,
            "experiences": [
                {
                    "lesson_id": exp.lesson_id,
                    "score_before": exp.score_before,
                    "score_after": exp.score_after,
                    "learning_gain": exp.learning_gain,
                    "timestamp": exp.timestamp.isoformat(),
                }
                for exp in self.experiences[-100:]  # Keep last 100
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeedbackProcessor:
        """Create processor from dictionary."""
        processor = cls()
        processor.total_score_before = data.get("total_score_before", 0)
        processor.total_score_after = data.get("total_score_after", 0)
        return processor
