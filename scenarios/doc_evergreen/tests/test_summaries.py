"""
Tests for versioned file summary storage system.
"""

from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import json

from doc_evergreen.core.summaries import add_summary
from doc_evergreen.core.summaries import get_file_summaries_dir
from doc_evergreen.core.summaries import get_git_commit_hash
from doc_evergreen.core.summaries import get_summary
from doc_evergreen.core.summaries import get_versioned_summary_path
from doc_evergreen.core.summaries import sanitize_filepath_to_filename


def test_sanitize_filepath_to_filename():
    """Test filepath to filename conversion."""
    test_cases = [
        ("src/auth.py", "src__auth__py.json"),
        ("README.md", "README__md.json"),
        ("docs/api/endpoints.md", "docs__api__endpoints__md.json"),
        ("path/to/file.test.py", "path__to__file__test__py.json"),
    ]

    for file_path, expected in test_cases:
        result = sanitize_filepath_to_filename(file_path)
        assert result == expected, f"Failed for {file_path}: got {result}, expected {expected}"


def test_get_file_summaries_dir(tmp_path: Path):
    """Test getting the file summaries directory path."""
    summaries_dir = get_file_summaries_dir(tmp_path)
    assert summaries_dir == tmp_path / ".doc-evergreen" / "2_file_summaries"


def test_get_versioned_summary_path(tmp_path: Path):
    """Test getting the versioned summary file path."""
    file_path = "src/auth.py"
    summary_path = get_versioned_summary_path(file_path, tmp_path)

    expected_path = tmp_path / ".doc-evergreen" / "2_file_summaries" / "src__auth__py.json"
    assert summary_path == expected_path


def test_add_and_get_summary_success(tmp_path: Path):
    """Test adding and retrieving a versioned summary."""
    file_path = "test/example.py"
    summary_text = "This file contains example code for testing."
    prompt_name = "summarize_file"
    prompt_version = "2025-01-13T19:00:00Z"

    # Add the summary
    add_summary(file_path, summary_text, tmp_path, prompt_name, prompt_version)

    # Verify it was saved
    summary_path = get_versioned_summary_path(file_path, tmp_path)
    assert summary_path.exists()

    # Retrieve it - should get the most recent version
    summary_data = get_summary(file_path, tmp_path)

    assert summary_data is not None
    assert summary_data["file_path"] == file_path
    assert summary_data["summary"] == summary_text
    assert "prompt" in summary_data
    prompt_data = summary_data["prompt"]
    assert isinstance(prompt_data, dict)
    assert prompt_data["name"] == f"prompts/{prompt_name}.json"  # type: ignore[index]
    assert prompt_data["version"] == prompt_version  # type: ignore[index]
    assert "commit_hash" in summary_data
    assert "timestamp" in summary_data


def test_add_multiple_versions(tmp_path: Path):
    """Test that multiple calls to add_summary append versions."""
    file_path = "test/multi.py"

    # Add first version
    add_summary(file_path, "First summary", tmp_path, "summarize_file", "2025-01-13T19:00:00Z")

    # Add second version
    add_summary(file_path, "Second summary", tmp_path, "summarize_file", "2025-01-13T20:00:00Z")

    # Add third version
    add_summary(file_path, "Third summary", tmp_path, "summarize_file", "2025-01-13T21:00:00Z")

    # Read the JSON file directly
    summary_path = get_versioned_summary_path(file_path, tmp_path)
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Should have 3 versions
    assert "versions" in data
    assert len(data["versions"]) == 3
    # Access summary from new standardized structure
    assert data["versions"][0]["outputs"]["summary"] == "First summary"
    assert data["versions"][1]["outputs"]["summary"] == "Second summary"
    assert data["versions"][2]["outputs"]["summary"] == "Third summary"


def test_get_summary_returns_most_recent(tmp_path: Path):
    """Test that get_summary returns the most recent version."""
    file_path = "test/recent.py"

    # Add versions with different timestamps (not in chronological order)
    import time

    add_summary(file_path, "Old summary", tmp_path, "summarize_file", "2025-01-13T19:00:00Z")
    time.sleep(0.01)  # Ensure different timestamps
    add_summary(file_path, "Middle summary", tmp_path, "summarize_file", "2025-01-13T20:00:00Z")
    time.sleep(0.01)
    add_summary(file_path, "Newest summary", tmp_path, "summarize_file", "2025-01-13T21:00:00Z")

    # Get summary should return the most recent
    summary_data = get_summary(file_path, tmp_path)

    assert summary_data is not None
    assert summary_data["summary"] == "Newest summary"
    prompt_data = summary_data["prompt"]
    assert isinstance(prompt_data, dict)
    assert prompt_data["version"] == "2025-01-13T21:00:00Z"  # type: ignore[index]


