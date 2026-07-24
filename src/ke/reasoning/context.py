"""Context builder for the reasoning pipeline."""

from __future__ import annotations

from typing import Any

from ke.reasoning.models import Intent, ReasoningContext


class ContextBuilder:
    """Build and manage reasoning context from various sources."""

    def __init__(self):
        self._context: ReasoningContext | None = None

    def build(
        self,
        query: str,
        intent: Intent | None = None,
        retrieved_entries: list[Any] | None = None,
        memory_entries: list[Any] | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        metadata: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> ReasoningContext:
        """Build a reasoning context from components."""
        self._context = ReasoningContext(
            user_query=query,
            intent=intent,
            retrieved_entries=retrieved_entries or [],
            memory_entries=memory_entries or [],
            conversation_history=conversation_history or [],
            metadata=metadata or {},
            session_id=session_id,
        )
        return self._context

    def build_from_pipeline(
        self,
        query: str,
        pipeline: Any,
        intent: Intent | None = None,
    ) -> ReasoningContext:
        """Build context using the existing query pipeline."""
        # Retrieve entries using the pipeline
        retrieved = []
        try:
            results = pipeline.query(query, limit=10)
            retrieved = [r.entry for r in results]
        except Exception:
            pass

        # Get memory entries if available
        memory = []
        try:
            if hasattr(pipeline, "metadata_store"):
                memory = pipeline.metadata_store.search_content(query, limit=5)
        except Exception:
            pass

        return self.build(
            query=query,
            intent=intent,
            retrieved_entries=retrieved,
            memory_entries=memory,
        )

    def add_retrieved_entries(self, entries: list[Any]) -> ReasoningContext:
        """Add retrieved entries to the context."""
        if self._context is None:
            raise ValueError("Context not initialized. Call build() first.")

        self._context.retrieved_entries.extend(entries)
        return self._context

    def add_memory_entries(self, entries: list[Any]) -> ReasoningContext:
        """Add memory entries to the context."""
        if self._context is None:
            raise ValueError("Context not initialized. Call build() first.")

        self._context.memory_entries.extend(entries)
        return self._context

    def add_conversation_turn(self, role: str, content: str) -> ReasoningContext:
        """Add a conversation turn to the context."""
        if self._context is None:
            raise ValueError("Context not initialized. Call build() first.")

        self._context.conversation_history.append({
            "role": role,
            "content": content,
        })
        return self._context

    def update_metadata(self, key: str, value: Any) -> ReasoningContext:
        """Update context metadata."""
        if self._context is None:
            raise ValueError("Context not initialized. Call build() first.")

        self._context.metadata[key] = value
        return self._context

    def get_context(self) -> ReasoningContext:
        """Get the current context."""
        if self._context is None:
            raise ValueError("Context not initialized. Call build() first.")
        return self._context

    def clear(self) -> None:
        """Clear the current context."""
        self._context = None

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the current context."""
        if self._context is None:
            return {"status": "empty"}

        return {
            "query": self._context.user_query,
            "intent": self._context.intent.type.value if self._context.intent else None,
            "retrieved_count": len(self._context.retrieved_entries),
            "memory_count": len(self._context.memory_entries),
            "conversation_turns": len(self._context.conversation_history),
            "metadata_keys": list(self._context.metadata.keys()),
            "session_id": self._context.session_id,
        }
