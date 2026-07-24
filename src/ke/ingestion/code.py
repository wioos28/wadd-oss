"""Source code ingestor with AST-based extraction."""

from __future__ import annotations

import time
from pathlib import Path

from ke.core.models import IngestionResult
from ke.ingestion.base import Ingestor, chunk_text, create_entries_from_chunks

# Supported code file extensions
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
    ".kt", ".scala", ".sh", ".bash", ".zsh", ".fish",
}

LANGUAGE_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".jsx": "javascript", ".tsx": "typescript", ".go": "go",
    ".rs": "rust", ".java": "java", ".c": "c", ".cpp": "cpp",
    ".h": "c", ".hpp": "cpp", ".cs": "csharp", ".rb": "ruby",
    ".php": "php", ".swift": "swift", ".kt": "kotlin",
    ".scala": "scala", ".sh": "bash", ".bash": "bash",
    ".zsh": "bash", ".fish": "bash",
}


class CodeIngestor(Ingestor):
    """Ingest source code files with comment and structure extraction."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in CODE_EXTENSIONS

    def ingest(self, path: Path) -> IngestionResult:
        start = time.time()
        result = IngestionResult(source_path=str(path))

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            language = LANGUAGE_MAP.get(path.suffix.lower(), "unknown")

            # Extract comments and docstrings
            comments = self._extract_comments(text, language)

            # Extract function/class signatures
            structures = self._extract_structures(text, language)

            tags = [language]
            if structures:
                tags.extend(structures[:10])

            metadata = {
                "language": language,
                "line_count": text.count("\n") + 1,
                "functions": structures,
                "comments": comments[:20],  # Limit stored comments
            }

            chunks = chunk_text(text, chunk_size=1024, overlap=128)
            entries = create_entries_from_chunks(
                chunks, path, "code", metadata=metadata, tags=tags
            )

            result.entries = entries
            result.chunks_created = len(chunks)
        except Exception as e:
            result.errors.append(f"Error reading code file: {e}")

        result.duration_ms = (time.time() - start) * 1000
        return result

    def _extract_comments(self, text: str, language: str) -> list[str]:
        """Extract comments from source code."""
        import re

        comments = []

        # Single-line comments
        if language in ("python", "ruby", "bash"):
            pattern = r"#\s*(.+)$"
        elif language in ("javascript", "typescript", "java", "c", "cpp", "go", "rust", "swift", "kotlin", "scala"):
            pattern = r"//\s*(.+)$"
        else:
            pattern = r"#\s*(.+)$|//\s*(.+)$"

        for match in re.finditer(pattern, text, re.MULTILINE):
            comment = match.group(1) or match.group(2) or ""
            comment = comment.strip()
            if comment and len(comment) > 5:
                comments.append(comment)

        # Multi-line comments (docstrings for Python, /* */ for others)
        if language == "python":
            docstrings = re.findall(r'"""(.*?)"""', text, re.DOTALL)
            docstrings += re.findall(r"'''(.*?)'''", text, re.DOTALL)
            comments.extend(d.strip() for d in docstrings if d.strip())
        else:
            block_comments = re.findall(r"/\*(.*?)\*/", text, re.DOTALL)
            comments.extend(c.strip() for c in block_comments if c.strip())

        return comments

    def _extract_structures(self, text: str, language: str) -> list[str]:
        """Extract function and class names from source code."""
        import re

        structures = []

        if language == "python":
            patterns = [
                r"^class\s+(\w+)",
                r"^def\s+(\w+)",
                r"^async\s+def\s+(\w+)",
            ]
        elif language in ("javascript", "typescript"):
            patterns = [
                r"(?:export\s+)?(?:class|function)\s+(\w+)",
                r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(",
                r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function",
            ]
        elif language == "go":
            patterns = [
                r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)",
                r"^type\s+(\w+)\s+struct",
            ]
        elif language == "rust":
            patterns = [
                r"^pub\s+(?:async\s+)?fn\s+(\w+)",
                r"^fn\s+(\w+)",
                r"^pub\s+struct\s+(\w+)",
                r"^pub\s+enum\s+(\w+)",
            ]
        else:
            patterns = [
                r"(?:function|def|fn|func)\s+(\w+)",
                r"(?:class|struct|enum|interface)\s+(\w+)",
            ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                name = match.group(1)
                if name and len(name) > 1:
                    structures.append(name)

        return list(dict.fromkeys(structures))  # Dedupe preserving order
