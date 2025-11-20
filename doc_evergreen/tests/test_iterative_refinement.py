"""Tests for iterative refinement workflow (Sprint 9 Day 3).

Following TDD: These tests are written FIRST and should FAIL until we implement the feature.
"""

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from doc_evergreen.cli import cli


@pytest.fixture
def test_template(tmp_path: Path) -> tuple[Path, Path]:
    """Create a simple test template and output file."""
    # Create template
    template_path = tmp_path / "test.json"
    template_path.write_text(
        """{
        "document": {
            "title": "Test Doc",
            "output": "output.md",
            "sections": [
                {
                    "heading": "Overview",
                    "prompt": "Write an overview",
                    "sources": ["source.md"]
                }
            ]
        }
    }"""
    )

    # Create source file
    source_path = tmp_path / "source.md"
    source_path.write_text("Test source content")

    # Create output file (existing)
    output_path = tmp_path / "output.md"
    output_path.write_text("# Old content\n\nThis is old.")

    return template_path, output_path


class TestIterativeRefinement:
    """Test iterative refinement workflow."""

    def test_offers_to_regenerate_after_applying_changes(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that after applying changes, user is asked if they want to regenerate.

        Given: A successful regeneration and applied changes
        When: Changes are applied
        Then: User is prompted "Regenerate with updated sources?"
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            # First generation returns new content
            mock_instance.generate.return_value = "# New Content\n\nFirst generation"
            mock_gen.return_value = mock_instance

            # Input: approve first change, reject regeneration
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\nn\n")

        # Should ask about regeneration
        assert "Regenerate" in result.output or "regenerate" in result.output

    def test_regenerates_when_user_confirms(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that regeneration happens when user says yes.

        Given: User confirms regeneration
        When: Prompted to regenerate
        Then: Generator is called again
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            # Two different generations
            mock_instance.generate.side_effect = [
                "# First Generation\n\nContent 1",
                "# Second Generation\n\nContent 2",
            ]
            mock_gen.return_value = mock_instance

            # Input: approve first, regenerate yes, reject second
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\ny\nn\n")

        # Generator should be called twice
        assert mock_instance.generate.call_count == 2

    def test_stops_when_user_rejects_regeneration(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that workflow stops when user rejects regeneration.

        Given: User rejects regeneration
        When: Prompted to regenerate
        Then: Workflow completes without regenerating
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# New Content\n\nGenerated"
            mock_gen.return_value = mock_instance

            # Input: approve first change, reject regeneration
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\nn\n")

        # Generator should only be called once
        assert mock_instance.generate.call_count == 1
        assert result.exit_code == 0

    def test_tracks_iteration_count(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that iteration count is tracked and displayed.

        Given: Multiple iterations
        When: User regenerates multiple times
        Then: Final output shows iteration count
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.side_effect = [
                "# Gen 1",
                "# Gen 2",
                "# Gen 3",
            ]
            mock_gen.return_value = mock_instance

            # Input: approve 1st, regen yes, approve 2nd, regen yes, approve 3rd, stop
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\ny\ny\ny\ny\nn\n")

        # Should mention iterations or count
        assert "iteration" in result.output.lower() or "3" in result.output

    def test_shows_diff_each_iteration(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that diff is shown for each iteration.

        Given: Multiple iterations with changes
        When: User regenerates
        Then: Diff is shown before each approval prompt
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.side_effect = [
                "# First",
                "# Second",
            ]
            mock_gen.return_value = mock_instance

            # Input: approve first, regenerate yes, approve second, stop
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\ny\ny\nn\n")

        # Should show diff markers (unified diff format)
        # Count how many times we see diff markers
        diff_markers = result.output.count("---") + result.output.count("+++")
        # Should see diff markers for multiple iterations
        assert diff_markers >= 2  # At least first and second iteration diffs

    def test_stops_if_no_changes_detected(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that iteration stops when regeneration produces no changes.

        Given: Regeneration produces identical content
        When: User confirms regeneration
        Then: Workflow stops with "No changes detected"
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            # First generates new content, second generates same content
            first_content = "# New Content\n\nThis is new"
            mock_instance.generate.side_effect = [
                first_content,
                first_content,  # Same content - no changes
            ]
            mock_gen.return_value = mock_instance

            # Input: approve first, regenerate yes
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\ny\n")

        # Should mention no changes
        assert "No changes" in result.output or "no changes" in result.output

    def test_iteration_works_with_auto_approve(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that --auto-approve flag works with iteration (no iteration with auto-approve).

        Given: --auto-approve flag is used
        When: Changes are applied
        Then: No regeneration prompt (one-shot mode)
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# New Content"
            mock_gen.return_value = mock_instance

            result = runner.invoke(cli, ["regen-doc", "--auto-approve", str(template_path)])

        # Should NOT ask about regeneration (auto-approve is one-shot)
        assert "Regenerate" not in result.output
        assert result.exit_code == 0
        assert mock_instance.generate.call_count == 1

    def test_user_can_reject_changes_during_iteration(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that user can reject changes during any iteration.

        Given: Multiple regenerations
        When: User rejects changes in second iteration
        Then: File keeps first generation content (not second)
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.side_effect = [
                "# First Generation",
                "# Second Generation",
            ]
            mock_gen.return_value = mock_instance

            # Input: approve first, regenerate yes, REJECT second
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\ny\nn\n")

        # Should have called generate twice
        assert mock_instance.generate.call_count == 2

        # Should show both diffs but only write first
        assert "First Generation" in result.output
        assert "Second Generation" in result.output

        # File should be written once (first iteration)
        # Note: We can't check file content directly because CliRunner uses isolated filesystem
        # Instead verify the workflow logic by checking output messages
        assert result.output.count("✓ File written") == 1  # Only written once
        assert result.exit_code == 0


class TestIterationCounting:
    """Test iteration count display."""

    def test_shows_completed_iterations_at_end(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test that final message shows how many iterations completed.

        Given: 3 successful iterations
        When: User stops iterating
        Then: Shows "Completed 3 iteration(s)"
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.side_effect = ["# Gen 1", "# Gen 2", "# Gen 3"]
            mock_gen.return_value = mock_instance

            # 3 iterations: approve, regen, approve, regen, approve, stop
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\ny\ny\ny\ny\nn\n")

        # Should show completion message with count
        assert "Completed" in result.output or "completed" in result.output
        assert "3" in result.output or "three" in result.output.lower()

    def test_shows_1_iteration_singular(self, test_template: tuple[Path, Path]) -> None:
        """
        🔴 RED: Test correct grammar for single iteration.

        Given: 1 iteration (no regeneration)
        When: Workflow completes
        Then: Shows "Completed 1 iteration" (singular)
        """
        template_path, output_path = test_template
        runner = CliRunner()

        with patch("doc_evergreen.cli.ChunkedGenerator") as mock_gen:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = "# Content"
            mock_gen.return_value = mock_instance

            # 1 iteration: approve, stop
            result = runner.invoke(cli, ["regen-doc", str(template_path)], input="y\nn\n")

        # Should show singular form
        assert ("1 iteration" in result.output) or ("Completed 1" in result.output)
