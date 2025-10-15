"""
Main orchestrator for repository synthesis.

Coordinates the entire synthesis process from tree building to final output.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from amplifier.ccsdk_toolkit import ClaudeSession
from amplifier.ccsdk_toolkit import SessionOptions
from amplifier.ccsdk_toolkit.defensive import parse_llm_json
from amplifier.utils.logger import get_logger

from ..prompts import get_directory_synthesis_prompt
from ..prompts import get_file_synthesis_prompt
from ..prompts import get_final_synthesis_prompt
from .hierarchy import SynthesisNode
from .hierarchy import SynthesisTree
from .paper_trail import PaperTrailManager
from .state import StateManager
from .state import SynthesisState
from .traversal import TreeBuilder

logger = get_logger(__name__)


class RepoSynthesizer:
    """Orchestrate the complete repository synthesis process."""

    def __init__(
        self,
        repo_path: Path,
        topic: str,
        output_path: Path | None = None,
        max_depth: int = 10,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        resume_session: str | None = None,
        paper_trail: bool = True,
    ):
        """
        Initialize the repository synthesizer.

        Args:
            repo_path: Path to repository to analyze
            topic: Topic/question to focus synthesis on
            output_path: Output path for final synthesis
            max_depth: Maximum directory depth to traverse
            include_patterns: File patterns to include
            exclude_patterns: Patterns to exclude
            resume_session: Session ID to resume from
            paper_trail: Whether to create paper trail
        """
        self.repo_path = repo_path.resolve()
        self.topic = topic
        self.output_path = output_path or Path(f"synthesis_{self.repo_path.name}.md")
        self.max_depth = max_depth
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self.resume_session = resume_session

        # Generate or resume session
        self.session_id = resume_session or str(uuid.uuid4())[:8]

        # Initialize components
        self.state_dir = Path(f".repo_synthesis_state_{self.session_id}")
        self.state_manager = StateManager(self.state_dir)
        self.paper_trail_manager = PaperTrailManager() if paper_trail else None

        # Will be initialized during run
        self.tree: SynthesisTree | None = None
        self.state: SynthesisState | None = None

    async def synthesize(self) -> Path:
        """
        Run the complete synthesis process.

        Returns:
            Path to the final synthesis output
        """
        logger.info(f"Starting repository synthesis for: {self.repo_path}")
        logger.info(f"Topic: {self.topic}")
        logger.info(f"Session: {self.session_id}")

        try:
            # Initialize or resume
            if self.resume_session:
                await self._resume()
            else:
                await self._initialize()

            # Process nodes bottom-up
            await self._process_nodes()

            # Generate final synthesis
            await self._generate_final_synthesis()

            # Cleanup
            await self._cleanup()

            logger.info(f"✅ Synthesis complete! Output: {self.output_path}")
            return self.output_path

        except KeyboardInterrupt:
            logger.warning("Synthesis interrupted - progress saved")
            logger.info(f"Resume with: --resume {self.session_id}")
            raise

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            if self.state:
                self.state.errors.append({"error": str(e), "timestamp": datetime.now().isoformat()})
                self.state_manager.save_state(self.state)
            raise

    async def _initialize(self) -> None:
        """Initialize new synthesis session."""
        logger.info("Initializing new synthesis session...")

        # Build repository tree
        builder = TreeBuilder(
            include_patterns=self.include_patterns,
            exclude_patterns=self.exclude_patterns,
            max_depth=self.max_depth,
        )

        self.tree = builder.build_tree(self.repo_path)

        # Estimate time
        min_time, max_time = builder.estimate_processing_time(self.tree)
        logger.info(f"Estimated time: {min_time}-{max_time} minutes")

        # Create initial state
        self.state = SynthesisState(
            session_id=self.session_id,
            repo_path=self.repo_path,
            topic=self.topic,
            started_at=datetime.now(),
            total_nodes=self.tree.total_nodes,
            processed_nodes=0,
            current_phase="processing",
            output_path=self.output_path,
            paper_trail_dir=self.paper_trail_manager.paper_trail_dir if self.paper_trail_manager else None,
            config={
                "max_depth": self.max_depth,
                "include_patterns": self.include_patterns,
                "exclude_patterns": self.exclude_patterns,
            },
        )

        # Save initial state
        self.state_manager.checkpoint(self.state, self.tree)

        logger.info(f"Found {self.tree.total_nodes} nodes to process")
        logger.info(f"  Files: {self.tree.file_count}")
        logger.info(f"  Directories: {self.tree.directory_count}")

    async def _resume(self) -> None:
        """Resume from saved state."""
        logger.info(f"Resuming session {self.resume_session}...")

        # Load state
        self.state = self.state_manager.load_state()
        if not self.state:
            raise ValueError(f"Cannot resume session {self.resume_session} - state not found")

        # Load tree
        self.tree = self.state_manager.load_tree()
        if not self.tree:
            raise ValueError(f"Cannot resume session {self.resume_session} - tree not found")

        logger.info(f"Resumed: {self.tree.processed_nodes}/{self.tree.total_nodes} nodes processed")
        logger.info(f"Progress: {self.tree.get_progress():.1f}%")

    async def _process_nodes(self) -> None:
        """Process all nodes in the tree bottom-up."""
        logger.info("Processing nodes bottom-up...")

        # Create AI session
        options = SessionOptions(
            system_prompt="You are an expert code analyst. Provide insightful synthesis focused on the given topic.",
            retry_attempts=2,
        )

        async with ClaudeSession(options) as session:
            while True:
                # Get next batch of nodes to process
                if not self.tree:
                    break
                batch = self.tree.get_next_batch()
                if not batch:
                    break

                # Process batch
                for node in batch:
                    try:
                        await self._process_single_node(node, session)

                        # Update progress
                        self.tree.mark_processed(node)
                        if self.state:
                            self.state.processed_nodes = self.tree.processed_nodes

                        # Save checkpoint after EVERY node for maximum resilience
                        if self.state and self.tree:
                            self.state_manager.checkpoint(self.state, self.tree)

                        # Show progress
                        progress = self.tree.get_progress()
                        logger.info(
                            f"[{self.tree.processed_nodes}/{self.tree.total_nodes}] "
                            f"{progress:.1f}% - Processed: {node.name}"
                        )

                    except Exception as e:
                        logger.error(f"Failed to process {node.path}: {e}")
                        node.error = str(e)
                        if self.tree:
                            self.tree.mark_processed(node)  # Mark as processed to continue
                            # Also save checkpoint on error
                            if self.state:
                                self.state_manager.checkpoint(self.state, self.tree)

        logger.info("✅ All nodes processed!")

    async def _process_single_node(self, node: SynthesisNode, session: ClaudeSession) -> None:
        """Process a single node with AI synthesis."""
        logger.debug(f"Processing node: {node.path}")

        if node.is_file():
            await self._process_file_node(node, session)
        else:
            await self._process_directory_node(node, session)

    async def _process_file_node(self, node: SynthesisNode, session: ClaudeSession) -> None:
        """Process a file node."""
        try:
            # Read file content
            content = node.path.read_text(encoding="utf-8", errors="ignore")
            node.content = content

            # Skip very large files
            if len(content) > 50000:
                logger.debug(f"Skipping large file: {node.path} ({len(content)} chars)")
                node.synthesis = "File too large for detailed analysis"
                return

            # Save to paper trail
            if self.paper_trail_manager:
                self.paper_trail_manager.save_node_content(node.path, content)

            # Generate prompt
            prompt = get_file_synthesis_prompt(node.path, content, self.topic)

            # Save prompt to paper trail
            if self.paper_trail_manager:
                self.paper_trail_manager.save_prompt(node.path, prompt, "file")

            # Get AI synthesis
            response = await session.query(prompt)

            # Parse response
            parsed = parse_llm_json(response.content, default={})

            # Save response to paper trail
            if self.paper_trail_manager and isinstance(parsed, dict):
                self.paper_trail_manager.save_response(node.path, parsed, "file")

            # Extract synthesis
            if isinstance(parsed, dict):
                node.synthesis = json.dumps(parsed, indent=2)
                node.key_insights = parsed.get("key_insights", [])
            else:
                node.synthesis = "No synthesis generated"
                node.key_insights = []

            # Save synthesis to paper trail
            if self.paper_trail_manager:
                self.paper_trail_manager.save_synthesis(node.path, node.synthesis, node.depth)

        except Exception as e:
            logger.warning(f"Error processing file {node.path}: {e}")
            node.synthesis = f"Error: {e}"
            node.error = str(e)

    async def _process_directory_node(self, node: SynthesisNode, session: ClaudeSession) -> None:
        """Process a directory node based on its children."""
        try:
            # Collect child syntheses
            child_syntheses = []
            for child in node.children:
                if child.synthesis:
                    child_syntheses.append((child.name, child.synthesis))

            if not child_syntheses:
                node.synthesis = "Empty directory or no processable content"
                return

            # Generate prompt
            prompt = get_directory_synthesis_prompt(node.path, child_syntheses, self.topic)

            # Save prompt to paper trail
            if self.paper_trail_manager:
                self.paper_trail_manager.save_prompt(node.path, prompt, "directory")

            # Get AI synthesis
            response = await session.query(prompt)

            # Parse response
            parsed = parse_llm_json(response.content, default={})

            # Save response to paper trail
            if self.paper_trail_manager and isinstance(parsed, dict):
                self.paper_trail_manager.save_response(node.path, parsed, "directory")

            # Extract synthesis
            if isinstance(parsed, dict):
                node.synthesis = json.dumps(parsed, indent=2)
                node.key_insights = parsed.get("key_insights", [])
            else:
                node.synthesis = "No synthesis generated"
                node.key_insights = []

            # Save synthesis to paper trail
            if self.paper_trail_manager:
                self.paper_trail_manager.save_synthesis(node.path, node.synthesis, node.depth)

        except Exception as e:
            logger.warning(f"Error processing directory {node.path}: {e}")
            node.synthesis = f"Error: {e}"
            node.error = str(e)

    async def _generate_final_synthesis(self) -> str:
        """Generate the final comprehensive synthesis."""
        logger.info("Generating final synthesis...")

        if not self.tree:
            logger.error("No tree available for final synthesis")
            return ""

        # Validate we have actual synthesis data
        if not self.tree._node_map:
            logger.error("Tree has no nodes - synthesis data is empty!")
            raise ValueError("Cannot generate final synthesis - no nodes were processed")

        # Count nodes with actual synthesis
        nodes_with_synthesis = sum(
            1
            for node in self.tree._node_map.values()
            if node.synthesis and node.synthesis != "Empty directory or no processable content"
        )

        if nodes_with_synthesis == 0:
            logger.error(f"No nodes have synthesis content (0/{len(self.tree._node_map)} nodes)")
            raise ValueError("Cannot generate final synthesis - no synthesis content was generated")

        logger.info(f"Found {nodes_with_synthesis}/{len(self.tree._node_map)} nodes with synthesis")

        # Collect all insights
        all_insights = []
        for node in self.tree._node_map.values():
            all_insights.extend(node.key_insights)

        # Get root synthesis
        root_synthesis = self.tree.root.synthesis or "No root synthesis available"

        # Generate final synthesis prompt
        prompt = get_final_synthesis_prompt(root_synthesis, all_insights, self.topic)

        # Get AI synthesis
        options = SessionOptions(
            system_prompt="You are an expert analyst creating a comprehensive synthesis report.",
            retry_attempts=2,
        )

        async with ClaudeSession(options) as session:
            response = await session.query(prompt)
            parsed = parse_llm_json(response.content, default={})
            final_synthesis = parsed if isinstance(parsed, dict) else {}

        # Generate markdown report
        report = self._format_final_report(final_synthesis)

        # Save report
        self.output_path.write_text(report, encoding="utf-8")

        # Save to paper trail
        if self.paper_trail_manager:
            self.paper_trail_manager.save_final_report(report)

        # Update state
        if self.state:
            self.state.current_phase = "completed"
            self.state.completed_at = datetime.now()
            self.state_manager.save_state(self.state)

        return report

    def _format_final_report(self, synthesis: dict[str, Any]) -> str:
        """Format the final synthesis into a markdown report."""
        lines = [
            f"# Repository Synthesis: {self.repo_path.name}",
            "",
            f"**Topic**: {self.topic}",
            f"**Repository**: {self.repo_path}",
            f"**Generated**: {datetime.now().isoformat()}",
            f"**Session**: {self.session_id}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            synthesis.get("executive_summary", "No summary generated"),
            "",
            "## Answer to Topic",
            "",
            synthesis.get("answer_to_topic", "No specific answer generated"),
            "",
        ]

        # Add novel capabilities
        if synthesis.get("novel_capabilities"):
            lines.extend(
                [
                    "## Novel Capabilities",
                    "",
                ]
            )
            for cap in synthesis["novel_capabilities"]:
                if isinstance(cap, dict):
                    lines.extend(
                        [
                            f"### {cap.get('capability', 'Unknown')}",
                            "",
                            f"**Significance**: {cap.get('significance', 'N/A')}",
                            "",
                            f"**Implementation**: {cap.get('implementation', 'N/A')}",
                            "",
                        ]
                    )
                else:
                    lines.append(f"- {cap}")
                    lines.append("")

        # Add architecture insights
        if synthesis.get("architecture_insights"):
            lines.extend(
                [
                    "## Architecture Insights",
                    "",
                ]
            )
            for insight in synthesis["architecture_insights"]:
                lines.append(f"- {insight}")
            lines.append("")

        # Add design philosophy
        if synthesis.get("design_philosophy"):
            lines.extend(
                [
                    "## Design Philosophy",
                    "",
                    synthesis["design_philosophy"],
                    "",
                ]
            )

        # Add unique approaches
        if synthesis.get("unique_approaches"):
            lines.extend(
                [
                    "## Unique Approaches",
                    "",
                ]
            )
            for approach in synthesis["unique_approaches"]:
                lines.append(f"- {approach}")
            lines.append("")

        # Add potential applications
        if synthesis.get("potential_applications"):
            lines.extend(
                [
                    "## Potential Applications",
                    "",
                ]
            )
            for app in synthesis["potential_applications"]:
                lines.append(f"- {app}")
            lines.append("")

        # Add key takeaways
        if synthesis.get("key_takeaways"):
            lines.extend(
                [
                    "## Key Takeaways",
                    "",
                ]
            )
            for takeaway in synthesis["key_takeaways"]:
                lines.append(f"1. {takeaway}")
            lines.append("")

        # Add tree structure summary
        if self.tree:
            lines.extend(
                [
                    "---",
                    "",
                    "## Repository Structure",
                    "",
                    f"- **Total Nodes**: {self.tree.total_nodes}",
                    f"- **Files Analyzed**: {self.tree.file_count}",
                    f"- **Directories**: {self.tree.directory_count}",
                    f"- **Max Depth**: {self.tree.max_depth}",
                    "",
                ]
            )

        return "\n".join(lines)

    async def _cleanup(self) -> None:
        """Clean up temporary files and paper trail."""
        if self.paper_trail_manager:
            logger.info(f"Paper trail preserved in: {self.paper_trail_manager.paper_trail_dir}")
            # Don't clean up - preserve the paper trail for inspection
            # self.paper_trail_manager.cleanup(keep_final=True)
