"""HTML file ingestor with readability extraction."""

from __future__ import annotations

import time
from pathlib import Path
from urllib.parse import urlparse

from ke.core.models import IngestionResult
from ke.ingestion.base import Ingestor, chunk_text, create_entries_from_chunks


class HTMLIngestor(Ingestor):
    """Ingest HTML files with clean text extraction."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in (".html", ".htm")

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            from bs4 import BeautifulSoup

            html = path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title = ""
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Extract meta description
            description = ""
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                description = meta_desc.get("content", "")

            # Try readability-lxml for clean content
            text = ""
            try:
                from readability import Document

                doc = Document(html)
                clean_html = doc.summary()
                clean_soup = BeautifulSoup(clean_html, "html.parser")
                text = clean_soup.get_text(separator="\n", strip=True)
            except ImportError:
                # Fallback: remove scripts and styles, get text
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)

            tags = []
            if title:
                tags.append(title)
            # Extract headings
            headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
            tags.extend(headings[:5])

            metadata = {"title": title, "description": description, "headings": headings}

            chunks = chunk_text(text)
            entries = create_entries_from_chunks(
                chunks, path, "html", metadata=metadata, tags=tags
            )

            result.entries = entries
            result.chunks_created = len(chunks)

        except ImportError:
            result.errors.append(
                "beautifulsoup4 or readability-lxml not installed. "
                "Install with: pip install beautifulsoup4 readability-lxml"
            )
        except Exception as e:
            result.errors.append(f"Error reading HTML: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result
