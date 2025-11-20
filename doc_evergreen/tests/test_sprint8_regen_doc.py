"""
Tests for regen-doc CLI command (Sprint 8, Day 2).

Following TDD RED phase - all tests should FAIL initially.
Tests cover: parsing, generation, change detection, approval workflow,
file operations, and edge cases.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

# Note: regen_doc command doesn't exist yet - this is RED phase
# Tests expect a Click group with regen-doc command to be added
try:
    from doc_evergreen.cli import cli  # type: ignore[attr-defined]
except (ImportError, AttributeError):
    # Command doesn't exist yet - tests will fail (RED phase)
    cli = None  # type: ignore[assignment]


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def sample_template(temp_dir):
    """Create a sample template JSON file."""
    template = {
        "template_version": "1.0",
        "metadata": {"title": "Test Document", "last_updated": "2025-01-19"},
        "output_path": "test_output.md",
        "chunks": [{"chunk_id": "intro", "prompt": "Write an introduction", "dependencies": []}],
    }
    template_path = temp_dir / "template.json"
    template_path.write_text(json.dumps(template, indent=2))
    return template_path


@pytest.fixture
def sample_output(temp_dir):
    """Create existing output file for update tests."""
    output_path = temp_dir / "test_output.md"
    output_path.write_text("# Old Content\n\nThis is the old version.")
    return output_path


# ============================================================================
# Unit Tests - Template Parsing
# ============================================================================


def test_template_parsing_reads_file(runner, sample_template):
    """
    Given: A valid template JSON file
    When: regen-doc is called with template path
    Then: Template is parsed correctly
    """
    result = runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    # Should not fail due to parsing errors
    assert "Invalid template" not in result.output
    assert result.exit_code == 0


def test_template_parsing_validates_schema(runner, temp_dir):
    """
    Given: An invalid template JSON (missing required fields)
    When: regen-doc is called
    Then: Validation error is shown
    """
    invalid_template = temp_dir / "invalid.json"
    invalid_template.write_text(json.dumps({"invalid": "schema"}))

    result = runner.invoke(cli, ["regen-doc", str(invalid_template)])

    assert result.exit_code != 0
    assert "template_version" in result.output.lower() or "invalid" in result.output.lower()


# ============================================================================
# Unit Tests - Content Generation
# ============================================================================


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_content_generation_uses_chunked_generator(mock_gen_class, runner, sample_template):
    """
    Given: A template with chunks
    When: regen-doc is called
    Then: ChunkedGenerator is instantiated and used
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# Generated Content"
    mock_gen_class.return_value = mock_gen

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    mock_gen_class.assert_called_once()
    mock_gen.generate.assert_called_once()


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_content_generation_passes_template_chunks(mock_gen_class, runner, sample_template):
    """
    Given: Template with specific chunks
    When: regen-doc generates content
    Then: Chunks are passed to generator correctly
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# Generated Content"
    mock_gen_class.return_value = mock_gen

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    # Should instantiate with template data
    call_args = mock_gen_class.call_args
    assert call_args is not None


# ============================================================================
# Unit Tests - Change Detection Integration
# ============================================================================


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_change_detection_called_for_new_file(mock_gen_class, mock_detect, runner, sample_template):
    """
    Given: Template targeting non-existent file
    When: regen-doc generates content
    Then: detect_changes() is called with path and new content
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    # detect_changes returns (has_changes, diff_lines)
    mock_detect.return_value = (True, ["NEW FILE"])

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    mock_detect.assert_called_once()
    args = mock_detect.call_args[0]
    # First arg is Path to output file
    assert isinstance(args[0], Path | str)
    # Second arg is new content
    assert args[1] == "# New Content"


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_change_detection_called_for_existing_file(mock_gen_class, mock_detect, runner, sample_template, sample_output):
    """
    Given: Template targeting existing file
    When: regen-doc generates content
    Then: detect_changes() is called with path to existing file
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# Updated Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["mock diff line"])

    # Update template to point to existing file
    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(sample_output)
    sample_template.write_text(json.dumps(template_data))

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    mock_detect.assert_called_once()
    args = mock_detect.call_args[0]
    # First arg is Path to existing file
    assert str(sample_output) in str(args[0])


# ============================================================================
# Unit Tests - Diff Display
# ============================================================================


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_diff_display_shows_changes(mock_gen_class, mock_detect, runner, sample_template):
    """
    Given: Changes detected between old and new content
    When: regen-doc runs
    Then: Diff is displayed to user
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_diff = ["--- old\n", "+++ new\n", "@@ -1 +1 @@\n", "-Old\n", "+New\n"]
    mock_detect.return_value = (True, mock_diff)

    result = runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    assert "---" in result.output or "diff" in result.output.lower()


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_diff_display_shows_new_file_indicator(mock_gen_class, mock_detect, runner, sample_template):
    """
    Given: New file creation
    When: regen-doc runs
    Then: Indicates file is new, not modified
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    result = runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    assert "new" in result.output.lower() or "creat" in result.output.lower()


# ============================================================================
# Unit Tests - Approval Workflow
# ============================================================================


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_approval_prompts_user_without_auto_approve(mock_gen_class, mock_detect, runner, sample_template):
    """
    Given: Changes detected and no --auto-approve flag
    When: regen-doc runs
    Then: User is prompted for approval
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    result = runner.invoke(cli, ["regen-doc", str(sample_template)], input="n\n")

    assert "apply" in result.output.lower() or "proceed" in result.output.lower()


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_approval_accepts_yes(mock_gen_class, mock_detect, runner, sample_template, temp_dir):
    """
    Given: User approves changes
    When: Prompted for approval
    Then: File is written
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    output_path = temp_dir / "output.md"
    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(output_path)
    sample_template.write_text(json.dumps(template_data))

    runner.invoke(cli, ["regen-doc", str(sample_template)], input="y\n")

    assert output_path.exists()
    assert "# New Content" in output_path.read_text()


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_approval_rejects_no(mock_gen_class, mock_detect, runner, sample_template, temp_dir):
    """
    Given: User rejects changes
    When: Prompted for approval
    Then: File is NOT written
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    output_path = temp_dir / "output.md"
    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(output_path)
    sample_template.write_text(json.dumps(template_data))

    result = runner.invoke(cli, ["regen-doc", str(sample_template)], input="n\n")

    assert not output_path.exists()
    assert "cancel" in result.output.lower() or "abort" in result.output.lower()


