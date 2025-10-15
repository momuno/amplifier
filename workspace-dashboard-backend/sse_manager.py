"""
SSE Manager Module

Handles Server-Sent Events for real-time updates.
Self-contained module for broadcasting events to connected clients.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class EventType(str, Enum):
    """SSE Event types"""

    SESSION_STATUS_CHANGED = "session.status.changed"
    SESSION_TASK_COMPLETED = "session.task.completed"
    SESSION_OUTPUTS_CREATED = "session.outputs.created"
    SESSION_ERROR = "session.error"
    HEARTBEAT = "heartbeat"


@dataclass
class SSEEvent:
    """SSE Event data structure"""

    event: EventType
    data: Dict[str, Any]
    timestamp: str = None
    id: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_sse_format(self) -> str:
        """Convert to SSE wire format"""
        lines = []
        lines.append(f"id: {self.id}")
        lines.append(f"event: {self.event}")
        lines.append(f"data: {json.dumps(asdict(self))}")
        lines.append("")  # Empty line to signal end of event
        return "\n".join(lines) + "\n"


class SSEConnection:
    """Represents a single SSE connection"""

    def __init__(self, connection_id: str, queue_size: int = 100):
        self.id = connection_id
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()

    async def send(self, event: SSEEvent) -> bool:
        """Send event to this connection"""
        try:
            await self.queue.put(event)
            self.last_activity = datetime.utcnow()
            return True
        except asyncio.QueueFull:
            # Drop event if queue is full
            return False

    async def receive(self) -> Optional[SSEEvent]:
        """Receive next event from queue"""
        try:
            event = await self.queue.get()
            return event
        except asyncio.CancelledError:
            return None


class SSEManager:
    """Manages SSE connections and event broadcasting"""

    def __init__(self):
        self.connections: Dict[str, SSEConnection] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._heartbeat_interval = 30  # seconds

    async def start(self):
        """Start the SSE manager"""
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self):
        """Stop the SSE manager"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    async def _heartbeat_loop(self):
        """Send periodic heartbeat events"""
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                await self.broadcast(SSEEvent(event=EventType.HEARTBEAT, data={"time": datetime.utcnow().isoformat()}))
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error but continue
                pass

    def create_connection(self) -> str:
        """Create a new SSE connection"""
        connection_id = str(uuid.uuid4())
        self.connections[connection_id] = SSEConnection(connection_id)
        return connection_id

    def remove_connection(self, connection_id: str) -> bool:
        """Remove an SSE connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            return True
        return False

    async def broadcast(self, event: SSEEvent) -> int:
        """Broadcast event to all connections"""
        sent_count = 0
        for connection in list(self.connections.values()):
            if await connection.send(event):
                sent_count += 1
        return sent_count

    async def send_to_connection(self, connection_id: str, event: SSEEvent) -> bool:
        """Send event to specific connection"""
        connection = self.connections.get(connection_id)
        if connection:
            return await connection.send(event)
        return False

    def get_connection(self, connection_id: str) -> Optional[SSEConnection]:
        """Get a connection by ID"""
        return self.connections.get(connection_id)

    def get_active_connections(self) -> List[str]:
        """Get list of active connection IDs"""
        return list(self.connections.keys())

    async def session_status_changed(self, session_id: str, old_status: str, new_status: str, **kwargs):
        """Broadcast session status change event"""
        event = SSEEvent(
            event=EventType.SESSION_STATUS_CHANGED,
            data={"session_id": session_id, "old_status": old_status, "new_status": new_status, **kwargs},
        )
        await self.broadcast(event)

    async def session_task_completed(self, session_id: str, task_name: str, result: Any = None):
        """Broadcast session task completion event"""
        event = SSEEvent(
            event=EventType.SESSION_TASK_COMPLETED,
            data={"session_id": session_id, "task_name": task_name, "result": result},
        )
        await self.broadcast(event)

    async def session_outputs_created(self, session_id: str, outputs: List[str]):
        """Broadcast session outputs created event"""
        event = SSEEvent(event=EventType.SESSION_OUTPUTS_CREATED, data={"session_id": session_id, "outputs": outputs})
        await self.broadcast(event)

    async def session_error(self, session_id: str, error: str, details: Optional[Dict] = None):
        """Broadcast session error event"""
        event = SSEEvent(
            event=EventType.SESSION_ERROR, data={"session_id": session_id, "error": error, "details": details or {}}
        )
        await self.broadcast(event)
