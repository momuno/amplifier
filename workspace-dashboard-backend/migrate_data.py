"""
Migration script to convert existing sessions to new entity model

Run this once to migrate from the old session-only model to the new
Project -> Task -> Session hierarchy.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from entities import TaskStatus
from entities import project_store, task_store, session_store


def load_old_sessions() -> List[Dict[str, Any]]:
    """Load sessions from old format"""
    old_path = Path("./sessions.json")
    if not old_path.exists():
        print("No existing sessions.json found - nothing to migrate")
        return []

    with open(old_path, "r") as f:
        return json.load(f)


def migrate():
    """Migrate old session data to new entity model"""
    print("Starting migration...")

    # Load old sessions
    old_sessions = load_old_sessions()
    if not old_sessions:
        return

    print(f"Found {len(old_sessions)} sessions to migrate")

    # Track mappings
    project_map = {}  # old_project_name -> new_project_id
    task_map = {}  # (project_name, task_name) -> new_task_id

    # Process each old session
    for old_session in old_sessions:
        project_name = old_session.get("project_name", "Unnamed Project")
        task_name = old_session.get("task_name", "Unnamed Task")

        # Create or get project
        if project_name not in project_map:
            # Check if project already exists
            existing_project = project_store.get_by_name(project_name)
            if existing_project:
                project_id = existing_project.id
            else:
                # Create new project
                project = project_store.create(name=project_name, metadata={"migrated": True})
                project_id = project.id
                print(f"  Created project: {project_name} ({project_id})")

            project_map[project_name] = project_id
        else:
            project_id = project_map[project_name]

        # Create or get task
        task_key = (project_name, task_name)
        if task_key not in task_map:
            # Create new task
            task = task_store.create(project_id=project_id, name=task_name)

            # Set task status and other fields from old session
            task_store.update(
                task.id,
                {
                    "status": old_session.get("status", TaskStatus.IDLE),
                    "last_accomplishment": old_session.get("last_accomplishment"),
                    "next_action": old_session.get("next_action"),
                },
            )

            task_id = task.id
            task_map[task_key] = task_id
            print(f"    Created task: {task_name} ({task_id})")
        else:
            task_id = task_map[task_key]

        # Create session (work session)
        session = session_store.create(
            task_id=task_id,
            metadata={
                "migrated": True,
                "old_session_id": old_session.get("id"),
                "old_metadata": old_session.get("metadata", {}),
            },
        )

        # Update session with old data
        updates = {}
        if "created_at" in old_session:
            updates["started_at"] = old_session["created_at"]
        if "outputs" in old_session:
            updates["outputs"] = old_session["outputs"]

        if updates:
            session_store.update(session.id, updates)

        print(f"      Created session: {session.id}")

    # Create migration record
    migration_record = {
        "migrated_at": datetime.utcnow().isoformat(),
        "sessions_migrated": len(old_sessions),
        "projects_created": len(project_map),
        "tasks_created": len(task_map),
        "project_map": project_map,
        "task_map": {f"{k[0]}::{k[1]}": v for k, v in task_map.items()},
    }

    with open("./data/migration.json", "w") as f:
        json.dump(migration_record, f, indent=2)

    # Backup old sessions file
    old_path = Path("./sessions.json")
    if old_path.exists():
        backup_path = Path("./sessions.json.backup")
        old_path.rename(backup_path)
        print(f"\nBacked up old sessions to: {backup_path}")

    print("\nMigration completed successfully!")
    print(f"  Projects: {len(project_map)}")
    print(f"  Tasks: {len(task_map)}")
    print(f"  Sessions: {len(old_sessions)}")


if __name__ == "__main__":
    migrate()
