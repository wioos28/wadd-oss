"""Code similarity search using text-based analysis."""

from __future__ import annotations

import re

from ke.core.models import KnowledgeEntry, QueryResult
from ke.storage.metadata import MetadataStore


class CodeSimilarityRetriever:
    """Search for similar code using text-based heuristics."""

    def __init__(self, metadata_store: MetadataStore):
        self.metadata_store = metadata_store

    def search(self, query: str, limit: int = 10) -> list[QueryResult]:
        """Search for code entries similar to the query."""
        # Extract code-specific features from query
        query_features = self._extract_features(query)

        # Get all code entries
        all_entries = self.metadata_store.list_entries(source_type="code", limit=1000)

        scored_entries = []
        for entry in all_entries:
            score = self._compute_similarity(query, entry, query_features)
            if score > 0.1:
                scored_entries.append((entry, score))

        # Sort by score
        scored_entries.sort(key=lambda x: x[1], reverse=True)

        results = []
        for entry, score in scored_entries[:limit]:
            results.append(QueryResult(
                entry=entry,
                score=score,
                source_layer="metadata",
                retrieval_mode="code_similarity",
                explanation=f"Code similarity score: {score:.3f}",
            ))

        return results

    def _extract_features(self, text: str) -> dict:
        """Extract code features from query text."""
        features = {
            "functions": set(),
            "classes": set(),
            "keywords": set(),
            "identifiers": set(),
        }

        # Function calls: word(
        func_calls = re.findall(r"(\w+)\s*\(", text)
        features["functions"].update(func_calls)

        # Class names: CapitalWord
        class_names = re.findall(r"\b([A-Z][a-zA-Z0-9]+)\b", text)
        features["classes"].update(class_names)

        # Common programming keywords
        keywords = re.findall(r"\b(def|class|function|return|if|else|for|while|import|from|async|await|const|let|var|type|struct|enum)\b", text)
        features["keywords"].update(keywords)

        # Identifiers: word_chars with underscores
        identifiers = re.findall(r"\b([a-z_][a-z0-9_]{2,})\b", text)
        features["identifiers"].update(identifiers)

        return features

    def _compute_similarity(self, query: str, entry: KnowledgeEntry, query_features: dict) -> float:
        """Compute code similarity score between query and entry."""
        entry_text = entry.content.lower()
        query_lower = query.lower()

        score = 0.0

        # Exact substring match
        if query_lower in entry_text:
            score += 0.4

        # Function name overlap
        entry_funcs = set(re.findall(r"(\w+)\s*\(", entry.content))
        func_overlap = len(query_features["functions"] & entry_funcs)
        if query_features["functions"]:
            score += 0.3 * (func_overlap / len(query_features["functions"]))

        # Class name overlap
        entry_classes = set(re.findall(r"\b([A-Z][a-zA-Z0-9]+)\b", entry.content))
        class_overlap = len(query_features["classes"] & entry_classes)
        if query_features["classes"]:
            score += 0.2 * (class_overlap / len(query_features["classes"]))

        # Keyword overlap
        entry_keywords = set(re.findall(r"\b(def|class|function|return|if|else|for|while|import|from|async|await|const|let|var|type|struct|enum)\b", entry.content))
        kw_overlap = len(query_features["keywords"] & entry_keywords)
        if query_features["keywords"]:
            score += 0.1 * min(1.0, kw_overlap / max(len(query_features["keywords"]), 1))

        return min(1.0, score)
