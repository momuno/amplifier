"""
Tests for versioned prompt loading system.
"""

from pathlib import Path

import pytest
import json

from doc_evergreen.prompts import get_prompt_version
from doc_evergreen.prompts import load_prompt


def test_load_prompt_success(tmp_path: Path):
    """Test loading a valid versioned prompt."""
    # Create a test prompt file
    prompt_data = {
        "versions": [
            {"version": "2025-01-13T19:00:00Z", "prompt": "This is version 1"},
            {"version": "2025-01-13T20:00:00Z", "prompt": "This is version 2 (most recent)"},
        ]
    }

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "test_prompt.json"

    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, indent=2, ensure_ascii=False)

    # Patch the prompts directory
    import doc_evergreen.prompts

    original_file = doc_evergreen.prompts.__file__
    try:
        doc_evergreen.prompts.__file__ = str(prompts_dir / "__init__.py")

        # Load the prompt - should get most recent version
        prompt = load_prompt("test_prompt")
        assert prompt == "This is version 2 (most recent)"

    finally:
        doc_evergreen.prompts.__file__ = original_file


def test_load_prompt_file_not_found(tmp_path: Path):
    """Test error when prompt file doesn't exist."""
    import doc_evergreen.prompts

    original_file = doc_evergreen.prompts.__file__
    try:
        doc_evergreen.prompts.__file__ = str(tmp_path / "__init__.py")

        with pytest.raises(FileNotFoundError, match="Prompt template not found"):
            load_prompt("nonexistent")

    finally:
        doc_evergreen.prompts.__file__ = original_file


def test_load_prompt_invalid_format(tmp_path: Path):
    """Test error when prompt file has invalid format."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "bad_prompt.json"

    # Write invalid format (missing versions key)
    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump({"prompt": "This is wrong"}, f, indent=2, ensure_ascii=False)

    import doc_evergreen.prompts

    original_file = doc_evergreen.prompts.__file__
    try:
        doc_evergreen.prompts.__file__ = str(prompts_dir / "__init__.py")

        with pytest.raises(ValueError, match="Invalid prompt file format"):
            load_prompt("bad_prompt")

    finally:
        doc_evergreen.prompts.__file__ = original_file


def test_load_prompt_no_versions(tmp_path: Path):
    """Test error when prompt file has no versions."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "empty_prompt.json"

    # Write empty versions list
    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump({"versions": []}, f, indent=2, ensure_ascii=False)

    import doc_evergreen.prompts

    original_file = doc_evergreen.prompts.__file__
    try:
        doc_evergreen.prompts.__file__ = str(prompts_dir / "__init__.py")

        with pytest.raises(ValueError, match="No versions found"):
            load_prompt("empty_prompt")

    finally:
        doc_evergreen.prompts.__file__ = original_file


def test_load_prompt_sorts_by_timestamp(tmp_path: Path):
    """Test that prompts are sorted by timestamp to get most recent."""
    # Create prompt with versions in non-chronological order
    prompt_data = {
        "versions": [
            {"version": "2025-01-13T22:00:00Z", "prompt": "Middle version"},
            {"version": "2025-01-13T20:00:00Z", "prompt": "Oldest version"},
            {"version": "2025-01-13T23:00:00Z", "prompt": "Newest version"},
        ]
    }

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "sorted_prompt.json"

    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, indent=2, ensure_ascii=False)

    import doc_evergreen.prompts

    original_file = doc_evergreen.prompts.__file__
    try:
        doc_evergreen.prompts.__file__ = str(prompts_dir / "__init__.py")

        # Should get the newest version
        prompt = load_prompt("sorted_prompt")
        assert prompt == "Newest version"

    finally:
        doc_evergreen.prompts.__file__ = original_file


def test_get_prompt_version_success(tmp_path: Path):
    """Test getting the version of a prompt."""
    prompt_data = {
        "versions": [
            {"version": "2025-01-13T19:00:00Z", "prompt": "Old version"},
            {"version": "2025-01-13T20:00:00Z", "prompt": "New version"},
        ]
    }

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "versioned_prompt.json"

    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, indent=2, ensure_ascii=False)

    import doc_evergreen.prompts

    original_file = doc_evergreen.prompts.__file__
    try:
        doc_evergreen.prompts.__file__ = str(prompts_dir / "__init__.py")

        # Should get the newest version timestamp
        version = get_prompt_version("versioned_prompt")
        assert version == "2025-01-13T20:00:00Z"

    finally:
        doc_evergreen.prompts.__file__ = original_file


def test_prompt_with_placeholders(tmp_path: Path):
    """Test that prompts with format placeholders are returned correctly."""
    prompt_data = {
        "versions": [{"version": "2025-01-13T19:00:00Z", "prompt": "Analyze {file_path}\n\nContent:\n{file_content}"}]
    }

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "placeholder_prompt.json"

    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, indent=2, ensure_ascii=False)

    import doc_evergreen.prompts

    original_file = doc_evergreen.prompts.__file__
    try:
        doc_evergreen.prompts.__file__ = str(prompts_dir / "__init__.py")

        prompt = load_prompt("placeholder_prompt")
        # Placeholders should be preserved
        assert "{file_path}" in prompt
        assert "{file_content}" in prompt

        # Should be able to format
        formatted = prompt.format(file_path="test.py", file_content="def foo(): pass")
        assert "test.py" in formatted
        assert "def foo(): pass" in formatted

    finally:
        doc_evergreen.prompts.__file__ = original_file
