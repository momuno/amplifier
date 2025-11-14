"""
Comprehensive logging for doc-evergreen operations.

Tracks all LLM interactions, file operations, and key decisions
to enable debugging and understanding of the generation process.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TextIO


class TeeStream:
    """Stream that writes to multiple targets (e.g., stdout and log file)."""

    def __init__(self, *streams: TextIO):
        """Initialize with multiple output streams."""
        self.streams = streams

    def write(self, data: str) -> None:
        """Write to all streams."""
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self) -> None:
        """Flush all streams."""
        for stream in self.streams:
            stream.flush()


class DocEvergreenLogger:
    """Logger that tracks LLM interactions and key decisions."""

    def __init__(self, log_dir: Path):
        """Initialize logger with output directory."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"doc-evergreen_{timestamp}.log"

        # Set up Python logging
        self.logger = logging.getLogger("doc-evergreen")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)

        # Format with timestamp
        formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Open a raw file handle for stdout/stderr capture
        self.stdout_log = open(self.log_file, "a", encoding="utf-8")

        # Store original stdout/stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # Create tee streams to capture all output
        sys.stdout = TeeStream(self.original_stdout, self.stdout_log)
        sys.stderr = TeeStream(self.original_stderr, self.stdout_log)

        self.logger.info("=" * 80)
        self.logger.info("DOC-EVERGREEN LOGGING SESSION STARTED")
        self.logger.info("=" * 80)

    def log_llm_call(
        self,
        operation: str,
        prompt: str,
        response: str,
        model: str = "claude-3-5-sonnet-20241022",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an LLM API call with full prompt and response."""
        self.logger.info(f"LLM CALL: {operation}")
        self.logger.info(f"Model: {model}")

        # Log prompt
        self.logger.debug("=" * 40 + " PROMPT " + "=" * 40)
        self.logger.debug(prompt)
        self.logger.debug("=" * 87)

        # Log response
        self.logger.debug("=" * 40 + " RESPONSE " + "=" * 38)
        self.logger.debug(response)
        self.logger.debug("=" * 87)

    def log_file_read(self, file_path: str, reason: str, content_preview: Optional[str] = None) -> None:
        """Log when a file is read."""
        self.logger.info(f"FILE READ: {file_path}")
        self.logger.info(f"  Reason: {reason}")
        if content_preview:
            self.logger.debug(f"  Preview (first 500 chars): {content_preview[:500]}")

    def log_decision(
        self,
        decision_type: str,
        decision: str,
        reasoning: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a key decision made during generation."""
        self.logger.info(f"DECISION: {decision_type}")
        self.logger.info(f"  Choice: {decision}")
        if reasoning:
            self.logger.info(f"  Reasoning: {reasoning}")

    def log_discovery_step(
        self,
        depth: int,
        directory: str,
        files_found: int,
        dirs_found: int,
        selected_files: list[str],
        selected_dirs: list[str],
        reasoning: str,
    ) -> None:
        """Log a discovery step with LLM's decisions."""
        self.logger.info(f"DISCOVERY STEP: Depth {depth}, Directory: {directory}")
        self.logger.info(f"  Found: {files_found} files, {dirs_found} subdirectories")
        self.logger.info(f"  Selected {len(selected_files)} files: {', '.join(selected_files)}")
        self.logger.info(f"  Selected {len(selected_dirs)} dirs to explore: {', '.join(selected_dirs)}")
        self.logger.info(f"  Reasoning: {reasoning}")

    def log_template_selection(
        self, selected_template: str, customization_needed: bool, customization_reasoning: Optional[str] = None
    ) -> None:
        """Log template selection and customization decision."""
        self.logger.info(f"TEMPLATE SELECTION: {selected_template}")
        self.logger.info(f"  Customization needed: {customization_needed}")
        if customization_reasoning:
            self.logger.info(f"  Reasoning: {customization_reasoning}")

    def log_source_mapping(self, section: str, sources: list[str], reasoning: Optional[str] = None) -> None:
        """Log source mapping for a template section."""
        self.logger.debug(f"SOURCE MAPPING: {section}")
        self.logger.debug(f"  Mapped to {len(sources)} sources: {', '.join(sources)}")
        if reasoning:
            self.logger.debug(f"  Reasoning: {reasoning}")

    def log_generation_output(self, output_path: str, content_length: int, backup_path: Optional[str] = None) -> None:
        """Log the final generation output."""
        self.logger.info(f"GENERATION OUTPUT: {output_path}")
        self.logger.info(f"  Content length: {content_length} characters")
        if backup_path:
            self.logger.info(f"  Backup saved to: {backup_path}")

    def log_error(self, error_type: str, error_message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log an error that occurred."""
        self.logger.error(f"ERROR: {error_type}")
        self.logger.error(f"  Message: {error_message}")
        if context:
            self.logger.error(f"  Context: {json.dumps(context, indent=2)}")

    def log_command_invocation(self, command: str, args: dict[str, Any]) -> None:
        """Log the command invocation with all arguments."""
        self.logger.info("=" * 80)
        self.logger.info("COMMAND INVOCATION")
        self.logger.info(f"Command: {command}")
        self.logger.info("Arguments:")
        for key, value in args.items():
            self.logger.info(f"  --{key}: {value}")
        self.logger.info("=" * 80)

    def log_function_call(self, function_name: str, args: dict[str, Any]) -> None:
        """Log a function call with its arguments."""
        self.logger.debug(f"FUNCTION CALL: {function_name}")
        for key, value in args.items():
            # Truncate long values for readability
            str_value = str(value)
            if len(str_value) > 200:
                str_value = str_value[:200] + "..."
            self.logger.debug(f"  {key}={str_value}")

    def close(self) -> None:
        """Close the logger and write summary."""
        self.logger.info("=" * 80)
        self.logger.info("DOC-EVERGREEN LOGGING SESSION ENDED")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info("=" * 80)

        # Restore original stdout/stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

        # Close the stdout log file
        self.stdout_log.close()

        # Close handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


# Global logger instance
_logger: Optional[DocEvergreenLogger] = None


def init_logger(log_dir: Path) -> DocEvergreenLogger:
    """Initialize the global logger."""
    global _logger
    _logger = DocEvergreenLogger(log_dir)
    return _logger


def get_logger() -> Optional[DocEvergreenLogger]:
    """Get the current logger instance."""
    return _logger


def close_logger() -> None:
    """Close the current logger."""
    global _logger
    if _logger:
        _logger.close()
        _logger = None


def trace_function(func):
    """Decorator to trace function calls with arguments."""
    import functools
    import inspect

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if _logger:
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Convert to dict, handling Path objects
            args_dict = {}
            for name, value in bound_args.arguments.items():
                if isinstance(value, Path):
                    args_dict[name] = str(value)
                elif isinstance(value, (list, tuple)) and value and isinstance(value[0], Path):
                    args_dict[name] = [str(v) for v in value]
                else:
                    args_dict[name] = value

            _logger.log_function_call(func.__name__, args_dict)

        return func(*args, **kwargs)

    return wrapper