def test_add_summary_creates_directory(tmp_path: Path):
    """Test that add_summary creates the summaries directory if it doesn't exist."""
    summaries_dir = get_file_summaries_dir(tmp_path)
    assert not summaries_dir.exists()

    # Add a summary
    add_summary("test.py", "Test summary", tmp_path, "summarize_file", "2025-01-13T19:00:00Z")

    # Directory should now exist
    assert summaries_dir.exists()


def test_get_summary_not_found(tmp_path: Path):
    """Test getting a summary that doesn't exist."""
    result = get_summary("nonexistent/file.py", tmp_path)
    assert result is None


def test_get_summary_invalid_json(tmp_path: Path):
    """Test handling of invalid JSON in summary file."""
    file_path = "test/bad.py"
    summary_path = get_versioned_summary_path(file_path, tmp_path)

    # Create the directory and write invalid JSON
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("{not valid json")

    # Should return None on error
    result = get_summary(file_path, tmp_path)
    assert result is None


def test_add_summary_appends_versions(tmp_path: Path):
    """Test that add_summary appends new versions instead of replacing."""
    file_path = "test/update.py"

    # Add initial summary
    add_summary(file_path, "Original summary", tmp_path, "summarize_file", "2025-01-13T19:00:00Z")
    original = get_summary(file_path, tmp_path)

    # Add another version
    add_summary(file_path, "Updated summary", tmp_path, "summarize_file", "2025-01-13T20:00:00Z")
    updated = get_summary(file_path, tmp_path)

    assert original is not None
    assert updated is not None

    # get_summary should return the most recent
    assert updated["summary"] == "Updated summary"
    prompt_data = updated["prompt"]
    assert isinstance(prompt_data, dict)
    assert prompt_data["version"] == "2025-01-13T20:00:00Z"  # type: ignore[index]
    assert updated["timestamp"] != original["timestamp"]

    # Both versions should exist in the file
    summary_path = get_versioned_summary_path(file_path, tmp_path)
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data["versions"]) == 2
    # Access summary from new standardized structure
    assert data["versions"][0]["outputs"]["summary"] == "Original summary"
    assert data["versions"][1]["outputs"]["summary"] == "Updated summary"


def test_get_git_commit_hash_success(tmp_path: Path):
    """Test getting git commit hash for a file."""
    # Mock successful git log command
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "abc123def456789\n"

    with patch("subprocess.run", return_value=mock_result):
        commit_hash = get_git_commit_hash("test.py", tmp_path)
        assert commit_hash == "abc123def456789"


def test_get_git_commit_hash_uncommitted(tmp_path: Path):
    """Test getting commit hash for uncommitted file."""
    # Mock git log returning nothing (file not committed)
    mock_log_result = Mock()
    mock_log_result.returncode = 0
    mock_log_result.stdout = ""

    # Mock git rev-parse HEAD returning current HEAD
    mock_head_result = Mock()
    mock_head_result.returncode = 0
    mock_head_result.stdout = "current_head_hash\n"

    with patch("subprocess.run", side_effect=[mock_log_result, mock_head_result]):
        commit_hash = get_git_commit_hash("test.py", tmp_path)
        assert commit_hash == "current_head_hash-uncommitted"


def test_get_git_commit_hash_not_in_git(tmp_path: Path):
    """Test getting commit hash when not in a git repo."""
    # Mock git commands failing
    mock_result = Mock()
    mock_result.returncode = 128  # Git error code
    mock_result.stdout = ""

    with patch("subprocess.run", return_value=mock_result):
        commit_hash = get_git_commit_hash("test.py", tmp_path)
        assert commit_hash is None


def test_get_git_commit_hash_exception(tmp_path: Path):
    """Test handling of exceptions when getting commit hash."""
    with patch("subprocess.run", side_effect=Exception("Git not available")):
        commit_hash = get_git_commit_hash("test.py", tmp_path)
        assert commit_hash is None


