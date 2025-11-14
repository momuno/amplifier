"""
Tests for relevancy scoring storage system.
"""

import json
from pathlib import Path

from doc_evergreen.core.relevancy import add_relevancy_score
from doc_evergreen.core.relevancy import get_project_relevancy_dir
from doc_evergreen.core.relevancy import get_relevancy_path
from doc_evergreen.core.relevancy import get_relevancy_score


def test_get_project_relevancy_dir(tmp_path: Path):
    """Test getting the project relevancy directory path."""
    relevancy_dir = get_project_relevancy_dir(tmp_path, "test-project")
    assert relevancy_dir == tmp_path / ".doc-evergreen" / "projects" / "test-project" / "3_relevancy"


def test_get_relevancy_path(tmp_path: Path):
    """Test getting the relevancy file path."""
    file_path = "src/auth.py"
    relevancy_path = get_relevancy_path(file_path, tmp_path, "test-project")

    expected_path = tmp_path / ".doc-evergreen" / "projects" / "test-project" / "3_relevancy" / "src__auth__py.json"
    assert relevancy_path == expected_path


def test_add_and_get_relevancy_score_success(tmp_path: Path):
    """Test adding and retrieving a relevancy score."""
    file_path = "test/example.py"
    doc_description = "API documentation for authentication module"
    relevancy_explanation = "This file contains the core authentication logic"
    relevancy_score = 9
    summary_timestamp = "2025-01-13T22:00:00Z"
    prompt_name = "score_relevancy"
    prompt_version = "2025-01-13T23:00:00Z"
    project_name = "api-docs"

    # Add the relevancy score
    summary_text = "This is the summary text used for scoring"
    add_relevancy_score(
        file_path,
        doc_description,
        relevancy_explanation,
        relevancy_score,
        summary_text,
        summary_timestamp,
        tmp_path,
        project_name,
        prompt_name,
        prompt_version,
    )

    # Verify it was saved
    relevancy_path = get_relevancy_path(file_path, tmp_path, project_name)
    assert relevancy_path.exists()

    # Retrieve it - should get the most recent version
    relevancy_data = get_relevancy_score(file_path, tmp_path, project_name)

    assert relevancy_data is not None
    assert relevancy_data["file_path"] == file_path
    assert relevancy_data["project_name"] == project_name
    assert relevancy_data["doc_description"] == doc_description
    assert relevancy_data["relevancy_explanation"] == relevancy_explanation
    assert relevancy_data["relevancy_score"] == relevancy_score
    assert "file_summary" in relevancy_data
    file_summary_data = relevancy_data["file_summary"]
    assert isinstance(file_summary_data, dict)
    assert file_summary_data["name"] == "2_file_summaries/test__example__py.json"  # type: ignore[index]
    assert file_summary_data["version"] == summary_timestamp  # type: ignore[index]
    assert "prompt" in relevancy_data
    prompt_data = relevancy_data["prompt"]
    assert isinstance(prompt_data, dict)
    assert prompt_data["name"] == f"prompts/{prompt_name}.json"  # type: ignore[index]
    assert prompt_data["version"] == prompt_version  # type: ignore[index]
    assert "timestamp" in relevancy_data


