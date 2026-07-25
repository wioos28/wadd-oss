"""Teacher Model - Mimo AI as the expert mentor."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass

from ke.llm.manager import LLMManager


@dataclass
class TeacherFeedback:
    """Feedback from teacher model."""
    score: float  # 0-1 score
    strengths: list[str]
    weaknesses: list[str]
    corrections: list[str]
    methodology: str  # How to think better
    improved_answer: str


class TeacherModel:
    """
    Teacher Model (Mimo AI) - Expert mentor for student learning.

    Uses a powerful LLM (Claude/GPT-4) to:
    1. Evaluate student understanding
    2. Identify knowledge gaps
    3. Provide methodology improvements
    4. Generate better answers for comparison
    """

    def __init__(self, provider: str = "anthropic", model: str | None = None):
        self.llm_manager = LLMManager()
        self.provider = provider
        self.model = model

    async def evaluate(
        self,
        original_data: str,
        student_understanding: str,
    ) -> TeacherFeedback:
        """
        Evaluate student's understanding and provide feedback.

        Args:
            original_data: The original knowledge/data
            student_understanding: What the student understood

        Returns:
            TeacherFeedback with detailed evaluation
        """
        evaluation_prompt = f"""You are Mimo AI, an expert AI architect mentoring a student AI system.

TASK: Evaluate the student's understanding of the following data.

ORIGINAL DATA:
{original_data[:2000]}

STUDENT'S UNDERSTANDING:
{student_understanding}

Provide your evaluation in this EXACT format:

SCORE: [0.0-1.0]

STRENGTHS:
- [strength 1]
- [strength 2]

WEAKNESSES:
- [weakness 1]
- [weakness 2]

CORRECTIONS:
- [correction 1]
- [correction 2]

METHODOLOGY:
[How the student should think about this type of data in the future]

IMPROVED_ANSWER:
[A better, more complete understanding of the data]"""

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": evaluation_prompt},
        ]

        response = await self.llm_manager.stream_chat(
            messages=messages,
            provider=self.provider,
            model=self.model,
            temperature=0.3,  # Low temperature for consistent evaluation
        )

        # Parse response
        full_response = ""
        async for token in response:
            full_response += token

        return self._parse_feedback(full_response)

    async def teach_methodology(
        self,
        topic: str,
        difficulty: str = "intermediate",
    ) -> str:
        """
        Generate a learning methodology for a topic.

        Args:
            topic: The topic to teach
            difficulty: Difficulty level

        Returns:
            Methodology string
        """
        prompt = f"""Create a learning methodology for an AI student learning about: {topic}

Difficulty level: {difficulty}

Include:
1. Key concepts to understand first
2. Common pitfalls to avoid
3. How to connect this to existing knowledge
4. Practice exercises

Keep it concise and actionable."""

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        response = await self.llm_manager.stream_chat(
            messages=messages,
            provider=self.provider,
            model=self.model,
            temperature=0.5,
        )

        full_response = ""
        async for token in response:
            full_response += token

        return full_response

    async def generate_better_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Generate an expert-level answer for comparison.

        Args:
            question: The question to answer
            context: Available context

        Returns:
            Expert answer string
        """
        prompt = f"""Based on the following context, provide an expert-level answer.

CONTEXT:
{context[:2000]}

QUESTION: {question}

Provide a comprehensive, well-structured answer that demonstrates deep understanding."""

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        response = await self.llm_manager.stream_chat(
            messages=messages,
            provider=self.provider,
            model=self.model,
            temperature=0.7,
        )

        full_response = ""
        async for token in response:
            full_response += token

        return full_response

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the teacher model."""
        return """You are Mimo AI, a world-class AI architect and mentor.

Your role is to:
1. Evaluate AI student systems with precision
2. Identify knowledge gaps and logical errors
3. Provide actionable methodology improvements
4. Generate expert-level answers for comparison

You are patient, thorough, and always focus on teaching the PROCESS of thinking, not just the answer.

Format your responses exactly as requested. Be specific and constructive."""

    def _parse_feedback(self, response: str) -> TeacherFeedback:
        """Parse teacher response into structured feedback."""
        lines = response.split("\n")

        score = 0.5
        strengths = []
        weaknesses = []
        corrections = []
        methodology = ""
        improved_answer = ""

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("SCORE:"):
                try:
                    score = float(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    score = 0.5
            elif line.startswith("STRENGTHS:"):
                current_section = "strengths"
            elif line.startswith("WEAKNESSES:"):
                current_section = "weaknesses"
            elif line.startswith("CORRECTIONS:"):
                current_section = "corrections"
            elif line.startswith("METHODOLOGY:"):
                current_section = "methodology"
            elif line.startswith("IMPROVED_ANSWER:"):
                current_section = "improved_answer"
            elif line.startswith("- ") and current_section in ["strengths", "weaknesses", "corrections"]:
                item = line[2:].strip()
                if current_section == "strengths":
                    strengths.append(item)
                elif current_section == "weaknesses":
                    weaknesses.append(item)
                elif current_section == "corrections":
                    corrections.append(item)
            elif current_section == "methodology" and line:
                methodology += line + " "
            elif current_section == "improved_answer" and line:
                improved_answer += line + " "

        return TeacherFeedback(
            score=max(0.0, min(1.0, score)),
            strengths=strengths,
            weaknesses=weaknesses,
            corrections=corrections,
            methodology=methodology.strip(),
            improved_answer=improved_answer.strip(),
        )
