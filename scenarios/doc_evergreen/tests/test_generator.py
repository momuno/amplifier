"""
Tests for LLM generation functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import anthropic
import pytest

from doc_evergreen.core.generator import (
    call_llm,
    customize_template,
    format_sources,
    generate_document,
    load_api_key,
)


def test_load_api_key_success():
    """Test loading API key from .claude/api_key.txt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create .claude directory with API key
        claude_dir = Path(tmpdir) / ".claude"
        claude_dir.mkdir()
        api_key_file = claude_dir / "api_key.txt"
        api_key_file.write_text("test-api-key-12345")

        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(tmpdir)
            api_key = load_api_key()
            assert api_key == "test-api-key-12345"
        finally:
            os.chdir(original_cwd)


def test_load_api_key_not_found():
    """Test error when API key file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(tmpdir)
            with pytest.raises(FileNotFoundError, match="API key not found"):
                load_api_key()
        finally:
            os.chdir(original_cwd)


def test_load_api_key_empty():
    """Test error when API key file is empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create .claude directory with empty API key
        claude_dir = Path(tmpdir) / ".claude"
        claude_dir.mkdir()
        api_key_file = claude_dir / "api_key.txt"
        api_key_file.write_text("")

        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(tmpdir)
            with pytest.raises(ValueError, match="API key file is empty"):
                load_api_key()
        finally:
            os.chdir(original_cwd)


