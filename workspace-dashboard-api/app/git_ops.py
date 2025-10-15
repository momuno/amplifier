"""
Git operations for workspace management

Handles git repository and worktree operations following the structure:
~/workspaces/
  └── project-name/
      ├── project-name-main/  (main git repo - hidden from UI)
      ├── task-1/             (worktree)
      └── task-2/             (worktree)
"""

import subprocess
from pathlib import Path


class GitOperationError(Exception):
    """Raised when a git operation fails"""

    pass


def sanitize_name(name: str) -> str:
    """
    Sanitize a name for use as directory/branch name
    Converts spaces to hyphens, removes special chars, lowercase
    """
    import re

    # Replace spaces with hyphens
    name = name.replace(" ", "-")
    # Remove special characters except hyphens
    name = re.sub(r"[^a-zA-Z0-9-]", "", name)
    # Convert to lowercase
    name = name.lower()
    # Remove multiple consecutive hyphens
    name = re.sub(r"-+", "-", name)
    # Strip leading/trailing hyphens
    name = name.strip("-")
    return name


def run_git_command(cmd: list[str], cwd: Path) -> str:
    """
    Run a git command and return output
    Raises GitOperationError if command fails
    """
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise GitOperationError(f"Git command failed: {' '.join(cmd)}\n{e.stderr}") from e


def create_project(base_dir: Path, project_name: str, git_remote: str | None = None) -> dict:
    """
    Create a new project structure

    Args:
        base_dir: Base workspace directory (e.g., ~/workspaces/)
        project_name: Name of the project
        git_remote: Optional git remote URL to clone

    Returns:
        dict with project_path and main_repo_path

    Structure created:
        base_dir/
          └── project-name/
              └── project-name-main/  (git repo)
    """
    sanitized_name = sanitize_name(project_name)
    project_path = base_dir / sanitized_name
    main_repo_name = f"{sanitized_name}-main"
    main_repo_path = project_path / main_repo_name

    # Create project directory
    project_path.mkdir(parents=True, exist_ok=True)

    if git_remote:
        # Clone existing repository
        run_git_command(["git", "clone", git_remote, main_repo_name], cwd=project_path)
    else:
        # Initialize new repository
        main_repo_path.mkdir(exist_ok=True)
        run_git_command(["git", "init"], cwd=main_repo_path)

        # Create initial commit
        run_git_command(
            ["git", "commit", "--allow-empty", "-m", "Initial commit"],
            cwd=main_repo_path,
        )

    return {
        "project_path": str(project_path),
        "main_repo_path": str(main_repo_path),
        "git_remote": git_remote,
    }


def create_worktree(main_repo_path: Path, task_name: str, parent_branch: str | None = None) -> dict:
    """
    Create a new worktree for a task

    Args:
        main_repo_path: Path to main repo (e.g., ~/workspaces/project/project-main/)
        task_name: Name of the task
        parent_branch: Optional parent branch to create from (for forks)

    Returns:
        dict with worktree_path and branch_name

    Creates:
        ~/workspaces/project/task-name/  (sibling to main repo)
    """
    sanitized_task = sanitize_name(task_name)
    project_path = main_repo_path.parent
    worktree_path = project_path / sanitized_task
    branch_name = sanitized_task

    # Check if worktree already exists
    if worktree_path.exists():
        raise GitOperationError(f"Worktree already exists: {worktree_path}")

    # Create worktree
    cmd = ["git", "worktree", "add"]

    if parent_branch:
        # Fork from parent branch
        cmd.extend([str(worktree_path), "-b", branch_name, parent_branch])
    else:
        # Create from current HEAD
        cmd.extend([str(worktree_path), "-b", branch_name])

    run_git_command(cmd, cwd=main_repo_path)

    return {"worktree_path": str(worktree_path), "branch_name": branch_name}


def delete_worktree(main_repo_path: Path, worktree_path: Path, branch_name: str):
    """
    Delete a worktree and its branch

    Args:
        main_repo_path: Path to main repo
        worktree_path: Path to worktree to delete
        branch_name: Name of branch to delete
    """
    # Remove worktree
    run_git_command(
        ["git", "worktree", "remove", str(worktree_path), "--force"],
        cwd=main_repo_path,
    )

    # Delete branch
    run_git_command(["git", "branch", "-D", branch_name], cwd=main_repo_path)


def list_worktrees(main_repo_path: Path) -> list[dict]:
    """
    List all worktrees for a project

    Returns:
        List of dicts with worktree_path and branch_name
    """
    output = run_git_command(["git", "worktree", "list", "--porcelain"], cwd=main_repo_path)

    worktrees = []
    current_worktree = {}

    for line in output.split("\n"):
        if line.startswith("worktree "):
            path = line.replace("worktree ", "")
            current_worktree["worktree_path"] = path
        elif line.startswith("branch "):
            branch = line.replace("branch refs/heads/", "")
            current_worktree["branch_name"] = branch
            worktrees.append(current_worktree)
            current_worktree = {}

    # Filter out the main repo worktree (we don't show it in UI)
    main_repo_str = str(main_repo_path)
    worktrees = [w for w in worktrees if w["worktree_path"] != main_repo_str]

    return worktrees


def get_fork_name(parent_task_name: str, existing_forks: list[str]) -> str:
    """
    Generate next fork name using hierarchical numbering

    Args:
        parent_task_name: Base name of parent task
        existing_forks: List of existing fork names

    Returns:
        Next fork name (e.g., "task-fork-1", "task-fork-1.1", etc.)

    Examples:
        parent="task", forks=[] -> "task-fork-1"
        parent="task", forks=["task-fork-1"] -> "task-fork-2"
        parent="task-fork-1", forks=["task-fork-1.1"] -> "task-fork-1.2"
    """
    sanitized_parent = sanitize_name(parent_task_name)

    # Determine fork depth
    if "-fork-" in sanitized_parent:
        # This is already a fork, add sub-level
        base = sanitized_parent
        # Count existing sub-forks
        sub_forks = [f for f in existing_forks if f.startswith(f"{base}.") and f != base]
        next_num = len(sub_forks) + 1
        return f"{base}.{next_num}"
    # First level fork
    # Count existing forks at this level
    fork_prefix = f"{sanitized_parent}-fork-"
    direct_forks = [
        f for f in existing_forks if f.startswith(fork_prefix) and "." not in f.replace(fork_prefix, "")
    ]
    next_num = len(direct_forks) + 1
    return f"{sanitized_parent}-fork-{next_num}"
