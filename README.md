# Knowledge Engine

A local-first, offline-capable knowledge management CLI tool.

## Features

- **Multi-format ingestion**: PDF, DOCX, Markdown, HTML, JSON, CSV, source code, and archives
- **Semantic search**: Vector embeddings for meaning-based retrieval
- **Keyword search**: Full-text search with SQLite
- **Hybrid search**: Combined semantic + keyword with reciprocal rank fusion
- **Code similarity**: AST-aware code search
- **Knowledge graph**: Auto-linking related entries via relationships
- **Learning**: Extract knowledge from tasks, documents, and conversations
- **Reasoning Engine**: AI-powered reasoning with intent detection, planning, verification, and reflection
- **Offline-first**: All core features work without internet
- **Cloud sync**: Optional sync with cloud providers

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Initialize
ke init

# Ingest files
ke ingest ./documents/
ke ingest paper.pdf
ke ingest src/

# Query
ke query "how does authentication work"
ke query --mode semantic "machine learning"
ke query --mode code "def calculate_sum"

# List entries
ke list
ke list --source-type code

# Show entry details
ke show <entry-id>

# Learn from a task
ke learn "Implemented auth module" "Added JWT tokens with refresh" --tag auth --tag security

# Check status
ke status
```

## Retrieval Modes

| Mode | Description |
|------|-------------|
| `semantic` | Vector similarity search |
| `keyword` | Full-text keyword search |
| `hybrid` | Combined semantic + keyword (default) |
| `code_similarity` | Code-aware search |
| `metadata` | Filter by tags, source type, date |
| `time` | Recent entries |
| `relationship` | Knowledge graph traversal |

## Reasoning Engine

The Reasoning Engine transforms Knowledge Engine from a Retrieval Engine into an AI Knowledge Engine capable of reasoning before answering.

### Pipeline Stages

1. **Intent Detection** — Pattern-based classification (question, command, search, code, memory, explain, compare, create, update, analyze, unknown)
2. **Planning** — Goal decomposition into executable steps with dependencies
3. **Reasoning** — 5-step chain: Analyze → Gather Evidence → Cross-Reference → Synthesize → Conclude
4. **Verification** — Logical consistency, conflicting facts, missing info, duplicate detection
5. **Reflection** — Post-task quality evaluation, lesson extraction, reusable knowledge identification
6. **Confidence Scoring** — Weighted 4-factor scoring: knowledge quality, retrieval score, evidence count, reasoning quality

### Usage

```python
from ke.reasoning import ReasoningPipeline

# Initialize with knowledge pipeline and embedding model
pipeline = ReasoningPipeline(
    knowledge_pipeline=knowledge_pipeline,
    embedding_model=embedding_model
)

# Process a query through reasoning
result = await pipeline.process(
    query="How does authentication work in this codebase?",
    memory_entries=memory_entries,
    retrieved_entries=retrieved_entries
)

print(result.response)          # Final reasoned response
print(result.confidence.score)  # Confidence score (0.0 - 1.0)
print(result.reflection.quality_score)  # Quality assessment
```

### Intent Types

| Intent | Description |
|--------|-------------|
| `question` | General questions (what, how, why, when, where) |
| `command` | Action requests (create, build, implement) |
| `search` | Information retrieval |
| `code` | Code-related queries |
| `memory` | Memory/recall queries |
| `explain` | Explanation requests |
| `compare` | Comparison requests |
| `create` | Creation requests |
| `update` | Update/modification requests |
| `analyze` | Analysis requests |
| `unknown` | Unclassified intent |

### Confidence Scoring

The 4-factor weighted scoring system:

- **Knowledge Quality** (0.25) — Quality of source entries used
- **Retrieval Score** (0.25) — Relevance of retrieved information
- **Evidence Count** (0.20) — Number of supporting evidence pieces
- **Reasoning Quality** (0.30) — Quality of reasoning chain

Final score = Σ(factor_score × weight) × verification_modifier × reflection_modifier

## Architecture

```
CLI (Typer) → Query Pipeline → Storage Layer
                ↓
    Cache → Metadata (SQLite) → Vector (ChromaDB) → Cloud → Internet

Reasoning Engine (Phase 9):
    Query → Intent Detection → Planning → Reasoning → Verification → Reflection → Response
```

## Configuration

Edit `~/.knowledge-engine/config.toml` to customize:

```toml
[embeddings]
model_name = "all-MiniLM-L6-v2"  # or your preferred model

[retrieval]
default_mode = "hybrid"
max_results = 10
min_score = 0.3
```

## Supported Formats

- **Documents**: PDF, DOCX, Markdown, HTML
- **Data**: JSON, CSV, TSV
- **Code**: Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, and more
- **Archives**: ZIP, EPUB

## License

MIT
