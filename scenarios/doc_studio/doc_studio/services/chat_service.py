"""Chat service for AI assistant interactions."""

from __future__ import annotations

import asyncio

from doc_studio.api.sse import sse_manager
from doc_studio.models.events import AssistantAction
from doc_studio.models.events import AssistantActionEvent
from doc_studio.models.events import ChatEvent


class ChatService:
    """Service for AI assistant chat interactions."""

    async def process_message(self, user_id: str, message: str, resource_id: str) -> None:
        """Process a user message and stream responses.

        Args:
            user_id: User identifier
            message: User's message
            resource_id: Resource ID for SSE events (e.g., "chat:user123")
        """
        # Send user message back as confirmation
        await sse_manager.send_chat(
            resource_id,
            ChatEvent(message=f"You: {message}", is_complete=True),
        )

        # Simulate typing delay
        await asyncio.sleep(0.5)

        # Parse message and respond
        message_lower = message.lower()

        if "help" in message_lower or "what can you do" in message_lower:
            response = self._get_help_message()
        elif "add" in message_lower and "file" in message_lower:
            response = "To add files, drag them from the file tree on the left into the template sections. You can also click the '+' button in each section."
        elif "generate" in message_lower or "create" in message_lower:
            response = 'To generate a document, click the "▶ Generate Document" button above the template editor. I\'ll show you real-time progress in the monitor panel.'
        elif "template" in message_lower:
            response = "You're currently working with the 'default' template. It has sections for Introduction, Architecture, Implementation, and Usage. You can add source files to each section by dragging them from the file tree."
        else:
            response = "I'm a simple assistant demo. Try asking 'what can you do?' for available features. Full AI capabilities will be added in a future phase!"

        # Stream response
        await self._stream_response(resource_id, response)

    async def _stream_response(self, resource_id: str, response: str) -> None:
        """Stream a response word by word.

        Args:
            resource_id: Resource ID for SSE events
            response: Response message to stream
        """
        words = response.split()
        accumulated = ""

        for i, word in enumerate(words):
            accumulated += word + (" " if i < len(words) - 1 else "")

            await sse_manager.send_chat(
                resource_id,
                ChatEvent(
                    message=f"Assistant: {accumulated}",
                    is_complete=(i == len(words) - 1),
                ),
            )

            # Simulate typing speed
            await asyncio.sleep(0.05)

    def _get_help_message(self) -> str:
        """Get help message listing capabilities.

        Returns:
            Help message string
        """
        return """I can help you with:

• Managing templates - Add/remove source files
• File organization - Understanding the file tree
• Document generation - Creating documentation
• Progress monitoring - Watching generation in real-time

This is a basic demo. Full AI capabilities (natural language understanding, intelligent suggestions, automated file selection) will be added in future phases with Claude Code SDK integration!"""

    async def notify_action(self, resource_id: str, action: AssistantAction, parameters: dict) -> None:
        """Notify about an assistant action.

        Args:
            resource_id: Resource ID for SSE events
            action: Action being performed
            parameters: Action parameters
        """
        await sse_manager.send_assistant_action(
            resource_id,
            AssistantActionEvent(action=action, parameters=parameters, result={"status": "completed"}),
        )
