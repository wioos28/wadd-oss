"""Tests for core models."""

import pytest
from datetime import datetime

from ke.core.models import (
    Confidence,
    KnowledgeEntry,
    NetworkState,
    QueryMode,
    QueryResult,
    Relationship,
)


class TestConfidence:
    def test_default_confidence(self):
        c = Confidence(score=0.5, source="reasoning")
        assert c.score == 0.5
        assert c.source == "reasoning"

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            Confidence(score=1.5, source="test")
        with pytest.raises(Exception):
            Confidence(score=-0.1, source="test")


class TestKnowledgeEntry:
    def test_create_entry(self):
        entry = KnowledgeEntry(content="Test content")
        assert entry.content == "Test content"
        assert entry.id is not None
        assert entry.source_type == "manual"
        assert isinstance(entry.created_at, datetime)

    def test_entry_with_tags(self):
        entry = KnowledgeEntry(content="Test", tags=["tag1", "tag2"])
        assert entry.tags == ["tag1", "tag2"]


class TestRelationship:
    def test_create_relationship(self):
        rel = Relationship(
            source_id="id1",
            target_id="id2",
            relationship_type="related_to",
        )
        assert rel.source_id == "id1"
        assert rel.target_id == "id2"
        assert rel.weight == 1.0


class TestQueryResult:
    def test_create_result(self):
        entry = KnowledgeEntry(content="Test")
        result = QueryResult(
            entry=entry,
            score=0.8,
            source_layer="vector",
            retrieval_mode="semantic",
        )
        assert result.score == 0.8
        assert result.source_layer == "vector"


class TestQueryMode:
    def test_modes(self):
        assert QueryMode.SEMANTIC == "semantic"
        assert QueryMode.KEYWORD == "keyword"
        assert QueryMode.HYBRID == "hybrid"
