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
from ke.llm.manager import LLMManager


class CognitiveEngine:
    """
    Main cognitive engine that orchestrates the AI reasoning pipeline.

    Flow:
    1. Intent Detection - Understand what the user wants
    2. Memory Integration - Load relevant memories
    3. RAG Retrieval - Find relevant knowledge
    4. Reasoning - Process and synthesize
    5. Response Generation - Generate response via LLM
    """

    def __init__(self, config: KeConfig):
        self.config = config
        self.memory_integrator = MemoryIntegrator(config)
        self.rag_pipeline = RAGPipeline(config)
        self.intent_detector = IntentDetector()
        self.llm_manager = LLMManager()

    async def process(
        self,
        message: str,
        conversation_history: list[dict[str, str]] | None = None,
        session_id: str | None = None,
        provider: str | None = None,
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

        # Step 5: Generate Response (streaming via LLM Manager)
        self._response_buffer = []
        try:
            messages = [
                {"role": "system", "content": "You are Knowledge Engine AI, a helpful assistant powered by a knowledge base."},
                {"role": "user", "content": context},
            ]

            async for token in self.llm_manager.stream_chat(
                messages=messages,
                provider=provider,
                temperature=0.7,
                max_tokens=2048,
            ):
                self._response_buffer.append(token)
                yield {"type": "token", "data": token}

        except Exception as e:
            # Fallback to template-based response
            fallback = self._generate_fallback_response(context)
            for word in fallback.split():
                token = word + " "
                self._response_buffer.append(token)
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
            "provider": provider or "auto",
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

        # Intent context
        parts.append(f"[Intent: {intent.type.value}]")
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

    def _generate_fallback_response(self, context: str) -> str:
        """Generate a fallback response when LLM is not available."""
        lines = context.split("\n")
        source_content = []
        in_sources = False

        for line in lines:
            if "[Knowledge Base]" in line:
                in_sources = True
                continue
            if in_sources and line.strip():
                source_content.append(line)
            if "[User Question]" in line:
                break

        response = "Based on the knowledge base, here's what I found:\n\n"
        if source_content:
            for line in source_content[:10]:
                response += f"{line}\n"
        else:
            response += "I don't have specific information about this. Could you provide more details?"

        return response

    def _source_to_dict(self, source: QueryResult) -> dict:
        """Convert QueryResult to dictionary."""
        return {
            "id": source.entry.id,
            "content": source.entry.content[:200],
            "source_type": source.entry.source_type,
            "source_path": source.entry.source_path,
            "score": source.score,
        }
