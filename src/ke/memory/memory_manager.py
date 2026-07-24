"""Memory Manager - Unified interface for all memory types."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ke.memory.conversation_memory import ConversationMemory
from ke.memory.episodic_memory import EpisodicMemory
from ke.memory.long_memory import LongTermMemory
from ke.memory.models import MemoryEntry, MemoryQuery, MemoryStats, MemoryType
from ke.memory.project_memory import ProjectMemory
from ke.memory.semantic_memory import SemanticMemory
from ke.memory.short_memory import ShortTermMemory
from ke.memory.visual_memory import VisualMemory
from ke.memory.working_memory import WorkingMemory


class MemoryManager:
    """Unified manager for all memory types.

    Coordinates between working, short-term, long-term, episodic,
    semantic, conversation, project, and visual memory.
    """

    def __init__(self, project_id: str = "default"):
        # Initialize all memory types
        self.working = WorkingMemory()
        self.short = ShortTermMemory()
        self.long = LongTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.conversation = ConversationMemory()
        self.project = ProjectMemory(project_id)
        self.visual = VisualMemory()

        # Memory type registry
        self._memories: dict[MemoryType, Any] = {
            MemoryType.WORKING: self.working,
            MemoryType.SHORT: self.short,
            MemoryType.LONG: self.long,
            MemoryType.EPISODIC: self.episodic,
            MemoryType.SEMANTIC: self.semantic,
            MemoryType.CONVERSATION: self.conversation,
            MemoryType.PROJECT: self.project,
            MemoryType.VISUAL: self.visual,
        }

    def store(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SHORT,
        **kwargs,
    ) -> MemoryEntry:
        """Store a memory entry in the specified type."""
        memory = self._memories.get(memory_type)
        if not memory:
            raise ValueError(f"Unknown memory type: {memory_type}")
        return memory.store(content, **kwargs)

    def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve a memory entry by ID from any memory type."""
        for memory in self._memories.values():
            entry = memory.retrieve(entry_id)
            if entry:
                return entry
        return None

    def search(
        self,
        query: str,
        memory_types: list[MemoryType] | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Search across specified memory types."""
        types_to_search = memory_types or list(MemoryType)
        results = []

        for mem_type in types_to_search:
            memory = self._memories.get(mem_type)
            if not memory:
                continue

            mq = MemoryQuery(
                text=query,
                memory_types=[mem_type],
                tags=tags or [],
                limit=limit,
            )
            results.extend(memory.search(mq))

        results.sort(key=lambda e: e.importance, reverse=True)
        return results[:limit]

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry from any memory type."""
        for memory in self._memories.values():
            if memory.delete(entry_id):
                return True
        return False

    def clear(self, memory_type: MemoryType | None = None) -> int:
        """Clear entries from specified or all memory types."""
        if memory_type:
            memory = self._memories.get(memory_type)
            return memory.clear() if memory else 0

        total = 0
        for memory in self._memories.values():
            total += memory.clear()
        return total

    def get_stats(self) -> MemoryStats:
        """Get statistics about the memory system."""
        by_type = {}
        total = 0
        all_entries = []

        for mem_type, memory in self._memories.items():
            count = memory.count()
            by_type[mem_type.value] = count
            total += count
            all_entries.extend(memory.get_all())

        avg_importance = (
            sum(e.importance for e in all_entries) / len(all_entries)
            if all_entries else 0
        )

        dates = [e.created_at for e in all_entries] if all_entries else []

        return MemoryStats(
            total_entries=total,
            by_type=by_type,
            avg_importance=avg_importance,
            oldest_entry=min(dates) if dates else None,
            newest_entry=max(dates) if dates else None,
        )

    def cleanup(self) -> dict[str, int]:
        """Run cleanup on all memory types. Returns counts by type."""
        results = {}
        for mem_type, memory in self._memories.items():
            if hasattr(memory, "cleanup_expired"):
                results[mem_type.value] = memory.cleanup_expired()
            elif hasattr(memory, "decay"):
                results[mem_type.value] = memory.decay()
            else:
                results[mem_type.value] = 0
        return results

    def get_context_summary(self) -> str:
        """Get a summary of the memory system for context injection."""
        stats = self.get_stats()
        parts = [
            f"Memory: {stats.total_entries} entries",
            f"Avg importance: {stats.avg_importance:.2f}",
        ]

        # Add type breakdown
        for mem_type, count in stats.by_type.items():
            if count > 0:
                parts.append(f"{mem_type}: {count}")

        return " | ".join(parts)

    def get_conversation_context(self, window_size: int = 5) -> list[dict[str, str]]:
        """Get conversation context for LLM input."""
        return self.conversation.get_context_window(window_size)

    def learn_from_interaction(
        self,
        user_input: str,
        assistant_response: str,
        importance: float = 0.6,
    ) -> list[MemoryEntry]:
        """Learn from a conversation interaction."""
        entries = []

        # Store in conversation memory
        self.conversation.add_message("user", user_input)
        self.conversation.add_message("assistant", assistant_response)

        # Store as episodic memory
        episode = self.episodic.store_episode(
            event=f"User asked: {user_input[:100]}\nAssistant responded: {assistant_response[:100]}",
            importance=importance,
            tags=["interaction"],
        )
        entries.append(episode)

        # If important enough, store in long-term
        if importance >= 0.7:
            long_entry = self.long.store(
                content=f"Q: {user_input}\nA: {assistant_response}",
                importance=importance,
                tags=["learned", "interaction"],
            )
            entries.append(long_entry)

        return entries

    def get_project_context(self) -> dict[str, Any]:
        """Get project-specific context."""
        return {
            "decisions": len(self.project.get_decisions()),
            "conventions": len(self.project.get_conventions()),
            "summary": self.project.get_project_summary(),
        }

    def __enter__(self) -> MemoryManager:
        return self

    def __exit__(self, *args) -> None:
        self.cleanup()
