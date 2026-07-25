"""Chat router - Streaming chat with Cognitive Engine and SSE support."""

from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ke.config import load_config

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
    intent: str | None = None


# ============================================================================
# SSE Streaming Generator with Cognitive Engine
# ============================================================================

async def stream_with_cognitive_engine(
    message: str,
    history: list[dict],
    session_id: str | None,
) -> AsyncGenerator[str, None]:
    """Stream response using the Cognitive Engine pipeline."""
    from ke.cognitive.engine import CognitiveEngine

    config = load_config()
    engine = CognitiveEngine(config)

    try:
        async for event in engine.process(
            message=message,
            conversation_history=history,
            session_id=session_id,
        ):
            # Convert event to SSE format
            yield f"data: {json.dumps(event)}\n\n"

    except Exception as e:
        # Error event
        yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"


# ============================================================================
# Legacy streaming (fallback)
# ============================================================================

async def stream_tokens_legacy(
    message: str,
    history: list[dict],
    session_id: str | None,
) -> AsyncGenerator[str, None]:
    """Legacy streaming fallback when Cognitive Engine fails."""
    from ke.application.services import QueryService

    config = load_config()
    query_service = QueryService(config)

    try:
        # Retrieve relevant knowledge
        results = query_service.query(text=message, mode="hybrid", limit=5)

        # Build context
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

        # Send sources
        yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"

        # Generate response
        from ke.llm.client import LLMClient
        llm = LLMClient()

        if llm.is_available():
            import asyncio

            system_prompt = """You are a helpful AI assistant powered by Knowledge Engine."""
            user_message = f"Context:\n{context}\n\nQuestion: {message}"

            response = await asyncio.to_thread(
                llm.complete_with_system,
                system_prompt,
                user_message,
            )

            # Stream tokens
            words = response.split()
            for i, word in enumerate(words):
                token = word + " " if i < len(words) - 1 else word
                yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
                await asyncio.sleep(0.02)
        else:
            # Fallback response
            response = f"Based on the knowledge base:\n\n{context[:500]}..."
            words = response.split()
            for word in words:
                yield f"data: {json.dumps({'type': 'token', 'data': word + ' '})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'data': ''})}\n\n"

    finally:
        query_service.close()


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
    intent = None

    try:
        async for event in stream_with_cognitive_engine(
            request.message, history, request.session_id
        ):
            if event.startswith("data: "):
                data = json.loads(event[6:])
                if data["type"] == "token":
                    full_response += data["data"]
                elif data["type"] == "sources":
                    sources = data["data"]
                elif data["type"] == "intent":
                    intent = data["data"].get("type") if isinstance(data["data"], dict) else None
    except Exception:
        # Fallback to legacy streaming
        async for event in stream_tokens_legacy(
            request.message, history, request.session_id
        ):
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
        intent=intent,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Chat with the knowledge base (streaming SSE with Cognitive Engine)."""
    history = [msg.model_dump() for msg in request.history]

    return StreamingResponse(
        stream_with_cognitive_engine(request.message, history, request.session_id),
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
