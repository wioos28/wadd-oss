"""Tests for the Memory System."""

import pytest
from datetime import datetime, timedelta

from ke.memory.models import MemoryEntry, MemoryType, MemoryQuery, MemoryStats
from ke.memory.base import BaseMemory
from ke.memory.working_memory import WorkingMemory
from ke.memory.short_memory import ShortTermMemory
from ke.memory.long_memory import LongTermMemory
from ke.memory.episodic_memory import EpisodicMemory
from ke.memory.semantic_memory import SemanticMemory
from ke.memory.conversation_memory import ConversationMemory
from ke.memory.project_memory import ProjectMemory
from ke.memory.visual_memory import VisualMemory
from ke.memory.memory_manager import MemoryManager


class TestMemoryModels:
    def test_memory_entry(self):
        entry = MemoryEntry(content="Test", memory_type=MemoryType.WORKING)
        assert entry.content == "Test"
        assert entry.memory_type == MemoryType.WORKING
        assert entry.importance == 0.5

    def test_memory_query(self):
        query = MemoryQuery(text="test", limit=5)
        assert query.text == "test"
        assert query.limit == 5


class TestWorkingMemory:
    def setup_method(self):
        self.memory = WorkingMemory(max_items=5)

    def test_store_and_retrieve(self):
        entry = self.memory.store("Test thought")
        retrieved = self.memory.retrieve(entry.id)
        assert retrieved is not None
        assert retrieved.content == "Test thought"

    def test_max_capacity(self):
        for i in range(7):
            self.memory.store(f"Item {i}")
        assert self.memory.count() <= 5

    def test_start_end_task(self):
        self.memory.start_task("My task")
        self.memory.add_thought("Thinking...")
        assert self.memory.count() > 0

        entries = self.memory.end_task()
        assert len(entries) > 0
        assert self.memory.count() == 0


class TestShortTermMemory:
    def setup_method(self):
        self.memory = ShortTermMemory(max_entries=50, decay_hours=1)

    def test_store_with_expiry(self):
        entry = self.memory.store("Test", ttl_seconds=60)
        assert entry.expires_at is not None

    def test_get_fresh(self):
        self.memory.store("Recent")
        fresh = self.memory.get_fresh(max_age_hours=1)
        assert len(fresh) >= 1


class TestLongTermMemory:
    def setup_method(self):
        self.memory = LongTermMemory(max_entries=100)

    def test_store_fact(self):
        entry = self.semantic = SemanticMemory()
        fact = entry.store_fact("Python is a language", confidence=0.9)
        assert fact.importance == 0.9
        assert "fact" in fact.tags

    def test_consolidate(self):
        entry = self.memory.store("Important fact", importance=0.5)
        self.memory.consolidate(entry.id, importance_boost=0.3)
        retrieved = self.memory.retrieve(entry.id)
        assert retrieved.importance == 0.8

    def test_get_by_importance(self):
        self.memory.store("Low", importance=0.3)
        self.memory.store("High", importance=0.9)
        high = self.memory.get_by_importance(min_importance=0.5)
        assert len(high) == 1
        assert high[0].importance == 0.9


class TestEpisodicMemory:
    def setup_method(self):
        self.memory = EpisodicMemory()

    def test_store_episode(self):
        entry = self.memory.store_episode("User asked about Python")
        assert "episode" in entry.tags
        assert "event_time" in entry.metadata

    def test_get_recent(self):
        self.memory.store_episode("Recent event")
        recent = self.memory.get_recent_episodes(hours=1)
        assert len(recent) >= 1


class TestSemanticMemory:
    def setup_method(self):
        self.memory = SemanticMemory()

    def test_store_fact(self):
        entry = self.memory.store_fact("Python is interpreted", confidence=0.95)
        assert "fact" in entry.tags
        assert entry.importance == 0.95

    def test_store_concept(self):
        entry = self.memory.store_concept(
            name="Variables",
            definition="Named storage locations",
            examples=["x = 5"],
        )
        assert "concept" in entry.tags
        assert "variables" in entry.tags

    def test_get_concepts(self):
        self.memory.store_concept("Functions", "Reusable code blocks")
        concepts = self.memory.get_concepts()
        assert len(concepts) == 1


class TestConversationMemory:
    def setup_method(self):
        self.memory = ConversationMemory()

    def test_session_flow(self):
        session_id = self.memory.start_session("test_session")
        assert session_id == "test_session"

        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there!")

        history = self.memory.get_session_history()
        assert len(history) == 2

    def test_context_window(self):
        self.memory.start_session()
        for i in range(5):
            self.memory.add_message("user" if i % 2 == 0 else "assistant", f"Message {i}")

        window = self.memory.get_context_window(window_size=3)
        assert len(window) == 3
        assert window[0]["content"] == "Message 2"


class TestProjectMemory:
    def setup_method(self):
        self.memory = ProjectMemory("test_project")

    def test_store_decision(self):
        entry = self.memory.store_decision(
            decision="Use SQLite",
            rationale="Simple, embedded",
        )
        assert "decision" in entry.tags

    def test_store_convention(self):
        entry = self.memory.store_convention("naming", "Use snake_case")
        assert "convention" in entry.tags

    def test_project_summary(self):
        self.memory.store_decision("Use FastAPI", "Modern, fast")
        self.memory.store_convention("style", "Black formatter")
        summary = self.memory.get_project_summary()
        assert "test_project" in summary
        assert "Decisions: 1" in summary


class TestVisualMemory:
    def setup_method(self):
        self.memory = VisualMemory()

    def test_store_image(self):
        entry = self.memory.store_image(
            path="/path/to/image.png",
            description="A chart showing growth",
        )
        assert "image" in entry.tags

    def test_store_screenshot(self):
        entry = self.memory.store_screenshot(
            path="/screenshot.png",
            description="Error message",
            context="Login page",
        )
        assert "screenshot" in entry.tags


class TestMemoryManager:
    def setup_method(self):
        self.manager = MemoryManager(project_id="test")

    def test_store_and_search(self):
        self.manager.store("Python is great", memory_type=MemoryType.LONG)
        results = self.manager.search("Python")
        assert len(results) >= 1

    def test_cross_type_search(self):
        self.manager.store("Python fact", memory_type=MemoryType.LONG, tags=["python"])
        self.manager.store("Python concept", memory_type=MemoryType.SEMANTIC, tags=["python"])

        results = self.manager.search("Python", tags=["python"])
        assert len(results) >= 1

    def test_stats(self):
        self.manager.store("Entry 1", memory_type=MemoryType.LONG)
        self.manager.store("Entry 2", memory_type=MemoryType.SEMANTIC)

        stats = self.manager.get_stats()
        assert stats.total_entries == 2
        assert stats.by_type["long"] == 1
        assert stats.by_type["semantic"] == 1

    def test_learn_from_interaction(self):
        entries = self.manager.learn_from_interaction(
            "What is Python?",
            "Python is a programming language.",
            importance=0.8,
        )
        assert len(entries) >= 1

    def test_context_summary(self):
        self.manager.store("Test", memory_type=MemoryType.LONG)
        summary = self.manager.get_context_summary()
        assert "Memory:" in summary
