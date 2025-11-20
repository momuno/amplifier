"""Tests for change detection module.

Following TDD red-green-refactor cycle:
🔴 RED: Write failing tests first
🟢 GREEN: Implement minimal code to pass
🔵 REFACTOR: Improve quality while tests protect
"""

from pathlib import Path

from doc_evergreen.change_detection import detect_changes


class TestDetectChangesNewFile:
    """Test detection when file doesn't exist."""

    def test_new_file_returns_true_with_new_file_marker(self, tmp_path: Path) -> None:
        """
        Given: A file path that doesn't exist
        When: detect_changes is called with new content
        Then: Returns (True, ["NEW FILE"])
        """
        # Arrange
        nonexistent_file = tmp_path / "new_file.md"
        new_content = "# New Content\n\nThis is new."

        # Act
        has_changes, diff_lines = detect_changes(nonexistent_file, new_content)

        # Assert
        assert has_changes is True
        assert diff_lines == ["NEW FILE"]

    def test_new_file_with_empty_content(self, tmp_path: Path) -> None:
        """
        Given: A file path that doesn't exist and empty content
        When: detect_changes is called
        Then: Returns (True, ["NEW FILE"])
        """
        # Arrange
        nonexistent_file = tmp_path / "empty_new.md"
        new_content = ""

        # Act
        has_changes, diff_lines = detect_changes(nonexistent_file, new_content)

        # Assert
        assert has_changes is True
        assert diff_lines == ["NEW FILE"]


class TestDetectChangesNoChanges:
    """Test detection when content is identical."""

    def test_identical_content_returns_false_with_empty_diff(self, tmp_path: Path) -> None:
        """
        Given: An existing file with content
        When: detect_changes is called with identical content
        Then: Returns (False, [])
        """
        # Arrange
        existing_file = tmp_path / "existing.md"
        content = "# Title\n\nSome content here.\n"
        existing_file.write_text(content)

        # Act
        has_changes, diff_lines = detect_changes(existing_file, content)

        # Assert
        assert has_changes is False
        assert diff_lines == []

    def test_empty_file_vs_empty_content(self, tmp_path: Path) -> None:
        """
        Given: An existing empty file
        When: detect_changes is called with empty content
        Then: Returns (False, [])
        """
        # Arrange
        existing_file = tmp_path / "empty.md"
        existing_file.write_text("")

        # Act
        has_changes, diff_lines = detect_changes(existing_file, "")

        # Assert
        assert has_changes is False
        assert diff_lines == []


class TestDetectChangesModified:
    """Test detection when content differs."""

    def test_modified_content_returns_true_with_diff(self, tmp_path: Path) -> None:
        """
        Given: An existing file with content
        When: detect_changes is called with different content
        Then: Returns (True, diff_lines) where diff_lines contains unified diff
        """
        # Arrange
        existing_file = tmp_path / "modified.md"
        old_content = "# Old Title\n\nOld content.\n"
        new_content = "# New Title\n\nNew content.\n"
        existing_file.write_text(old_content)

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert len(diff_lines) > 0
        # Verify it's a valid unified diff format
        assert any(line.startswith("-") for line in diff_lines)  # Removed lines
        assert any(line.startswith("+") for line in diff_lines)  # Added lines

    def test_added_lines_only(self, tmp_path: Path) -> None:
        """
        Given: An existing file with content
        When: detect_changes is called with additional lines
        Then: Returns diff showing added lines
        """
        # Arrange
        existing_file = tmp_path / "added.md"
        old_content = "# Title\n\nOriginal line.\n"
        new_content = "# Title\n\nOriginal line.\nNew line added.\n"
        existing_file.write_text(old_content)

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert any(line.startswith("+") and "New line added" in line for line in diff_lines)

    def test_removed_lines_only(self, tmp_path: Path) -> None:
        """
        Given: An existing file with multiple lines
        When: detect_changes is called with fewer lines
        Then: Returns diff showing removed lines
        """
        # Arrange
        existing_file = tmp_path / "removed.md"
        old_content = "# Title\n\nLine 1.\nLine 2 to remove.\nLine 3.\n"
        new_content = "# Title\n\nLine 1.\nLine 3.\n"
        existing_file.write_text(old_content)

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert any(line.startswith("-") and "Line 2" in line for line in diff_lines)


class TestDetectChangesEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_file_vs_nonempty_content(self, tmp_path: Path) -> None:
        """
        Given: An existing empty file
        When: detect_changes is called with non-empty content
        Then: Returns (True, diff_lines) showing additions
        """
        # Arrange
        existing_file = tmp_path / "was_empty.md"
        existing_file.write_text("")
        new_content = "# New Content\n"

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert any(line.startswith("+") for line in diff_lines)

    def test_nonempty_file_vs_empty_content(self, tmp_path: Path) -> None:
        """
        Given: An existing file with content
        When: detect_changes is called with empty content
        Then: Returns (True, diff_lines) showing deletions
        """
        # Arrange
        existing_file = tmp_path / "becomes_empty.md"
        existing_file.write_text("# Content to remove\n")
        new_content = ""

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert any(line.startswith("-") for line in diff_lines)

    def test_whitespace_only_changes(self, tmp_path: Path) -> None:
        """
        Given: An existing file with content
        When: detect_changes is called with only whitespace differences
        Then: Returns (True, diff_lines) - whitespace changes are real changes
        """
        # Arrange
        existing_file = tmp_path / "whitespace.md"
        old_content = "# Title\n\nContent with spaces.\n"
        new_content = "# Title\n\nContent with  spaces.\n"  # Extra space
        existing_file.write_text(old_content)

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert len(diff_lines) > 0

    def test_line_ending_differences_unix_vs_windows(self, tmp_path: Path) -> None:
        """
        Given: An existing file with Unix line endings
        When: detect_changes is called with Windows line endings
        Then: Returns (True, diff_lines) - line ending changes are detected
        """
        # Arrange
        existing_file = tmp_path / "line_endings.md"
        old_content = "Line 1\nLine 2\n"  # Unix: \n
        new_content = "Line 1\r\nLine 2\r\n"  # Windows: \r\n
        existing_file.write_text(old_content)

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert len(diff_lines) > 0

    def test_unicode_content_handling(self, tmp_path: Path) -> None:
        """
        Given: An existing file with Unicode content
        When: detect_changes is called with modified Unicode content
        Then: Returns correct diff handling Unicode characters
        """
        # Arrange
        existing_file = tmp_path / "unicode.md"
        old_content = "# Title\n\n你好世界\n"
        new_content = "# Title\n\nこんにちは世界\n"
        existing_file.write_text(old_content, encoding="utf-8")

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        assert len(diff_lines) > 0


class TestDetectChangesDiffFormat:
    """Test that diff output follows unified diff format conventions."""

    def test_diff_contains_file_indicators(self, tmp_path: Path) -> None:
        """
        Given: Modified content
        When: detect_changes generates a diff
        Then: Diff includes file path indicators (---, +++)
        """
        # Arrange
        existing_file = tmp_path / "test.md"
        existing_file.write_text("Old\n")

        # Act
        has_changes, diff_lines = detect_changes(existing_file, "New\n")

        # Assert
        assert has_changes is True
        # Unified diff should have file indicators
        assert any(line.startswith("---") for line in diff_lines)
        assert any(line.startswith("+++") for line in diff_lines)

    def test_diff_contains_hunk_headers(self, tmp_path: Path) -> None:
        """
        Given: Modified content
        When: detect_changes generates a diff
        Then: Diff includes hunk headers (@@)
        """
        # Arrange
        existing_file = tmp_path / "test.md"
        existing_file.write_text("Line 1\nLine 2\n")

        # Act
        has_changes, diff_lines = detect_changes(existing_file, "Line 1\nModified Line 2\n")

        # Assert
        assert has_changes is True
        # Unified diff should have hunk headers
        assert any(line.startswith("@@") for line in diff_lines)

    def test_diff_shows_context_lines(self, tmp_path: Path) -> None:
        """
        Given: Modified content with surrounding unchanged lines
        When: detect_changes generates a diff
        Then: Diff includes context lines (lines without +/- prefix)
        """
        # Arrange
        existing_file = tmp_path / "context.md"
        old_content = "# Title\n\nLine 1\nLine 2 OLD\nLine 3\n"
        new_content = "# Title\n\nLine 1\nLine 2 NEW\nLine 3\n"
        existing_file.write_text(old_content)

        # Act
        has_changes, diff_lines = detect_changes(existing_file, new_content)

        # Assert
        assert has_changes is True
        # Should include context lines (unchanged lines around the change)
        context_lines = [line for line in diff_lines if not line.startswith(("+", "-", "@", "---", "+++"))]
        assert len(context_lines) > 0
