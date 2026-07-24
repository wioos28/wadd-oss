"""Ingestion manager that orchestrates all ingestors."""

from __future__ import annotations

import time
from pathlib import Path

from ke.core.models import IngestionResult, KnowledgeEntry
from ke.ingestion.archive import ArchiveIngestor
from ke.ingestion.base import Ingestor
from ke.ingestion.code import CodeIngestor
from ke.ingestion.docx import DocxIngestor
from ke.ingestion.html import HTMLIngestor
from ke.ingestion.json_csv import CSVIngestor, JSONIngestor
from ke.ingestion.pdf import PDFIngestor
from ke.ingestion.text import MarkdownIngestor, TextIngestor


class IngestionManager:
    """Manages all ingestors and routes files to the correct one."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.ingestors: list[Ingestor] = [
            PDFIngestor(),
            DocxIngestor(),
            MarkdownIngestor(),
            HTMLIngestor(),
            JSONIngestor(),
            CSVIngestor(),
            CodeIngestor(),
            ArchiveIngestor(),
            TextIngestor(),  # Fallback
        ]

    def ingest_file(self, path: Path) -> IngestionResult:
        """Ingest a single file."""
        for ingestor in self.ingestors:
            if ingestor.can_handle(path):
                return ingestor.ingest(path)
        return IngestionResult(
            source_path=str(path),
            errors=[f"No ingestor found for {path.suffix}"],
        )

    def ingest_directory(self, path: Path, recursive: bool = True) -> list[IngestionResult]:
        """Ingest all supported files in a directory."""
        results = []
        pattern = "**/*" if recursive else "*"
        for file_path in sorted(path.glob(pattern)):
            if file_path.is_file():
                result = self.ingest_file(file_path)
                results.append(result)
        return results

    def ingest(self, path: Path, recursive: bool = True) -> IngestionResult | list[IngestionResult]:
        """Ingest a file or directory."""
        if path.is_file():
            return self.ingest_file(path)
        elif path.is_dir():
            return self.ingest_directory(path, recursive=recursive)
        else:
            return IngestionResult(
                source_path=str(path),
                errors=[f"Path does not exist: {path}"],
            )

    def get_supported_extensions(self) -> set[str]:
        """Get all supported file extensions."""
        extensions = set()
        for ext in [".pdf"]:
            extensions.add(ext)
        for ext in [".docx"]:
            extensions.add(ext)
        for ext in [".md", ".markdown", ".mdx"]:
            extensions.add(ext)
        for ext in [".html", ".htm"]:
            extensions.add(ext)
        for ext in [".json"]:
            extensions.add(ext)
        for ext in [".csv", ".tsv"]:
            extensions.add(ext)
        for ext in [".zip", ".epub"]:
            extensions.add(ext)
        for ext in [".txt", ".log", ".cfg", ".ini", ".conf"]:
            extensions.add(ext)
        # Code extensions
        from ke.ingestion.code import CODE_EXTENSIONS
        extensions.update(CODE_EXTENSIONS)
        return extensions
