"""Chat History Storage - Persistent chat history using ChromaDB Cloud."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from ke.config import ChromaDBCloudConfig
from ke.storage.cloud import CloudVectorStore


class ChatMessage:
    """A single chat message."""

    def __init__(
        self,
        role: str,
        content: str,
        session_id: str,
        turn: int,
        timestamp: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        message_id: str | None = None,
    ):
        self.message_id = message_id or str(uuid4())
        self.role = role
        self.content = content
        self.session_id = session_id
        self.turn = turn
        self.timestamp = timestamp or datetime.now(tz=UTC)
        self.metadata = metadata or {}

    def to_metadata(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "session_id": self.session_id,
            "turn": self.turn,
            "timestamp": self.timestamp.isoformat(),
            **self.metadata,
        }


class ChatHistoryStore:
    """Persistent chat history storage using ChromaDB Cloud."""

    def __init__(self, config: ChromaDBCloudConfig):
        self.config = config
        self._cloud: CloudVectorStore | None = None
        self._current_session: str | None = None
        self._turn_count: int = 0

    @property
    def cloud(self) -> CloudVectorStore:
        if self._cloud is None:
            self._cloud = CloudVectorStore(self.config)
        return self._cloud

    def start_session(self, session_id: str | None = None) -> str:
        """Start a new chat session."""
        self._current_session = session_id or f"session_{datetime.now(tz=UTC).isoformat()}"
        self._turn_count = 0
        return self._current_session

    def add_message(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        """Add a message to chat history."""
        self._turn_count += 1
        msg = ChatMessage(
            role=role,
            content=content,
            session_id=self._current_session or "default",
            turn=self._turn_count,
            metadata=metadata,
        )

        # Store in ChromaDB with a simple embedding (content itself as document)
        self.cloud.chat_collection.upsert(
            ids=[msg.message_id],
            documents=[content],
            metadatas=[msg.to_metadata()],
        )

        return msg

    def get_session_history(self, session_id: str | None = None) -> list[ChatMessage]:
        """Get messages from a session."""
        target_session = session_id or self._current_session
        if not target_session:
            return []

        results = self.cloud.chat_collection.get(
            where={"session_id": target_session},
            include=["documents", "metadatas"],
        )

        messages = []
        if results["ids"]:
            for i, msg_id in enumerate(results["ids"]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                messages.append(ChatMessage(
                    message_id=msg_id,
                    role=meta.get("role", "unknown"),
                    content=results["documents"][0][i] if results["documents"] else "",
                    session_id=meta.get("session_id", target_session),
                    turn=meta.get("turn", 0),
                    timestamp=datetime.fromisoformat(meta["timestamp"]) if "timestamp" in meta else None,
                    metadata={k: v for k, v in meta.items() if k not in ("role", "session_id", "turn", "timestamp")},
                ))

        return sorted(messages, key=lambda m: m.turn)

    def get_recent_messages(self, count: int = 10) -> list[ChatMessage]:
        """Get recent messages across all sessions."""
        results = self.cloud.chat_collection.get(
            include=["documents", "metadatas"],
        )

        messages = []
        if results["ids"]:
            for i, msg_id in enumerate(results["ids"]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                messages.append(ChatMessage(
                    message_id=msg_id,
                    role=meta.get("role", "unknown"),
                    content=results["documents"][0][i] if results["documents"] else "",
                    session_id=meta.get("session_id", ""),
                    turn=meta.get("turn", 0),
                    timestamp=datetime.fromisoformat(meta["timestamp"]) if "timestamp" in meta else None,
                ))

        return sorted(messages, key=lambda m: m.timestamp or datetime.min, reverse=True)[:count]

    def get_context_window(self, window_size: int = 5) -> list[dict[str, str]]:
        """Get recent messages as context window for LLM."""
        recent = self.get_recent_messages(window_size)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(recent)
        ]

    def search_messages(self, query: str, limit: int = 5) -> list[ChatMessage]:
        """Search messages by content."""
        results = self.cloud.chat_collection.query(
            query_texts=[query],
            n_results=limit,
        )

        messages = []
        if results["ids"] and results["ids"][0]:
            for i, msg_id in enumerate(results["ids"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                messages.append(ChatMessage(
                    message_id=msg_id,
                    role=meta.get("role", "unknown"),
                    content=results["documents"][0][i] if results["documents"] else "",
                    session_id=meta.get("session_id", ""),
                    turn=meta.get("turn", 0),
                    timestamp=datetime.fromisoformat(meta["timestamp"]) if "timestamp" in meta else None,
                ))

        return messages

    def delete_session(self, session_id: str) -> None:
        """Delete all messages in a session."""
        results = self.cloud.chat_collection.get(
            where={"session_id": session_id},
            include=["ids"],
        )
        if results["ids"]:
            self.cloud.chat_collection.delete(ids=results["ids"])

    def count(self) -> int:
        """Get total number of messages."""
        return self.cloud.chat_collection.count()

    def close(self) -> None:
        """Clean up resources."""
        if self._cloud:
            self._cloud.close()
            self._cloud = None

    def __enter__(self) -> ChatHistoryStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
