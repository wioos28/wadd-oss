"""User Account Storage - Persistent user accounts using ChromaDB Cloud."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import hashlib
import secrets

from ke.config import ChromaDBCloudConfig
from ke.storage.cloud import CloudVectorStore


class UserAccount:
    """A user account."""

    def __init__(
        self,
        username: str,
        email: str,
        password_hash: str | None = None,
        user_id: str | None = None,
        created_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.user_id = user_id or str(uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now(tz=UTC)
        self.metadata = metadata or {}

    def to_metadata(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash or "",
            "created_at": self.created_at.isoformat(),
            "type": "user_account",
            **self.metadata,
        }

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return f"{salt}:{password_hash}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        if ":" not in password_hash:
            return False
        salt, stored_hash = password_hash.split(":", 1)
        computed_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return computed_hash == stored_hash


class AccountStore:
    """User account storage using ChromaDB Cloud."""

    def __init__(self, config: ChromaDBCloudConfig):
        self.config = config
        self._cloud: CloudVectorStore | None = None
        self._collection: Any = None

    @property
    def cloud(self) -> CloudVectorStore:
        if self._cloud is None:
            self._cloud = CloudVectorStore(self.config)
        return self._cloud

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.cloud.client.get_or_create_collection(
                name="user_accounts",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def create_account(
        self,
        username: str,
        email: str,
        password: str,
        metadata: dict[str, Any] | None = None,
    ) -> UserAccount:
        """Create a new user account."""
        # Check if username already exists
        if self.get_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        # Check if email already exists
        if self.get_by_email(email):
            raise ValueError(f"Email '{email}' already exists")

        account = UserAccount(
            username=username,
            email=email,
            password_hash=UserAccount.hash_password(password),
            metadata=metadata,
        )

        # Store in ChromaDB
        self.collection.upsert(
            ids=[account.user_id],
            documents=[f"{username} {email}"],
            metadatas=[account.to_metadata()],
        )

        return account

    def get_by_id(self, user_id: str) -> UserAccount | None:
        """Get user by ID."""
        results = self.collection.get(
            ids=[user_id],
            include=["documents", "metadatas"],
        )
        if not results["ids"]:
            return None
        return self._parse_account(results["ids"][0], results["metadatas"][0])

    def get_by_username(self, username: str) -> UserAccount | None:
        """Get user by username."""
        results = self.collection.get(
            where={"username": username},
            include=["documents", "metadatas"],
        )
        if not results["ids"]:
            return None
        return self._parse_account(results["ids"][0], results["metadatas"][0])

    def get_by_email(self, email: str) -> UserAccount | None:
        """Get user by email."""
        results = self.collection.get(
            where={"email": email},
            include=["documents", "metadatas"],
        )
        if not results["ids"]:
            return None
        return self._parse_account(results["ids"][0], results["metadatas"][0])

    def authenticate(self, username: str, password: str) -> UserAccount | None:
        """Authenticate user with username and password."""
        account = self.get_by_username(username)
        if not account:
            return None
        if not account.password_hash:
            return None
        if not UserAccount.verify_password(password, account.password_hash):
            return None
        return account

    def update_account(
        self,
        user_id: str,
        email: str | None = None,
        password: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UserAccount | None:
        """Update user account."""
        account = self.get_by_id(user_id)
        if not account:
            return None

        if email:
            existing = self.get_by_email(email)
            if existing and existing.user_id != user_id:
                raise ValueError(f"Email '{email}' already exists")
            account.email = email

        if password:
            account.password_hash = UserAccount.hash_password(password)

        if metadata:
            account.metadata.update(metadata)

        # Update in ChromaDB
        self.collection.upsert(
            ids=[account.user_id],
            documents=[f"{account.username} {account.email}"],
            metadatas=[account.to_metadata()],
        )

        return account

    def delete_account(self, user_id: str) -> bool:
        """Delete user account."""
        account = self.get_by_id(user_id)
        if not account:
            return False
        self.collection.delete(ids=[user_id])
        return True

    def list_accounts(self, limit: int = 100) -> list[UserAccount]:
        """List all user accounts."""
        results = self.collection.get(
            include=["documents", "metadatas"],
            limit=limit,
        )
        accounts = []
        if results["ids"] and results["metadatas"]:
            for i, user_id in enumerate(results["ids"]):
                meta = results["metadatas"][i] if i < len(results["metadatas"]) else {}
                if meta.get("type") == "user_account":
                    accounts.append(self._parse_account(user_id, meta))
        return accounts

    def count(self) -> int:
        """Get total number of accounts."""
        results = self.collection.get(include=["metadatas"])
        count = 0
        if results["metadatas"]:
            for meta in results["metadatas"]:
                if meta.get("type") == "user_account":
                    count += 1
        return count

    def _parse_account(self, user_id: str, metadata: dict) -> UserAccount:
        """Parse metadata into UserAccount."""
        return UserAccount(
            user_id=user_id,
            username=metadata.get("username", ""),
            email=metadata.get("email", ""),
            password_hash=metadata.get("password_hash") or None,
            created_at=datetime.fromisoformat(metadata["created_at"]) if "created_at" in metadata else None,
            metadata={k: v for k, v in metadata.items() if k not in ("username", "email", "password_hash", "created_at", "type")},
        )

    def close(self) -> None:
        """Clean up resources."""
        if self._cloud:
            self._cloud.close()
            self._cloud = None
        self._collection = None

    def __enter__(self) -> AccountStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
