"""Tests for chunked document generator.

RED PHASE: All tests written FIRST and will FAIL.

Tests verify the CORE VALUE of Sprint 5:
"Does section-by-section generation with explicit prompts improve control
and predictability over single-shot?"

This test suite validates:
1. DFS traversal order
2. Section-by-section generation with sources
3. Context flow between sections
4. Integration with SourceValidator and ContextManager
5. Complete document assembly
"""

from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from pydantic_ai.models.test import TestModel

from doc_evergreen.context_manager import ContextManager
from doc_evergreen.core.source_validator import SourceValidationResult
from doc_evergreen.core.template_schema import Document
from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def test_model():
    """Provide TestModel for tests that need LLM without API key."""
    return TestModel(custom_output_text="Generated test content for documentation section.")


@pytest.fixture
def flat_sections() -> list[Section]:
    """Flat section structure (single level)."""
    return [
        Section(heading="Introduction", prompt="Write an intro", sources=["intro.md"]),
        Section(heading="Features", prompt="List features", sources=["features.md"]),
        Section(heading="Installation", prompt="Installation guide", sources=["install.md"]),
    ]


@pytest.fixture
def nested_sections() -> list[Section]:
    """Nested section structure (multi-level).

    Structure:
    Introduction          → 1
    Features              → 2
      ├── Core Features   → 3
      └── Advanced        → 4
    Installation          → 5
      ├── Prerequisites   → 6
      └── Steps           → 7
    """
    return [
        Section(heading="Introduction", prompt="Write intro", sources=["intro.md"]),
        Section(
            heading="Features",
            prompt="Describe features",
            sources=["features.md"],
            sections=[
                Section(heading="Core Features", prompt="Core features", sources=["core.md"]),
                Section(heading="Advanced", prompt="Advanced features", sources=["advanced.md"]),
            ],
        ),
        Section(
            heading="Installation",
            prompt="Installation guide",
            sources=["install.md"],
            sections=[
                Section(heading="Prerequisites", prompt="List prereqs", sources=["prereqs.md"]),
                Section(heading="Steps", prompt="Installation steps", sources=["steps.md"]),
            ],
        ),
    ]


@pytest.fixture
def mock_template(flat_sections: list[Section]) -> Template:
    """Template with flat sections."""
    document = Document(title="Test Doc", output="output.md", sections=flat_sections)
    return Template(document=document)


@pytest.fixture
def mock_nested_template(nested_sections: list[Section]) -> Template:
    """Template with nested sections."""
    document = Document(title="Test Doc", output="output.md", sections=nested_sections)
    return Template(document=document)


@pytest.fixture
def mock_llm():
    """Mock LLM that returns predictable content."""
    mock = AsyncMock()
    # Return section heading as content (for easy verification)
    mock.side_effect = lambda section, sources, context: f"Generated content for {section.heading}"
    return mock


@pytest.fixture
def mock_source_files(tmp_path: Path) -> Path:
    """Create mock source files."""
    files = [
        "intro.md",
        "features.md",
        "install.md",
        "core.md",
        "advanced.md",
        "prereqs.md",
        "steps.md",
    ]

    for filename in files:
        filepath = tmp_path / filename
        filepath.write_text(f"Content of {filename}")

    return tmp_path


# ============================================================================
# DFS TRAVERSAL TESTS
# ============================================================================


def test_dfs_traversal_flat_sections(flat_sections: list[Section]):
    """Test DFS traversal with flat (single-level) sections.

    Given: Flat section structure
    When: Traversing in DFS order
    Then: Sections yielded in sequential order
    """
    # Import the function we're testing (doesn't exist yet!)
    from doc_evergreen.chunked_generator import traverse_dfs

    # Act
    result = list(traverse_dfs(flat_sections))

    # Assert - should yield all sections in order
    assert len(result) == 3
    assert result[0].heading == "Introduction"
    assert result[1].heading == "Features"
    assert result[2].heading == "Installation"


