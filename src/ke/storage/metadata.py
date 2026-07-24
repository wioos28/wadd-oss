"""SQLite metadata store for knowledge entries."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ke.core.models import KnowledgeEntry, Relationship


class MetadataStore:
    """SQLite-based metadata storage for knowledge entries and relationships."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    summary TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    source_path TEXT,
                    source_type TEXT DEFAULT 'manual',
                    confidence_score REAL DEFAULT 0.5,
                    confidence_source TEXT DEFAULT 'reasoning',
                    confidence_explanation TEXT DEFAULT '',
                    metadata TEXT DEFAULT '{}',
                    embedding_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS relationships (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (source_id, target_id, relationship_type),
                    FOREIGN KEY (source_id) REFERENCES knowledge(id),
                    FOREIGN KEY (target_id) REFERENCES knowledge(id)
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    data TEXT DEFAULT '{}',
                    timestamp TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge(source_path);
                CREATE INDEX IF NOT EXISTS idx_knowledge_source_type ON knowledge(source_type);
                CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge(created_at);
                CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id);
                CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id);
                CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(event_type);
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
            """)

    def add_entry(self, entry: KnowledgeEntry) -> None:
        """Add a knowledge entry to the store."""
        with self.conn:
            self.conn.execute(
                """INSERT OR REPLACE INTO knowledge
                   (id, content, summary, tags, source_path, source_type,
                    confidence_score, confidence_source, confidence_explanation,
                    metadata, embedding_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    entry.id,
                    entry.content,
                    entry.summary,
                    json.dumps(entry.tags),
                    entry.source_path,
                    entry.source_type,
                    entry.confidence.score,
                    entry.confidence.source,
                    entry.confidence.explanation,
                    json.dumps(entry.metadata),
                    entry.embedding_id,
                    entry.created_at.isoformat(),
                    entry.updated_at.isoformat(),
                ),
            )

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """Retrieve a knowledge entry by ID."""
        row = self.conn.execute(
            "SELECT * FROM knowledge WHERE id = ?", (entry_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_entry(row)

    def search_content(self, query: str, limit: int = 10) -> list[KnowledgeEntry]:
        """Full-text search on knowledge content."""
        rows = self.conn.execute(
            """SELECT * FROM knowledge
               WHERE content LIKE ? OR summary LIKE ? OR tags LIKE ?
               LIMIT ?""",
            (f"%{query}%", f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def search_by_tags(self, tags: list[str], limit: int = 10) -> list[KnowledgeEntry]:
        """Search entries by tags."""
        conditions = " OR ".join(["tags LIKE ?"] * len(tags))
        params = [f'%"{tag}"%' for tag in tags] + [limit]
        rows = self.conn.execute(
            f"SELECT * FROM knowledge WHERE {conditions} LIMIT ?",
            params,
        ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def search_by_source(self, source_path: str) -> list[KnowledgeEntry]:
        """Search entries by source file path."""
        rows = self.conn.execute(
            "SELECT * FROM knowledge WHERE source_path = ?", (source_path,)
        ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def list_entries(
        self,
        source_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeEntry]:
        """List entries with optional filtering."""
        query = "SELECT * FROM knowledge"
        params: list[Any] = []
        if source_type:
            query += " WHERE source_type = ?"
            params.append(source_type)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def count_entries(self) -> int:
        """Count total knowledge entries."""
        row = self.conn.execute("SELECT COUNT(*) as cnt FROM knowledge").fetchone()
        return row["cnt"] if row else 0

    def add_relationship(self, rel: Relationship) -> None:
        """Add a relationship between two entries."""
        with self.conn:
            self.conn.execute(
                """INSERT OR REPLACE INTO relationships
                   (source_id, target_id, relationship_type, weight, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (rel.source_id, rel.target_id, rel.relationship_type, rel.weight, rel.created_at.isoformat()),
            )

    def get_relationships(self, entry_id: str) -> list[Relationship]:
        """Get all relationships for an entry (both directions)."""
        rows = self.conn.execute(
            """SELECT * FROM relationships
               WHERE source_id = ? OR target_id = ?""",
            (entry_id, entry_id),
        ).fetchall()
        return [
            Relationship(
                source_id=row["source_id"],
                target_id=row["target_id"],
                relationship_type=row["relationship_type"],
                weight=row["weight"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def get_related_entries(self, entry_id: str, limit: int = 10) -> list[KnowledgeEntry]:
        """Get knowledge entries related to the given entry."""
        rels = self.conn.execute(
            """SELECT k.* FROM knowledge k
               JOIN relationships r ON (k.id = r.target_id OR k.id = r.source_id)
               WHERE (r.source_id = ? OR r.target_id = ?) AND k.id != ?
               ORDER BY r.weight DESC
               LIMIT ?""",
            (entry_id, entry_id, entry_id, limit),
        ).fetchall()
        return [self._row_to_entry(row) for row in rels]

    def log_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """Log an event."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO logs (event_type, data, timestamp) VALUES (?, ?, ?)",
                (event_type, json.dumps(data or {}), datetime.now(tz=UTC).isoformat()),
            )

    def _row_to_entry(self, row: sqlite3.Row) -> KnowledgeEntry:
        """Convert a database row to a KnowledgeEntry."""
        return KnowledgeEntry(
            id=row["id"],
            content=row["content"],
            summary=row["summary"],
            tags=json.loads(row["tags"]),
            source_path=row["source_path"],
            source_type=row["source_type"],
            confidence=__import__("ke.core.models", fromlist=["Confidence"]).Confidence(
                score=row["confidence_score"],
                source=row["confidence_source"],
                explanation=row["confidence_explanation"],
            ),
            metadata=json.loads(row["metadata"]),
            embedding_id=row["embedding_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __enter__(self) -> MetadataStore:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