# ============================================================================
# Unit Tests - Auto-Approve Flag
# ============================================================================


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_auto_approve_skips_prompt(mock_gen_class, mock_detect, runner, sample_template):
    """
    Given: --auto-approve flag set
    When: regen-doc runs
    Then: No approval prompt shown
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    result = runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    # Should not contain approval prompt text
    assert "apply" not in result.output.lower() or "automatically" in result.output.lower()


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_auto_approve_writes_file_immediately(mock_gen_class, mock_detect, runner, sample_template, temp_dir):
    """
    Given: --auto-approve flag set
    When: regen-doc runs
    Then: File written without user input
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    output_path = temp_dir / "output.md"
    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(output_path)
    sample_template.write_text(json.dumps(template_data))

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    assert output_path.exists()
    assert "# New Content" in output_path.read_text()


# ============================================================================
# Unit Tests - Output Path Override
# ============================================================================


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_output_override_uses_custom_path(mock_gen_class, mock_detect, runner, sample_template, temp_dir):
    """
    Given: --output flag with custom path
    When: regen-doc runs
    Then: File written to custom path, not template path
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    custom_path = temp_dir / "custom_output.md"

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve", "--output", str(custom_path)])

    assert custom_path.exists()
    assert "# New Content" in custom_path.read_text()


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_output_override_ignores_template_path(mock_gen_class, mock_detect, runner, sample_template, temp_dir):
    """
    Given: --output flag with custom path
    When: regen-doc runs
    Then: Template output_path is ignored
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    template_output = temp_dir / "template_output.md"
    custom_output = temp_dir / "custom_output.md"

    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(template_output)
    sample_template.write_text(json.dumps(template_data))

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve", "--output", str(custom_output)])

    assert custom_output.exists()
    assert not template_output.exists()


# ============================================================================
# Unit Tests - File Writing
# ============================================================================


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_file_writing_creates_parent_dirs(mock_gen_class, mock_detect, runner, sample_template, temp_dir):
    """
    Given: Output path with non-existent parent directories
    When: regen-doc writes file
    Then: Parent directories are created
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# New Content"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    nested_path = temp_dir / "subdir" / "nested" / "output.md"
    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(nested_path)
    sample_template.write_text(json.dumps(template_data))

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    assert nested_path.exists()
    assert nested_path.parent.exists()


@patch("doc_evergreen.cli.detect_changes")
@patch("doc_evergreen.cli.ChunkedGenerator")
def test_file_writing_preserves_utf8(mock_gen_class, mock_detect, runner, sample_template, temp_dir):
    """
    Given: Generated content with UTF-8 characters
    When: regen-doc writes file
    Then: UTF-8 encoding is preserved
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# Test 测试 🎉"
    mock_gen_class.return_value = mock_gen

    mock_detect.return_value = (True, ["NEW FILE"])

    output_path = temp_dir / "output.md"
    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(output_path)
    sample_template.write_text(json.dumps(template_data))

    runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    content = output_path.read_text(encoding="utf-8")
    assert "测试" in content
    assert "🎉" in content