def test_dfs_traversal_nested_sections(nested_sections: list[Section]):
    """Test DFS traversal with nested sections.

    Given: Nested section structure (2 levels)
    When: Traversing in DFS order
    Then: Sections yielded in depth-first order

    Expected order:
    1. Introduction
    2. Features
    3.   Core Features (child of Features)
    4.   Advanced (child of Features)
    5. Installation
    6.   Prerequisites (child of Installation)
    7.   Steps (child of Installation)
    """
    # Import the function we're testing (doesn't exist yet!)
    from doc_evergreen.chunked_generator import traverse_dfs

    # Act
    result = list(traverse_dfs(nested_sections))

    # Assert - correct DFS order
    assert len(result) == 7
    assert result[0].heading == "Introduction"
    assert result[1].heading == "Features"
    assert result[2].heading == "Core Features"  # Child of Features
    assert result[3].heading == "Advanced"  # Child of Features
    assert result[4].heading == "Installation"
    assert result[5].heading == "Prerequisites"  # Child of Installation
    assert result[6].heading == "Steps"  # Child of Installation


def test_dfs_traversal_empty_sections():
    """Test DFS traversal with empty section list.

    Given: Empty section list
    When: Traversing in DFS order
    Then: No sections yielded
    """
    from doc_evergreen.chunked_generator import traverse_dfs

    # Act
    result = list(traverse_dfs([]))

    # Assert - empty result
    assert len(result) == 0


# ============================================================================
# SECTION GENERATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_generate_section_with_sources(mock_source_files: Path, test_model):
    """Test generating a single section with sources.

    Given: Section with sources and prompt
    When: Generating section
    Then: LLM receives section, sources, and context
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    section = Section(heading="Introduction", prompt="Write an intro", sources=["intro.md"])

    template = Template(document=Document(title="Test", output="out.md", sections=[section]))

    generator = ChunkedGenerator(template, base_dir=mock_source_files, model=test_model)

    # Act
    result = await generator.generate_section(section=section, sources=[mock_source_files / "intro.md"], context="")

    # Assert - should return generated content
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_generate_section_with_context(test_model):
    """Test generating section with prior context.

    Given: Section with context from previous sections
    When: Generating section
    Then: Context passed to LLM
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    section = Section(heading="Features", prompt="List features", sources=["features.md"])

    template = Template(document=Document(title="Test", output="out.md", sections=[section]))

    generator = ChunkedGenerator(template, base_dir=Path("."), model=test_model)

    prior_context = """Previous Sections Context:

## Introduction
Summary: This is the introduction section.
"""

    # Act
    result = await generator.generate_section(section=section, sources=[], context=prior_context)

    # Assert
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_generate_section_uses_prompt():
    """Test that generation uses section's explicit prompt.

    Given: Section with specific prompt
    When: Generating section
    Then: Prompt passed to LLM
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    explicit_prompt = "Write a detailed technical introduction"
    section = Section(heading="Introduction", prompt=explicit_prompt, sources=["intro.md"])

    template = Template(document=Document(title="Test", output="out.md", sections=[section]))

    generator = ChunkedGenerator(template, base_dir=Path("."))

    with patch.object(generator, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Generated content"

        # Act
        await generator.generate_section(section=section, sources=[], context="")

        # Assert - LLM called with explicit prompt
        mock_llm.assert_called_once()
        call_args = mock_llm.call_args
        assert explicit_prompt in str(call_args)


# ============================================================================
# COMPLETE DOCUMENT GENERATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_generate_validates_sources_first(mock_template: Template, mock_source_files: Path):
    """Test that generation validates sources before starting.

    Given: Template with sources
    When: Generating document
    Then: Sources validated BEFORE any generation starts
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_template, base_dir=mock_source_files)

    with patch("doc_evergreen.chunked_generator.validate_all_sources") as mock_validate:
        # Mock needs section_sources mapping for all sections
        mock_validate.return_value = SourceValidationResult(
            valid=True,
            errors=[],
            section_sources={"Introduction": [], "Features": [], "Installation": []},
            section_stats={},
        )

        with patch.object(generator, "generate_section", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Generated content"

            # Act
            await generator.generate()

            # Assert - validation called before generation
            mock_validate.assert_called_once()


@pytest.mark.asyncio
async def test_generate_produces_complete_document(mock_template: Template, mock_source_files: Path, test_model):
    """Test that generation produces complete markdown document.

    Given: Template with multiple sections
    When: Generating document
    Then: Returns complete assembled markdown
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_template, base_dir=mock_source_files, model=test_model)

    # Mock generate_section to return content with section heading
    async def mock_generate(section, sources, context):
        return f"# {section.heading}\n\nGenerated content for {section.heading}"

    with patch.object(generator, "generate_section", side_effect=mock_generate):
        # Act
        result = await generator.generate()

        # Assert - complete document with all sections
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Introduction" in result  # Section heading present
        assert "Features" in result
        assert "Installation" in result


@pytest.mark.asyncio
async def test_generate_sections_in_dfs_order(mock_nested_template: Template, mock_source_files: Path):
    """Test that sections generated in DFS order.

    Given: Nested template
    When: Generating document
    Then: Sections generated in depth-first order
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_nested_template, base_dir=mock_source_files)

    # Track generation order
    generation_order = []

    async def track_generation(section, sources, context):
        generation_order.append(section.heading)
        return f"Content for {section.heading}"

    with patch.object(generator, "generate_section", side_effect=track_generation):
        # Act
        await generator.generate()

        # Assert - correct DFS order
        assert generation_order == [
            "Introduction",
            "Features",
            "Core Features",  # Child of Features
            "Advanced",  # Child of Features
            "Installation",
            "Prerequisites",  # Child of Installation
            "Steps",  # Child of Installation
        ]


