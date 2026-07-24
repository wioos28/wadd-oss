"""Dream Mode - Autonomous learning during idle time."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ke.learning.v2.graph import KnowledgeGraph
from ke.learning.v2.models import DreamReport


class DreamMode:
    """Autonomous learning during idle time."""

    def __init__(self, graph: KnowledgeGraph | None = None):
        self.graph = graph or KnowledgeGraph()
        self._reports: list[DreamReport] = []

    def run_dream_session(self) -> DreamReport:
        """Run a dream mode session."""
        report = DreamReport()

        # Activity 1: Check for new documentation
        report.activities.append("Checking for new documentation")
        new_knowledge = self._check_new_documentation()
        report.new_knowledge = new_knowledge

        # Activity 2: Merge related knowledge
        report.activities.append("Merging related knowledge")
        merged = self._merge_related_knowledge()
        report.removed_duplicates = merged

        # Activity 3: Detect contradictions
        report.activities.append("Detecting contradictions")
        contradictions = self._detect_contradictions()
        report.contradictions_found = contradictions

        # Activity 4: Build knowledge graph
        report.activities.append("Building knowledge graph")
        nodes, relations = self._build_knowledge_graph()
        report.graph_nodes_added = nodes
        report.graph_relations_added = relations

        # Activity 5: Generate self-test questions
        report.activities.append("Generating self-test questions")
        self._generate_self_tests()

        # Activity 6: Optimize embeddings
        report.activities.append("Optimizing embeddings")
        embeddings = self._optimize_embeddings()
        report.embeddings_updated = embeddings

        # Activity 7: Generate next actions
        report.next_actions = self._generate_next_actions()

        report.completed_at = datetime.now(tz=UTC)
        self._reports.append(report)

        return report

    def _check_new_documentation(self) -> int:
        """Check for new documentation sources."""
        # Simulate checking for new docs
        topics = ["FastAPI", "Docker", "PostgreSQL", "React"]
        count = 0

        for topic in topics:
            existing = self.graph.find_by_concept(topic)
            if not existing:
                # Add new knowledge node
                self.graph.add_node(
                    concept=topic,
                    definition=f"{topic} documentation",
                    summary=f"Knowledge about {topic}",
                )
                count += 1

        return count

    def _merge_related_knowledge(self) -> int:
        """Merge related knowledge nodes."""
        merged = 0

        # Find nodes with similar concepts
        nodes = list(self.graph._nodes.values())
        seen = set()

        for i, node1 in enumerate(nodes):
            if node1.id in seen:
                continue

            for node2 in nodes[i + 1:]:
                if node2.id in seen:
                    continue

                # Check if concepts are similar
                if self._concepts_similar(node1.concept, node2.concept):
                    self.graph.merge_nodes(node1.id, node2.id)
                    seen.add(node2.id)
                    merged += 1

        return merged

    def _concepts_similar(self, concept1: str, concept2: str) -> bool:
        """Check if two concepts are similar."""
        words1 = set(concept1.lower().split())
        words2 = set(concept2.lower().split())

        # Simple similarity check
        intersection = words1 & words2
        union = words1 | words2

        if not union:
            return False

        return len(intersection) / len(union) > 0.5

    def _detect_contradictions(self) -> int:
        """Detect contradictions in knowledge."""
        contradictions = self.graph.detect_contradictions()
        return len(contradictions)

    def _build_knowledge_graph(self) -> tuple[int, int]:
        """Build knowledge graph relationships."""
        nodes_added = 0
        relations_added = 0

        # Add missing relationships
        nodes = list(self.graph._nodes.values())

        for node in nodes:
            # Find related concepts
            for other in nodes:
                if node.id == other.id:
                    continue

                # Check if concepts are related
                if self._concepts_related(node.concept, other.concept):
                    existing = any(
                        r.source_id == node.id and r.target_id == other.id
                        for r in self.graph._relations
                    )
                    if not existing:
                        self.graph.add_relation(node.id, other.id, "related")
                        relations_added += 1

        return nodes_added, relations_added

    def _concepts_related(self, concept1: str, concept2: str) -> bool:
        """Check if two concepts are related."""
        # Simple keyword-based check
        tech_pairs = [
            ("python", "fastapi"),
            ("docker", "kubernetes"),
            ("react", "javascript"),
            ("sql", "database"),
            ("git", "github"),
        ]

        c1 = concept1.lower()
        c2 = concept2.lower()

        for pair in tech_pairs:
            if (pair[0] in c1 and pair[1] in c2) or (pair[1] in c1 and pair[0] in c2):
                return True

        return False

    def _generate_self_tests(self) -> None:
        """Generate self-test questions."""
        # This would generate questions for each topic
        pass

    def _optimize_embeddings(self) -> int:
        """Optimize embedding indices."""
        # This would re-index embeddings
        return 0

    def _generate_next_actions(self) -> list[str]:
        """Generate next learning actions."""
        actions = []

        # Check for topics needing review
        stats = self.graph.get_stats()
        if stats["total_nodes"] < 100:
            actions.append("Continue learning new topics")

        if stats["total_relations"] < stats["total_nodes"]:
            actions.append("Build more relationships between concepts")

        contradictions = self.graph.detect_contradictions()
        if contradictions:
            actions.append(f"Resolve {len(contradictions)} contradictions")

        actions.append("Run self-exam on weak areas")
        actions.append("Update knowledge graph")

        return actions

    def get_reports(self) -> list[DreamReport]:
        """Get all dream reports."""
        return self._reports.copy()

    def get_stats(self) -> dict[str, Any]:
        """Get dream mode statistics."""
        return {
            "total_sessions": len(self._reports),
            "total_new_knowledge": sum(r.new_knowledge for r in self._reports),
            "total_merged": sum(r.removed_duplicates for r in self._reports),
            "total_contradictions": sum(r.contradictions_found for r in self._reports),
        }
