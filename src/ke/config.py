"""Configuration management for the Knowledge Engine."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

DEFAULT_CONFIG_DIR = Path.home() / ".knowledge-engine"
DEFAULT_CONFIG_FILE = Path(__file__).parent.parent.parent / "config" / "default.toml"


class EmbeddingConfig(BaseModel):
    model_name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"
    batch_size: int = 32


class StorageConfig(BaseModel):
    vector_db_path: str = "~/.knowledge-engine/vectors"
    metadata_db_path: str = "~/.knowledge-engine/metadata.db"
    cache_path: str = "~/.knowledge-engine/cache"


class ChunkingConfig(BaseModel):
    strategy: str = "fixed"  # fixed | semantic | sentence
    chunk_size: int = 512
    chunk_overlap: int = 64


class RetrievalConfig(BaseModel):
    default_mode: str = "hybrid"
    max_results: int = 10
    min_score: float = 0.3
    enable_relationships: bool = True


class PipelineConfig(BaseModel):
    layers: list[str] = Field(
        default_factory=lambda: ["cache", "metadata", "vector", "cloud", "internet"]
    )
    cloud_enabled: bool = False
    internet_enabled: bool = False
    internet_requires_permission: bool = True


class SyncConfig(BaseModel):
    provider: str = "local"  # local | s3 | gcs | custom
    remote_url: str = ""


class NetworkConfig(BaseModel):
    check_interval: int = 30
    probes: list[str] = Field(default_factory=lambda: ["dns", "http"])
    quality_threshold_latency_ms: float = 500.0


class EngineConfig(BaseModel):
    version: str = "0.1.0"
    data_dir: str = "~/.knowledge-engine"


class KeConfig(BaseModel):
    engine: EngineConfig = Field(default_factory=EngineConfig)
    embeddings: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    query: PipelineConfig = Field(default_factory=PipelineConfig)
    sync: SyncConfig = Field(default_factory=SyncConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)

    def data_dir_path(self) -> Path:
        return Path(self.engine.data_dir).expanduser()

    def metadata_db_path(self) -> Path:
        return Path(self.storage.metadata_db_path).expanduser()

    def vector_db_path(self) -> Path:
        return Path(self.storage.vector_db_path).expanduser()

    def cache_path(self) -> Path:
        return Path(self.storage.cache_path).expanduser()


def load_config(config_path: Path | None = None) -> KeConfig:
    """Load configuration from TOML file, falling back to defaults."""
    path = config_path or (Path.home() / ".knowledge-engine" / "config.toml")

    data: dict[str, Any] = {}
    if path.exists():
        with open(path, "rb") as f:
            data = tomllib.load(f)

    # Also try loading default config as base
    if DEFAULT_CONFIG_FILE.exists():
        with open(DEFAULT_CONFIG_FILE, "rb") as f:
            default_data = tomllib.load(f)
        # User config overrides defaults
        merged = _deep_merge(default_data, data)
        return KeConfig(**merged)

    return KeConfig(**data)


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, override takes precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def ensure_data_dirs(config: KeConfig) -> None:
    """Create data directories if they don't exist."""
    for path in [
        config.data_dir_path(),
        config.metadata_db_path().parent,
        config.vector_db_path(),
        config.cache_path().parent,
    ]:
        path.mkdir(parents=True, exist_ok=True)
