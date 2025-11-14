"""
LLM generation for doc-evergreen.

Uses direct Anthropic API calls to generate documentation.
Does NOT use Claude Code SDK to avoid conflicts with git hooks.
"""

import time

import anthropic

from doc_evergreen.prompts import load_prompt


def load_api_key() -> str:
    """
    Load Anthropic API key from .claude/api_key.txt.

    Returns:
        API key as string

    Raises:
        FileNotFoundError: If API key file doesn't exist
        ValueError: If API key is empty
    """
    from pathlib import Path

    # Try .claude/api_key.txt in current directory or parent directories
    current = Path.cwd()

    # Search up to 5 levels for .claude directory
    for _ in range(5):
        api_key_path = current / ".claude" / "api_key.txt"
        if api_key_path.exists():
            with open(api_key_path, "r", encoding="utf-8") as f:
                api_key = f.read().strip()

            if not api_key:
                raise ValueError(f"API key file is empty: {api_key_path}")

            # Handle format: CLAUDE_API_KEY=sk-ant-... or ANTHROPIC_API_KEY=sk-ant-...
            if "=" in api_key:
                # Extract value after the equals sign
                api_key = api_key.split("=", 1)[1].strip()

            return api_key

        # Go up one level
        parent = current.parent
        if parent == current:
            # Reached root
            break
        current = parent

    # Not found
    raise FileNotFoundError(
        "API key not found. Please create .claude/api_key.txt with your Anthropic API key.\n"
        "Example: echo 'your-api-key' > .claude/api_key.txt"
    )


def call_llm(
    prompt: str,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4000,
    temperature: float = 0.3,
    max_retries: int = 3,
) -> str:
    """
    Call Anthropic API with retry logic.

    Args:
        prompt: Prompt to send to LLM
        model: Model to use
        max_tokens: Maximum tokens in response
        temperature: Temperature (0-1, lower = more deterministic)
        max_retries: Maximum number of retries on failure

    Returns:
        LLM response as string

    Raises:
        RuntimeError: If API call fails after all retries
    """
    api_key = load_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    retry_delay = 1.0  # Start with 1 second delay

    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text from response
            if message.content and len(message.content) > 0:
                first_block = message.content[0]
                # Check if it's a text block (has text attribute)
                if hasattr(first_block, "text"):
                    return first_block.text  # type: ignore[attr-defined]

            raise ValueError("Empty response from API")

        except anthropic.RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise RuntimeError(f"Rate limit exceeded after {max_retries} retries: {e}")

        except anthropic.APIError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise RuntimeError(f"API error after {max_retries} retries: {e}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error calling LLM: {e}")

    raise RuntimeError("Failed to get response from LLM")


def summarize_file(file_path: str, file_content: str) -> tuple[str, str, str]:
    """
    Generate a summary of a source file.

    Args:
        file_path: Path to the file (for context)
        file_content: Content of the file to summarize

    Returns:
        Tuple of (summary_text, prompt_name, prompt_version)
    """
    prompt_name = "summarize_file"
    prompt_template, prompt_version = load_prompt(prompt_name, return_version=True)
    prompt = prompt_template.format(file_path=file_path, file_content=file_content)

    summary_text = call_llm(prompt, max_tokens=200)
    return (summary_text, prompt_name, prompt_version)


def score_file_relevancy(file_path: str, file_summary: str, doc_description: str) -> tuple[str, int]:
    """
    Score the relevancy of a source file for generating a specific document.

    Args:
        file_path: Path to the source file
        file_summary: Summary of the source file
        doc_description: Description of the document to be generated

    Returns:
        Tuple of (relevancy_explanation, relevancy_score)
        where score is 1-10 (10 = most relevant)
    """
    prompt_template = load_prompt("score_relevancy")
    prompt = prompt_template.format(file_path=file_path, file_summary=file_summary, doc_description=doc_description)

    response = call_llm(prompt, max_tokens=300)

    # Parse JSON response
    import json

    try:
        result = json.loads(response)
        explanation = result.get("relevancy_explanation", "")
        score = result.get("relevancy_score", 5)
        return (explanation, score)
    except json.JSONDecodeError:
        # If JSON parsing fails, return default values
        return ("Unable to parse relevancy response", 5)


