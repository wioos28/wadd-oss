"""Presentation Layer - CLI interface using Typer."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ke import __version__
from ke.config import KeConfig, ensure_data_dirs, load_config
from ke.domain.models import QueryMode

app = typer.Typer(
    name="ke",
    help="Knowledge Engine - A local-first, offline-capable knowledge management CLI",
    no_args_is_help=True,
)
console = Console()


def get_config() -> KeConfig:
    """Load and initialize configuration."""
    config = load_config()
    ensure_data_dirs(config)
    return config


# ============================================================================
# Core Commands
# ============================================================================

@app.command()
def init(
    config_path: Optional[str] = typer.Option(None, help="Custom config file path"),
) -> None:
    """Initialize the knowledge base."""
    config = load_config(Path(config_path) if config_path else None)
    ensure_data_dirs(config)

    console.print(Panel.fit(
        f"[bold green]Knowledge Engine initialized![/]\n\n"
        f"Data directory: {config.data_dir_path()}\n"
        f"Metadata DB: {config.metadata_db_path()}\n"
        f"Vector DB: {config.vector_db_path()}\n"
        f"Cache: {config.cache_path()}",
        title="Initialization Complete",
    ))


@app.command()
def status() -> None:
    """Show system status."""
    from ke.core.network import NetworkDetector

    config = get_config()

    detector = NetworkDetector()
    network = detector.detect()

    from ke.storage.metadata import MetadataStore
    from ke.storage.vector import VectorStore

    with MetadataStore(config.metadata_db_path()) as store:
        entry_count = store.count_entries()

    with VectorStore(config.vector_db_path()) as vec:
        vector_count = vec.count()

    console.print(Panel.fit(
        f"[bold]Knowledge Engine Status[/]\n\n"
        f"Version: {__version__}\n"
        f"Data Dir: {config.data_dir_path()}\n\n"
        f"[bold]Storage:[/]\n"
        f"  Entries: {entry_count}\n"
        f"  Vectors: {vector_count}\n\n"
        f"[bold]Network:[/]\n"
        f"  Status: {network.status}\n"
        f"  Interfaces: {', '.join(network.interfaces) if network.interfaces else 'None'}\n"
        f"  Latency: {network.latency_ms:.0f}ms" if network.latency_ms else "  Latency: N/A",
        title="System Status",
    ))


@app.command()
def config_cmd() -> None:
    """Show current configuration."""
    config = get_config()
    console.print_json(config.model_dump_json(indent=2))


# ============================================================================
# Ingestion Commands
# ============================================================================

@app.command()
def ingest(
    path: str = typer.Argument(help="File or directory to ingest"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="Recursively ingest directories"),
    tags: Optional[list[str]] = typer.Option(None, "--tag", help="Additional tags for ingested content"),
) -> None:
    """Ingest files into the knowledge base."""
    from ke.application.services import IngestionService, KnowledgeService

    config = get_config()
    ingestion_service = IngestionService(config)
    knowledge_service = KnowledgeService(config)

    console.print(f"[bold]Ingesting: {path}[/]")

    try:
        entries = ingestion_service.ingest(path, recursive=recursive)
        knowledge_service.add_entries(entries)

        table = Table(title="Ingestion Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Files processed", str(len(entries)))
        table.add_row("Entries created", str(len(entries)))
        table.add_row("Errors", "[green]None[/]")
        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)
    finally:
        knowledge_service.close()


# ============================================================================
# Query Commands
# ============================================================================

@app.command()
def query(
    text: str = typer.Argument(help="Query text"),
    mode: str = typer.Option("hybrid", help="Retrieval mode: semantic, keyword, hybrid, code_similarity, metadata, time, relationship"),
    limit: int = typer.Option(10, help="Maximum number of results"),
    min_score: float = typer.Option(0.3, help="Minimum relevance score"),
    tag: Optional[list[str]] = typer.Option(None, help="Filter by tags"),
    source_type: Optional[str] = typer.Option(None, help="Filter by source type"),
) -> None:
    """Search the knowledge base."""
    from ke.application.services import QueryService

    config = get_config()
    query_service = QueryService(config)

    try:
        kwargs = {}
        if tag:
            kwargs["tags"] = tag
        if source_type:
            kwargs["source_type"] = source_type

        results = query_service.query(
            text=text,
            mode=mode,
            limit=limit,
            min_score=min_score,
            **kwargs,
        )

        if not results:
            console.print("[yellow]No results found.[/]")
            return

        console.print(f"\n[bold]Found {len(results)} results:[/]\n")

        for i, result in enumerate(results, 1):
            panel_content = f"[bold]{result.entry.content[:200]}[/]"
            if len(result.entry.content) > 200:
                panel_content += "..."

            metadata_parts = []
            if result.entry.source_path:
                metadata_parts.append(f"Source: {result.entry.source_path}")
            if result.entry.tags:
                metadata_parts.append(f"Tags: {', '.join(result.entry.tags)}")
            metadata_parts.append(f"Score: {result.score:.3f}")
            metadata_parts.append(f"Mode: {result.retrieval_mode}")

            footer = " | ".join(metadata_parts)

            console.print(Panel(
                panel_content,
                title=f"[{i}] {result.entry.source_type}",
                subtitle=footer,
            ))

    finally:
        query_service.close()


# ============================================================================
# List/Show Commands
# ============================================================================

@app.command("list")
def list_entries(
    source_type: Optional[str] = typer.Option(None, help="Filter by source type"),
    limit: int = typer.Option(20, help="Maximum entries to show"),
    offset: int = typer.Option(0, help="Offset for pagination"),
) -> None:
    """List knowledge entries."""
    from ke.application.services import KnowledgeService

    config = get_config()
    knowledge_service = KnowledgeService(config)

    try:
        entries = knowledge_service.list_entries(source_type=source_type, limit=limit)
        total = knowledge_service.count_entries()

        if not entries:
            console.print("[yellow]No entries found.[/]")
            return

        table = Table(title=f"Knowledge Entries (showing {len(entries)}/{total})")
        table.add_column("ID", style="cyan", max_width=12)
        table.add_column("Type", style="green")
        table.add_column("Content", max_width=50)
        table.add_column("Tags", max_width=20)
        table.add_column("Created", style="dim")

        for entry in entries:
            content_preview = entry.content[:50].replace("\n", " ")
            if len(entry.content) > 50:
                content_preview += "..."
            tags_str = ", ".join(entry.tags[:3])
            if len(entry.tags) > 3:
                tags_str += "..."

            table.add_row(
                entry.id[:12],
                entry.source_type,
                content_preview,
                tags_str,
                entry.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)

    finally:
        knowledge_service.close()


@app.command()
def show(
    entry_id: str = typer.Argument(help="Entry ID to show"),
) -> None:
    """Show details of a knowledge entry."""
    from ke.application.services import KnowledgeService

    config = get_config()
    knowledge_service = KnowledgeService(config)

    try:
        entry = knowledge_service.get_entry(entry_id)

        if not entry:
            console.print(f"[red]Entry not found: {entry_id}[/]")
            raise typer.Exit(1)

        console.print(Panel(
            entry.content,
            title=f"Entry: {entry.id}",
            subtitle=f"Type: {entry.source_type} | Created: {entry.created_at.isoformat()}",
        ))

        if entry.summary:
            console.print(f"\n[bold]Summary:[/] {entry.summary}")

        if entry.tags:
            console.print(f"[bold]Tags:[/] {', '.join(entry.tags)}")

        if entry.source_path:
            console.print(f"[bold]Source:[/] {entry.source_path}")

    finally:
        knowledge_service.close()


# ============================================================================
# Learning Commands
# ============================================================================

@app.command()
def learn(
    task: str = typer.Argument(help="Task description"),
    result: str = typer.Argument(help="Task result"),
    tag: Optional[list[str]] = typer.Option(None, help="Tags for the learned knowledge"),
) -> None:
    """Learn from a completed task."""
    from ke.core.learning import KnowledgeLearner
    from ke.application.services import KnowledgeService

    config = get_config()
    knowledge_service = KnowledgeService(config)

    try:
        learner = KnowledgeLearner(
            knowledge_service.metadata_store,
            knowledge_service.embedding_model,
            knowledge_service.vector_store,
        )
        entry = learner.learn_from_task(task, result, tags=tag)

        console.print(Panel(
            f"[green]Knowledge learned![/]\n\n"
            f"ID: {entry.id}\n"
            f"Tags: {', '.join(entry.tags)}\n"
            f"Summary: {entry.summary}",
            title="Learning Complete",
        ))

    finally:
        knowledge_service.close()


# ============================================================================
# Cloud Commands
# ============================================================================

@app.command("cloud-status")
def cloud_status() -> None:
    """Show ChromaDB Cloud status."""
    from ke.config import load_config
    from ke.storage.cloud import CloudVectorStore
    from ke.storage.chat_history import ChatHistoryStore

    config = load_config()

    if not config.chromadb_cloud.enabled:
        console.print(Panel.fit(
            "[bold]ChromaDB Cloud Status[/]\n\n"
            "Status: [red]Disabled[/]\n\n"
            "To enable, add to ~/.knowledge-engine/config.toml:\n"
            "[chromadb_cloud]\n"
            'enabled = true\n'
            'api_key = "your-api-key"\n'
            'tenant = "your-tenant-id"\n'
            'database = "your-database"',
            title="Cloud Status",
        ))
        return

    try:
        with CloudVectorStore(config.chromadb_cloud) as cloud:
            knowledge_count = cloud.count()

        with ChatHistoryStore(config.chromadb_cloud) as chat:
            chat_count = chat.count()

        console.print(Panel.fit(
            f"[bold]ChromaDB Cloud Status[/]\n\n"
            f"Status: [green]Connected[/]\n"
            f"Tenant: {config.chromadb_cloud.tenant}\n"
            f"Database: {config.chromadb_cloud.database}\n\n"
            f"[bold]Collections:[/]\n"
            f"  Knowledge: {knowledge_count} entries\n"
            f"  Chat History: {chat_count} messages",
            title="Cloud Status",
        ))
    except Exception as e:
        console.print(Panel.fit(
            f"[bold]ChromaDB Cloud Status[/]\n\n"
            f"Status: [red]Error[/]\n"
            f"Error: {e}",
            title="Cloud Status",
        ))


# ============================================================================
# Account Commands
# ============================================================================

@app.command("account-create")
def account_create(
    username: str = typer.Argument(help="Username"),
    email: str = typer.Argument(help="Email address"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password"),
) -> None:
    """Create a new user account."""
    from ke.application.services import AuthService

    config = get_config()
    if not config.chromadb_cloud.enabled:
        console.print("[red]ChromaDB Cloud not configured.[/]")
        raise typer.Exit(1)

    auth_service = AuthService(config)

    try:
        user = auth_service.create_account(username, email, password)
        console.print(Panel(
            f"[green]Account created![/]\n\n"
            f"User ID: {user.user_id}\n"
            f"Username: {user.username}\n"
            f"Email: {user.email}\n"
            f"Created: {user.created_at.isoformat()}",
            title="Account Created",
        ))
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)


@app.command("account-login")
def account_login(
    username: str = typer.Argument(help="Username"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password"),
) -> None:
    """Login to user account."""
    from ke.application.services import AuthService

    config = get_config()
    if not config.chromadb_cloud.enabled:
        console.print("[red]ChromaDB Cloud not configured.[/]")
        raise typer.Exit(1)

    auth_service = AuthService(config)

    try:
        user = auth_service.login(username, password)
        if user:
            console.print(Panel(
                f"[green]Login successful![/]\n\n"
                f"User ID: {user.user_id}\n"
                f"Username: {user.username}\n"
                f"Email: {user.email}",
                title="Welcome",
            ))
        else:
            console.print("[red]Invalid username or password.[/]")
            raise typer.Exit(1)
    finally:
        pass


@app.command("account-list")
def account_list(
    limit: int = typer.Option(20, help="Maximum accounts to show"),
) -> None:
    """List all user accounts."""
    from ke.application.services import AuthService

    config = get_config()
    if not config.chromadb_cloud.enabled:
        console.print("[red]ChromaDB Cloud not configured.[/]")
        raise typer.Exit(1)

    auth_service = AuthService(config)

    try:
        users = auth_service.list_users(limit=limit)

        if not users:
            console.print("[yellow]No accounts found.[/]")
            return

        table = Table(title=f"User Accounts ({len(users)})")
        table.add_column("User ID", style="cyan", max_width=12)
        table.add_column("Username", style="green")
        table.add_column("Email")
        table.add_column("Created", style="dim")

        for user in users:
            table.add_row(
                user.user_id[:12],
                user.username,
                user.email,
                user.created_at.strftime("%Y-%m-%d %H:%M"),
            )

        console.print(table)

    finally:
        pass


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    app()