def test_add_multiple_versions(tmp_path: Path):
    """Test that multiple calls to add_relevancy_score append versions."""
    file_path = "test/multi.py"
    project_name = "docs"

    # Add first version
    add_relevancy_score(
        file_path,
        "First doc",
        "First explanation",
        7,
        "First summary text",
        "2025-01-13T19:00:00Z",
        tmp_path,
        project_name,
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )

    # Add second version
    add_relevancy_score(
        file_path,
        "Second doc",
        "Second explanation",
        8,
        "Second summary text",
        "2025-01-13T20:00:00Z",
        tmp_path,
        project_name,
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )

    # Add third version
    add_relevancy_score(
        file_path,
        "Third doc",
        "Third explanation",
        9,
        "Third summary text",
        "2025-01-13T21:00:00Z",
        tmp_path,
        project_name,
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )

    # Read the JSON file directly
    relevancy_path = get_relevancy_path(file_path, tmp_path, project_name)
    with open(relevancy_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Should have 3 versions
    assert "versions" in data
    assert len(data["versions"]) == 3
    # Access from new standardized structure
    assert data["versions"][0]["outputs"]["relevancy"]["explanation"] == "First explanation"
    assert data["versions"][1]["outputs"]["relevancy"]["explanation"] == "Second explanation"
    assert data["versions"][2]["outputs"]["relevancy"]["explanation"] == "Third explanation"


def test_get_relevancy_score_returns_most_recent(tmp_path: Path):
    """Test that get_relevancy_score returns the most recent version."""
    file_path = "test/recent.py"
    project_name = "docs"

    # Add versions with different timestamps (not in chronological order)
    import time

    add_relevancy_score(
        file_path,
        "Old doc",
        "Old explanation",
        5,
        "Old summary",
        "2025-01-13T19:00:00Z",
        tmp_path,
        project_name,
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )
    time.sleep(0.01)  # Ensure different timestamps
    add_relevancy_score(
        file_path,
        "Middle doc",
        "Middle explanation",
        7,
        "Middle summary",
        "2025-01-13T20:00:00Z",
        tmp_path,
        project_name,
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )
    time.sleep(0.01)
    add_relevancy_score(
        file_path,
        "Newest doc",
        "Newest explanation",
        9,
        "Newest summary",
        "2025-01-13T21:00:00Z",
        tmp_path,
        project_name,
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )

    # Get relevancy score should return the most recent
    relevancy_data = get_relevancy_score(file_path, tmp_path, project_name)

    assert relevancy_data is not None
    assert relevancy_data["relevancy_explanation"] == "Newest explanation"
    assert relevancy_data["relevancy_score"] == 9


def test_add_relevancy_score_creates_directory(tmp_path: Path):
    """Test that add_relevancy_score creates the directory if it doesn't exist."""
    project_name = "docs"
    relevancy_dir = get_project_relevancy_dir(tmp_path, project_name)
    assert not relevancy_dir.exists()

    # Add a relevancy score
    add_relevancy_score(
        "test.py",
        "Test doc",
        "Test explanation",
        5,
        "Test summary",
        "2025-01-13T19:00:00Z",
        tmp_path,
        project_name,
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )

    # Directory should now exist
    assert relevancy_dir.exists()


def test_get_relevancy_score_not_found(tmp_path: Path):
    """Test getting a relevancy score that doesn't exist."""
    result = get_relevancy_score("nonexistent/file.py", tmp_path, "nonexistent-project")
    assert result is None


def test_get_relevancy_score_invalid_json(tmp_path: Path):
    """Test handling of invalid JSON in relevancy file."""
    file_path = "test/bad.py"
    project_name = "docs"
    relevancy_path = get_relevancy_path(file_path, tmp_path, project_name)

    # Create the directory and write invalid JSON
    relevancy_path.parent.mkdir(parents=True, exist_ok=True)
    relevancy_path.write_text("{not valid json")

    # Should return None on error
    result = get_relevancy_score(file_path, tmp_path, project_name)
    assert result is None


def test_relevancy_json_structure(tmp_path: Path):
    """Test that saved relevancy has correct versioned JSON structure."""
    file_path = "test/structure.py"
    doc_description = "Test documentation"
    relevancy_explanation = "Test explanation"
    relevancy_score = 8
    summary_text = "Test summary text"
    summary_timestamp = "2025-01-13T22:00:00Z"
    prompt_name = "score_relevancy"
    prompt_version = "2025-01-13T23:00:00Z"
    project_name = "docs"

    add_relevancy_score(
        file_path,
        doc_description,
        relevancy_explanation,
        relevancy_score,
        summary_text,
        summary_timestamp,
        tmp_path,
        project_name,
        prompt_name,
        prompt_version,
    )

    # Read the JSON file directly
    relevancy_path = get_relevancy_path(file_path, tmp_path, project_name)
    with open(relevancy_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify top-level structure (uses 'name' with parent directory)
    assert "name" in data
    assert "project_name" in data
    assert "versions" in data
    from doc_evergreen.core.summaries import sanitize_filepath_to_filename

    # Name should include parent directory and sanitized filename
    expected_name = f"3_relevancy/{sanitize_filepath_to_filename(file_path).replace('.json', '')}"
    assert data["name"] == expected_name
    assert data["project_name"] == project_name

    # Verify versions array has one entry
    assert len(data["versions"]) == 1
    version = data["versions"][0]

    # Verify new standardized structure
    assert "version" in version  # version field contains the timestamp
    assert "outputs" in version
    assert "prompt" in version
    assert "inputs" in version

    # Verify prompt structure
    assert "name" in version["prompt"]
    assert "version" in version["prompt"]

    # Verify inputs structure
    assert "doc_description" in version["inputs"]
    assert "file_summary" in version["inputs"]
    assert "name" in version["inputs"]["file_summary"]
    assert "version" in version["inputs"]["file_summary"]

    # Verify outputs structure
    assert "relevancy" in version["outputs"]
    assert "explanation" in version["outputs"]["relevancy"]
    assert "score" in version["outputs"]["relevancy"]

    # Verify values
    assert version["inputs"]["doc_description"] == doc_description
    assert version["prompt"]["name"] == f"prompts/{prompt_name}.json"
    assert version["prompt"]["version"] == prompt_version
    assert version["inputs"]["file_summary"]["version"] == summary_timestamp
    assert version["outputs"]["relevancy"]["explanation"] == relevancy_explanation
    assert version["outputs"]["relevancy"]["score"] == relevancy_score


def test_multiple_projects_same_file(tmp_path: Path):
    """Test storing relevancy for same file in different projects."""
    file_path = "src/shared.py"

    # Add relevancy for first project
    add_relevancy_score(
        file_path,
        "API docs",
        "Core API logic",
        9,
        "Shared utilities summary",
        "2025-01-13T22:00:00Z",
        tmp_path,
        "api-docs",
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )

    # Add relevancy for second project
    add_relevancy_score(
        file_path,
        "User guide",
        "Not relevant to user guide",
        2,
        "Shared utilities summary",
        "2025-01-13T22:00:00Z",
        tmp_path,
        "user-guide",
        "score_relevancy",
        "2025-01-13T23:00:00Z",
    )

    # Verify both were saved independently
    api_relevancy = get_relevancy_score(file_path, tmp_path, "api-docs")
    guide_relevancy = get_relevancy_score(file_path, tmp_path, "user-guide")

    assert api_relevancy is not None
    assert guide_relevancy is not None

    assert api_relevancy["relevancy_score"] == 9
    assert guide_relevancy["relevancy_score"] == 2

    assert api_relevancy["project_name"] == "api-docs"
    assert guide_relevancy["project_name"] == "user-guide"
