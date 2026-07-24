"""Tests for ingestion modules."""

import tempfile
from pathlib import Path

import pytest

from ke.ingestion.base import chunk_text
from ke.ingestion.code import CodeIngestor
from ke.ingestion.json_csv import CSVIngestor, JSONIngestor
from ke.ingestion.text import MarkdownIngestor, TextIngestor
from ke.ingestion.manager import IngestionManager


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestChunkText:
    def test_short_text(self):
        chunks = chunk_text("Hello world")
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_long_text(self):
        text = "word " * 200  # ~1000 chars
        chunks = chunk_text(text, chunk_size=200, overlap=50)
        assert len(chunks) > 1

    def test_empty_text(self):
        chunks = chunk_text("")
        assert len(chunks) == 0

    def test_whitespace_only(self):
        chunks = chunk_text("   \n  \t  ")
        assert len(chunks) == 0


class TestTextIngestor:
    def test_can_handle(self):
        ingestor = TextIngestor()
        assert ingestor.can_handle(Path("test.txt"))
        assert ingestor.can_handle(Path("test.log"))
        assert not ingestor.can_handle(Path("test.py"))

    def test_ingest(self, fixtures_dir):
        ingestor = TextIngestor()
        # Create a test file
        test_file = fixtures_dir / "test.txt"
        test_file.write_text("This is test content.\nIt has multiple lines.")

        result = ingestor.ingest(test_file)
        assert result.chunks_created >= 1
        assert len(result.entries) >= 1
        assert result.errors == []


class TestMarkdownIngestor:
    def test_can_handle(self):
        ingestor = MarkdownIngestor()
        assert ingestor.can_handle(Path("test.md"))
        assert ingestor.can_handle(Path("test.markdown"))
        assert not ingestor.can_handle(Path("test.txt"))

    def test_ingest(self, fixtures_dir):
        ingestor = MarkdownIngestor()
        result = ingestor.ingest(fixtures_dir / "sample.md")
        assert result.chunks_created >= 1
        assert len(result.entries) >= 1
        # Check that headings were extracted as tags
        assert any("Features" in e.tags for e in result.entries)


class TestJSONIngestor:
    def test_can_handle(self):
        ingestor = JSONIngestor()
        assert ingestor.can_handle(Path("test.json"))
        assert not ingestor.can_handle(Path("test.txt"))

    def test_ingest(self, fixtures_dir):
        ingestor = JSONIngestor()
        result = ingestor.ingest(fixtures_dir / "sample.json")
        assert result.chunks_created >= 1
        assert len(result.entries) >= 1


class TestCSVIngestor:
    def test_can_handle(self):
        ingestor = CSVIngestor()
        assert ingestor.can_handle(Path("test.csv"))
        assert ingestor.can_handle(Path("test.tsv"))
        assert not ingestor.can_handle(Path("test.json"))

    def test_ingest(self, fixtures_dir):
        ingestor = CSVIngestor()
        result = ingestor.ingest(fixtures_dir / "sample.csv")
        assert result.chunks_created >= 1
        assert len(result.entries) >= 1
        # Check that headers were extracted as tags
        assert any("name" in e.tags for e in result.entries)


class TestCodeIngestor:
    def test_can_handle(self):
        ingestor = CodeIngestor()
        assert ingestor.can_handle(Path("test.py"))
        assert ingestor.can_handle(Path("test.js"))
        assert ingestor.can_handle(Path("test.go"))
        assert not ingestor.can_handle(Path("test.txt"))

    def test_ingest(self, fixtures_dir):
        ingestor = CodeIngestor()
        result = ingestor.ingest(fixtures_dir / "sample.py")
        assert result.chunks_created >= 1
        assert len(result.entries) >= 1
        # Check that Python was added as tag
        assert "python" in result.entries[0].tags


class TestIngestionManager:
    def test_get_supported_extensions(self):
        manager = IngestionManager()
        exts = manager.get_supported_extensions()
        assert ".pdf" in exts
        assert ".py" in exts
        assert ".json" in exts
        assert ".md" in exts

    def test_ingest_file(self, fixtures_dir):
        manager = IngestionManager()
        result = manager.ingest_file(fixtures_dir / "sample.py")
        assert result.chunks_created >= 1

    def test_ingest_nonexistent(self):
        manager = IngestionManager()
        result = manager.ingest(Path("/nonexistent/path"))
        assert len(result.errors) > 0
