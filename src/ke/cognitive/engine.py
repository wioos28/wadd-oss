"""Cognitive Engine - Main orchestrator for the AI reasoning system."""

from __future__ import annotations

from typing import Any, AsyncGenerator
from datetime import datetime

from ke.config import KeConfig
from ke.domain.models import (
    KnowledgeEntry,
    QueryResult,
    ChatMessage,
    MessageRole,
    MemoryEntry,
    MemoryType,
)
from ke.cognitive.memory_integration import MemoryIntegrator
from ke.cognitive.rag_pipeline import RAGPipeline
from ke.cognitive.intent_detector import IntentDetector, Intent


class CognitiveEngine:
    """
    Main cognitive engine that orchestrates the AI reasoning pipeline.

    Flow:
    1. Intent Detection - Understand what the user wants
    2. Memory Integration - Load relevant memories
    3. RAG Retrieval - Find relevant knowledge
    4. Reasoning - Process and synthesize
    5. Response Generation - Generate response
    """

    def __init__(self, config: KeConfig):
        self.config = config
        self.memory_integrator = MemoryIntegrator(config)
        self.rag_pipeline = RAGPipeline(config)
        self.intent_detector = IntentDetector()
        self._llm_client = None

    @property
    def llm_client(self):
        """Lazy-load LLM client."""
        if self._llm_client is None:
            from ke.llm.client import LLMClient
            self._llm_client = LLMClient()
        return self._llm_client

    async def process(
        self,
        message: str,
        conversation_history: list[dict[str, str]] | None = None,
        session_id: str | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Process a user message through the cognitive pipeline.

        Yields events:
        - {"type": "intent", "data": Intent}
        - {"type": "memory", "data": {"short_term": [...], "long_term": [...]}}
        - {"type": "sources", "data": [QueryResult]}
        - {"type": "token", "data": str}
        - {"type": "done", "data": {...}}
        """
        # Step 1: Intent Detection
        intent = self.intent_detector.detect(message)
        yield {"type": "intent", "data": intent}

        # Step 2: Memory Integration
        memory_context = await self.memory_integrator.integrate(
            message=message,
            conversation_history=conversation_history or [],
            session_id=session_id,
        )
        yield {"type": "memory", "data": memory_context}

        # Step 3: RAG Retrieval
        sources = await self.rag_pipeline.retrieve(
            query=message,
            intent=intent,
            memory_context=memory_context,
        )
        yield {"type": "sources", "data": [self._source_to_dict(s) for s in sources]}

        # Step 4: Build Context
        context = self._build_context(
            message=message,
            intent=intent,
            memory_context=memory_context,
            sources=sources,
            conversation_history=conversation_history or [],
        )

        # Step 5: Generate Response (streaming)
        async for token in self._generate_response(context):
            yield {"type": "token", "data": token}

        # Step 6: Store in Memory
        await self.memory_integrator.store_interaction(
            user_message=message,
            assistant_response="".join(self._response_buffer),
            session_id=session_id,
        )

        yield {"type": "done", "data": {
            "session_id": session_id,
            "intent": intent.type.value,
            "sources_count": len(sources),
        }}

    def _build_context(
        self,
        message: str,
        intent: Intent,
        memory_context: dict[str, Any],
        sources: list[QueryResult],
        conversation_history: list[dict[str, str]],
    ) -> str:
        """Build the context for LLM generation."""
        parts = []

        # System prompt
        parts.append("""You are Knowledge Engine AI, a helpful assistant powered by a knowledge base.
Answer questions accurately based on the provided context and memories.
Be concise, clear, and helpful. If you don't know, say so.""")

        # Intent context
        parts.append(f"\n[Intent: {intent.type.value}]")
        if intent.entities:
            parts.append(f"[Entities: {', '.join(intent.entities)}]")

        # Memory context
        if memory_context.get("short_term"):
            parts.append("\n[Recent Conversation]")
            for mem in memory_context["short_term"][-3:]:
                parts.append(f"- {mem.get('role', 'user')}: {mem.get('content', '')[:200]}")

        if memory_context.get("long_term"):
            parts.append("\n[Relevant Memories]")
            for mem in memory_context["long_term"][:3]:
                parts.append(f"- {mem.get('content', '')[:200]}")

        # Knowledge sources
        if sources:
            parts.append("\n[Knowledge Base]")
            for i, source in enumerate(sources[:5], 1):
                parts.append(f"\nSource {i} ({source.entry.source_type}):")
                parts.append(source.entry.content[:500])

        # Conversation history
        if conversation_history:
            parts.append("\n[Conversation History]")
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:200]
                parts.append(f"{role}: {content}")

        # Current question
        parts.append(f"\n[User Question]")
        parts.append(message)

        return "\n".join(parts)

    async def _generate_response(self, context: str) -> AsyncGenerator[str, None]:
        """Generate response using LLM."""
        self._response_buffer = []

        try:
            if self.llm_client.is_available():
                # Use LLM
                response = await self._run_in_executor(
                    self.llm_client.complete_with_system,
                    "You are a helpful AI assistant.",
                    context,
                )

                # Stream tokens
                for word in response.split():
                    token = word + " "
                    self._response_buffer.append(token)
                    yield token
            else:
                # Fallback: Generate based on context
                response = self._generate_fallback_response(context)
                for word in response.split():
                    token = word + " "
                    self._response_buffer.append(token)
                    yield token

        except Exception as e:
            error_msg = f"I encountered an error processing your request: {str(e)}"
            self._response_buffer.append(error_msg)
            yield error_msg

    def _generate_fallback_response(self, context: str) -> str:
        """Generate a fallback response when LLM is not available."""
        # Extract relevant information from context
        lines = context.split("\n")
        relevant_lines = []
        capture = False

        for line in lines:
            if "[User Question]" in line:
                capture = True
                continue
            if capture and line.strip():
                relevant_lines.append(line)

        question = " ".join(relevant_lines) if relevant_lines else "your question"

        # Build response from knowledge sources
        response = f"Based on the knowledge base, here's what I found about your question:\n\n"

        in_sources = False
        source_content = []
        for line in lines:
            if "[Knowledge Base]" in line:
                in_sources = True
                continue
            if in_sources and line.strip():
                source_content.append(line)
            if "[User Question]" in line:
                break

        if source_content:
            for line in source_content[:10]:
                response += f"{line}\n"
        else:
            response += "I don't have specific information about this in my knowledge base. Could you provide more details or try a different query?"

        return response

    async def _run_in_executor(self, func, *args):
        """Run a synchronous function in an executor."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

    def _source_to_dict(self, source: QueryResult) -> dict:
        """Convert QueryResult to dictionary."""
        return {
            "id": source.entry.id,
            "content": source.entry.content[:200],
            "source_type": source.entry.source_type,
            "source_path": source.entry.source_path,
            "score": source.score,
        }
