"""
Tests for LLM generation functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import anthropic
import pytest

from doc_evergreen.core.generator import call_llm
from doc_evergreen.core.generator import create_customized_template
from doc_evergreen.core.generator import customize_template
from doc_evergreen.core.generator import format_sources
from doc_evergreen.core.generator import generate_document
from doc_evergreen.core.generator import load_api_key
from doc_evergreen.core.generator import score_file_relevancy
from doc_evergreen.core.generator import summarize_file


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


@pytest.mark.skip(
    reason="Old customize_template function deprecated - now using create_customized_template with relevancy"
)
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


@pytest.mark.skip(
    reason="Old customize_template function deprecated - now using create_customized_template with relevancy"
)
@patch("doc_evergreen.core.generator.call_llm")
def test_customize_template_with_existing_doc(mock_call_llm):
    """Test template customization with existing document."""
    mock_call_llm.return_value = "Customized template"

    builtin = "# Template"
    about = "README"
    existing = "# My Project\nExisting content here..."

    result = customize_template(builtin, about, existing_doc=existing)

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
@patch("doc_evergreen.core.generator.load_prompt")
def test_generate_document(mock_load_prompt, mock_call_llm):
    """Test document generation."""
    # Mock prompt loading
    mock_load_prompt.return_value = (
        "Generate docs:\nTemplate: {customized_template}\n"
        "About: {about}\nSelected: {selected_files_with_reasons}\nContent: {source_files_content}"
    )

    # Mock LLM response
    mock_call_llm.return_value = "# Generated Documentation\nContent here"

    customized_template = "# Template\nInstructions\n{{FILE:test.py}}"
    about = "Test documentation"
    selected_files = {"test.py": "Main implementation"}
    source_files_content = {"test.py": "def main():\n    pass"}

    result = generate_document(customized_template, about, selected_files, source_files_content)

    assert result == "# Generated Documentation\nContent here"

    # Verify prompt was loaded
    mock_load_prompt.assert_called_once_with("generate_document")

    # Check prompt includes all parts
    call_args = mock_call_llm.call_args[0][0]
    assert "Template" in call_args
    assert "Test documentation" in call_args


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_generate_document_with_large_sources(mock_load_prompt, mock_call_llm):
    """Test document generation with many source files."""
    # Mock prompt loading
    mock_load_prompt.return_value = (
        "Generate docs:\nTemplate: {customized_template}\n"
        "About: {about}\nSelected: {selected_files_with_reasons}\nContent: {source_files_content}"
    )

    # Mock LLM response
    mock_call_llm.return_value = "Generated doc"

    customized_template = "Template"
    about = "Large project"
    selected_files = {f"file{i}.py": f"File {i}" for i in range(10)}
    source_files_content = {f"file{i}.py": f"content {i}" for i in range(10)}

    result = generate_document(customized_template, about, selected_files, source_files_content)

    assert result == "Generated doc"

    # Verify prompt was loaded
    mock_load_prompt.assert_called_once_with("generate_document")


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_summarize_file_success(mock_load_prompt, mock_call_llm):
    """Test file summarization with LLM."""
    # Mock prompt loading - return tuple when return_version=True
    mock_load_prompt.return_value = ("Summarize: {file_path}\nContent: {file_content}", "2025-01-14T00:00:00Z")

    # Mock LLM response
    mock_call_llm.return_value = "This file implements authentication logic."

    # Call function
    file_path = "src/auth.py"
    file_content = "def login():\n    pass"

    summary, prompt_name, prompt_version = summarize_file(file_path, file_content)

    # Verify result
    assert summary == "This file implements authentication logic."
    assert prompt_name == "summarize_file"
    assert prompt_version == "2025-01-14T00:00:00Z"

    # Verify prompt was loaded with return_version=True
    mock_load_prompt.assert_called_once_with("summarize_file", return_version=True)

    # Verify LLM was called with formatted prompt
    mock_call_llm.assert_called_once()
    call_args = mock_call_llm.call_args[0][0]
    assert "src/auth.py" in call_args
    assert "def login():" in call_args


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_summarize_file_with_long_content(mock_load_prompt, mock_call_llm):
    """Test summarization handles long file content."""
    mock_load_prompt.return_value = ("Summarize: {file_path}\nContent: {file_content}", "2025-01-14T00:00:00Z")
    mock_call_llm.return_value = "Complex module with multiple classes."

    file_path = "src/complex.py"
    file_content = "class A:\n    pass\n" * 100  # Long content

    summary, prompt_name, prompt_version = summarize_file(file_path, file_content)

    assert summary == "Complex module with multiple classes."
    assert prompt_name == "summarize_file"
    assert prompt_version == "2025-01-14T00:00:00Z"
    mock_call_llm.assert_called_once()


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_create_customized_template_success(mock_load_prompt, mock_call_llm):
    """Test template customization with file summaries."""
    # Mock prompt loading with correct placeholders - return tuple when return_version=True
    mock_load_prompt.return_value = (
        "Template: {template_guide}\nAbout: {about}\nFiles: {formatted_source_data}",
        "2025-01-14T00:00:00Z",
    )

    # Mock LLM response with JSON
    mock_call_llm.return_value = '{"customized_template": "# Customized Template\\n\\nInstructions for documentation...", "selected_files": {"src/auth.py": "Needed for auth section", "src/api.py": "Needed for API section"}}'

    # Call function
    template_guide = "# Generic Template Guide\nInstructions here"
    template_guide_version = "2025-01-13T23:00:00Z"
    about = "API documentation"
    source_file_data = [
        {
            "file_path": "src/auth.py",
            "summary": {"text": "Authentication module", "timestamp": "2025-01-13T20:00:00Z"},
            "relevancy": {
                "explanation": "Needed for auth",
                "score": 9,
                "prompt": {"name": "score_relevancy", "version": "2025-01-13T23:00:00Z"},
            },
        },
        {
            "file_path": "src/api.py",
            "summary": {"text": "API endpoints", "timestamp": "2025-01-13T20:00:00Z"},
            "relevancy": {
                "explanation": "Core API logic",
                "score": 10,
                "prompt": {"name": "score_relevancy", "version": "2025-01-13T23:00:00Z"},
            },
        },
    ]

    customized_template, selected_files, prompt_name, prompt_version = create_customized_template(
        template_guide, template_guide_version, about, source_file_data
    )

    # Verify result
    assert customized_template == "# Customized Template\n\nInstructions for documentation..."
    assert selected_files == {"src/auth.py": "Needed for auth section", "src/api.py": "Needed for API section"}
    assert prompt_name == "create_customized_template"
    assert prompt_version == "2025-01-14T00:00:00Z"

    # Verify prompt was loaded with return_version=True
    mock_load_prompt.assert_called_once_with("create_customized_template", return_version=True)

    # Verify LLM was called with formatted prompt
    mock_call_llm.assert_called_once()
    call_args = mock_call_llm.call_args[0][0]
    assert "Generic Template Guide" in call_args
    assert "API documentation" in call_args
    assert "Authentication module" in call_args
    assert "API endpoints" in call_args


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_create_customized_template_empty_summaries(mock_load_prompt, mock_call_llm):
    """Test template customization with no file summaries."""
    # Mock prompt loading with correct placeholders - return tuple when return_version=True
    mock_load_prompt.return_value = (
        "Template: {template_guide}\nAbout: {about}\nFiles: {formatted_source_data}",
        "2025-01-14T00:00:00Z",
    )
    mock_call_llm.return_value = '{"customized_template": "# Simple Template", "selected_files": {}}'

    template_guide = "# Guide"
    template_guide_version = "2025-01-13T23:00:00Z"
    about = "README"
    source_file_data = []

    customized_template, selected_files, prompt_name, prompt_version = create_customized_template(
        template_guide, template_guide_version, about, source_file_data
    )

    assert customized_template == "# Simple Template"
    assert selected_files == {}
    assert prompt_name == "create_customized_template"
    assert prompt_version == "2025-01-14T00:00:00Z"
    mock_call_llm.assert_called_once()


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_create_customized_template_many_files(mock_load_prompt, mock_call_llm):
    """Test template customization with many file summaries."""
    # Mock prompt loading with correct placeholders - return tuple when return_version=True
    mock_load_prompt.return_value = (
        "Template: {template_guide}\nAbout: {about}\nFiles: {formatted_source_data}",
        "2025-01-14T00:00:00Z",
    )
    # Mock LLM response with JSON containing selected files
    import json

    selected_files_dict = {f"file{i}.py": f"Reason {i}" for i in range(10)}
    mock_response = {"customized_template": "# Comprehensive Template", "selected_files": selected_files_dict}
    mock_call_llm.return_value = json.dumps(mock_response)

    template_guide = "# Guide"
    template_guide_version = "2025-01-13T23:00:00Z"
    about = "Full project docs"
    source_file_data = [
        {
            "file_path": f"file{i}.py",
            "summary": {"text": f"Summary {i}", "timestamp": "2025-01-13T20:00:00Z"},
            "relevancy": {
                "explanation": f"Relevant {i}",
                "score": 8,
                "prompt": {"name": "score_relevancy", "version": "2025-01-13T23:00:00Z"},
            },
        }
        for i in range(50)
    ]

    customized_template, selected_files, prompt_name, prompt_version = create_customized_template(
        template_guide, template_guide_version, about, source_file_data
    )

    assert customized_template == "# Comprehensive Template"
    assert len(selected_files) == 10
    assert prompt_name == "create_customized_template"
    assert prompt_version == "2025-01-14T00:00:00Z"
    mock_call_llm.assert_called_once()

    # Verify all summaries were included in the prompt
    call_args = mock_call_llm.call_args[0][0]
    assert "Summary 0" in call_args
    assert "Summary 49" in call_args


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_score_file_relevancy_success(mock_load_prompt, mock_call_llm):
    """Test scoring file relevancy with LLM."""
    # Mock prompt loading
    mock_load_prompt.return_value = (
        "Score relevancy:\nFile: {file_path}\nSummary: {file_summary}\nDoc: {doc_description}"
    )

    # Mock LLM response with valid JSON
    mock_call_llm.return_value = '{"relevancy_explanation": "This file is highly relevant", "relevancy_score": 9}'

    # Call function
    file_path = "src/auth.py"
    file_summary = "Authentication module"
    doc_description = "API documentation"

    explanation, score = score_file_relevancy(file_path, file_summary, doc_description)

    # Verify result
    assert explanation == "This file is highly relevant"
    assert score == 9

    # Verify prompt was loaded
    mock_load_prompt.assert_called_once_with("score_relevancy")

    # Verify LLM was called with formatted prompt
    mock_call_llm.assert_called_once()
    call_args = mock_call_llm.call_args[0][0]
    assert "src/auth.py" in call_args
    assert "Authentication module" in call_args
    assert "API documentation" in call_args


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_score_file_relevancy_invalid_json(mock_load_prompt, mock_call_llm):
    """Test handling of invalid JSON response."""
    mock_load_prompt.return_value = "Score relevancy: {file_path}"

    # Mock LLM response with invalid JSON
    mock_call_llm.return_value = "This is not JSON"

    explanation, score = score_file_relevancy("test.py", "Summary", "Doc description")

    # Should return default values
    assert explanation == "Unable to parse relevancy response"
    assert score == 5


@patch("doc_evergreen.core.generator.call_llm")
@patch("doc_evergreen.core.generator.load_prompt")
def test_score_file_relevancy_missing_fields(mock_load_prompt, mock_call_llm):
    """Test handling of JSON with missing fields."""
    mock_load_prompt.return_value = "Score relevancy"

    # Mock LLM response with partial JSON
    mock_call_llm.return_value = '{"relevancy_score": 7}'

    explanation, score = score_file_relevancy("test.py", "Summary", "Doc description")

    # Should handle missing explanation field
    assert explanation == ""
    assert score == 7
