"""Tests for storage modules."""

import tempfile
from pathlib import Path

import pytest

from ke.core.models import KnowledgeEntry, Relationship
from ke.storage.cache import LocalCache
from ke.storage.metadata import MetadataStore


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def metadata_store(tmp_dir):
    db_path = tmp_dir / "test.db"
    store = MetadataStore(db_path)
    yield store
    store.close()


@pytest.fixture
def cache(tmp_dir):
    cache_path = tmp_dir / "test_cache"
    c = LocalCache(cache_path)
    yield c
    c.close()


class TestMetadataStore:
    def test_add_and_get_entry(self, metadata_store):
        entry = KnowledgeEntry(content="Test content", tags=["test"])
        metadata_store.add_entry(entry)

        retrieved = metadata_store.get_entry(entry.id)
        assert retrieved is not None
        assert retrieved.content == "Test content"
        assert "test" in retrieved.tags

    def test_search_content(self, metadata_store):
        entry1 = KnowledgeEntry(content="Python is a programming language")
        entry2 = KnowledgeEntry(content="JavaScript is used for web development")
        metadata_store.add_entry(entry1)
        metadata_store.add_entry(entry2)

        results = metadata_store.search_content("Python")
        assert len(results) >= 1
        assert any("Python" in r.content for r in results)

    def test_count_entries(self, metadata_store):
        assert metadata_store.count_entries() == 0

        metadata_store.add_entry(KnowledgeEntry(content="Test 1"))
        metadata_store.add_entry(KnowledgeEntry(content="Test 2"))
        assert metadata_store.count_entries() == 2

    def test_add_relationship(self, metadata_store):
        entry1 = KnowledgeEntry(content="Entry 1")
        entry2 = KnowledgeEntry(content="Entry 2")
        metadata_store.add_entry(entry1)
        metadata_store.add_entry(entry2)

        rel = Relationship(
            source_id=entry1.id,
            target_id=entry2.id,
            relationship_type="related_to",
        )
        metadata_store.add_relationship(rel)

        rels = metadata_store.get_relationships(entry1.id)
        assert len(rels) == 1
        assert rels[0].relationship_type == "related_to"

    def test_list_entries(self, metadata_store):
        for i in range(5):
            metadata_store.add_entry(KnowledgeEntry(
                content=f"Entry {i}",
                source_type="test" if i % 2 == 0 else "other",
            ))

        all_entries = metadata_store.list_entries()
        assert len(all_entries) == 5

        test_entries = metadata_store.list_entries(source_type="test")
        assert len(test_entries) == 3


class TestLocalCache:
    def test_set_and_get(self, cache):
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent(self, cache):
        assert cache.get("nonexistent") is None

    def test_exists(self, cache):
        cache.set("key", "value")
        assert cache.exists("key")
        assert not cache.exists("other")

    def test_delete(self, cache):
        cache.set("key", "value")
        cache.delete("key")
        assert cache.get("key") is None

    def test_clear(self, cache):
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
