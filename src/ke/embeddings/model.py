"""Embedding model wrapper with lazy loading."""

from __future__ import annotations

from typing import Any


class EmbeddingModel:
    """Wrapper around sentence-transformers with lazy loading."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model: Any = None

    def _load_model(self) -> Any:
        """Lazy load the sentence-transformers model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        model = self._load_model()
        embedding = model.encode(text, show_progress_bar=False)
        return embedding.tolist()

    def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []
        model = self._load_model()
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
            batch_size=batch_size,
        )
        return [e.tolist() for e in embeddings]

    def similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        model = self._load_model()
        embeddings = model.encode([text1, text2], show_progress_bar=False)
        import numpy as np

        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        model = self._load_model()
        return model.get_sentence_embedding_dimension()
