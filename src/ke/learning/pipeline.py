"""Learning pipeline - Process knowledge from sources to knowledge base."""

from __future__ import annotations

import hashlib
from typing import Any

from ke.learning.models import (
    Difficulty,
    KnowledgeCategory,
    KnowledgeEntry,
    LearningReport,
    LearningSource,
    SourceType,
)


class LearningPipeline:
    """Pipeline for learning and storing knowledge."""

    def __init__(self, storage: Any = None, embeddings: Any = None):
        self.storage = storage
        self.embeddings = embeddings
        self._entries: dict[str, KnowledgeEntry] = {}

    def learn_from_text(
        self,
        content: str,
        source: LearningSource,
        topic: str = "",
        difficulty: Difficulty = Difficulty.BEGINNER,
    ) -> KnowledgeEntry:
        """Learn from raw text content."""
        # Step 1: Read & Understand
        understood = self._understand(content)

        # Step 2: Extract key information
        extracted = self._extract(understood, topic)

        # Step 3: Summarize
        summary = self._summarize(extracted)

        # Step 4: Split if needed
        chunks = self._split(extracted)

        # Step 5: Generate metadata
        metadata = self._generate_metadata(extracted, source)

        # Step 6: Generate keywords
        keywords = self._generate_keywords(extracted)

        # Step 7: Create entry
        entry = KnowledgeEntry(
            title=extracted.get("title", topic or "Untitled"),
            summary=summary,
            explanation=extracted.get("explanation", content[:500]),
            examples=extracted.get("examples", []),
            best_practices=extracted.get("best_practices", []),
            common_mistakes=extracted.get("common_mistakes", []),
            references=extracted.get("references", []),
            metadata=metadata,
            tags=keywords,
            difficulty=difficulty,
            category=self._classify_category(extracted),
            source=source,
            confidence=self._assess_confidence(source, extracted),
        )

        # Step 8: Store
        self._store(entry)

        return entry

    def learn_from_code(
        self,
        code: str,
        language: str,
        source: LearningSource,
        filename: str = "",
    ) -> KnowledgeEntry:
        """Learn from source code."""
        analyzed = self._analyze_code(code, language)

        entry = KnowledgeEntry(
            title=analyzed.get("title", filename or "Code Snippet"),
            summary=analyzed.get("summary", f"Code in {language}"),
            explanation=analyzed.get("explanation", ""),
            examples=[code[:500]],
            best_practices=analyzed.get("best_practices", []),
            common_mistakes=analyzed.get("common_mistakes", []),
            references=analyzed.get("references", []),
            metadata={
                "language": language,
                "filename": filename,
                "architecture": analyzed.get("architecture", ""),
                "patterns": analyzed.get("patterns", []),
                "dependencies": analyzed.get("dependencies", []),
            },
            tags=analyzed.get("tags", [language]),
            difficulty=Difficulty.INTERMEDIATE,
            category=KnowledgeCategory.ARCHITECTURE,
            source=source,
            confidence=0.7,
        )

        self._store(entry)
        return entry

    def learn_from_error(
        self,
        error_message: str,
        solution: str,
        context: str = "",
    ) -> KnowledgeEntry:
        """Learn from an error and its solution."""
        entry = KnowledgeEntry(
            title=f"Error: {error_message[:100]}",
            summary=f"Solution for: {error_message[:200]}",
            explanation=solution,
            examples=[error_message],
            best_practices=[f"Prevent: {solution[:200]}"],
            common_mistakes=[error_message],
            metadata={
                "error_message": error_message,
                "solution": solution,
                "context": context,
            },
            tags=["error", "solution", "troubleshooting"],
            difficulty=Difficulty.INTERMEDIATE,
            category=KnowledgeCategory.ERROR,
            source=LearningSource(type=SourceType.EXPERIENCE),
            confidence=0.8,
        )

        self._store(entry)
        return entry

    def learn_best_practice(
        self,
        topic: str,
        practice: str,
        reason: str,
        examples: list[str] | None = None,
    ) -> KnowledgeEntry:
        """Learn a best practice."""
        entry = KnowledgeEntry(
            title=f"Best Practice: {topic}",
            summary=practice,
            explanation=reason,
            examples=examples or [],
            best_practices=[practice],
            metadata={"topic": topic, "reason": reason},
            tags=["best-practice", topic.lower()],
            difficulty=Difficulty.INTERMEDIATE,
            category=KnowledgeCategory.BEST_PRACTICE,
            source=LearningSource(type=SourceType.EXPERIENCE),
            confidence=0.85,
        )

        self._store(entry)
        return entry

    def _understand(self, content: str) -> dict[str, Any]:
        """Understand the content structure."""
        return {
            "raw": content,
            "length": len(content),
            "lines": content.count("\n") + 1,
            "has_code": "```" in content or "def " in content or "class " in content,
            "has_headers": any(line.startswith("#") for line in content.split("\n")),
        }

    def _extract(self, understood: dict[str, Any], topic: str) -> dict[str, Any]:
        """Extract key information from content."""
        content = understood["raw"]

        # Extract title (first header or topic)
        title = topic
        for line in content.split("\n"):
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break

        # Extract examples (code blocks)
        examples = []
        in_code = False
        code_block = []
        for line in content.split("\n"):
            if line.startswith("```"):
                if in_code:
                    examples.append("\n".join(code_block))
                    code_block = []
                in_code = not in_code
            elif in_code:
                code_block.append(line)

        return {
            "title": title,
            "explanation": content[:1000],
            "examples": examples[:5],
            "best_practices": [],
            "common_mistakes": [],
            "references": [],
        }

    def _summarize(self, extracted: dict[str, Any]) -> str:
        """Create a summary of the extracted content."""
        explanation = extracted.get("explanation", "")
        if len(explanation) <= 200:
            return explanation
        return explanation[:200] + "..."

    def _split(self, extracted: dict[str, Any]) -> list[str]:
        """Split content into manageable chunks."""
        explanation = extracted.get("explanation", "")
        if len(explanation) <= 1000:
            return [explanation]

        chunks = []
        lines = explanation.split("\n")
        current_chunk = []
        current_length = 0

        for line in lines:
            current_chunk.append(line)
            current_length += len(line) + 1

            if current_length >= 800:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _generate_metadata(
        self, extracted: dict[str, Any], source: LearningSource
    ) -> dict[str, Any]:
        """Generate metadata for the entry."""
        return {
            "source_type": source.type.value,
            "source_url": source.url,
            "content_length": len(extracted.get("explanation", "")),
            "has_code": len(extracted.get("examples", [])) > 0,
        }

    def _generate_keywords(self, extracted: dict[str, Any]) -> list[str]:
        """Generate keywords from content."""
        content = extracted.get("explanation", "").lower()
        title = extracted.get("title", "").lower()

        # Simple keyword extraction
        keywords = set()

        # From title
        for word in title.split():
            if len(word) > 3:
                keywords.add(word)

        # Common programming keywords
        programming_terms = [
            "python", "javascript", "typescript", "react", "fastapi",
            "django", "flask", "node", "database", "sql", "api",
            "function", "class", "method", "variable", "module",
            "import", "export", "async", "await", "error", "exception",
        ]

        for term in programming_terms:
            if term in content:
                keywords.add(term)

        return list(keywords)[:10]

    def _classify_category(self, extracted: dict[str, Any]) -> KnowledgeCategory:
        """Classify the knowledge category."""
        examples = extracted.get("examples", [])
        if examples:
            return KnowledgeCategory.SYNTAX
        return KnowledgeCategory.CONCEPT

    def _assess_confidence(
        self, source: LearningSource, extracted: dict[str, Any]
    ) -> float:
        """Assess confidence in the knowledge."""
        base_confidence = source.reliability_score

        # Boost if has examples
        if extracted.get("examples"):
            base_confidence += 0.1

        # Boost if has best practices
        if extracted.get("best_practices"):
            base_confidence += 0.05

        return min(1.0, base_confidence)

    def _analyze_code(self, code: str, language: str) -> dict[str, Any]:
        """Analyze source code."""
        return {
            "title": f"{language} Code",
            "summary": f"Code snippet in {language}",
            "explanation": f"Source code analysis for {language}",
            "best_practices": [],
            "common_mistakes": [],
            "references": [],
            "architecture": "",
            "patterns": [],
            "dependencies": [],
            "tags": [language],
        }

    def _store(self, entry: KnowledgeEntry) -> None:
        """Store entry in memory (and optionally to persistent storage)."""
        self._entries[entry.id] = entry

        if self.storage:
            try:
                self.storage.add_entry(entry)
            except Exception:
                pass

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """Get an entry by ID."""
        return self._entries.get(entry_id)

    def search(self, query: str) -> list[KnowledgeEntry]:
        """Search entries by query."""
        results = []
        query_lower = query.lower()

        for entry in self._entries.values():
            if (
                query_lower in entry.title.lower()
                or query_lower in entry.summary.lower()
                or any(query_lower in tag for tag in entry.tags)
            ):
                results.append(entry)

        return results

    def get_all(self) -> list[KnowledgeEntry]:
        """Get all entries."""
        return list(self._entries.values())

    def count(self) -> int:
        """Get entry count."""
        return len(self._entries)

    def generate_report(self) -> LearningReport:
        """Generate a learning report."""
        entries = self.get_all()

        return LearningReport(
            topics_learned=list(set(tag for e in entries for tag in e.tags)),
            entries_created=len(entries),
            examples_generated=sum(len(e.examples) for e in entries),
            coverage_percent=min(100.0, len(entries) * 0.5),
            knowledge_score=sum(e.confidence for e in entries) / max(len(entries), 1),
        )
