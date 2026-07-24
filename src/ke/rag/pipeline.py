"""RAG Pipeline - Retrieval-Augmented Generation.

Flow: Knowledge → Top N Chunks → Prompt Builder → LLM → Answer
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from ke.config import KeConfig
from ke.core.models import QueryMode
from ke.core.pipeline import QueryPipeline
from ke.llm.client import LLMClient


@dataclass
class RAGResult:
    """Result from RAG pipeline."""

    query: str
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    chunks_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    processing_time_ms: float = 0.0
    model: str = ""


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline.

    Flow:
        1. Retrieve top N chunks from knowledge base
        2. Build prompt with chunks as context
        3. Call LLM to generate answer
        4. Return answer with sources
    """

    def __init__(
        self,
        config: KeConfig | None = None,
        llm_client: LLMClient | None = None,
        top_k: int = 10,
        max_context_length: int = 8000,
        system_prompt: str | None = None,
    ):
        self.config = config
        self.top_k = top_k
        self.max_context_length = max_context_length
        self.system_prompt = system_prompt or self._default_system_prompt()

        # Initialize components
        self.llm = llm_client or LLMClient()
        self.knowledge_pipeline: QueryPipeline | None = None

        if config:
            self.knowledge_pipeline = QueryPipeline(config)

    def _default_system_prompt(self) -> str:
        return """You are a helpful AI assistant that answers questions based on the provided knowledge base context.

Rules:
1. Answer based ONLY on the provided context when possible
2. If the context doesn't contain enough information, say so clearly
3. Cite specific sources when referencing information
4. Be concise and accurate
5. If multiple sources conflict, mention the discrepancy"""

    def query(
        self,
        question: str,
        top_k: int | None = None,
        mode: str = "hybrid",
        min_score: float = 0.3,
    ) -> RAGResult:
        """Execute RAG query.

        Args:
            question: User's question
            top_k: Number of chunks to retrieve (overrides default)
            mode: Retrieval mode (semantic, keyword, hybrid)
            min_score: Minimum relevance score

        Returns:
            RAGResult with answer and sources
        """
        start_time = time.time()
        k = top_k or self.top_k

        # Step 1: Retrieve top N chunks
        chunks = self._retrieve_chunks(question, k, mode, min_score)

        # Step 2: Build prompt with context
        prompt = self._build_rag_prompt(question, chunks)

        # Step 3: Call LLM
        answer = self.llm.complete_with_system(self.system_prompt, prompt)

        # Step 4: Build result
        sources = self._extract_sources(chunks)

        return RAGResult(
            query=question,
            answer=answer,
            sources=sources,
            chunks_used=len(chunks),
            processing_time_ms=(time.time() - start_time) * 1000,
            model=self.llm.model,
        )

    def _retrieve_chunks(
        self,
        query: str,
        top_k: int,
        mode: str,
        min_score: float,
    ) -> list[Any]:
        """Retrieve top N chunks from knowledge base."""
        if not self.knowledge_pipeline:
            return []

        try:
            results = self.knowledge_pipeline.query(
                text=query,
                mode=mode,
                limit=top_k,
                min_score=min_score,
            )
            return [r.entry for r in results]
        except Exception:
            return []

    def _build_rag_prompt(self, question: str, chunks: list[Any]) -> str:
        """Build prompt with question and context chunks."""
        parts = []

        # Context section
        parts.append("## Context from Knowledge Base")
        parts.append("")

        if chunks:
            for i, chunk in enumerate(chunks, 1):
                content = getattr(chunk, "content", str(chunk))
                source = getattr(chunk, "source_path", "unknown")
                chunk_id = getattr(chunk, "id", f"chunk_{i}")

                # Truncate if too long
                max_chunk_length = self.max_context_length // max(len(chunks), 1)
                if len(content) > max_chunk_length:
                    content = content[:max_chunk_length] + "..."

                parts.append(f"### Source {i}: {source}")
                parts.append(f"ID: {chunk_id}")
                parts.append(content)
                parts.append("")
        else:
            parts.append("No relevant context found in knowledge base.")
            parts.append("")

        # Question section
        parts.append("## Question")
        parts.append(question)
        parts.append("")

        # Instructions
        parts.append("## Instructions")
        parts.append("Answer the question based on the context above.")
        parts.append("If the context doesn't contain enough information, say so.")
        parts.append("Cite sources when referencing specific information.")

        prompt = "\n".join(parts)

        # Truncate if too long
        if len(prompt) > self.max_context_length:
            prompt = prompt[: self.max_context_length - 200] + "\n\n[Context truncated]"

        return prompt

    def _extract_sources(self, chunks: list[Any]) -> list[dict[str, Any]]:
        """Extract source information from chunks."""
        sources = []
        for chunk in chunks:
            source = {
                "id": getattr(chunk, "id", "unknown"),
                "content_preview": getattr(chunk, "content", "")[:200],
                "source_path": getattr(chunk, "source_path", ""),
                "source_type": getattr(chunk, "source_type", ""),
                "tags": getattr(chunk, "tags", []),
            }
            sources.append(source)
        return sources

    def chat(
        self,
        question: str,
        history: list[dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> RAGResult:
        """Chat with RAG (supports conversation history)."""
        # Build messages with history
        messages = []

        if history:
            for msg in history[-5:]:  # Last 5 messages
                messages.append(msg)

        # Add current question
        messages.append({"role": "user", "content": question})

        # Retrieve chunks
        chunks = self._retrieve_chunks(
            question,
            kwargs.get("top_k", self.top_k),
            kwargs.get("mode", "hybrid"),
            kwargs.get("min_score", 0.3),
        )

        # Build prompt
        rag_prompt = self._build_rag_prompt(question, chunks)

        # Combine with history
        system_msg = self.system_prompt + "\n\n" + rag_prompt

        # Call LLM
        all_messages = [{"role": "system", "content": system_msg}] + messages
        answer = self.llm.chat(all_messages)

        return RAGResult(
            query=question,
            answer=answer,
            sources=self._extract_sources(chunks),
            chunks_used=len(chunks),
            model=self.llm.model,
        )

    def close(self) -> None:
        """Close resources."""
        if self.knowledge_pipeline:
            self.knowledge_pipeline.close()

    def __enter__(self) -> RAGPipeline:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
