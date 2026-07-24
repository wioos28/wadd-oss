"""Plain text and Markdown file ingestor."""

from __future__ import annotations

import re
import time
from pathlib import Path

from ke.core.models import IngestionResult
from ke.ingestion.base import Ingestor, chunk_text, create_entries_from_chunks


class TextIngestor(Ingestor):
    """Ingest plain text files."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in (".txt", ".log", ".cfg", ".ini", ".conf")

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            chunks = chunk_text(text)
            entries = create_entries_from_chunks(chunks, path, "text")
            result.entries = entries
            result.chunks_created = len(chunks)
        except Exception as e:
            result.errors.append(f"Error reading text file: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result


class MarkdownIngestor(Ingestor):
    """Ingest Markdown files with heading extraction."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in (".md", ".markdown", ".mdx")

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            text = path.read_text(encoding="utf-8", errors="replace")

            # Extract headings for tags
            headings = re.findall(r"^#+\s+(.+)$", text, re.MULTILINE)
            tags = [h.strip() for h in headings[:10]]

            # Extract code blocks as separate context
            code_blocks = re.findall(r"```(\w+)?\n(.*?)```", text, re.DOTALL)

            chunks = chunk_text(text)
            entries = create_entries_from_chunks(
                chunks, path, "markdown",
                metadata={"headings": headings, "code_block_count": len(code_blocks)},
                tags=tags,
            )

            result.entries = entries
            result.chunks_created = len(chunks)
        except Exception as e:
            result.errors.append(f"Error reading Markdown file: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result
