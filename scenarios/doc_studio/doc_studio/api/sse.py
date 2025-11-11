"""Server-Sent Events (SSE) management for real-time updates."""

from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict
from typing import Any

from doc_studio.models.events import AssistantActionEvent
from doc_studio.models.events import ChatEvent
from doc_studio.models.events import DiscoveryEvent
from doc_studio.models.events import ErrorEvent
from doc_studio.models.events import EventType
from doc_studio.models.events import ProgressEvent


class SSEManager:
    """Manages SSE connections and event broadcasting."""

    def __init__(self) -> None:
        """Initialize SSE manager."""
        # Connection ID -> queue
        self.connections: dict[str, asyncio.Queue[dict[str, Any]]] = {}
        # Resource ID -> set of connection IDs
        self.subscriptions: dict[str, set[str]] = defaultdict(set)

    async def add_connection(
        self, resource_id: str, user_id: str = "default"
    ) -> tuple[asyncio.Queue[dict[str, Any]], str]:
        """Add a new SSE connection.

        Args:
            resource_id: ID of resource to subscribe to (e.g., "job:123")
            user_id: User identifier

        Returns:
            Tuple of (event queue, connection ID)
        """
        connection_id = str(uuid.uuid4())
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

        self.connections[connection_id] = queue
        self.subscriptions[resource_id].add(connection_id)

        return queue, connection_id

    def remove_connection(self, connection_id: str) -> None:
        """Remove a connection and clean up subscriptions.

        Args:
            connection_id: Connection to remove
        """
        # Remove from connections
        self.connections.pop(connection_id, None)

        # Remove from all subscriptions
        for subscribers in self.subscriptions.values():
            subscribers.discard(connection_id)

    async def send_event(
        self,
        resource_id: str,
        event_type: EventType,
        data: ProgressEvent | DiscoveryEvent | ChatEvent | AssistantActionEvent | ErrorEvent,
    ) -> None:
        """Send an event to all subscribers of a resource.

        Args:
            resource_id: Resource ID to send to
            event_type: Type of event
            data: Event data (Pydantic model)
        """
        event = {"event": event_type.value, "data": data.model_dump()}

        # Send to all connections subscribed to this resource
        subscribers = self.subscriptions.get(resource_id, set())
        for conn_id in subscribers:
            queue = self.connections.get(conn_id)
            if queue:
                await queue.put(event)

    async def send_progress(self, resource_id: str, event: ProgressEvent) -> None:
        """Send a progress event.

        Args:
            resource_id: Resource ID
            event: Progress event
        """
        await self.send_event(resource_id, EventType.PROGRESS, event)

    async def send_discovery(self, resource_id: str, event: DiscoveryEvent) -> None:
        """Send a discovery event.

        Args:
            resource_id: Resource ID
            event: Discovery event
        """
        await self.send_event(resource_id, EventType.DISCOVERY, event)

    async def send_chat(self, resource_id: str, event: ChatEvent) -> None:
        """Send a chat event.

        Args:
            resource_id: Resource ID
            event: Chat event
        """
        await self.send_event(resource_id, EventType.CHAT, event)

    async def send_assistant_action(self, resource_id: str, event: AssistantActionEvent) -> None:
        """Send an assistant action event.

        Args:
            resource_id: Resource ID
            event: Assistant action event
        """
        await self.send_event(resource_id, EventType.ASSISTANT_ACTION, event)

    async def send_error(self, resource_id: str, event: ErrorEvent) -> None:
        """Send an error event.

        Args:
            resource_id: Resource ID
            event: Error event
        """
        await self.send_event(resource_id, EventType.ERROR, event)


# Global SSE manager instance
sse_manager = SSEManager()
