"""Tests for progress feedback system (Sprint 9 Day 1).

Following TDD: These tests are written FIRST and should FAIL until we implement the feature.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from doc_evergreen.chunked_generator import ChunkedGenerator
from doc_evergreen.core.template_schema import Document
from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template


@pytest.fixture
def simple_template(tmp_path: Path) -> tuple[Template, Path]:
    """Create a simple template with source files for testing."""
    # Create source files
    source1 = tmp_path / "source1.md"
    source1.write_text("# Source 1\n\nContent from source 1.")

    source2 = tmp_path / "source2.md"
    source2.write_text("# Source 2\n\nContent from source 2.")

    # Create template
    template = Template(
        document=Document(
            title="Test Document",
            output=str(tmp_path / "output.md"),
            sections=[
                Section(
                    heading="Overview",
                    prompt="Write an overview section",
                    sources=["source1.md"],
                ),
                Section(
                    heading="Details",
                    prompt="Write a details section",
                    sources=["source2.md"],
                ),
            ],
        )
    )

    return template, tmp_path


class TestProgressCallback:
    """Test progress callback functionality."""

    @pytest.mark.asyncio
    async def test_progress_callback_called_for_each_section(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test that progress callback is called for each section.

        Given: A template with 2 sections and a progress callback
        When: Generator runs
        Then: Callback is called at least once per section
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        # Mock callback to track calls
        progress_callback = MagicMock()

        # This should fail - progress_callback parameter doesn't exist yet
        await generator.generate(progress_callback=progress_callback)

        # Should be called at least 2 times (one per section minimum)
        assert progress_callback.call_count >= 2

    @pytest.mark.asyncio
    async def test_progress_callback_includes_section_info(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test that progress messages include section information.

        Given: A progress callback
        When: Generator runs
        Then: Messages include section heading and index
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        messages: list[str] = []

        def capture_callback(msg: str) -> None:
            messages.append(msg)

        await generator.generate(progress_callback=capture_callback)

        # Should mention both section headings
        all_messages = "".join(messages)
        assert "Overview" in all_messages
        assert "Details" in all_messages

        # Should include progress like [1/2], [2/2]
        assert "[1/2]" in all_messages
        assert "[2/2]" in all_messages

    @pytest.mark.asyncio
    async def test_progress_callback_includes_source_count(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test that progress messages show source file count.

        Given: Sections with different source counts
        When: Generator runs
        Then: Messages include source file counts
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        messages: list[str] = []

        def capture_callback(msg: str) -> None:
            messages.append(msg)

        await generator.generate(progress_callback=capture_callback)

        # Should mention source counts (1 file, 1 file)
        all_messages = "".join(messages)
        assert "1 file" in all_messages or "source1.md" in all_messages

    @pytest.mark.asyncio
    async def test_progress_callback_includes_timing(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test that progress includes timing information.

        Given: A progress callback
        When: Generator completes a section
        Then: Timing information is included (e.g., "3.2s")
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        messages: list[str] = []

        def capture_callback(msg: str) -> None:
            messages.append(msg)

        await generator.generate(progress_callback=capture_callback)

        # Should include timing like "3.2s" or "(5.1s)"
        all_messages = "".join(messages)
        assert "s)" in all_messages or " s" in all_messages  # Look for seconds

    @pytest.mark.asyncio
    async def test_progress_callback_shows_completion_marker(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test that progress shows completion markers.

        Given: A progress callback
        When: Section generation completes
        Then: Completion marker (✓) is shown
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        messages: list[str] = []

        def capture_callback(msg: str) -> None:
            messages.append(msg)

        await generator.generate(progress_callback=capture_callback)

        # Should include completion markers
        all_messages = "".join(messages)
        assert "✓" in all_messages or "Complete" in all_messages

    @pytest.mark.asyncio
    async def test_progress_callback_none_works(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test that passing None for callback works (no progress output).

        Given: progress_callback=None
        When: Generator runs
        Then: No errors, generation succeeds
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        # Should not raise any errors
        result = await generator.generate(progress_callback=None)

        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_progress_callback_not_required(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test that progress_callback parameter is optional.

        Given: No progress_callback specified
        When: Generator runs
        Then: Works without errors (backward compatible)
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        # Should work without progress_callback parameter (backward compatible)
        result = await generator.generate()

        assert result is not None
        assert len(result) > 0


class TestProgressCallbackFormat:
    """Test the specific format of progress messages."""

    @pytest.mark.asyncio
    async def test_progress_format_section_start(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test section start message format.

        Expected format:
        [1/2] Generating: Overview
              Sources: source1.md (1 file)
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        messages: list[str] = []

        def capture_callback(msg: str) -> None:
            messages.append(msg)

        await generator.generate(progress_callback=capture_callback)

        # Find message for first section
        overview_msgs = [m for m in messages if "Overview" in m]
        assert len(overview_msgs) > 0

        # Should have format with section name
        assert any("[1/2]" in m for m in overview_msgs)

    @pytest.mark.asyncio
    async def test_progress_format_section_complete(self, simple_template: tuple[Template, Path]) -> None:
        """
        🔴 RED: Test section completion message format.

        Expected format:
              ✓ Complete (3.2s)
        """
        template, base_dir = simple_template
        generator = ChunkedGenerator(template, base_dir, model="test")

        messages: list[str] = []

        def capture_callback(msg: str) -> None:
            messages.append(msg)

        await generator.generate(progress_callback=capture_callback)

        # Should have completion messages with timing
        complete_msgs = [m for m in messages if "✓" in m or "Complete" in m]
        assert len(complete_msgs) >= 2  # One per section