# ============================================================================
# Integration Tests - Complete Workflows
# ============================================================================


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_new_file_workflow_end_to_end(mock_gen_class, runner, sample_template, temp_dir):
    """
    Given: Template for new file
    When: Full regen-doc workflow executes
    Then: File created with correct content
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# Brand New Document\n\nGenerated content here."
    mock_gen_class.return_value = mock_gen

    output_path = temp_dir / "new_doc.md"
    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(output_path)
    sample_template.write_text(json.dumps(template_data))

    result = runner.invoke(cli, ["regen-doc", str(sample_template)], input="y\n")

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Brand New Document" in output_path.read_text()


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_update_file_workflow_end_to_end(mock_gen_class, runner, sample_template, sample_output):
    """
    Given: Template for existing file
    When: Full regen-doc workflow executes
    Then: File updated with new content
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# Updated Document\n\nNew content here."
    mock_gen_class.return_value = mock_gen

    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(sample_output)
    sample_template.write_text(json.dumps(template_data))

    result = runner.invoke(cli, ["regen-doc", str(sample_template)], input="y\n")

    assert result.exit_code == 0
    assert "Updated Document" in sample_output.read_text()
    assert "Old Content" not in sample_output.read_text()


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_no_changes_workflow(mock_gen_class, runner, sample_template, sample_output):
    """
    Given: Generated content identical to existing file
    When: regen-doc runs
    Then: Reports no changes, doesn't prompt
    """
    # Generate same content as existing file
    existing_content = sample_output.read_text()

    mock_gen = Mock()
    mock_gen.generate.return_value = existing_content
    mock_gen_class.return_value = mock_gen

    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(sample_output)
    sample_template.write_text(json.dumps(template_data))

    result = runner.invoke(cli, ["regen-doc", str(sample_template)])

    assert "no changes" in result.output.lower() or "identical" in result.output.lower()
    # Should not prompt for approval
    assert "apply" not in result.output.lower()


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_rejection_workflow(mock_gen_class, runner, sample_template, sample_output):
    """
    Given: User rejects changes
    When: Full workflow executes
    Then: Original file unchanged
    """
    original_content = sample_output.read_text()

    mock_gen = Mock()
    mock_gen.generate.return_value = "# Different Content"
    mock_gen_class.return_value = mock_gen

    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(sample_output)
    sample_template.write_text(json.dumps(template_data))

    runner.invoke(cli, ["regen-doc", str(sample_template)], input="n\n")

    # File should remain unchanged
    assert sample_output.read_text() == original_content


# ============================================================================
# Edge Cases
# ============================================================================


def test_missing_template_file_error(runner):
    """
    Given: Non-existent template file
    When: regen-doc is called
    Then: Clear error message shown
    """
    result = runner.invoke(cli, ["regen-doc", "/nonexistent/template.json"])

    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "exist" in result.output.lower()


def test_invalid_json_error(runner, temp_dir):
    """
    Given: Template file with invalid JSON
    When: regen-doc is called
    Then: JSON parse error shown
    """
    invalid_json = temp_dir / "invalid.json"
    invalid_json.write_text("{invalid json content")

    result = runner.invoke(cli, ["regen-doc", str(invalid_json)])

    assert result.exit_code != 0
    assert "json" in result.output.lower() or "parse" in result.output.lower()


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_read_only_output_path_error(mock_gen_class, runner, sample_template, temp_dir):
    """
    Given: Output path that cannot be written
    When: regen-doc tries to write file
    Then: Permission error shown
    """
    mock_gen = Mock()
    mock_gen.generate.return_value = "# Content"
    mock_gen_class.return_value = mock_gen

    # Create read-only file
    readonly_path = temp_dir / "readonly.md"
    readonly_path.write_text("existing")
    readonly_path.chmod(0o444)

    template_data = json.loads(sample_template.read_text())
    template_data["output_path"] = str(readonly_path)
    sample_template.write_text(json.dumps(template_data))

    result = runner.invoke(cli, ["regen-doc", str(sample_template), "--auto-approve"])

    # Should handle permission error gracefully
    assert result.exit_code != 0
    assert "permission" in result.output.lower() or "error" in result.output.lower()

    # Cleanup
    readonly_path.chmod(0o644)


@patch("doc_evergreen.cli.ChunkedGenerator")
def test_generation_error_handling(mock_gen_class, runner, sample_template):
    """
    Given: Generator raises exception during generation
    When: regen-doc runs
    Then: Error is caught and reported gracefully
    """
    mock_gen = Mock()
    mock_gen.generate.side_effect = Exception("Generation failed!")
    mock_gen_class.return_value = mock_gen

    result = runner.invoke(cli, ["regen-doc", str(sample_template)])

    assert result.exit_code != 0
    assert "error" in result.output.lower() or "fail" in result.output.lower()
