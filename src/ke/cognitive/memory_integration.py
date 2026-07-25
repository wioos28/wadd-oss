"""Memory Integration - Load and manage conversation memories."""

from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta

from ke.config import KeConfig
from ke.domain.models import MemoryEntry, MemoryType


class MemoryIntegrator:
    """
    Integrates short-term and long-term memory into the conversation.

    Memory Types:
    - Short-term: Recent conversation context (last N messages)
    - Long-term: Persistent knowledge and facts
    - Working: Current task context
    """

    def __init__(self, config: KeConfig):
        self.config = config
        self._memory_manager = None
        self._conversation_store = {}

    @property
    def memory_manager(self):
        """Lazy-load memory manager."""
        if self._memory_manager is None:
            from ke.memory.memory_manager import MemoryManager
            self._memory_manager = MemoryManager()
        return self._memory_manager

    async def integrate(
        self,
        message: str,
        conversation_history: list[dict[str, str]],
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Integrate memories into the current context.

        Returns:
            {
                "short_term": [...],  # Recent conversation
                "long_term": [...],   # Relevant long-term memories
                "working": [...],     # Current task context
                "session_id": str,
            }
        """
        # Get short-term memory (recent conversation)
        short_term = self._get_short_term_memory(conversation_history, session_id)

        # Get long-term memory (relevant facts and knowledge)
        long_term = await self._get_long_term_memory(message)

        # Get working memory (current task)
        working = self._get_working_memory(session_id)

        return {
            "short_term": short_term,
            "long_term": long_term,
            "working": working,
            "session_id": session_id or "default",
            "timestamp": datetime.now().isoformat(),
        }

    async def store_interaction(
        self,
        user_message: str,
        assistant_response: str,
        session_id: str | None = None,
    ) -> None:
        """Store the interaction in memory."""
        # Store in short-term memory
        session_id = session_id or "default"
        if session_id not in self._conversation_store:
            self._conversation_store[session_id] = []

        self._conversation_store[session_id].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
        })

        self._conversation_store[session_id].append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.now().isoformat(),
        })

        # Keep only last 20 messages in short-term
        if len(self._conversation_store[session_id]) > 20:
            self._conversation_store[session_id] = self._conversation_store[session_id][-20:]

        # Store important information in long-term memory
        await self._store_in_long_term(user_message, assistant_response, session_id)

    def _get_short_term_memory(
        self,
        conversation_history: list[dict[str, str]],
        session_id: str | None,
    ) -> list[dict[str, str]]:
        """Get recent conversation history."""
        # Use provided history or stored history
        if conversation_history:
            return conversation_history[-10:]  # Last 10 messages

        session_id = session_id or "default"
        return self._conversation_store.get(session_id, [])[-10:]

    async def _get_long_term_memory(self, query: str) -> list[dict[str, Any]]:
        """Get relevant long-term memories."""
        try:
            # Search memory for relevant facts
            results = self.memory_manager.search(query, limit=5)
            return [
                {
                    "id": r.id,
                    "content": r.content,
                    "type": r.memory_type.value,
                    "importance": r.importance,
                }
                for r in results
            ]
        except Exception:
            return []

    def _get_working_memory(self, session_id: str | None) -> list[dict[str, Any]]:
        """Get current task context."""
        # For now, return empty - this would be populated during task execution
        return []

    async def _store_in_long_term(
        self,
        user_message: str,
        assistant_response: str,
        session_id: str,
    ) -> None:
        """Store important information in long-term memory."""
        # Only store if the message seems important
        importance = self._calculate_importance(user_message)

        if importance > 0.3:
            try:
                # Store user question as semantic memory
                self.memory_manager.store(
                    content=user_message,
                    memory_type=MemoryType.SEMANTIC,
                    tags=["question", session_id],
                    importance=importance,
                )

                # Store assistant response as knowledge
                if len(assistant_response) > 50:
                    self.memory_manager.store(
                        content=assistant_response[:500],
                        memory_type=MemoryType.LONG,
                        tags=["knowledge", session_id],
                        importance=importance * 0.8,
                    )
            except Exception:
                pass  # Memory storage is best-effort

    def _calculate_importance(self, message: str) -> float:
        """Calculate importance score for a message."""
        importance = 0.3  # Base importance

        # Increase importance for certain patterns
        important_patterns = [
            "remember", "important", "note", "always", "never",
            "rule", "preference", "like", "dislike", "need",
            "how to", "explain", "teach", "learn",
        ]

        for pattern in important_patterns:
            if pattern in message.lower():
                importance += 0.1

        # Decrease importance for simple greetings
        simple_patterns = ["hi", "hello", "hey", "thanks", "ok", "yes", "no"]
        if any(p in message.lower() for p in simple_patterns):
            importance -= 0.2

        return max(0.0, min(1.0, importance))

    def clear_session(self, session_id: str) -> None:
        """Clear session from short-term memory."""
        if session_id in self._conversation_store:
            del self._conversation_store[session_id]
