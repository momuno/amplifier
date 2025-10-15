"""
Paper trail management for synthesis process.

Creates and manages temporary files during synthesis for debugging and review.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from amplifier.utils.logger import get_logger

logger = get_logger(__name__)


class PaperTrailManager:
    """Manage temporary files and paper trail during synthesis."""

    def __init__(self, paper_trail_dir: Path | None = None):
        """
        Initialize paper trail manager.

        Args:
            paper_trail_dir: Directory for paper trail (default: .repo_synthesis/)
        """
        self.paper_trail_dir = paper_trail_dir or Path(".repo_synthesis")
        self.enabled = True
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure paper trail directory exists."""
        if self.enabled:
            self.paper_trail_dir.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            (self.paper_trail_dir / "nodes").mkdir(exist_ok=True)
            (self.paper_trail_dir / "syntheses").mkdir(exist_ok=True)
            (self.paper_trail_dir / "prompts").mkdir(exist_ok=True)
            (self.paper_trail_dir / "responses").mkdir(exist_ok=True)

    def save_node_content(self, node_path: Path, content: str) -> Path | None:
        """
        Save node content to paper trail.

        Args:
            node_path: Path of the node
            content: Content to save

        Returns:
            Path to saved file or None if disabled
        """
        if not self.enabled:
            return None

        try:
            # Create safe filename from path
            safe_name = str(node_path).replace("/", "_").replace("\\", "_")
            if len(safe_name) > 100:
                safe_name = f"{safe_name[:50]}...{safe_name[-47:]}"

            output_path = self.paper_trail_dir / "nodes" / f"{safe_name}.txt"

            output_path.write_text(content, encoding="utf-8")
            logger.debug(f"Saved node content: {output_path}")

            return output_path

        except Exception as e:
            logger.warning(f"Failed to save node content: {e}")
            return None

    def save_synthesis(self, node_path: Path, synthesis: str, depth: int) -> Path | None:
        """
        Save synthesis result to paper trail.

        Args:
            node_path: Path of the node
            synthesis: Synthesis text
            depth: Depth level of the node

        Returns:
            Path to saved file
        """
        if not self.enabled:
            return None

        try:
            safe_name = str(node_path).replace("/", "_").replace("\\", "_")
            if len(safe_name) > 100:
                safe_name = f"{safe_name[:50]}...{safe_name[-47:]}"

            filename = f"depth_{depth:02d}_{safe_name}.md"
            output_path = self.paper_trail_dir / "syntheses" / filename

            # Format synthesis with metadata
            formatted = f"""# Synthesis: {node_path.name}

**Path**: {node_path}
**Depth**: {depth}
**Generated**: {datetime.now().isoformat()}

---

{synthesis}
"""

            output_path.write_text(formatted, encoding="utf-8")
            logger.debug(f"Saved synthesis: {output_path}")

            return output_path

        except Exception as e:
            logger.warning(f"Failed to save synthesis: {e}")
            return None

    def save_prompt(self, node_path: Path, prompt: str, prompt_type: str) -> Path | None:
        """
        Save prompt used for synthesis.

        Args:
            node_path: Path of the node
            prompt: Prompt text
            prompt_type: Type of prompt (file, directory, final)

        Returns:
            Path to saved file
        """
        if not self.enabled:
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = str(node_path).replace("/", "_").replace("\\", "_")
            if len(safe_name) > 80:
                safe_name = f"{safe_name[:40]}...{safe_name[-37:]}"

            filename = f"{timestamp}_{prompt_type}_{safe_name}.txt"
            output_path = self.paper_trail_dir / "prompts" / filename

            output_path.write_text(prompt, encoding="utf-8")
            logger.debug(f"Saved prompt: {output_path}")

            return output_path

        except Exception as e:
            logger.warning(f"Failed to save prompt: {e}")
            return None

    def save_response(self, node_path: Path, response: str | dict, response_type: str) -> Path | None:
        """
        Save AI response.

        Args:
            node_path: Path of the node
            response: Response text or dict
            response_type: Type of response

        Returns:
            Path to saved file
        """
        if not self.enabled:
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = str(node_path).replace("/", "_").replace("\\", "_")
            if len(safe_name) > 80:
                safe_name = f"{safe_name[:40]}...{safe_name[-37:]}"

            filename = f"{timestamp}_{response_type}_{safe_name}.json"
            output_path = self.paper_trail_dir / "responses" / filename

            if isinstance(response, dict):
                output_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
            else:
                output_path.write_text(str(response), encoding="utf-8")

            logger.debug(f"Saved response: {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Failed to save response: {e}")
            return None

    def save_final_report(self, content: str, filename: str = "final_synthesis.md") -> Path | None:
        """
        Save final synthesis report.

        Args:
            content: Report content
            filename: Output filename

        Returns:
            Path to saved file
        """
        if not self.enabled:
            return None

        try:
            output_path = self.paper_trail_dir / filename
            output_path.write_text(content, encoding="utf-8")

            logger.info(f"Saved final report: {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Failed to save final report: {e}")
            return None

    def cleanup(self, keep_final: bool = True) -> None:
        """
        Clean up paper trail directory.

        Args:
            keep_final: Whether to keep the final report
        """
        if not self.enabled or not self.paper_trail_dir.exists():
            return

        try:
            if keep_final:
                # Keep only the final report
                final_report = self.paper_trail_dir / "final_synthesis.md"
                if final_report.exists():
                    # Save final report
                    temp_path = self.paper_trail_dir.parent / "final_synthesis.md"
                    shutil.copy2(final_report, temp_path)

                    # Remove directory
                    shutil.rmtree(self.paper_trail_dir)

                    # Restore final report
                    self.paper_trail_dir.mkdir()
                    shutil.move(str(temp_path), str(final_report))

                    logger.info("Paper trail cleaned, final report preserved")
                else:
                    shutil.rmtree(self.paper_trail_dir)
                    logger.info("Paper trail cleaned")
            else:
                shutil.rmtree(self.paper_trail_dir)
                logger.info("Paper trail removed completely")

        except Exception as e:
            logger.warning(f"Failed to cleanup paper trail: {e}")

    def disable(self) -> None:
        """Disable paper trail creation."""
        self.enabled = False
        logger.debug("Paper trail disabled")

    def enable(self) -> None:
        """Enable paper trail creation."""
        self.enabled = True
        self._ensure_directory()
        logger.debug("Paper trail enabled")
