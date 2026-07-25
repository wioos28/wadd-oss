"""Knowledge router - Search and manage knowledge base."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ke.config import load_config

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class QueryRequest(BaseModel):
    text: str
    mode: str = "hybrid"
    limit: int = 10
    min_score: float = 0.3


class QueryResponse(BaseModel):
    id: str
    content: str
    source_type: str
    source_path: str | None
    tags: list[str]
    score: float
    retrieval_mode: str


class EntryResponse(BaseModel):
    id: str
    content: str
    source_type: str
    source_path: str | None
    tags: list[str]
    created_at: str


class IngestRequest(BaseModel):
    path: str
    recursive: bool = True


class IngestResponse(BaseModel):
    entries_created: int
    errors: list[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/query", response_model=list[QueryResponse])
async def query_knowledge(request: QueryRequest):
    """Search the knowledge base."""
    from ke.application.services import QueryService

    config = load_config()
    query_service = QueryService(config)

    try:
        results = query_service.query(
            text=request.text,
            mode=request.mode,
            limit=request.limit,
            min_score=request.min_score,
        )

        return [
            QueryResponse(
                id=r.entry.id,
                content=r.entry.content,
                source_type=r.entry.source_type,
                source_path=r.entry.source_path,
                tags=r.entry.tags,
                score=r.score,
                retrieval_mode=r.retrieval_mode,
            )
            for r in results
        ]
    finally:
        query_service.close()


@router.get("/entries", response_model=list[EntryResponse])
async def list_entries(
    source_type: str | None = Query(None, description="Filter by source type"),
    limit: int = Query(20, ge=1, le=1000),
):
    """List knowledge entries."""
    from ke.application.services import KnowledgeService

    config = load_config()
    knowledge_service = KnowledgeService(config)

    try:
        entries = knowledge_service.list_entries(
            source_type=source_type,
            limit=limit,
        )

        return [
            EntryResponse(
                id=e.id,
                content=e.content,
                source_type=e.source_type,
                source_path=e.source_path,
                tags=e.tags,
                created_at=e.created_at.isoformat(),
            )
            for e in entries
        ]
    finally:
        knowledge_service.close()


@router.get("/entries/{entry_id}", response_model=EntryResponse)
async def get_entry(entry_id: str):
    """Get a specific knowledge entry."""
    from ke.application.services import KnowledgeService

    config = load_config()
    knowledge_service = KnowledgeService(config)

    try:
        entry = knowledge_service.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        return EntryResponse(
            id=entry.id,
            content=entry.content,
            source_type=entry.source_type,
            source_path=entry.source_path,
            tags=entry.tags,
            created_at=entry.created_at.isoformat(),
        )
    finally:
        knowledge_service.close()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_files(request: IngestRequest):
    """Ingest files into the knowledge base."""
    from ke.application.services import IngestionService, KnowledgeService

    config = load_config()
    ingestion_service = IngestionService(config)
    knowledge_service = KnowledgeService(config)

    try:
        entries = ingestion_service.ingest(request.path, recursive=request.recursive)
        knowledge_service.add_entries(entries)

        return IngestResponse(
            entries_created=len(entries),
            errors=[],
        )
    except Exception as e:
        return IngestResponse(
            entries_created=0,
            errors=[str(e)],
        )
    finally:
        knowledge_service.close()
