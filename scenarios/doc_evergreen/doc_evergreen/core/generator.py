"""
LLM generation for doc-evergreen.

Uses direct Anthropic API calls to generate documentation.
Does NOT use Claude Code SDK to avoid conflicts with git hooks.
"""

import time
from pathlib import Path

import anthropic


def load_api_key() -> str:
    """
    Load Anthropic API key from .claude/api_key.txt.

    Returns:
        API key as string

    Raises:
        FileNotFoundError: If API key file doesn't exist
        ValueError: If API key is empty
    """
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


def customize_template(builtin_template: str, about: str, existing_doc: str | None = None) -> str:
    """
    Customize a built-in template for a specific project.

    Args:
        builtin_template: Built-in template content
        about: Description of what documentation is about
        existing_doc: Optional existing doc to analyze for style

    Returns:
        Customized template content
    """
    existing_doc_context = ""
    if existing_doc:
        existing_doc_context = f"\n- Existing Document Structure:\n{existing_doc[:2000]}"  # Limit to 2000 chars

    prompt = f"""You are customizing a documentation template for a software project.

Built-in Template:
{builtin_template}

Project Context:
- Topic: {about}{existing_doc_context}

Task:
Create a customized version of this template that:
1. Maintains the overall structure and instructions for AI
2. Adjusts tone/style for the specific project context
3. Adds project-specific sections if beneficial
4. Includes appropriate placeholder examples

IMPORTANT: The customized template should still be a template with instructions for generating documentation, not the final documentation itself.

Return ONLY the customized template in markdown format. Do not add YAML frontmatter - that will be added automatically.
"""

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


def generate_document(template: str, sources: dict[str, str], about: str) -> str:
    """
    Generate documentation from template and source files.

    Args:
        template: Template content (with instructions)
        sources: Dictionary of file paths to contents
        about: Description of what documentation is about

    Returns:
        Generated documentation content
    """
    formatted_sources = format_sources(sources)

    prompt = f"""You are generating documentation for a software project.

Template:
{template}

Source Files:
{formatted_sources}

Topic: {about}

Instructions:
1. Follow the template structure and instructions carefully
2. Extract relevant information from the source files provided
3. Generate clear, accurate, technical documentation
4. Use proper markdown formatting
5. Include code examples from the source files where appropriate
6. Ensure all information is based on the actual source files
7. If the template has a {{{{SOURCE_FILES}}}} placeholder, replace it with content extracted from the sources

Generate the complete documentation following the template:
"""

    return call_llm(prompt, max_tokens=4000)