def test_load_api_key_searches_parent_dirs():
    """Test that load_api_key searches up directory tree."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create nested structure: root/.claude/api_key.txt
        claude_dir = root / ".claude"
        claude_dir.mkdir()
        api_key_file = claude_dir / "api_key.txt"
        api_key_file.write_text("parent-key")

        # Create child directory
        child = root / "child" / "nested"
        child.mkdir(parents=True)

        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(child)
            api_key = load_api_key()
            assert api_key == "parent-key"
        finally:
            os.chdir(original_cwd)


@patch("doc_evergreen.core.generator.anthropic.Anthropic")
@patch("doc_evergreen.core.generator.load_api_key")
def test_call_llm_success(mock_load_key, mock_anthropic):
    """Test successful LLM API call."""
    # Mock API key
    mock_load_key.return_value = "test-key"

    # Mock Anthropic client
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    # Mock successful response
    mock_message = Mock()
    mock_content = Mock()
    mock_content.text = "Generated response"
    mock_message.content = [mock_content]
    mock_client.messages.create.return_value = mock_message

    # Call function
    result = call_llm("Test prompt")

    # Verify
    assert result == "Generated response"
    mock_load_key.assert_called_once()
    mock_anthropic.assert_called_once_with(api_key="test-key")
    mock_client.messages.create.assert_called_once()


@patch("doc_evergreen.core.generator.anthropic.Anthropic")
@patch("doc_evergreen.core.generator.load_api_key")
@patch("doc_evergreen.core.generator.time.sleep")
def test_call_llm_retry_on_rate_limit(mock_sleep, mock_load_key, mock_anthropic):
    """Test retry logic on rate limit error."""
    mock_load_key.return_value = "test-key"
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    # First call fails with rate limit, second succeeds
    mock_message = Mock()
    mock_content = Mock()
    mock_content.text = "Generated response"
    mock_message.content = [mock_content]

    # Create proper RateLimitError with required args
    mock_response = Mock()
    mock_response.status_code = 429
    rate_limit_error = anthropic.RateLimitError("Rate limited", response=mock_response, body=None)

    mock_client.messages.create.side_effect = [
        rate_limit_error,
        mock_message,
    ]

    # Call function
    result = call_llm("Test prompt", max_retries=3)

    # Verify retry happened
    assert result == "Generated response"
    assert mock_client.messages.create.call_count == 2
    mock_sleep.assert_called_once_with(1.0)  # First retry delay


@patch("doc_evergreen.core.generator.anthropic.Anthropic")
@patch("doc_evergreen.core.generator.load_api_key")
@patch("doc_evergreen.core.generator.time.sleep")
def test_call_llm_retry_exhausted(mock_sleep, mock_load_key, mock_anthropic):
    """Test that retries are exhausted and error is raised."""
    mock_load_key.return_value = "test-key"
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    # Create proper RateLimitError
    mock_response = Mock()
    mock_response.status_code = 429
    rate_limit_error = anthropic.RateLimitError("Rate limited", response=mock_response, body=None)

    # All calls fail
    mock_client.messages.create.side_effect = rate_limit_error

    # Call function
    with pytest.raises(RuntimeError, match="Rate limit exceeded"):
        call_llm("Test prompt", max_retries=3)

    # Verify all retries attempted
    assert mock_client.messages.create.call_count == 3


@patch("doc_evergreen.core.generator.anthropic.Anthropic")
@patch("doc_evergreen.core.generator.load_api_key")
def test_call_llm_api_error(mock_load_key, mock_anthropic):
    """Test handling of API errors."""
    mock_load_key.return_value = "test-key"
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    # Create proper APIError
    api_error = anthropic.APIError("API error", request=Mock(), body=None)

    # Simulate API error
    mock_client.messages.create.side_effect = api_error

    # Call function
    with pytest.raises(RuntimeError, match="API error"):
        call_llm("Test prompt", max_retries=1)


@patch("doc_evergreen.core.generator.anthropic.Anthropic")
@patch("doc_evergreen.core.generator.load_api_key")
def test_call_llm_empty_response(mock_load_key, mock_anthropic):
    """Test handling of empty response."""
    mock_load_key.return_value = "test-key"
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    # Mock empty response
    mock_message = Mock()
    mock_message.content = []
    mock_client.messages.create.return_value = mock_message

    # Call function - ValueError gets wrapped in RuntimeError
    with pytest.raises(RuntimeError, match="Unexpected error"):
        call_llm("Test prompt")


@patch("doc_evergreen.core.generator.call_llm")
def test_customize_template_basic(mock_call_llm):
    """Test basic template customization."""
    mock_call_llm.return_value = "Customized template content"

    builtin = "# Original Template\nInstructions here"
    about = "API documentation for my project"

    result = customize_template(builtin, about)

    assert result == "Customized template content"
    mock_call_llm.assert_called_once()

    # Check that prompt includes both template and about
    call_args = mock_call_llm.call_args[0][0]
    assert "Original Template" in call_args
    assert "API documentation" in call_args


@patch("doc_evergreen.core.generator.call_llm")
def test_customize_template_with_existing_doc(mock_call_llm):
    """Test template customization with existing document."""
    mock_call_llm.return_value = "Customized template"

    builtin = "# Template"
    about = "README"
    existing = "# My Project\nExisting content here..."

    result = customize_template(builtin, about, existing)

    assert result == "Customized template"

    # Check that prompt includes existing doc
    call_args = mock_call_llm.call_args[0][0]
    assert "Existing content" in call_args


def test_format_sources_basic():
    """Test basic source file formatting."""
    sources = {
        "file1.py": "def hello():\n    pass",
        "file2.py": "def world():\n    pass",
    }

    result = format_sources(sources)

    assert "--- File: file1.py ---" in result
    assert "def hello():" in result
    assert "--- File: file2.py ---" in result
    assert "def world():" in result


def test_format_sources_truncation():
    """Test that sources are truncated when too large."""
    # Create sources that exceed limit
    large_content = "x" * 30000
    sources = {
        "file1.py": large_content,
        "file2.py": large_content,
    }

    result = format_sources(sources, max_total_length=50000)

    # Should be truncated
    assert len(result) <= 50000
    assert "[... truncated ...]" in result


def test_format_sources_empty():
    """Test formatting with no sources."""
    sources = {}
    result = format_sources(sources)
    assert result == ""


@patch("doc_evergreen.core.generator.call_llm")
def test_generate_document(mock_call_llm):
    """Test document generation."""
    mock_call_llm.return_value = "# Generated Documentation\nContent here"

    template = "# Template\nInstructions\n{{SOURCE_FILES}}"
    sources = {"file.py": "def test(): pass"}
    about = "Test documentation"

    result = generate_document(template, sources, about)

    assert result == "# Generated Documentation\nContent here"

    # Check prompt includes all parts
    call_args = mock_call_llm.call_args[0][0]
    assert "Template" in call_args
    assert "def test():" in call_args
    assert "Test documentation" in call_args
    assert "{{SOURCE_FILES}}" in call_args or "SOURCE_FILES" in call_args


@patch("doc_evergreen.core.generator.call_llm")
def test_generate_document_with_large_sources(mock_call_llm):
    """Test document generation with many source files."""
    mock_call_llm.return_value = "Generated doc"

    template = "Template"
    sources = {f"file{i}.py": f"content {i}" for i in range(100)}
    about = "Large project"

    result = generate_document(template, sources, about)

    assert result == "Generated doc"

    # Verify format_sources was used (implicit in the call)
    call_args = mock_call_llm.call_args[0][0]
    assert "file0.py" in call_args  # At least first file included