@pytest.mark.asyncio
async def test_generate_passes_context_between_sections(mock_template: Template, mock_source_files: Path):
    """Test that context flows correctly between sections.

    Given: Multiple sections
    When: Generating document
    Then: Each section receives context from previous sections
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_template, base_dir=mock_source_files)

    contexts_received = []

    async def capture_context(section, sources, context):
        contexts_received.append((section.heading, context))
        return f"Content for {section.heading}"

    with patch.object(generator, "generate_section", side_effect=capture_context):
        # Act
        await generator.generate()

        # Assert - context flows correctly
        # First section gets empty context
        assert contexts_received[0][0] == "Introduction"
        assert contexts_received[0][1] == ""

        # Second section gets context from first
        assert contexts_received[1][0] == "Features"
        assert "Introduction" in contexts_received[1][1]

        # Third section gets context from first two
        assert contexts_received[2][0] == "Installation"
        assert "Introduction" in contexts_received[2][1]
        assert "Features" in contexts_received[2][1]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_integration_with_source_validator(mock_template: Template, mock_source_files: Path, test_model):
    """Test integration with SourceValidator.

    Given: Template with sources
    When: Generating document
    Then: SourceValidator used to validate and resolve sources
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_template, base_dir=mock_source_files, model=test_model)

    # Act
    await generator.generate()

    # Assert - should complete successfully with validated sources (no exception raised)


