"""Student Model - Wcore X as the learning system."""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass

from ke.llm.manager import LLMManager


@dataclass
class StudentResponse:
    """Student's response to learning material."""
    understanding: str
    key_concepts: list[str]
    connections: list[str]  # Connections to existing knowledge
    questions: list[str]  # Questions for clarification
    confidence: float


class StudentModel:
    """
    Student Model (Wcore X) - Learning system.

    Uses a faster/smaller LLM to:
    1. Read and understand learning material
    2. Extract key concepts
    3. Connect to existing knowledge
    4. Generate questions for improvement
    """

    def __init__(self, provider: str = "openai", model: str | None = None):
        self.llm_manager = LLMManager()
        self.provider = provider
        self.model = model

    async def learn(
        self,
        material: str,
        existing_knowledge: list[str] | None = None,
    ) -> StudentResponse:
        """
        Learn from educational material.

        Args:
            material: The learning material
            existing_knowledge: Previously learned concepts

        Returns:
            StudentResponse with understanding
        """
        knowledge_context = ""
        if existing_knowledge:
            knowledge_context = "\n\nPreviously learned:\n" + "\n".join(
                f"- {k}" for k in existing_knowledge[:10]
            )

        learning_prompt = f"""You are Wcore X, an AI learning system.

TASK: Read and understand the following material, then extract key knowledge.

MATERIAL:
{material[:3000]}
{knowledge_context}

Provide your understanding in this EXACT format:

UNDERSTANDING:
[Your understanding of the material in 2-3 paragraphs]

KEY_CONCEPTS:
- [concept 1]
- [concept 2]
- [concept 3]

CONNECTIONS:
- [How this connects to existing knowledge 1]
- [How this connects to existing knowledge 2]

QUESTIONS:
- [Question 1 for clarification]
- [Question 2 for deeper understanding]

CONFIDENCE: [0.0-1.0]"""

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": learning_prompt},
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

        return self._parse_response(full_response)

    async def apply_feedback(
        self,
        original_understanding: str,
        teacher_feedback: str,
    ) -> str:
        """
        Apply teacher feedback to improve understanding.

        Args:
            original_understanding: What the student understood
            teacher_feedback: Feedback from teacher

        Returns:
            Improved understanding string
        """
        improvement_prompt = f"""You are Wcore X, learning from your teacher's feedback.

YOUR ORIGINAL UNDERSTANDING:
{original_understanding}

TEACHER'S FEEDBACK:
{teacher_feedback}

TASK: Revise your understanding based on the feedback.
Focus on:
1. Correcting the weaknesses identified
2. Incorporating the methodology improvements
3. Making connections the teacher pointed out

Provide your IMPROVED UNDERSTANDING:"""

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": improvement_prompt},
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

    async def generate_questions(
        self,
        topic: str,
        depth: str = "intermediate",
    ) -> list[str]:
        """
        Generate questions for self-assessment.

        Args:
            topic: Topic to generate questions about
            depth: Difficulty level

        Returns:
            List of questions
        """
        prompt = f"""Generate 5 questions to test understanding of: {topic}

Difficulty: {depth}

Return ONLY the questions, one per line, starting with "- "."""

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        response = await self.llm_manager.stream_chat(
            messages=messages,
            provider=self.provider,
            model=self.model,
            temperature=0.8,
        )

        full_response = ""
        async for token in response:
            full_response += token

        questions = [
            line[2:].strip()
            for line in full_response.split("\n")
            if line.strip().startswith("- ")
        ]

        return questions[:5]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the student model."""
        return """You are Wcore X, an AI learning system.

Your role is to:
1. Read and understand educational material
2. Extract key concepts and relationships
3. Connect new knowledge to existing understanding
4. Ask thoughtful questions for clarification

Be thorough in your analysis but concise in your responses.
Always format your responses exactly as requested."""

    def _parse_response(self, response: str) -> StudentResponse:
        """Parse student response into structured data."""
        lines = response.split("\n")

        understanding = ""
        key_concepts = []
        connections = []
        questions = []
        confidence = 0.5

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("UNDERSTANDING:"):
                current_section = "understanding"
            elif line.startswith("KEY_CONCEPTS:"):
                current_section = "key_concepts"
            elif line.startswith("CONNECTIONS:"):
                current_section = "connections"
            elif line.startswith("QUESTIONS:"):
                current_section = "questions"
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    confidence = 0.5
            elif line.startswith("- ") and current_section in ["key_concepts", "connections", "questions"]:
                item = line[2:].strip()
                if current_section == "key_concepts":
                    key_concepts.append(item)
                elif current_section == "connections":
                    connections.append(item)
                elif current_section == "questions":
                    questions.append(item)
            elif current_section == "understanding" and line:
                understanding += line + " "

        return StudentResponse(
            understanding=understanding.strip(),
            key_concepts=key_concepts,
            connections=connections,
            questions=questions,
            confidence=max(0.0, min(1.0, confidence)),
        )
