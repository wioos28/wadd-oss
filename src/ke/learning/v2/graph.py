"""Knowledge Graph - Build and query concept relationships."""

from __future__ import annotations

from typing import Any

from ke.learning.v2.models import KnowledgeNode, Relation, RelationType


class KnowledgeGraph:
    """Knowledge graph for concept relationships."""

    def __init__(self):
        self._nodes: dict[str, KnowledgeNode] = {}
        self._relations: list[Relation] = []

    def add_node(
        self,
        concept: str,
        definition: str = "",
        summary: str = "",
        parent_id: str | None = None,
        examples: list[str] | None = None,
        references: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        confidence: float = 0.5,
    ) -> KnowledgeNode:
        """Add a concept node to the graph."""
        node = KnowledgeNode(
            concept=concept,
            definition=definition,
            summary=summary,
            parent_id=parent_id,
            examples=examples or [],
            references=references or [],
            metadata=metadata or {},
            confidence=confidence,
        )

        self._nodes[node.id] = node

        # Add parent-child relation
        if parent_id and parent_id in self._nodes:
            parent = self._nodes[parent_id]
            parent.child_ids.append(node.id)
            self._add_relation(node.id, parent_id, RelationType.CHILD)

        return node

    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        weight: float = 1.0,
    ) -> Relation | None:
        """Add a relation between two nodes."""
        if source_id not in self._nodes or target_id not in self._nodes:
            return None

        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
        )

        self._relations.append(relation)

        # Update node references
        source = self._nodes[source_id]
        target = self._nodes[target_id]

        if relation_type == RelationType.RELATED:
            if target_id not in source.related_ids:
                source.related_ids.append(target_id)
            if source_id not in target.related_ids:
                target.related_ids.append(source_id)
        elif relation_type == RelationType.DEPENDS_ON:
            if target_id not in source.dependency_ids:
                source.dependency_ids.append(target_id)
        elif relation_type == RelationType.ALTERNATIVE:
            if target_id not in source.alternative_ids:
                source.alternative_ids.append(target_id)
            if source_id not in target.alternative_ids:
                target.alternative_ids.append(source_id)

        return relation

    def _add_relation(
        self, source_id: str, target_id: str, relation_type: RelationType
    ) -> None:
        """Internal method to add relation."""
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
        )
        self._relations.append(relation)

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def find_by_concept(self, concept: str) -> list[KnowledgeNode]:
        """Find nodes by concept name."""
        concept_lower = concept.lower()
        return [
            node
            for node in self._nodes.values()
            if concept_lower in node.concept.lower()
        ]

    def get_children(self, node_id: str) -> list[KnowledgeNode]:
        """Get child nodes."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        return [self._nodes[cid] for cid in node.child_ids if cid in self._nodes]

    def get_parents(self, node_id: str) -> list[KnowledgeNode]:
        """Get parent nodes."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        parents = []
        for rel in self._relations:
            if rel.target_id == node_id and rel.relation_type == RelationType.CHILD:
                if rel.source_id in self._nodes:
                    parents.append(self._nodes[rel.source_id])
        return parents

    def get_related(self, node_id: str) -> list[KnowledgeNode]:
        """Get related nodes."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        return [self._nodes[rid] for rid in node.related_ids if rid in self._nodes]

    def get_dependencies(self, node_id: str) -> list[KnowledgeNode]:
        """Get dependency nodes."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        return [self._nodes[did] for did in node.dependency_ids if did in self._nodes]

    def get_alternatives(self, node_id: str) -> list[KnowledgeNode]:
        """Get alternative nodes."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        return [self._nodes[aid] for aid in node.alternative_ids if aid in self._nodes]

    def get_examples(self, node_id: str) -> list[str]:
        """Get examples for a node."""
        node = self._nodes.get(node_id)
        if not node:
            return []
        return node.examples

    def get_path(self, source_id: str, target_id: str) -> list[KnowledgeNode]:
        """Find path between two nodes (BFS)."""
        if source_id not in self._nodes or target_id not in self._nodes:
            return []

        visited = {source_id}
        queue = [[source_id]]

        while queue:
            path = queue.pop(0)
            current = path[-1]

            if current == target_id:
                return [self._nodes[nid] for nid in path if nid in self._nodes]

            node = self._nodes.get(current)
            if not node:
                continue

            # Check all connections
            neighbors = set()
            neighbors.update(node.child_ids)
            neighbors.update(node.related_ids)
            neighbors.update(node.dependency_ids)

            for rel in self._relations:
                if rel.source_id == current:
                    neighbors.add(rel.target_id)
                if rel.target_id == current:
                    neighbors.add(rel.source_id)

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return []

    def merge_nodes(self, node_id_1: str, node_id_2: str) -> KnowledgeNode | None:
        """Merge two nodes (keep first, update references)."""
        node1 = self._nodes.get(node_id_1)
        node2 = self._nodes.get(node_id_2)

        if not node1 or not node2:
            return None

        # Merge data
        node1.examples.extend(node2.examples)
        node1.references.extend(node2.references)
        node1.related_ids.extend(node2.related_ids)

        # Update all relations pointing to node2
        for rel in self._relations:
            if rel.source_id == node_id_2:
                rel.source_id = node_id_1
            if rel.target_id == node_id_2:
                rel.target_id = node_id_1

        # Remove node2
        del self._nodes[node_id_2]

        return node1

    def detect_contradictions(self) -> list[tuple[str, str, str]]:
        """Detect potential contradictions in the graph."""
        contradictions = []

        for rel in self._relations:
            if rel.relation_type == RelationType.CONTRADICTS:
                source = self._nodes.get(rel.source_id)
                target = self._nodes.get(rel.target_id)
                if source and target:
                    contradictions.append(
                        (source.concept, target.concept, rel.metadata.get("reason", ""))
                    )

        return contradictions

    def get_stats(self) -> dict[str, Any]:
        """Get graph statistics."""
        relation_counts = {}
        for rel in self._relations:
            rel_type = rel.relation_type.value
            relation_counts[rel_type] = relation_counts.get(rel_type, 0) + 1

        return {
            "total_nodes": len(self._nodes),
            "total_relations": len(self._relations),
            "relation_counts": relation_counts,
            "avg_confidence": (
                sum(n.confidence for n in self._nodes.values()) / max(len(self._nodes), 1)
            ),
        }

    def to_mermaid(self) -> str:
        """Export graph as Mermaid diagram."""
        lines = ["graph TD"]

        for node in self._nodes.values():
            label = node.concept.replace('"', "'")
            lines.append(f'    {node.id}["{label}"]')

        for rel in self._relations:
            if rel.relation_type == RelationType.PARENT:
                lines.append(f"    {rel.target_id} --> {rel.source_id}")
            elif rel.relation_type == RelationType.RELATED:
                lines.append(f"    {rel.source_id} -.- {rel.target_id}")
            elif rel.relation_type == RelationType.DEPENDS_ON:
                lines.append(f"    {rel.source_id} -->|depends on| {rel.target_id}")
            elif rel.relation_type == RelationType.ALTERNATIVE:
                lines.append(f"    {rel.source_id} -.-|alternative| {rel.target_id}")

        return "\n".join(lines)