@pytest.mark.asyncio
async def test_integration_with_context_manager(mock_template: Template, mock_source_files: Path, test_model):
    """Test integration with ContextManager.

    Given: Multiple sections
    When: Generating document
    Then: ContextManager tracks and provides context
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_template, base_dir=mock_source_files, model=test_model)

    # Assert - ContextManager should be initialized
    assert hasattr(generator, "context_manager")
    assert isinstance(generator.context_manager, ContextManager)

    # Act
    await generator.generate()

    # Assert - context manager used during generation
    assert len(generator.context_manager.sections) > 0


@pytest.mark.asyncio
async def test_end_to_end_generation(mock_nested_template: Template, mock_source_files: Path, test_model):
    """Test complete end-to-end generation workflow.

    Given: Complete template with nested sections and sources
    When: Running full generation
    Then: Complete document generated with correct structure

    This is the CRITICAL test validating Sprint 5's core hypothesis:
    "Does section-by-section generation improve control?"
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_nested_template, base_dir=mock_source_files, model=test_model)

    # Mock generate_section to return content with section heading
    async def mock_generate(section, sources, context):
        return f"# {section.heading}\n\nGenerated content for {section.heading}"

    with patch.object(generator, "generate_section", side_effect=mock_generate):
        # Act - full generation
        result = await generator.generate()

        # Assert - complete valid markdown document
        assert isinstance(result, str)
        assert len(result) > 0

        # All section headings present
        assert "# Introduction" in result or "Introduction" in result
        assert "Features" in result
        assert "Core Features" in result
        assert "Advanced" in result
        assert "Installation" in result
        assert "Prerequisites" in result
        assert "Steps" in result

        # Sections in correct order (DFS)
        intro_pos = result.find("Introduction")
        features_pos = result.find("Features")
        install_pos = result.find("Installation")

        assert intro_pos < features_pos < install_pos


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_generate_fails_with_invalid_sources(mock_template: Template):
    """Test that generation fails early with invalid sources.

    Given: Template with non-existent sources
    When: Generating document
    Then: Raises error BEFORE generation starts
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator
    from doc_evergreen.core.source_validator import SourceValidationError

    # Arrange - non-existent base directory
    generator = ChunkedGenerator(mock_template, base_dir=Path("/nonexistent"))

    # Act & Assert - should raise validation error
    with pytest.raises(SourceValidationError):
        await generator.generate()


@pytest.mark.asyncio
async def test_generate_section_with_empty_prompt():
    """Test error when section has no prompt.

    Given: Section without prompt
    When: Generating section
    Then: Raises error or uses default prompt
    """
    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    section = Section(heading="Introduction", prompt=None, sources=["intro.md"])

    template = Template(document=Document(title="Test", output="out.md", sections=[section]))

    generator = ChunkedGenerator(template, base_dir=Path("."))

    # Act & Assert - should handle missing prompt
    # (Implementation can choose to raise error or use default)
    try:
        result = await generator.generate_section(section=section, sources=[], context="")
        assert isinstance(result, str)
    except ValueError as e:
        assert "prompt" in str(e).lower()


# ============================================================================
# PROGRESS REPORTING TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_generate_reports_progress(
    mock_template: Template, mock_source_files: Path, test_model, caplog: pytest.LogCaptureFixture
):
    """Test that generation reports progress.

    Given: Multiple sections
    When: Generating document
    Then: Progress messages show which section and sources
    """
    import logging

    from doc_evergreen.chunked_generator import ChunkedGenerator

    # Arrange
    generator = ChunkedGenerator(mock_template, base_dir=mock_source_files, model=test_model)

    # Capture INFO level logs
    caplog.set_level(logging.INFO)

    # Act
    await generator.generate()

    # Assert - progress output captured in logs
    output = caplog.text
    # Should mention section names
    assert "Introduction" in output or "Features" in output


# ============================================================================
# WHY THESE TESTS WILL FAIL
# ============================================================================

"""
ALL TESTS ABOVE WILL FAIL because:

1. ChunkedGenerator class doesn't exist yet
2. traverse_dfs() function doesn't exist
3. generate() method not implemented
4. generate_section() method not implemented
5. Integration with SourceValidator not implemented
6. Integration with ContextManager not implemented
7. Progress reporting not implemented

This is EXPECTED - RED phase of TDD.

Next step: Write minimal implementation to make tests pass (GREEN phase).
"""
