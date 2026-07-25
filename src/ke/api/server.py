"""FastAPI server with streaming support."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ke.config import load_config, ensure_data_dirs, KeConfig
from ke.api.routers import auth, knowledge, chat, status_router
from ke.api.middleware.auth import get_current_user


# ============================================================================
# App Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    config = load_config()
    ensure_data_dirs(config)
    app.state.config = config
    yield
    # Shutdown
    pass


def create_app(config: KeConfig | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Knowledge Engine API",
        description="AI-powered knowledge management with streaming support",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Store config
    if config:
        app.state.config = config

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge"])
    app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
    app.include_router(status_router.router, prefix="/api", tags=["Status"])

    @app.get("/")
    async def root():
        return {
            "name": "Knowledge Engine API",
            "version": "1.0.0",
            "docs": "/docs",
        }

    return app
