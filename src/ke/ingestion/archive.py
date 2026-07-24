"""Archive file ingestor (ZIP, EPUB)."""

from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

from ke.core.models import IngestionResult
from ke.ingestion.base import Ingestor, chunk_text, create_entries_from_chunks


class ArchiveIngestor(Ingestor):
    """Ingest ZIP and EPUB archive files."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in (".zip", ".epub")

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            if path.suffix.lower() == ".epub":
                return self._ingest_epub(path, start)
            else:
                return self._ingest_zip(path, start)
        except ImportError as e:
            result.errors.append(f"Missing dependency: {e}")
        except Exception as e:
            result.errors.append(f"Error reading archive: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result

    def _ingest_zip(self, path: Path, start: float) -> IngestionResult:
        """Ingest a ZIP archive."""
        result = IngestionResult(source_path=str(path))

        with zipfile.ZipFile(path) as zf:
            text_parts = []
            file_list = []

            for info in zf.infolist():
                if info.is_dir():
                    continue

                file_list.append(info.filename)
                ext = Path(info.filename).suffix.lower()

                # Only extract text-based files
                text_extensions = {
                    ".txt", ".md", ".py", ".js", ".ts", ".go", ".rs",
                    ".java", ".c", ".cpp", ".h", ".json", ".yaml", ".yml",
                    ".toml", ".xml", ".html", ".css", ".sh", ".bash",
                }

                if ext in text_extensions:
                    try:
                        content = zf.read(info.filename).decode("utf-8", errors="replace")
                        if content.strip():
                            text_parts.append(f"=== {info.filename} ===\n{content}")
                    except Exception:
                        pass

            tags = [Path(f).suffix.lstrip(".").lower() for f in file_list[:20]]
            tags = list(set(tags))

            combined_text = "\n\n".join(text_parts)
            chunks = chunk_text(combined_text)
            entries = create_entries_from_chunks(
                chunks, path, "archive",
                metadata={"file_list": file_list[:100], "file_count": len(file_list)},
                tags=tags,
            )

            result.entries = entries
            result.chunks_created = len(chunks)

        result.duration_ms = (time.time() - start) * 1000
        return result

    def _ingest_epub(self, path: Path, start: float) -> IngestionResult:
        """Ingest an EPUB ebook."""
        result = IngestionResult(source_path=str(path))

        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup

            book = epub.read_epub(str(path))

            # Extract metadata
            title = book.get_metadata("DC", "title")
            title_text = title[0][0] if title else path.stem
            description = book.get_metadata("DC", "description")
            desc_text = description[0][0] if description else ""

            text_parts = []
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    text = soup.get_text(separator="\n", strip=True)
                    if text.strip():
                        text_parts.append(text)

            tags = [title_text]
            if desc_text:
                tags.append(desc_text[:50])

            combined_text = "\n\n".join(text_parts)
            chunks = chunk_text(combined_text)
            entries = create_entries_from_chunks(
                chunks, path, "epub",
                metadata={"title": title_text, "description": desc_text},
                tags=tags,
            )

            result.entries = entries
            result.chunks_created = len(chunks)

        except ImportError:
            result.errors.append("ebooklib not installed. Install with: pip install ebooklib")
        except Exception as e:
            result.errors.append(f"Error reading EPUB: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result
