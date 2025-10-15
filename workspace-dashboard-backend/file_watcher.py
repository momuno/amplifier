"""
File Watcher Module

Monitors session output directories for changes.
Self-contained module for file system monitoring with debouncing.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Callable, Optional, Set
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class DebouncedFileHandler(FileSystemEventHandler):
    """File system event handler with debouncing"""

    def __init__(self, callback: Callable, debounce_ms: int = 100):
        self.callback = callback
        self.debounce_ms = debounce_ms
        self.pending_events: Dict[str, asyncio.Task] = {}
        self.loop = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the event loop for async operations"""
        self.loop = loop

    def on_any_event(self, event: FileSystemEvent):
        """Handle any file system event with debouncing"""
        if event.is_directory:
            return

        # Cancel previous pending event for this path
        if event.src_path in self.pending_events:
            self.pending_events[event.src_path].cancel()

        # Schedule new event after debounce period
        if self.loop:
            task = self.loop.create_task(self._debounced_callback(event))
            self.pending_events[event.src_path] = task

    async def _debounced_callback(self, event: FileSystemEvent):
        """Execute callback after debounce period"""
        await asyncio.sleep(self.debounce_ms / 1000)
        self.pending_events.pop(event.src_path, None)

        # Call the callback with event info
        if asyncio.iscoroutinefunction(self.callback):
            await self.callback(event)
        else:
            self.callback(event)


class FileWatcher:
    """Monitors directories for file changes"""

    def __init__(self, base_dir: str = "./session_outputs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.observers: Dict[str, Observer] = {}
        self.session_handlers: Dict[str, DebouncedFileHandler] = {}
        self.session_outputs: Dict[str, Set[str]] = {}

    def watch_session(self, session_id: str, callback: Optional[Callable] = None) -> Path:
        """Start watching a session's output directory"""
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Stop existing observer if any
        self.stop_watching(session_id)

        # Create debounced handler
        handler = DebouncedFileHandler(callback or self._default_callback, debounce_ms=100)
        handler.set_loop(asyncio.get_event_loop())

        # Start observer
        observer = Observer()
        observer.schedule(handler, str(session_dir), recursive=True)
        observer.start()

        self.observers[session_id] = observer
        self.session_handlers[session_id] = handler
        self.session_outputs[session_id] = set()

        # Initial scan of existing files
        self._scan_directory(session_id)

        return session_dir

    def stop_watching(self, session_id: str) -> bool:
        """Stop watching a session's directory"""
        if session_id in self.observers:
            observer = self.observers[session_id]
            observer.stop()
            observer.join(timeout=1)
            del self.observers[session_id]

            if session_id in self.session_handlers:
                del self.session_handlers[session_id]
            if session_id in self.session_outputs:
                del self.session_outputs[session_id]

            return True
        return False

    def stop_all(self):
        """Stop all file watchers"""
        for session_id in list(self.observers.keys()):
            self.stop_watching(session_id)

    def _scan_directory(self, session_id: str) -> List[str]:
        """Scan session directory for existing files"""
        session_dir = self.base_dir / session_id
        if not session_dir.exists():
            return []

        files = []
        for path in session_dir.rglob("*"):
            if path.is_file():
                relative_path = str(path.relative_to(session_dir))
                files.append(relative_path)
                self.session_outputs[session_id].add(relative_path)

        return files

    def get_session_outputs(self, session_id: str) -> List[str]:
        """Get list of output files for a session"""
        if session_id not in self.session_outputs:
            return self._scan_directory(session_id)
        return list(self.session_outputs[session_id])

    def get_new_outputs(self, session_id: str, since: datetime) -> List[str]:
        """Get files created after a specific time"""
        session_dir = self.base_dir / session_id
        if not session_dir.exists():
            return []

        new_files = []
        for path in session_dir.rglob("*"):
            if path.is_file():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime > since:
                    relative_path = str(path.relative_to(session_dir))
                    new_files.append(relative_path)

        return new_files

    def _default_callback(self, event: FileSystemEvent):
        """Default callback for file events"""
        # Extract session ID from path
        try:
            path = Path(event.src_path)
            session_id = path.relative_to(self.base_dir).parts[0]

            # Track new files
            if event.event_type in ["created", "modified"]:
                relative_path = str(path.relative_to(self.base_dir / session_id))
                if session_id in self.session_outputs:
                    self.session_outputs[session_id].add(relative_path)
        except (ValueError, IndexError):
            pass

    def clear_session_data(self, session_id: str) -> bool:
        """Clear session output directory"""
        session_dir = self.base_dir / session_id
        if session_dir.exists():
            import shutil

            shutil.rmtree(session_dir)
            if session_id in self.session_outputs:
                self.session_outputs[session_id].clear()
            return True
        return False
