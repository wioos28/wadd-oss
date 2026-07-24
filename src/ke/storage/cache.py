"""Local shelve-based cache for frequently accessed data."""

from __future__ import annotations

import shelve
from pathlib import Path
from typing import Any


class LocalCache:
    """Simple key-value cache using Python's shelve module."""

    def __init__(self, cache_path: Path | str):
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._db: shelve.Shelf | None = None

    def _open(self) -> shelve.Shelf:
        if self._db is None:
            self._db = shelve.open(str(self.cache_path), flag="c")
        return self._db

    def get(self, key: str) -> Any | None:
        """Get a value from cache."""
        db = self._open()
        return db.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set a value in cache."""
        db = self._open()
        db[key] = value
        db.sync()

    def delete(self, key: str) -> None:
        """Delete a value from cache."""
        db = self._open()
        if key in db:
            del db[key]
            db.sync()

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        db = self._open()
        return key in db

    def keys(self) -> list[str]:
        """Get all keys in cache."""
        db = self._open()
        return list(db.keys())

    def clear(self) -> None:
        """Clear all entries from cache."""
        db = self._open()
        db.clear()
        db.sync()

    def close(self) -> None:
        """Close the cache."""
        if self._db is not None:
            self._db.close()
            self._db = None

    def __enter__(self) -> LocalCache:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