def test_add_summary_with_not_in_git(tmp_path: Path):
    """Test add_summary when file is not in git."""
    file_path = "test/no_git.py"

    # Mock git returning None
    with patch("doc_evergreen.core.summaries.get_git_commit_hash", return_value=None):
        add_summary(file_path, "Test summary", tmp_path, "summarize_file", "2025-01-13T19:00:00Z")

        summary_data = get_summary(file_path, tmp_path)
        assert summary_data is not None
        assert summary_data["commit_hash"] == "not-in-git"


def test_summary_json_structure(tmp_path: Path):
    """Test that saved summary has correct versioned JSON structure."""
    file_path = "test/structure.py"
    summary_text = "Test summary text"
    prompt_name = "summarize_file"
    prompt_version = "2025-01-13T19:00:00Z"

    # Mock git to return a specific hash
    with patch("doc_evergreen.core.summaries.get_git_commit_hash", return_value="test_commit_hash"):
        add_summary(file_path, summary_text, tmp_path, prompt_name, prompt_version)

    # Read the JSON file directly
    summary_path = get_versioned_summary_path(file_path, tmp_path)
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify top-level structure (uses 'name' with parent directory)
    assert "name" in data
    assert "versions" in data
    # Name should include parent directory and sanitized filename
    expected_name = f"2_file_summaries/{sanitize_filepath_to_filename(file_path).replace('.json', '')}"
    assert data["name"] == expected_name

    # Verify versions array has one entry
    assert len(data["versions"]) == 1
    version = data["versions"][0]

    # Verify new standardized structure
    assert "version" in version  # version field contains the timestamp
    assert "prompt" in version
    assert "inputs" in version
    assert "outputs" in version

    # Verify version field exists (timestamp)
    assert version["version"]  # Just verify it exists

    # Verify prompt structure
    assert "name" in version["prompt"]
    assert "version" in version["prompt"]

    # Verify inputs
    assert version["inputs"]["commit_hash"] == "test_commit_hash"
    assert version["inputs"]["file_path"] == file_path

    # Verify prompt values (name is now full file path)
    assert version["prompt"]["name"] == f"prompts/{prompt_name}.json"
    assert version["prompt"]["version"] == prompt_version

    # Verify outputs
    assert version["outputs"]["summary"] == summary_text


def test_multiple_files_in_same_directory(tmp_path: Path):
    """Test storing summaries for multiple files."""
    files = ["src/auth.py", "src/models.py", "src/utils.py"]

    for file_path in files:
        add_summary(file_path, f"Summary for {file_path}", tmp_path, "summarize_file", "2025-01-13T19:00:00Z")

    # Verify all were saved
    summaries_dir = get_file_summaries_dir(tmp_path)
    saved_files = list(summaries_dir.glob("*.json"))
    assert len(saved_files) == len(files)

    # Verify each can be retrieved
    for file_path in files:
        summary_data = get_summary(file_path, tmp_path)
        assert summary_data is not None
        assert summary_data["summary"] == f"Summary for {file_path}"


def test_legacy_format_conversion(tmp_path: Path):
    """Test that legacy format is automatically converted to versioned format."""
    file_path = "test/legacy.py"
    summary_path = get_versioned_summary_path(file_path, tmp_path)

    # Create a legacy format file
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_data = {
        "file_path": file_path,
        "commit_hash": "legacy_hash",
        "prompt_version": "2025-01-13T19:00:00Z",
        "summary": "Legacy summary",
        "timestamp": "2025-01-13T22:00:00Z",
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(legacy_data, f, indent=2, ensure_ascii=False)

    # get_summary should read the legacy format
    summary_data = get_summary(file_path, tmp_path)
    assert summary_data is not None
    assert summary_data["summary"] == "Legacy summary"
    assert summary_data["commit_hash"] == "legacy_hash"

    # Adding a new summary should convert to versioned format
    add_summary(file_path, "New summary", tmp_path, "summarize_file", "2025-01-13T21:00:00Z")

    # Read the file directly
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Should now be in versioned format with 2 versions
    assert "versions" in data
    assert len(data["versions"]) == 2
    # Access summary from new standardized structure
    assert data["versions"][0]["outputs"]["summary"] == "Legacy summary"  # Converted legacy
    assert data["versions"][1]["outputs"]["summary"] == "New summary"  # New version

    # get_summary should return the most recent
    summary_data = get_summary(file_path, tmp_path)
    assert summary_data is not None
    assert summary_data["summary"] == "New summary"
