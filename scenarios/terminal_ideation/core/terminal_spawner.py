"""Spawn Windows Terminal tabs with Claude Code sessions."""

import logging
import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def spawn_terminal(variant: dict[str, Any], worktree_path: Path, auto_execute: bool = True) -> dict[str, Any]:
    """
    Spawn a Windows Terminal tab with a Claude Code session.

    Args:
        variant: Variant info with id, title, prompt, and color
        worktree_path: Directory to run Claude Code in
        auto_execute: Whether to auto-start the prompt (default True)

    Returns:
        Dictionary with tab_id, pid, and launch_time

    Raises:
        OSError: If terminal launch fails
    """
    tab_id = str(uuid.uuid4())[:8]
    launch_time = datetime.now().isoformat()

    # Create a startup script for the terminal
    startup_script = _create_startup_script(variant, worktree_path, auto_execute)
    script_path = worktree_path / ".claude_startup.sh"
    script_path.write_text(startup_script)
    script_path.chmod(0o755)

    try:
        # Detect the platform and launch appropriately
        if sys.platform == "linux" or sys.platform.startswith("linux"):
            # Check if we're in WSL
            if "microsoft" in os.uname().release.lower():
                # WSL - use Windows Terminal
                result = _spawn_windows_terminal_wsl(variant, worktree_path, script_path)
            else:
                # Native Linux - use available terminal
                result = _spawn_linux_terminal(variant, worktree_path, script_path)
        elif sys.platform == "darwin":
            # macOS - use Terminal.app or iTerm2
            result = _spawn_macos_terminal(variant, worktree_path, script_path)
        elif sys.platform == "win32":
            # Native Windows - use Windows Terminal
            result = _spawn_windows_terminal_native(variant, worktree_path, script_path)
        else:
            raise OSError(f"Unsupported platform: {sys.platform}")

        logger.info(f"Spawned terminal for variant {variant['id']}")
        return {"tab_id": tab_id, "pid": result.pid if hasattr(result, "pid") else 0, "launch_time": launch_time}

    except Exception as e:
        error_msg = f"Failed to spawn terminal: {str(e)}"
        logger.error(error_msg)
        raise OSError(error_msg)


def _create_startup_script(variant: dict[str, Any], worktree_path: Path, auto_execute: bool) -> str:
    """Create a startup script for the Claude Code session."""
    prompt_file = worktree_path / ".claude_prompt.txt"
    prompt_file.write_text(variant["prompt"])

    script = f"""#!/bin/bash
# Terminal Ideation Startup Script
# Variant: {variant["title"]}
# ID: {variant["id"]}

cd {worktree_path}

echo "========================================="
echo "Terminal Ideation Tool"
echo "Variant: {variant["title"]}"
echo "Approach: {variant["approach"]}"
echo "========================================="
echo ""

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

"""

    if auto_execute:
        # Auto-execute the prompt in Claude Code
        script += f"""
# Auto-execute the variant prompt
echo "Starting Claude Code with auto-execution..."
echo ""
claude < {prompt_file}
"""
    else:
        # Just start Claude Code
        script += """
# Start Claude Code
echo "Starting Claude Code..."
echo "To execute the variant, run: claude < .claude_prompt.txt"
echo ""
claude
"""

    return script


def _spawn_windows_terminal_wsl(variant: dict[str, Any], worktree_path: Path, script_path: Path) -> subprocess.Popen:
    """Spawn Windows Terminal from WSL."""
    # Convert WSL path to Windows path
    windows_path = _wsl_path_to_windows(worktree_path)

    # Build Windows Terminal command
    cmd = [
        "wt.exe",
        "new-tab",
        "--title",
        variant["title"],
        "--tabColor",
        variant["color"],
        "--startingDirectory",
        windows_path,
        "wsl.exe",
        "-d",
        "Ubuntu",
        "--",
        "bash",
        str(script_path),
    ]

    logger.debug(f"Spawning Windows Terminal with command: {' '.join(cmd)}")
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _spawn_linux_terminal(variant: dict[str, Any], worktree_path: Path, script_path: Path) -> subprocess.Popen:
    """Spawn a terminal on native Linux."""
    # Try different terminal emulators
    terminals = [
        [
            "gnome-terminal",
            "--tab",
            "--title",
            variant["title"],
            "--working-directory",
            str(worktree_path),
            "--",
            "bash",
            str(script_path),
        ],
        ["konsole", "--new-tab", "--workdir", str(worktree_path), "-e", f"bash {script_path}"],
        ["xterm", "-T", variant["title"], "-e", f"cd {worktree_path} && bash {script_path}"],
    ]

    for terminal_cmd in terminals:
        try:
            return subprocess.Popen(terminal_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            continue

    raise OSError("No suitable terminal emulator found")


def _spawn_macos_terminal(variant: dict[str, Any], worktree_path: Path, script_path: Path) -> subprocess.Popen:
    """Spawn Terminal.app on macOS."""
    # Use AppleScript to create a new tab in Terminal.app
    applescript = f"""
    tell application "Terminal"
        activate
        do script "cd {worktree_path} && bash {script_path}"
        set current settings of selected tab of window 1 to settings set "{variant["title"]}"
    end tell
    """

    cmd = ["osascript", "-e", applescript]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _spawn_windows_terminal_native(variant: dict[str, Any], worktree_path: Path, script_path: Path) -> subprocess.Popen:
    """Spawn Windows Terminal on native Windows."""
    cmd = [
        "wt.exe",
        "new-tab",
        "--title",
        variant["title"],
        "--tabColor",
        variant["color"],
        "--startingDirectory",
        str(worktree_path),
        "cmd.exe",
        "/c",
        f"bash {script_path}",
    ]

    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _wsl_path_to_windows(wsl_path: Path) -> str:
    """Convert a WSL path to a Windows path."""
    try:
        result = subprocess.run(["wslpath", "-w", str(wsl_path)], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # Fallback: assume standard WSL mount
        path_str = str(wsl_path)
        if path_str.startswith("/mnt/"):
            # /mnt/c/... -> C:\...
            parts = path_str[5:].split("/")
            drive = parts[0].upper() + ":"
            return "\\".join([drive] + parts[1:])
        # Home directory or other
        return path_str
