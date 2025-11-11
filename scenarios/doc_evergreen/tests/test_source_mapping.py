"""
Tests for source mapping functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from doc_evergreen.core.source_mapping import (
    extract_template_sections,
    load_source_map,
    map_sources_to_sections,
    save_source_map,
)


def test_extract_template_sections_basic():
    """Test extracting sections from a simple template."""
    template = """# Installation

Install the package...

## Usage

Use the package...

### Configuration

Configure the package...
"""
    sections = extract_template_sections(template)

    assert len(sections) == 3
    assert "Installation" in sections
    assert "Usage" in sections
    assert "Configuration" in sections


def test_extract_template_sections_skips_meta():
    """Test that meta sections like Instructions are skipped."""
    template = """# Instructions

These are instructions for the AI...

# Actual Section

This is the actual content.
"""
    sections = extract_template_sections(template)

    assert len(sections) == 1
    assert "Actual Section" in sections
    assert "Instructions" not in sections


def test_extract_template_sections_empty():
    """Test extracting from template with no sections."""
    template = "No headers here, just text."
    sections = extract_template_sections(template)

    assert len(sections) == 0


@patch("doc_evergreen.core.source_mapping.call_llm")
def test_map_sources_to_sections_success(mock_call_llm):
    """Test successful source mapping."""
    template = """# Installation

Setup instructions...

# Usage

How to use...
"""
    sources = {
        "README.md": "Installation guide...",
        "src/api.py": "API functions...",
    }

    # Mock LLM response
    mock_call_llm.return_value = """{
  "Installation": ["README.md"],
  "Usage": ["README.md", "src/api.py"]
}"""

    result = map_sources_to_sections(template, sources, "Project documentation")

    assert len(result) == 2
    assert result["Installation"] == ["README.md"]
    assert result["Usage"] == ["README.md", "src/api.py"]


@patch("doc_evergreen.core.source_mapping.call_llm")
def test_map_sources_to_sections_no_sections(mock_call_llm):
    """Test mapping with template that has no sections."""
    template = "Just some text with no headers"
    sources = {"README.md": "Content"}

    result = map_sources_to_sections(template, sources, "Test")

    # Should return empty mapping when no sections found
    assert result == {}
    # LLM should not be called
    mock_call_llm.assert_not_called()


@patch("doc_evergreen.core.source_mapping.call_llm")
def test_map_sources_to_sections_llm_error(mock_call_llm):
    """Test handling of LLM errors."""
    template = """# Section

Content...
"""
    sources = {"file.py": "code"}

    # Mock LLM returning invalid JSON
    mock_call_llm.return_value = "Not valid JSON"

    with pytest.raises(ValueError, match="Failed to parse source mapping"):
        map_sources_to_sections(template, sources, "Test")


def test_save_source_map_first_version():
    """Test saving first version of source map."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        mapping = {
            "Installation": ["README.md", "setup.py"],
            "Usage": ["README.md"],
        }

        map_file = save_source_map(mapping, "readme", repo, metadata={"about": "Test README"})

        # Verify file was created
        assert map_file.exists()
        assert map_file.name == "readme-map.v1.yaml"

        # Verify content
        with open(map_file, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)

        assert content["metadata"]["template_name"] == "readme"
        assert content["metadata"]["version"] == 1
        assert content["metadata"]["about"] == "Test README"
        assert content["sections"]["Installation"]["sources"] == ["README.md", "setup.py"]
        assert content["sections"]["Usage"]["sources"] == ["README.md"]


def test_save_source_map_subsequent_versions():
    """Test saving creates incremented versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        mapping1 = {"Section1": ["file1.py"]}
        mapping2 = {"Section1": ["file1.py", "file2.py"]}

        # Save first version
        map_file1 = save_source_map(mapping1, "test", repo)
        assert map_file1.name == "test-map.v1.yaml"

        # Save second version
        map_file2 = save_source_map(mapping2, "test", repo)
        assert map_file2.name == "test-map.v2.yaml"

        # Both files should exist
        assert map_file1.exists()
        assert map_file2.exists()


def test_load_source_map_success():
    """Test loading source map from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Create a source map file
        mapping = {
            "Installation": ["README.md"],
            "API": ["src/api.py", "src/models.py"],
        }
        map_file = save_source_map(mapping, "test", repo)

        # Load it back
        loaded_mapping = load_source_map(map_file)

        assert len(loaded_mapping) == 2
        assert loaded_mapping["Installation"] == ["README.md"]
        assert loaded_mapping["API"] == ["src/api.py", "src/models.py"]


def test_load_source_map_not_found():
    """Test loading non-existent source map."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        map_file = repo / "nonexistent-map.yaml"

        with pytest.raises(FileNotFoundError):
            load_source_map(map_file)


def test_save_and_load_round_trip():
    """Test that saving and loading preserves mapping."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        original_mapping = {
            "Section A": ["file1.py", "file2.py"],
            "Section B": [],
            "Section C": ["file3.py"],
        }

        # Save
        map_file = save_source_map(original_mapping, "roundtrip", repo)

        # Load
        loaded_mapping = load_source_map(map_file)

        # Verify they match
        assert loaded_mapping == original_mapping


def test_save_source_map_creates_directory():
    """Test that save_source_map creates directory if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)

        # Directory should not exist yet
        maps_dir = repo / ".doc-evergreen" / "source-maps"
        assert not maps_dir.exists()

        mapping = {"Section": ["file.py"]}
        save_source_map(mapping, "test", repo)

        # Directory should now exist
        assert maps_dir.exists()
        assert maps_dir.is_dir()
