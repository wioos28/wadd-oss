"""API Key Store - Persistent storage for API keys."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class APIKeyRecord:
    """API Key record stored in database."""
    id: str
    user_id: str
    key_hash: str
    name: str
    prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    metadata: dict | None = None


class APIKeyStore:
    """
    SQLite-based API Key storage.

    Features:
    - Secure storage (only hashes stored)
    - Active/inactive status
    - Expiration support
    - Usage tracking
    """

    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path.home() / ".knowledge-engine" / "api_keys.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    key_hash TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    prefix TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_used_at TEXT,
                    expires_at TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_keys_user_id
                ON api_keys(user_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash
                ON api_keys(key_hash)
            """)
            conn.commit()

    def create_key(
        self,
        user_id: str,
        key_hash: str,
        name: str,
        prefix: str,
        expires_at: datetime | None = None,
        metadata: dict | None = None,
    ) -> APIKeyRecord:
        """Create a new API key record."""
        import uuid
        import json

        key_id = str(uuid.uuid4())
        now = datetime.utcnow()

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO api_keys (id, user_id, key_hash, name, prefix, is_active, created_at, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    key_id,
                    user_id,
                    key_hash,
                    name,
                    prefix,
                    True,
                    now.isoformat(),
                    expires_at.isoformat() if expires_at else None,
                    json.dumps(metadata) if metadata else None,
                ),
            )
            conn.commit()

        return APIKeyRecord(
            id=key_id,
            user_id=user_id,
            key_hash=key_hash,
            name=name,
            prefix=prefix,
            is_active=True,
            created_at=now,
            last_used_at=None,
            expires_at=expires_at,
            metadata=metadata,
        )

    def verify_key(self, key_hash: str) -> APIKeyRecord | None:
        """
        Verify an API key and return its record.

        Returns:
            APIKeyRecord if valid, None if invalid or expired
        """
        import json

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT * FROM api_keys WHERE key_hash = ?",
                (key_hash,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Parse the record
            record = self._row_to_record(row)

            # Check if active
            if not record.is_active:
                return None

            # Check expiration
            if record.expires_at and record.expires_at < datetime.utcnow():
                return None

            # Update last used
            self._update_last_used(record.id)

            return record

    def _update_last_used(self, key_id: str):
        """Update the last_used_at timestamp."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "UPDATE api_keys SET last_used_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), key_id),
            )
            conn.commit()

    def deactivate_key(self, key_id: str) -> bool:
        """Deactivate an API key."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "UPDATE api_keys SET is_active = 0 WHERE id = ?",
                (key_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def activate_key(self, key_id: str) -> bool:
        """Activate an API key."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "UPDATE api_keys SET is_active = 1 WHERE id = ?",
                (key_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_key(self, key_id: str) -> bool:
        """Permanently delete an API key."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "DELETE FROM api_keys WHERE id = ?",
                (key_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_key(self, key_id: str) -> APIKeyRecord | None:
        """Get an API key by ID."""
        import json

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT * FROM api_keys WHERE id = ?",
                (key_id,),
            )
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None

    def list_user_keys(self, user_id: str) -> list[APIKeyRecord]:
        """List all API keys for a user."""
        import json

        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT * FROM api_keys WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,),
            )
            return [self._row_to_record(row) for row in cursor.fetchall()]

    def count_active_keys(self, user_id: str) -> int:
        """Count active API keys for a user."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM api_keys WHERE user_id = ? AND is_active = 1",
                (user_id,),
            )
            return cursor.fetchone()[0]

    def _row_to_record(self, row: tuple) -> APIKeyRecord:
        """Convert a database row to APIKeyRecord."""
        import json

        return APIKeyRecord(
            id=row[0],
            user_id=row[1],
            key_hash=row[2],
            name=row[3],
            prefix=row[4],
            is_active=bool(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            last_used_at=datetime.fromisoformat(row[7]) if row[7] else None,
            expires_at=datetime.fromisoformat(row[8]) if row[8] else None,
            metadata=json.loads(row[9]) if row[9] else None,
        )
