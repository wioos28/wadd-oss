"""PDF file ingestor using PyMuPDF."""

from __future__ import annotations

import time
from pathlib import Path

from ke.core.models import IngestionResult
from ke.ingestion.base import Ingestor, chunk_text, create_entries_from_chunks


class PDFIngestor(Ingestor):
    """Ingest PDF files using PyMuPDF (fitz)."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            import fitz  # PyMuPDF

            doc = fitz.open(str(path))

            # Extract metadata
            metadata = doc.metadata or {}
            tags = []
            if metadata.get("subject"):
                tags.append(metadata["subject"])

            full_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    full_text.append(f"[Page {page_num + 1}]\n{text}")

            doc.close()

            combined_text = "\n\n".join(full_text)
            chunks = chunk_text(combined_text)
            entries = create_entries_from_chunks(
                chunks, path, "pdf",
                metadata={"pdf_metadata": metadata, "page_count": len(full_text)},
                tags=tags,
            )

            result.entries = entries
            result.chunks_created = len(chunks)

        except ImportError:
            result.errors.append("PyMuPDF (fitz) not installed. Install with: pip install pymupdf")
        except Exception as e:
            result.errors.append(f"Error reading PDF: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result
