"""Configuration file loading for doc_evergreen.

Handles loading and parsing of .doc-evergreen.yaml configuration files,
with graceful fallback to defaults when files are missing or malformed.
"""

import logging
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class FileConfig:
    """Configuration for a specific documentation file."""

    template: str | None = None
    sources: list[str] | None = None


@dataclass
class LLMConfig:
    """LLM provider settings."""

    provider: str = "claude"
    model: str = "claude-3-5-sonnet-20241022"


@dataclass
class Config:
    """Project configuration for doc_evergreen."""

    template_dir: str | None = None
    files: dict[str, FileConfig] = field(default_factory=dict)
    default_sources: list[str] = field(default_factory=list)
    llm: LLMConfig = field(default_factory=LLMConfig)


def default_config() -> Config:
    """Return default configuration with sensible defaults.

    Returns:
        Config object with default values for all fields
    """
    return Config()


def find_project_root(start_dir: Path | None = None) -> Path | None:
    """Find project root by looking for .doc-evergreen.yaml or .git directory.

    Searches up from start_dir (defaults to cwd) looking for:
    1. .doc-evergreen.yaml file
    2. .git directory (fallback)

    Args:
        start_dir: Directory to start searching from (defaults to cwd)

    Returns:
        Path to project root, or None if no root found
    """
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()

    # Search up directory tree
    while True:
        # Check for .doc-evergreen.yaml
        if (current / ".doc-evergreen.yaml").exists():
            return current

        # Check for .git directory (fallback)
        if (current / ".git").exists():
            return current

        # Move up one level
        parent = current.parent
        if parent == current:  # Reached filesystem root
            return None
        current = parent


def parse_config_data(data: dict[str, Any]) -> Config:
    """Parse YAML dict into Config dataclass.

    Args:
        data: Dictionary loaded from YAML file

    Returns:
        Config object with parsed values merged with defaults
    """
    # Extract top-level fields with defaults
    template_dir = data.get("template_dir")
    default_sources = data.get("default_sources", [])

    # Parse files section
    files = {}
    files_data = data.get("files", {})
    if isinstance(files_data, dict):
        for filename, file_data in files_data.items():
            if isinstance(file_data, dict):
                files[filename] = FileConfig(
                    template=file_data.get("template"),
                    sources=file_data.get("sources"),
                )
            else:
                logger.warning(f"Invalid file config for {filename}, skipping")

    # Parse LLM section
    llm_data = data.get("llm", {})
    if isinstance(llm_data, dict):
        llm = LLMConfig(
            provider=llm_data.get("provider", "claude"),
            model=llm_data.get("model", "claude-3-5-sonnet-20241022"),
        )
    else:
        logger.warning("Invalid llm config, using defaults")
        llm = LLMConfig()

    return Config(
        template_dir=template_dir,
        files=files,
        default_sources=default_sources,
        llm=llm,
    )


def load_config(project_root: Path | None = None) -> Config:
    """Load .doc-evergreen.yaml from project root.

    If project_root is None, uses find_project_root() to locate it.
    If config file doesn't exist or is malformed, returns default_config().

    Handles:
    - Missing file (use defaults)
    - Malformed YAML (log warning, use defaults)
    - Partial config (merge with defaults)

    Args:
        project_root: Path to project root (defaults to auto-discovery)

    Returns:
        Config object with loaded/default values
    """
    if project_root is None:
        project_root = find_project_root()

    if project_root is None:
        return default_config()

    config_path = project_root / ".doc-evergreen.yaml"
    if not config_path.exists():
        return default_config()

    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.warning(f"Malformed YAML in {config_path}: {e}, using defaults")
        return default_config()
    except OSError as e:
        logger.warning(f"Error reading {config_path}: {e}, using defaults")
        return default_config()

    if data is None:  # Empty file
        return default_config()

    if not isinstance(data, dict):
        logger.warning(f"Config file {config_path} must contain a YAML object, using defaults")
        return default_config()

    # Parse into Config object
    return parse_config_data(data)
