"""Conversation Memory - Chat history and context."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ke.memory.base import BaseMemory
from ke.memory.models import MemoryEntry, MemoryType


class ConversationMemory(BaseMemory):
    """Memory of conversation history and context.

    - Stores message exchanges
    - Tracks conversation flow
    - Used for multi-turn dialogue
    """

    def __init__(self, max_entries: int = 200):
        super().__init__(MemoryType.CONVERSATION, max_entries=max_entries)
        self._current_session: str | None = None
        self._turn_count: int = 0

    def start_session(self, session_id: str | None = None) -> str:
        """Start a new conversation session."""
        self._current_session = session_id or f"session_{datetime.now(tz=UTC).isoformat()}"
        self._turn_count = 0
        return self._current_session

    def add_message(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """Add a message to conversation history."""
        self._turn_count += 1
        return self.store(
            content=content,
            importance=0.6 if role == "user" else 0.5,
            tags=["conversation", role],
            metadata={
                "role": role,
                "session_id": self._current_session,
                "turn": self._turn_count,
                **(metadata or {}),
            },
        )

    def get_session_history(self, session_id: str | None = None) -> list[MemoryEntry]:
        """Get messages from a session."""
        target_session = session_id or self._current_session
        return sorted(
            [e for e in self._entries.values()
             if e.metadata.get("session_id") == target_session],
            key=lambda e: e.metadata.get("turn", 0),
        )

    def get_recent_messages(self, count: int = 10) -> list[MemoryEntry]:
        """Get recent messages across all sessions."""
        return sorted(
            self._entries.values(),
            key=lambda e: e.created_at,
            reverse=True,
        )[:count]

    def get_user_messages(self, limit: int = 50) -> list[MemoryEntry]:
        """Get all user messages."""
        return [
            e for e in self._entries.values()
            if e.metadata.get("role") == "user"
        ][:limit]

    def get_context_window(self, window_size: int = 5) -> list[dict[str, str]]:
        """Get recent messages as context window for LLM."""
        recent = self.get_recent_messages(window_size)
        return [
            {"role": e.metadata.get("role", "unknown"), "content": e.content}
            for e in reversed(recent)
        ]

    def get_turn_count(self) -> int:
        """Get current session turn count."""
        return self._turn_count

    def summarize_session(self) -> str:
        """Generate a summary of the current session."""
        history = self.get_session_history()
        if not history:
            return "No conversation history"

        user_msgs = [e for e in history if e.metadata.get("role") == "user"]
        assistant_msgs = [e for e in history if e.metadata.get("role") == "assistant"]

        summary_parts = [
            f"Session: {self._current_session}",
            f"Turns: {len(history)}",
            f"User messages: {len(user_msgs)}",
            f"Assistant messages: {len(assistant_msgs)}",
        ]

        if user_msgs:
            topics = set()
            for msg in user_msgs[:5]:
                words = msg.content.lower().split()[:3]
                topics.update(words)
            summary_parts.append(f"Topics: {', '.join(list(topics)[:5])}")

        return " | ".join(summary_parts)
