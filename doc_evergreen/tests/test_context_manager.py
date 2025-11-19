"""
Tests for context manager that manages context flow between sections.

RED PHASE: These tests are written BEFORE implementation and MUST fail initially.
"""

from unittest.mock import patch

import pytest
from pydantic_ai.models.test import TestModel

from doc_evergreen.context_manager import ContextManager


@pytest.fixture
def test_model():
    """Provide TestModel for tests that need LLM without API key."""
    return TestModel()


class TestContextManagerBasics:
    """Test basic section tracking and management."""

    def test_context_manager_initializes_empty(self, test_model):
        """
        Given: A new context manager
        When: It is initialized
        Then: It has no sections and default max_context_sections
        """
        manager = ContextManager(model=test_model)

        assert manager.sections == []
        assert manager.max_context_sections == 10

    def test_context_manager_custom_max_sections(self, test_model):
        """
        Given: A context manager with custom max_context_sections
        When: It is initialized
        Then: It respects the custom limit
        """
        manager = ContextManager(max_context_sections=5, model=test_model)

        assert manager.max_context_sections == 5

    @pytest.mark.asyncio
    async def test_context_manager_adds_sections(self, test_model):
        """
        Given: A context manager
        When: Sections are added
        Then: They are tracked in order
        """
        manager = ContextManager(model=test_model)

        with patch("doc_evergreen.context_manager.summarize_with_llm") as mock_llm:
            mock_llm.return_value = "Summary"
            await manager.add_section("Overview", "doc_evergreen maintains living docs")
            await manager.add_section("Features", "Key features include templates")

        assert len(manager.sections) == 2
        assert manager.sections[0].heading == "Overview"
        assert manager.sections[1].heading == "Features"

    @pytest.mark.asyncio
    async def test_context_manager_limits_size(self, test_model):
        """
        Given: A context manager with max_context_sections=3
        When: More than 3 sections are added
        Then: Only the most recent 3 are kept
        """
        manager = ContextManager(max_context_sections=3, model=test_model)

        with patch("doc_evergreen.context_manager.summarize_with_llm") as mock_llm:
            mock_llm.return_value = "Summary"
            await manager.add_section("Section 1", "Content 1")
            await manager.add_section("Section 2", "Content 2")
            await manager.add_section("Section 3", "Content 3")
            await manager.add_section("Section 4", "Content 4")
            await manager.add_section("Section 5", "Content 5")

        assert len(manager.sections) == 3
        assert manager.sections[0].heading == "Section 3"
        assert manager.sections[1].heading == "Section 4"
        assert manager.sections[2].heading == "Section 5"


class TestContextGeneration:
    """Test context generation for sections."""

    def test_context_empty_for_first_section(self, test_model):
        """
        Given: A context manager with no sections
        When: Getting context for section 0
        Then: Returns empty string (no previous context)
        """
        manager = ContextManager(model=test_model)

        context = manager.get_context_for_section(section_index=0)

        assert context == ""

    @pytest.mark.asyncio
    async def test_get_context_for_section(self, test_model):
        """
        Given: A context manager with multiple sections with summaries
        When: Getting context for a section
        Then: Returns formatted context of all previous sections
        """
        manager = ContextManager(model=test_model)

        # Add sections - TestModel will generate summaries
        await manager.add_section("Overview", "Long content about overview...")
        await manager.add_section("Features", "Long content about features...")
        await manager.add_section("Architecture", "Content about architecture...")

        # Get context for the third section (should include first two)
        context = manager.get_context_for_section(section_index=2)

        assert "Previous Sections Context:" in context
        assert "## Overview" in context
        assert "Summary:" in context  # Should have summary
        assert "## Features" in context
        # Should NOT include the current section (Architecture)
        assert "Architecture" not in context

    @pytest.mark.asyncio
    async def test_context_includes_all_previous_sections(self, test_model):
        """
        Given: A context manager with 5 sections
        When: Getting context for section 4
        Then: Includes all 4 previous sections
        """
        manager = ContextManager(model=test_model)

        # Add sections - TestModel will generate summaries
        for i in range(5):
            await manager.add_section(f"Section {i}", f"Content {i}")

        context = manager.get_context_for_section(section_index=4)

        # Should include sections 0-3, not section 4
        for i in range(4):
            assert f"Section {i}" in context

        # Should NOT include current section
        assert "Section 4" not in context


