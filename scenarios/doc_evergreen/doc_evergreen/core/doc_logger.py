"""
Comprehensive logging for doc-evergreen operations.

Tracks all LLM interactions, file operations, and key decisions
to enable debugging and understanding of the generation process.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


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

        # Also create JSON log for structured data
        self.json_log_file = self.log_dir / f"doc-evergreen_{timestamp}.jsonl"

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

        # Log to JSON for structured analysis
        self._log_json(
            {
                "type": "llm_call",
                "operation": operation,
                "model": model,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_file_read(self, file_path: str, reason: str, content_preview: Optional[str] = None) -> None:
        """Log when a file is read."""
        self.logger.info(f"FILE READ: {file_path}")
        self.logger.info(f"  Reason: {reason}")
        if content_preview:
            self.logger.debug(f"  Preview (first 500 chars): {content_preview[:500]}")

        self._log_json(
            {"type": "file_read", "file_path": file_path, "reason": reason, "timestamp": datetime.now().isoformat()}
        )

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

        self._log_json(
            {
                "type": "decision",
                "decision_type": decision_type,
                "decision": decision,
                "reasoning": reasoning,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
            }
        )

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

        self._log_json(
            {
                "type": "discovery_step",
                "depth": depth,
                "directory": directory,
                "files_found": files_found,
                "dirs_found": dirs_found,
                "selected_files": selected_files,
                "selected_dirs": selected_dirs,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_template_selection(
        self, selected_template: str, customization_needed: bool, customization_reasoning: Optional[str] = None
    ) -> None:
        """Log template selection and customization decision."""
        self.logger.info(f"TEMPLATE SELECTION: {selected_template}")
        self.logger.info(f"  Customization needed: {customization_needed}")
        if customization_reasoning:
            self.logger.info(f"  Reasoning: {customization_reasoning}")

        self._log_json(
            {
                "type": "template_selection",
                "template": selected_template,
                "customization_needed": customization_needed,
                "customization_reasoning": customization_reasoning,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_source_mapping(self, section: str, sources: list[str], reasoning: Optional[str] = None) -> None:
        """Log source mapping for a template section."""
        self.logger.debug(f"SOURCE MAPPING: {section}")
        self.logger.debug(f"  Mapped to {len(sources)} sources: {', '.join(sources)}")
        if reasoning:
            self.logger.debug(f"  Reasoning: {reasoning}")

        self._log_json(
            {
                "type": "source_mapping",
                "section": section,
                "sources": sources,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_generation_output(self, output_path: str, content_length: int, backup_path: Optional[str] = None) -> None:
        """Log the final generation output."""
        self.logger.info(f"GENERATION OUTPUT: {output_path}")
        self.logger.info(f"  Content length: {content_length} characters")
        if backup_path:
            self.logger.info(f"  Backup saved to: {backup_path}")

        self._log_json(
            {
                "type": "generation_output",
                "output_path": output_path,
                "content_length": content_length,
                "backup_path": backup_path,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def log_error(self, error_type: str, error_message: str, context: Optional[dict[str, Any]] = None) -> None:
        """Log an error that occurred."""
        self.logger.error(f"ERROR: {error_type}")
        self.logger.error(f"  Message: {error_message}")
        if context:
            self.logger.error(f"  Context: {json.dumps(context, indent=2)}")

        self._log_json(
            {
                "type": "error",
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
            }
        )

    def _log_json(self, data: dict[str, Any]) -> None:
        """Log structured data to JSON file."""
        with open(self.json_log_file, "a") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def close(self) -> None:
        """Close the logger and write summary."""
        self.logger.info("=" * 80)
        self.logger.info("DOC-EVERGREEN LOGGING SESSION ENDED")
        self.logger.info(f"Log files: {self.log_file}, {self.json_log_file}")
        self.logger.info("=" * 80)

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
