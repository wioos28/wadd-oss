"""JSON and CSV file ingestor."""

from __future__ import annotations

import csv
import io
import json
import time
from pathlib import Path
from typing import Any

from ke.core.models import IngestionResult
from ke.ingestion.base import Ingestor, chunk_text, create_entries_from_chunks


class JSONIngestor(Ingestor):
    """Ingest JSON files."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".json"

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            # Convert to readable text
            if isinstance(data, dict):
                text = json.dumps(data, indent=2, ensure_ascii=False)
                tags = list(data.keys())[:10] if isinstance(data, dict) else []
            elif isinstance(data, list):
                text = json.dumps(data, indent=2, ensure_ascii=False)
                tags = []
            else:
                text = str(data)
                tags = []

            chunks = chunk_text(text)
            entries = create_entries_from_chunks(
                chunks, path, "json",
                metadata={"json_type": type(data).__name__, "structure": self._describe_structure(data)},
                tags=tags,
            )

            result.entries = entries
            result.chunks_created = len(chunks)
        except json.JSONDecodeError as e:
            result.errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            result.errors.append(f"Error reading JSON: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result

    def _describe_structure(self, data: Any) -> str:
        """Describe JSON structure for metadata."""
        if isinstance(data, dict):
            return f"object with {len(data)} keys: {list(data.keys())[:5]}"
        elif isinstance(data, list):
            return f"array with {len(data)} items"
        return type(data).__name__


class CSVIngestor(Ingestor):
    """Ingest CSV files."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in (".csv", ".tsv")

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            delimiter = "\t" if path.suffix.lower() == ".tsv" else ","

            reader = csv.reader(io.StringIO(content), delimiter=delimiter)
            rows = list(reader)

            if not rows:
                result.errors.append("CSV file is empty")
                return result

            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []

            # Convert to readable text
            lines = [f"Headers: {', '.join(headers)}"]
            for i, row in enumerate(data_rows[:1000]):  # Limit rows
                line = " | ".join(f"{h}: {v}" for h, v in zip(headers, row) if v.strip())
                if line.strip():
                    lines.append(f"Row {i + 1}: {line}")

            tags = [h.strip() for h in headers if h.strip()][:10]

            text = "\n".join(lines)
            chunks = chunk_text(text)
            entries = create_entries_from_chunks(
                chunks, path, "csv",
                metadata={"headers": headers, "row_count": len(data_rows)},
                tags=tags,
            )

            result.entries = entries
            result.chunks_created = len(chunks)
        except Exception as e:
            result.errors.append(f"Error reading CSV: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result