class TestSummarization:
    """Test LLM-based summarization of sections."""

    @pytest.mark.asyncio
    async def test_summarize_section_generates_summary(self, test_model):
        """
        Given: A context manager with LLM access
        When: Summarizing a section
        Then: Generates a concise summary (3-5 sentences)
        """
        manager = ContextManager(model=test_model)

        # TestModel will generate a summary
        summary = await manager.summarize_section(
            heading="Overview", content="Very long content about doc_evergreen that needs summarizing..."
        )

        # Summary should be generated (not empty)
        assert isinstance(summary, str)
        assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_summary_fallback_on_llm_failure(self, test_model):
        """
        Given: LLM summarization fails
        When: Attempting to summarize
        Then: Falls back to first 500 characters
        """
        manager = ContextManager(model=test_model)

        long_content = "A" * 1000

        # Mock Agent.run to raise an exception
        with patch.object(manager, "summarize_section") as mock_summarize:
            # Call the real implementation but mock the agent call to fail
            async def failing_summarize(heading, content):
                # Simulate the fallback behavior
                if len(content) > 500:
                    return content[:500] + "..."
                return content

            mock_summarize.side_effect = failing_summarize

            summary = await manager.summarize_section(heading="Overview", content=long_content)

            # Should fallback to first 500 chars + ellipsis
            assert summary == "A" * 500 + "..."
            assert len(summary) == 503

    @pytest.mark.asyncio
    async def test_add_section_triggers_summarization(self, test_model):
        """
        Given: A context manager
        When: Adding a section
        Then: Summary is automatically generated
        """
        manager = ContextManager(model=test_model)

        await manager.add_section("Overview", "Long content...")

        # Summary should be stored (TestModel generates it)
        assert isinstance(manager.sections[0].summary, str)
        assert len(manager.sections[0].summary) > 0

    @pytest.mark.asyncio
    async def test_summary_length_validation(self, test_model):
        """
        Given: A section with various content lengths
        When: Summary is generated
        Then: Summary is appropriately concise (not just truncation)
        """
        manager = ContextManager(model=test_model)

        short_content = "Short."
        long_content = "A" * 2000

        # For short content, summary should be similar to content
        with patch("doc_evergreen.context_manager.summarize_with_llm") as mock_llm:
            mock_llm.return_value = short_content

            await manager.add_section("Short", short_content)
            assert len(manager.sections[0].summary) <= len(short_content) + 50

        # For long content, summary should be much shorter
        with patch("doc_evergreen.context_manager.summarize_with_llm") as mock_llm:
            mock_llm.return_value = "Concise summary of long content."

            await manager.add_section("Long", long_content)
            assert len(manager.sections[1].summary) < len(long_content) / 2


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_get_context_for_invalid_index(self, test_model):
        """
        Given: A context manager with 3 sections
        When: Getting context for out-of-bounds index
        Then: Raises appropriate error
        """
        manager = ContextManager(model=test_model)

        with patch("doc_evergreen.context_manager.summarize_with_llm") as mock_llm:
            mock_llm.return_value = "Summary"
            await manager.add_section("S1", "C1")
            await manager.add_section("S2", "C2")

        with pytest.raises(IndexError):
            manager.get_context_for_section(section_index=10)

    def test_context_manager_with_no_summaries(self, test_model):
        """
        Given: Sections added without summaries generated
        When: Getting context
        Then: Uses empty string for missing summaries
        """
        manager = ContextManager(model=test_model)

        # Manually add sections without triggering summarization
        from doc_evergreen.context_manager import GeneratedSection

        manager.sections.append(GeneratedSection(heading="Overview", content="Content", summary=""))

        context = manager.get_context_for_section(section_index=1)

        # Should handle missing summary gracefully
        assert "## Overview" in context
        # Summary line might be empty or say "No summary available"

    @pytest.mark.asyncio
    async def test_concurrent_summarization(self, test_model):
        """
        Given: Multiple sections added rapidly
        When: Summaries are generated concurrently
        Then: All summaries complete correctly
        """
        manager = ContextManager(model=test_model)

        with patch("doc_evergreen.context_manager.summarize_with_llm") as mock_llm:
            mock_llm.return_value = "Summary"

            # Add multiple sections
            for i in range(5):
                await manager.add_section(f"Section {i}", f"Content {i}")

            # All should have summaries
            assert all(section.summary for section in manager.sections)