def create_customized_template(
    template_guide: str,
    template_guide_version: str,
    about: str,
    source_file_data: list[dict],
) -> tuple[str, dict[str, str], str, str]:
    """
    Create a customized template with section-to-file mappings using relevancy scores.

    Args:
        template_guide: Base template guide content
        template_guide_version: Version timestamp of the template guide
        about: Description of what documentation is about
        source_file_data: List of dicts containing file_path, summary, and relevancy data

    Returns:
        Tuple of (customized_template, selected_files, prompt_name, prompt_version)
        where selected_files maps file path to reason for inclusion
    """
    import json
    import logging

    logger = logging.getLogger(__name__)

    # Format source file data with summaries and relevancy for the prompt
    formatted_lines = []
    for file_data in source_file_data:
        file_path = file_data["file_path"]
        summary = file_data["summary"]["text"]
        relevancy_explanation = file_data["relevancy"]["explanation"]
        relevancy_score = file_data["relevancy"]["score"]

        formatted_lines.append(
            f"- {file_path}:\n"
            f"  Summary: {summary}\n"
            f"  Relevancy Score: {relevancy_score}/10\n"
            f"  Relevancy Explanation: {relevancy_explanation}"
        )

    formatted_source_data = "\n\n".join(formatted_lines)

    prompt_name = "create_customized_template"
    prompt_template, prompt_version = load_prompt(prompt_name, return_version=True)
    prompt = prompt_template.format(
        template_guide=template_guide, doc_description=about, formatted_source_data=formatted_source_data
    )

    response = call_llm(prompt, max_tokens=4000)

    # Log raw response for debugging
    logger.debug(f"LLM raw response preview: {response[:500]}")

    # Parse JSON response - handle markdown-wrapped JSON and other formats
    import re

    try:
        # First, try direct JSON parsing
        result = json.loads(response)
        customized_template = result.get("customized_template", "")
        selected_files = result.get("selected_files_with_reasons", {})
        return (customized_template, selected_files, prompt_name, prompt_version)
    except (json.JSONDecodeError, KeyError) as e:
        # Try to extract JSON from markdown code blocks or surrounding text
        # Look for JSON between ```json and ``` or just between { and }
        json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, response, re.DOTALL)

        if match:
            try:
                result = json.loads(match.group(1))
                customized_template = result.get("customized_template", "")
                selected_files = result.get("selected_files_with_reasons", {})
                return (customized_template, selected_files, prompt_name, prompt_version)
            except (json.JSONDecodeError, KeyError):
                pass

        # Try to find JSON object in the response
        brace_match = re.search(r"\{.*\}", response, re.DOTALL)
        if brace_match:
            try:
                result = json.loads(brace_match.group(0))
                customized_template = result.get("customized_template", "")
                selected_files = result.get("selected_files_with_reasons", {})
                return (customized_template, selected_files, prompt_name, prompt_version)
            except (json.JSONDecodeError, KeyError):
                pass

        # Last resort: log error with details and return response as template
        logger.error(f"Failed to parse LLM response as JSON. Error: {e}")
        logger.error(f"Response preview: {response[:500]}")

        # Fallback: treat entire response as template with no file selection
        return (response, {}, prompt_name, prompt_version)


def customize_template(
    builtin_template: str, about: str, sources: dict[str, str] | None = None, existing_doc: str | None = None
) -> str:
    """
    Customize a built-in template for a specific project.

    Args:
        builtin_template: Built-in template content
        about: Description of what documentation is about
        sources: Dictionary of source file paths to contents (for understanding project structure)
        existing_doc: Optional existing doc to analyze for style

    Returns:
        Customized template content
    """
    source_context = ""
    if sources:
        # Format a sample of source files to give context (limit to prevent overwhelming)
        formatted_sources = format_sources(sources, max_total_length=10000)  # Smaller limit for customization
        source_context = f"\n- Source Files Preview:\n{formatted_sources}"

    existing_doc_context = ""
    if existing_doc:
        existing_doc_context = f"\n- Existing Document Structure:\n{existing_doc[:2000]}"  # Limit to 2000 chars

    prompt_template = load_prompt("customize_template")
    prompt = prompt_template.format(
        builtin_template=builtin_template,
        about=about,
        source_context=source_context,
        existing_doc_context=existing_doc_context,
    )

    return call_llm(prompt, max_tokens=4000)


def format_sources(sources: dict[str, str], max_total_length: int = 50000) -> str:
    """
    Format source files for inclusion in prompt.

    Args:
        sources: Dictionary of file paths to contents
        max_total_length: Maximum total length of formatted sources

    Returns:
        Formatted string of source files
    """
    formatted = []
    total_length = 0

    for path, content in sources.items():
        header = f"\n--- File: {path} ---\n"
        entry = header + content + "\n"

        if total_length + len(entry) > max_total_length:
            # Truncate this file
            remaining = max_total_length - total_length - len(header) - 100
            if remaining > 0:
                truncated = content[:remaining] + "\n\n[... truncated ...]"
                formatted.append(header + truncated)
            break

        formatted.append(entry)
        total_length += len(entry)

    return "".join(formatted)


def generate_document(
    customized_template: str,
    about: str,
    selected_files: dict[str, str],
    source_files_content: dict[str, str],
) -> str:
    """
    Generate documentation from customized template and selected source files.

    Args:
        customized_template: Customized template content with instructions and placeholders
        about: Description of what documentation is about
        selected_files: Dictionary mapping file paths to reasons for inclusion
        source_files_content: Dictionary mapping file paths to their full content

    Returns:
        Generated documentation content
    """
    # Format selected files with reasons for the prompt
    selected_files_lines = []
    for file_path, reason in selected_files.items():
        selected_files_lines.append(f"- {file_path}: {reason}")
    selected_files_with_reasons = "\n".join(selected_files_lines)

    # Format source files content for the prompt
    source_content_lines = []
    for file_path, content in source_files_content.items():
        source_content_lines.append(f"--- File: {file_path} ---\n{content}\n")
    source_files_content_formatted = "\n".join(source_content_lines)

    prompt_template = load_prompt("generate_document")
    prompt = prompt_template.format(
        doc_description=about,
        customized_template=customized_template,
        selected_files_with_reasons=selected_files_with_reasons,
        source_files_content=source_files_content_formatted,
    )

    return call_llm(prompt, max_tokens=4000)
