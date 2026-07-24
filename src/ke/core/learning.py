"""Knowledge learning and self-study capabilities."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from ke.core.models import Confidence, KnowledgeEntry, Relationship
from ke.embeddings.model import EmbeddingModel
from ke.storage.metadata import MetadataStore


class KnowledgeLearner:
    """Extract and learn knowledge from tasks, documents, and conversations."""

    def __init__(self, metadata_store: MetadataStore, embedding_model: EmbeddingModel):
        self.metadata_store = metadata_store
        self.embedding_model = embedding_model

    def learn_from_task(
        self,
        task_description: str,
        task_result: str,
        tags: list[str] | None = None,
    ) -> KnowledgeEntry:
        """Extract knowledge from a completed task."""
        # Combine task info into learnable content
        content = f"Task: {task_description}\n\nResult: {task_result}"

        # Generate summary
        summary = self._generate_summary(content)

        # Extract tags automatically
        auto_tags = self._extract_tags(content)
        all_tags = list(set((tags or []) + auto_tags))

        # Create entry
        entry = KnowledgeEntry(
            content=content,
            summary=summary,
            tags=all_tags,
            source_type="task",
            confidence=Confidence(score=0.7, source="task_learning"),
            metadata={
                "task_description": task_description[:500],
                "learned_at": datetime.now(tz=UTC).isoformat(),
            },
        )

        # Store
        self.metadata_store.add_entry(entry)

        # Generate and store embedding
        embedding = self.embedding_model.embed(content)
        entry.embedding_id = entry.id
        self.metadata_store.add_entry(entry)

        return entry

    def learn_from_document(
        self,
        content: str,
        source_path: str | None = None,
        tags: list[str] | None = None,
    ) -> list[KnowledgeEntry]:
        """Extract key knowledge from a document."""
        entries = []

        # Extract key concepts
        concepts = self._extract_concepts(content)

        # Extract definitions
        definitions = self._extract_definitions(content)

        # Extract examples
        examples = self._extract_examples(content)

        # Create entries for each type of knowledge
        for concept in concepts[:10]:  # Limit
            entry = KnowledgeEntry(
                content=concept,
                summary=f"Concept: {concept[:100]}",
                tags=(tags or []) + ["concept"],
                source_path=source_path,
                source_type="document",
                confidence=Confidence(score=0.6, source="document_extraction"),
            )
            self.metadata_store.add_entry(entry)
            entries.append(entry)

        for definition in definitions[:10]:
            entry = KnowledgeEntry(
                content=definition,
                summary=f"Definition: {definition[:100]}",
                tags=(tags or []) + ["definition"],
                source_path=source_path,
                source_type="document",
                confidence=Confidence(score=0.7, source="document_extraction"),
            )
            self.metadata_store.add_entry(entry)
            entries.append(entry)

        return entries

    def learn_from_conversation(
        self,
        messages: list[dict[str, str]],
        tags: list[str] | None = None,
    ) -> list[KnowledgeEntry]:
        """Extract knowledge from a conversation."""
        entries = []

        # Find knowledge-dense messages (longer, more detailed)
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "unknown")

            if len(content) > 100:  # Only extract from substantial messages
                summary = self._generate_summary(content)
                auto_tags = self._extract_tags(content)

                entry = KnowledgeEntry(
                    content=content,
                    summary=summary,
                    tags=(tags or []) + auto_tags + [f"role:{role}"],
                    source_type="conversation",
                    confidence=Confidence(score=0.5, source="conversation_extraction"),
                    metadata={"role": role},
                )
                self.metadata_store.add_entry(entry)
                entries.append(entry)

        return entries

    def auto_link_entries(self, entry_id: str, max_links: int = 5) -> list[Relationship]:
        """Automatically create relationships between entries."""
        entry = self.metadata_store.get_entry(entry_id)
        if not entry:
            return []

        # Find similar entries by content
        similar_entries = self.metadata_store.search_content(
            entry.summary or entry.content[:100],
            limit=max_links + 1,
        )

        relationships = []
        for similar in similar_entries:
            if similar.id == entry_id:
                continue

            # Compute similarity
            embedding1 = self.embedding_model.embed(entry.content)
            embedding2 = self.embedding_model.embed(similar.content)
            similarity = self._cosine_similarity(embedding1, embedding2)

            if similarity > 0.5:  # Threshold for auto-linking
                rel = Relationship(
                    source_id=entry_id,
                    target_id=similar.id,
                    relationship_type="related_to",
                    weight=similarity,
                )
                self.metadata_store.add_relationship(rel)
                relationships.append(rel)

        return relationships

    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of content."""
        # Simple extractive summary - take first N chars
        if len(content) <= max_length:
            return content
        return content[:max_length].rsplit(" ", 1)[0] + "..."

    def _extract_tags(self, content: str) -> list[str]:
        """Extract relevant tags from content."""
        tags = set()

        # Look for common patterns
        patterns = [
            (r"\b(Python|JavaScript|TypeScript|Go|Rust|Java|C\+\+)\b", "language"),
            (r"\b(function|class|method|API|endpoint)\b", "code"),
            (r"\b(bug|error|fix|issue|problem)\b", "debugging"),
            (r"\b(test|testing|spec|assertion)\b", "testing"),
            (r"\b(deploy|deployed|deployment|release)\b", "deployment"),
            (r"\b(security|auth|permission|access)\b", "security"),
            (r"\b(performance|optimize|fast|slow)\b", "performance"),
            (r"\b(database|sql|query|schema)\b", "database"),
        ]

        content_lower = content.lower()
        for pattern, tag in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                tags.add(tag)

        return list(tags)[:5]

    def _extract_concepts(self, content: str) -> list[str]:
        """Extract key concepts from content."""
        concepts = []

        # Look for definition patterns
        patterns = [
            r"(?:is|are|refers to|means|defined as)\s+(.+?)(?:\.|$)",
            r"(?:concept|idea|principle|notion)\s+(?:of|called|named)\s+(.+?)(?:\.|$)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            concepts.extend(matches[:3])

        return concepts[:10]

    def _extract_definitions(self, content: str) -> list[str]:
        """Extract definitions from content."""
        definitions = []

        # Look for "X is Y" patterns
        pattern = r"([A-Z][a-zA-Z\s]+)\s+(?:is|are)\s+(.+?)(?:\.|$)"
        matches = re.findall(pattern, content)
        for match in matches:
            if len(match[0]) > 3 and len(match[1]) > 10:
                definitions.append(f"{match[0].strip()}: {match[1].strip()}")

        return definitions[:10]

    def _extract_examples(self, content: str) -> list[str]:
        """Extract examples from content."""
        examples = []

        # Look for "for example" / "such as" / code blocks
        patterns = [
            r"(?:for example|such as|e\.g\.|including)\s+(.+?)(?:\.|$)",
            r"```[\s\S]*?```",  # Code blocks
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:3]:
                if isinstance(match, str) and len(match) > 5:
                    examples.append(match.strip())

        return examples[:5]

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import numpy as np

        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
