"""Knowledge Engine CLI - Command-line interface."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from ke import __version__
from ke.config import KeConfig, ensure_data_dirs, load_config
from ke.core.models import QueryMode

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
def ingest(
    path: str = typer.Argument(help="File or directory to ingest"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="Recursively ingest directories"),
    tags: Optional[list[str]] = typer.Option(None, "--tag", help="Additional tags for ingested content"),
) -> None:
    """Ingest files into the knowledge base."""
    from ke.ingestion.manager import IngestionManager
    from ke.core.pipeline import QueryPipeline

    target = Path(path)
    if not target.exists():
        console.print(f"[red]Error: Path does not exist: {path}[/]")
        raise typer.Exit(1)

    config = get_config()
    manager = IngestionManager(
        chunk_size=config.chunking.chunk_size,
        chunk_overlap=config.chunking.chunk_overlap,
    )

    console.print(f"[bold]Ingesting: {target}[/]")

    with QueryPipeline(config) as pipeline:
        results = manager.ingest(target, recursive=recursive)

        if isinstance(results, list):
            total_entries = sum(len(r.entries) for r in results)
            total_errors = sum(len(r.errors) for r in results)
            files_processed = len(results)
        else:
            total_entries = len(results.entries)
            total_errors = len(results.errors)
            files_processed = 1
            results = [results]

        # Add entries to pipeline
        all_entries = []
        for r in results:
            all_entries.extend(r.entries)

        if all_entries:
            pipeline.add_entries(all_entries)

        # Display results
        table = Table(title="Ingestion Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Files processed", str(files_processed))
        table.add_row("Entries created", str(total_entries))
        table.add_row("Errors", str(total_errors) if total_errors else "[green]None[/]")
        console.print(table)

        # Show errors if any
        if total_errors:
            console.print("\n[bold yellow]Errors:[/]")
            for r in results:
                for error in r.errors:
                    console.print(f"  [red]✗[/] {error}")


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
    from ke.core.pipeline import QueryPipeline

    config = get_config()

    with QueryPipeline(config) as pipeline:
        kwargs = {}
        if tag:
            kwargs["tags"] = tag
        if source_type:
            kwargs["source_type"] = source_type

        results = pipeline.query(
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


@app.command()
def list_entries(
    source_type: Optional[str] = typer.Option(None, help="Filter by source type"),
    limit: int = typer.Option(20, help="Maximum entries to show"),
    offset: int = typer.Option(0, help="Offset for pagination"),
) -> None:
    """List knowledge entries."""
    from ke.storage.metadata import MetadataStore

    config = get_config()

    with MetadataStore(config.metadata_db_path()) as store:
        entries = store.list_entries(source_type=source_type, limit=limit, offset=offset)
        total = store.count_entries()

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


@app.command()
def show(
    entry_id: str = typer.Argument(help="Entry ID to show"),
) -> None:
    """Show details of a knowledge entry."""
    from ke.storage.metadata import MetadataStore

    config = get_config()

    with MetadataStore(config.metadata_db_path()) as store:
        entry = store.get_entry(entry_id)

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

        # Show relationships
        rels = store.get_relationships(entry.id)
        if rels:
            console.print(f"\n[bold]Relationships ({len(rels)}):[/]")
            for rel in rels:
                other_id = rel.target_id if rel.source_id == entry.id else rel.source_id
                console.print(f"  → {rel.relationship_type}: {other_id} (weight: {rel.weight:.2f})")


@app.command()
def relationships(
    entry_id: str = typer.Argument(help="Entry ID to show relationships for"),
) -> None:
    """Show relationships for an entry."""
    from ke.storage.metadata import MetadataStore

    config = get_config()

    with MetadataStore(config.metadata_db_path()) as store:
        rels = store.get_relationships(entry_id)

        if not rels:
            console.print(f"[yellow]No relationships found for {entry_id}[/]")
            return

        console.print(f"\n[bold]Relationships for {entry_id}:[/]\n")

        for rel in rels:
            other_id = rel.target_id if rel.source_id == entry_id else rel.source_id
            direction = "→" if rel.source_id == entry_id else "←"
            console.print(f"  {direction} {rel.relationship_type}: {other_id} (weight: {rel.weight:.2f})")


@app.command()
def sync(
    dry_run: bool = typer.Option(False, help="Show what would be synced without actually syncing"),
) -> None:
    """Sync with cloud (if configured)."""
    from ke.storage.sync import LocalSyncProvider

    config = get_config()

    if config.sync.provider == "local":
        sync_dir = config.data_dir_path() / "sync"
        provider = LocalSyncProvider(sync_dir)

        status = provider.status()
        console.print(Panel(
            f"Provider: {status['provider']}\n"
            f"Sync Dir: {status['sync_dir']}\n"
            f"Entries: {status['entries_count']}",
            title="Sync Status",
        ))
    else:
        console.print(f"[yellow]Cloud sync with provider '{config.sync.provider}' not yet implemented.[/]")


@app.command()
def status() -> None:
    """Show system status."""
    from ke.core.network import NetworkDetector
    from ke.storage.metadata import MetadataStore
    from ke.storage.vector import VectorStore

    config = get_config()

    # Network status
    detector = NetworkDetector()
    network = detector.detect()

    # Storage status
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


@app.command()
def export(
    output: str = typer.Argument(help="Output file path"),
) -> None:
    """Export knowledge base to JSON."""
    from ke.storage.metadata import MetadataStore

    config = get_config()

    with MetadataStore(config.metadata_db_path()) as store:
        entries = store.list_entries(limit=10000)

        data = [entry.model_dump(mode="json") for entry in entries]
        output_path = Path(output)
        output_path.write_text(json.dumps(data, indent=2, default=str))

        console.print(f"[green]Exported {len(data)} entries to {output}[/]")


@app.command()
def import_cmd(
    input_file: str = typer.Argument(help="Input JSON file path"),
) -> None:
    """Import knowledge base from JSON."""
    from ke.storage.metadata import MetadataStore

    config = get_config()
    input_path = Path(input_file)

    if not input_path.exists():
        console.print(f"[red]File not found: {input_file}[/]")
        raise typer.Exit(1)

    data = json.loads(input_path.read_text())

    with MetadataStore(config.metadata_db_path()) as store:
        from ke.core.models import KnowledgeEntry

        entries = [KnowledgeEntry(**item) for item in data]
        for entry in entries:
            store.add_entry(entry)

        console.print(f"[green]Imported {len(entries)} entries from {input_file}[/]")


@app.command()
def learn(
    task: str = typer.Argument(help="Task description"),
    result: str = typer.Argument(help="Task result"),
    tag: Optional[list[str]] = typer.Option(None, help="Tags for the learned knowledge"),
) -> None:
    """Learn from a completed task."""
    from ke.core.learning import KnowledgeLearner
    from ke.core.pipeline import QueryPipeline

    config = get_config()

    with QueryPipeline(config) as pipeline:
        learner = KnowledgeLearner(pipeline.metadata_store, pipeline.embedding_model)
        entry = learner.learn_from_task(task, result, tags=tag)

        console.print(Panel(
            f"[green]Knowledge learned![/]\n\n"
            f"ID: {entry.id}\n"
            f"Tags: {', '.join(entry.tags)}\n"
            f"Summary: {entry.summary}",
            title="Learning Complete",
        ))


@app.command()
def ask(
    question: str = typer.Argument(help="Question to ask"),
    top_k: int = typer.Option(10, help="Number of context chunks to retrieve"),
    mode: str = typer.Option("hybrid", help="Retrieval mode: semantic, keyword, hybrid"),
    model: str = typer.Option("gpt-3.5-turbo", help="LLM model name"),
    api_key: str = typer.Option(None, envvar="OPENAI_API_KEY", help="LLM API key"),
    base_url: str = typer.Option(None, envvar="OPENAI_BASE_URL", help="LLM API base URL"),
) -> None:
    """Ask a question using RAG (Retrieval-Augmented Generation).

    Flow: Knowledge → Top K chunks → Prompt Builder → LLM → Answer
    """
    from ke.llm.client import LLMClient
    from ke.rag.pipeline import RAGPipeline

    config = get_config()

    # Initialize LLM client
    llm = LLMClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    console.print(f"[bold]Retrieving top {top_k} chunks...[/]")

    with RAGPipeline(config=config, llm_client=llm, top_k=top_k) as rag:
        result = rag.query(question, top_k=top_k, mode=mode)

        # Display answer
        console.print(Panel(
            result.answer,
            title="Answer",
            subtitle=f"Model: {result.model} | Chunks used: {result.chunks_used} | Time: {result.processing_time_ms:.0f}ms",
        ))

        # Display sources
        if result.sources:
            console.print(f"\n[bold]Sources ({len(result.sources)}):[/]")
            for i, source in enumerate(result.sources, 1):
                source_path = source.get("source_path", "unknown")
                preview = source.get("content_preview", "")[:100]
                console.print(f"  [{i}] {source_path}")
                console.print(f"      {preview}...")


@app.command()
def ask_chat(
    question: str = typer.Argument(help="Question to ask"),
    top_k: int = typer.Option(10, help="Number of context chunks to retrieve"),
    model: str = typer.Option("gpt-3.5-turbo", help="LLM model name"),
    api_key: str = typer.Option(None, envvar="OPENAI_API_KEY", help="LLM API key"),
    base_url: str = typer.Option(None, envvar="OPENAI_BASE_URL", help="LLM API base URL"),
) -> None:
    """Interactive chat with RAG."""
    from ke.llm.client import LLMClient
    from ke.rag.pipeline import RAGPipeline

    config = get_config()

    llm = LLMClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    console.print(Panel.fit(
        "[bold]RAG Chat Mode[/]\n\n"
        "Ask questions based on your knowledge base.\n"
        "Type 'quit' to exit.",
        title="Knowledge Engine Chat",
    ))

    history = []

    with RAGPipeline(config=config, llm_client=llm, top_k=top_k) as rag:
        while True:
            try:
                user_input = console.input("\n[bold cyan]You:[/] ").strip()

                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "q"):
                    console.print("[dim]Goodbye![/]")
                    break

                # Add to history
                history.append({"role": "user", "content": user_input})

                # Get answer
                result = rag.chat(user_input, history=history)

                # Add to history
                history.append({"role": "assistant", "content": result.answer})

                # Display
                console.print(f"\n[bold green]Assistant:[/] {result.answer}")
                console.print(f"[dim]({result.chunks_used} chunks, {result.processing_time_ms:.0f}ms)[/]")

            except KeyboardInterrupt:
                console.print("\n[dim]Goodbye![/]")
                break
            except EOFError:
                break


if __name__ == "__main__":
    app()
