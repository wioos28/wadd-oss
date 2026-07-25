"""Chat router - Streaming chat with SSE support."""

from __future__ import annotations

import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ke.config import load_config
from ke.api.middleware.auth import get_current_user

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    session_id: str | None = None
    stream: bool = True


class ChatResponse(BaseModel):
    response: str
    sources: list[dict] = []
    session_id: str


# ============================================================================
# SSE Streaming Generator
# ============================================================================

async def stream_tokens(
    message: str,
    history: list[dict],
    session_id: str | None,
) -> AsyncGenerator[str, None]:
    """Stream tokens from LLM using Server-Sent Events."""
    from ke.application.services import QueryService

    config = load_config()
    query_service = QueryService(config)

    try:
        # First, retrieve relevant knowledge
        results = query_service.query(text=message, mode="hybrid", limit=5)

        # Build context from retrieved knowledge
        context_parts = []
        sources = []
        for r in results:
            context_parts.append(f"[Source: {r.entry.source_path or 'unknown'}]\n{r.entry.content}")
            sources.append({
                "id": r.entry.id,
                "content": r.entry.content[:200],
                "source_type": r.entry.source_type,
                "source_path": r.entry.source_path,
                "score": r.score,
            })

        context = "\n\n".join(context_parts) if context_parts else "No relevant context found."

        # Build prompt
        system_prompt = """You are a helpful AI assistant powered by Knowledge Engine.
Answer questions based on the provided context. Be concise and accurate.
If the context doesn't contain relevant information, say so."""

        # Build messages for LLM
        messages = [{"role": "system", "content": system_prompt}]

        # Add history
        for h in history[-5:]:  # Last 5 messages
            messages.append({"role": h["role"], "content": h["content"]})

        # Add current message with context
        user_message = f"""Context from knowledge base:
{context}

User question: {message}

Please answer based on the context above. If the context is not relevant, answer based on your knowledge."""

        messages.append({"role": "user", "content": user_message})

        # Send initial sources as SSE event
        yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"

        # Try to use LLM client for streaming
        try:
            from ke.llm.client import LLMClient

            llm = LLMClient()

            if llm.is_available():
                # Stream response from LLM
                # Note: Current LLMClient doesn't support streaming
                # This is a placeholder for when streaming is implemented
                response = await asyncio.to_thread(
                    llm.complete_with_system,
                    system_prompt,
                    user_message,
                )

                # Simulate streaming by sending tokens one by one
                words = response.split()
                for i, word in enumerate(words):
                    token = word + " " if i < len(words) - 1 else word
                    yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
                    await asyncio.sleep(0.02)  # Small delay for streaming effect
            else:
                # Fallback: Generate response based on context
                response = generate_response_from_context(message, context, history)
                words = response.split()
                for i, word in enumerate(words):
                    token = word + " " if i < len(words) - 1 else word
                    yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
                    await asyncio.sleep(0.02)

        except Exception as e:
            # Fallback response
            response = f"I found relevant information in the knowledge base, but I'm having trouble generating a response. Here's what I found:\n\n{context[:500]}..."
            words = response.split()
            for word in words:
                yield f"data: {json.dumps({'type': 'token', 'data': word + ' '})}\n\n"
                await asyncio.sleep(0.02)

        # Send completion event
        yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"

    finally:
        query_service.close()


def generate_response_from_context(
    query: str,
    context: str,
    history: list[dict],
) -> str:
    """Generate a response based on context when LLM is not available."""
    # Simple template-based response
    if "no relevant context" in context.lower():
        return f"I don't have specific information about '{query}' in my knowledge base. Could you provide more details or try a different query?"

    response = f"Based on the knowledge base, here's what I found about your question:\n\n"

    # Extract relevant parts from context
    context_parts = context.split("[Source:")
    for part in context_parts[1:3]:  # Top 2 sources
        source_end = part.find("]")
        if source_end != -1:
            source_name = part[:source_end].strip()
            source_content = part[source_end + 1:].strip()[:300]
            response += f"**From {source_name}:**\n{source_content}...\n\n"

    return response


# ============================================================================
# Endpoints
# ============================================================================

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the knowledge base (non-streaming)."""
    history = [msg.model_dump() for msg in request.history]

    # Collect streamed response
    full_response = ""
    sources = []

    async for event in stream_tokens(request.message, history, request.session_id):
        if event.startswith("data: "):
            data = json.loads(event[6:])
            if data["type"] == "token":
                full_response += data["data"]
            elif data["type"] == "sources":
                sources = data["data"]

    return ChatResponse(
        response=full_response,
        sources=sources,
        session_id=request.session_id or "default",
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Chat with the knowledge base (streaming SSE)."""
    history = [msg.model_dump() for msg in request.history]

    return StreamingResponse(
        stream_tokens(request.message, history, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    from ke.application.services import ChatService

    config = load_config()
    chat_service = ChatService(config)

    try:
        messages = chat_service.get_history(session_id)
        return [
            {
                "message_id": m.message_id,
                "role": m.role.value,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in messages
        ]
    finally:
        pass
