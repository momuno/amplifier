# doc-studio Architecture

**An AI-amplified interactive workspace for documentation generation**

---

## Overview

doc-studio is a web application that provides an interactive, visual interface for the doc-evergreen documentation generation tool. It adds:

- **Visual template editing** with section-to-source file mapping
- **Interactive file tree** with drag-and-drop source management
- **Real-time progress monitoring** during LLM-guided discovery and generation
- **AI chat interface** for natural language control of all features
- **Document preview** with source attribution links

## Core Concept

The chat interface isn't just a chatbot—it's a **first-class control mechanism** with full visibility into app state and tool-based actions to manipulate it.

### Three Ways to Control

1. **Manual UI**: Drag-and-drop files, click buttons, edit text
2. **AI Chat**: Natural language commands that execute the same actions
3. **Hybrid**: AI suggests actions, user approves/refines via UI

---

## Directory Structure

```
scenarios/doc_studio/
├── doc_studio/                      # Backend Python package
│   ├── __init__.py
│   ├── server.py                   # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # REST endpoints
│   │   ├── sse.py                 # Server-Sent Events for streaming
│   │   └── websocket.py           # WebSocket for chat (alternative)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── template_service.py    # Template CRUD + validation
│   │   ├── discovery_service.py   # Wraps doc-evergreen discovery
│   │   ├── generation_service.py  # Wraps doc-evergreen generator
│   │   └── ai_assistant.py        # Claude Code SDK integration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── state.py              # App state models (Pydantic)
│   │   └── events.py             # SSE event types
│   └── utils/
│       ├── __init__.py
│       └── file_tree.py          # Repository tree scanning
│
├── frontend/                       # React TypeScript app
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts            # Vite for fast dev server
│   ├── src/
│   │   ├── main.tsx              # Entry point
│   │   ├── App.tsx               # Root component
│   │   ├── components/
│   │   │   ├── TemplateEditor/
│   │   │   │   ├── TemplateEditor.tsx
│   │   │   │   ├── SectionList.tsx
│   │   │   │   └── SourceFileMapping.tsx
│   │   │   ├── FileTree/
│   │   │   │   ├── FileTree.tsx
│   │   │   │   ├── TreeNode.tsx
│   │   │   │   └── DragDropContext.tsx
│   │   │   ├── ProgressMonitor/
│   │   │   │   ├── ProgressMonitor.tsx
│   │   │   │   ├── StageProgress.tsx
│   │   │   │   └── LLMReasoning.tsx
│   │   │   ├── DocumentPreview/
│   │   │   │   ├── DocumentPreview.tsx
│   │   │   │   ├── MarkdownRenderer.tsx
│   │   │   │   └── SourceAttribution.tsx
│   │   │   ├── ChatPanel/
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   └── AssistantActions.tsx
│   │   │   └── Layout/
│   │   │       ├── AppLayout.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── MainContent.tsx
│   │   ├── hooks/
│   │   │   ├── useSSE.ts         # Hook for SSE connections
│   │   │   ├── useChat.ts        # Hook for chat interface
│   │   │   ├── useAppState.ts    # Global state management
│   │   │   └── useDragDrop.ts    # Drag-and-drop logic
│   │   ├── services/
│   │   │   ├── api.ts            # REST API client
│   │   │   └── sse.ts            # SSE client
│   │   ├── types/
│   │   │   ├── template.ts
│   │   │   ├── fileTree.ts
│   │   │   ├── events.ts
│   │   │   └── chat.ts
│   │   └── styles/
│   │       └── global.css
│   └── public/
│       └── index.html
│
├── pyproject.toml                  # Python dependencies
├── ARCHITECTURE.md                 # This file
├── IMPLEMENTATION_PLAN.md          # Phased implementation guide
└── README.md                       # Setup and usage
```

---

## Key Backend Modules

### `server.py` - FastAPI Application

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from doc_studio.api import routes, sse

app = FastAPI(title="doc-studio", version="0.1.0")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(routes.router, prefix="/api")
app.include_router(sse.router, prefix="/api/events")

# Serve frontend static files in production
# app.mount("/", StaticFiles(directory="frontend/dist", html=True))
```

### `api/routes.py` - REST Endpoints

```python
from fastapi import APIRouter, HTTPException
from doc_studio.models.state import Template, AppState
from doc_studio.services import template_service, generation_service

router = APIRouter()

# Template management
@router.get("/templates")
async def list_templates():
    """List available templates"""
    return await template_service.list_templates()

@router.get("/templates/{name}")
async def get_template(name: str):
    """Get template content"""
    return await template_service.get_template(name)

@router.put("/templates/{name}")
async def update_template(name: str, template: Template):
    """Update template"""
    return await template_service.update_template(name, template)

# File tree
@router.get("/files/tree")
async def get_file_tree():
    """Get repository file tree"""
    return await file_tree_service.get_tree()

# Template-source mapping
@router.post("/templates/{name}/sections/{section_id}/sources")
async def add_source_to_section(name: str, section_id: str, file_path: str):
    """Add source file to template section"""
    return await template_service.add_source(name, section_id, file_path)

@router.delete("/templates/{name}/sections/{section_id}/sources/{file_path:path}")
async def remove_source_from_section(name: str, section_id: str, file_path: str):
    """Remove source file from template section"""
    return await template_service.remove_source(name, section_id, file_path)

# Generation
@router.post("/generate")
async def start_generation(template_name: str, output_path: str = None):
    """Start documentation generation"""
    job_id = await generation_service.start_job(template_name, output_path)
    return {"job_id": job_id}

@router.get("/generate/{job_id}/status")
async def get_generation_status(job_id: str):
    """Check generation job status"""
    return await generation_service.get_status(job_id)

@router.get("/generated/{doc_id}")
async def get_generated_document(doc_id: str):
    """Get generated document"""
    return await generation_service.get_document(doc_id)

# App state
@router.get("/state")
async def get_app_state():
    """Get current application state"""
    return await state_service.get_state()

@router.post("/state")
async def update_app_state(state: AppState):
    """Update application state"""
    return await state_service.update_state(state)

# Chat
@router.post("/chat")
async def send_chat_message(message: str):
    """Send chat message to AI assistant (response streams via SSE)"""
    await ai_assistant.handle_message(message)
    return {"status": "streaming"}
```

### `api/sse.py` - Server-Sent Events

```python
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from doc_studio.models.events import ProgressEvent, DiscoveryEvent, ChatEvent
import asyncio

router = APIRouter()

class SSEManager:
    """Manages Server-Sent Event connections"""

    def __init__(self):
        self.connections: dict[str, asyncio.Queue] = {}

    def add_connection(self, client_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.connections[client_id] = queue
        return queue

    def remove_connection(self, client_id: str):
        if client_id in self.connections:
            del self.connections[client_id]

    async def emit(self, event: dict):
        """Broadcast event to all connected clients"""
        event_data = f"data: {json.dumps(event)}\n\n"

        for queue in self.connections.values():
            await queue.put(event_data)

sse_manager = SSEManager()

@router.get("/progress")
async def progress_stream(request: Request):
    """Stream generation progress updates"""
    client_id = str(uuid.uuid4())
    queue = sse_manager.add_connection(client_id)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                event_data = await queue.get()
                yield event_data

        finally:
            sse_manager.remove_connection(client_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.get("/chat")
async def chat_stream(request: Request):
    """Stream AI assistant responses"""
    # Similar to progress_stream but for chat messages
    pass

@router.get("/discovery")
async def discovery_stream(request: Request):
    """Stream LLM discovery reasoning"""
    # Similar to progress_stream but for discovery events
    pass
```

### `services/ai_assistant.py` - AI Integration

```python
from anthropic import Anthropic
from doc_studio.models.state import AppState
import json

class AIAssistant:
    """Claude Code SDK integration for chat interface"""

    def __init__(self, state_manager, event_emitter):
        self.client = Anthropic()  # Uses ANTHROPIC_API_KEY
        self.state = state_manager
        self.events = event_emitter

    async def handle_message(self, user_message: str):
        """Process user message with streaming response"""

        # Build system prompt with current state
        system_prompt = f"""
You are an AI assistant helping users with documentation generation.

Current State:
{json.dumps(self._build_context(), indent=2)}

You can control the application using these tools:
- update_template_section
- add_source_file_to_section
- remove_source_file_from_section
- start_generation
- search_files_by_pattern

Be helpful, concise, and proactive. When users ask to add files,
actually add them using the tools. When they ask to generate docs,
start the generation process.
"""

        # Stream response with tool use
        async with self.client.messages.stream(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=self._get_tool_definitions()
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    # Emit chat event
                    await self.events.emit({
                        "type": "chat",
                        "message": event.delta.text,
                        "is_final": False
                    })

                elif event.type == "tool_use":
                    # Execute tool
                    result = await self._execute_tool(event.name, event.input)

                    # Emit action event
                    await self.events.emit({
                        "type": "assistant_action",
                        "action": event.name,
                        "params": event.input,
                        "result": result,
                        "status": "completed"
                    })

    def _build_context(self) -> dict:
        """Serialize all relevant state for Claude"""
        template = self.state.get_template()

        return {
            "current_template": {
                "name": template.name,
                "sections": [
                    {
                        "id": s.id,
                        "title": s.title,
                        "source_files": s.source_files,
                        "file_count": len(s.source_files)
                    }
                    for s in template.sections
                ]
            },
            "capabilities": [
                "update_template_section",
                "add_source_file_to_section",
                "remove_source_file_from_section",
                "start_generation",
                "search_files_by_pattern"
            ]
        }

    def _get_tool_definitions(self) -> list[dict]:
        """Return Claude-compatible tool definitions"""
        return [
            {
                "name": "add_source_file_to_section",
                "description": "Add a source file to a template section",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "section_id": {"type": "string"},
                        "file_path": {"type": "string"}
                    },
                    "required": ["section_id", "file_path"]
                }
            },
            {
                "name": "start_generation",
                "description": "Start generating documentation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "template_name": {"type": "string"},
                        "output_path": {"type": "string"}
                    },
                    "required": ["template_name"]
                }
            },
            {
                "name": "search_files_by_pattern",
                "description": "Find files matching a glob pattern",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"}
                    },
                    "required": ["pattern"]
                }
            }
            # ... other tools
        ]

    async def _execute_tool(self, tool_name: str, params: dict):
        """Execute a tool and return result"""
        if tool_name == "add_source_file_to_section":
            return await self._tool_add_source_file(**params)
        elif tool_name == "start_generation":
            return await self._tool_start_generation(**params)
        # ... handle other tools

    async def _tool_add_source_file(self, section_id: str, file_path: str):
        """Tool: Add source file to template section"""
        await self.state.add_source_mapping(section_id, file_path)
        return {"status": "added", "section_id": section_id, "file": file_path}

    async def _tool_start_generation(self, template_name: str, output_path: str = None):
        """Tool: Start documentation generation"""
        job_id = await generation_service.start_job(template_name, output_path)
        return {"status": "started", "job_id": job_id}
```

---

## Key Frontend Components

### `App.tsx` - Root Component

```typescript
import { useAppState } from './hooks/useAppState';
import { useChat } from './hooks/useChat';
import { useSSE } from './hooks/useSSE';

function App() {
  const { state, dispatch } = useAppState();
  const { messages, sendMessage, isConnected } = useChat();
  const { events } = useSSE(['/api/events/progress', '/api/events/chat']);

  return (
    <AppLayout>
      <Sidebar>
        <FileTree
          tree={state.fileTree}
          onDragStart={(file) => dispatch({ type: 'START_DRAG', file })}
        />
      </Sidebar>

      <MainContent>
        <TemplateEditor
          template={state.currentTemplate}
          onUpdate={(template) => dispatch({ type: 'UPDATE_TEMPLATE', template })}
        />

        {state.activeJob && (
          <ProgressMonitor job={state.activeJob} events={events} />
        )}

        {state.generatedDoc && (
          <DocumentPreview doc={state.generatedDoc} />
        )}
      </MainContent>

      <ChatPanel
        messages={messages}
        onSend={sendMessage}
        isConnected={isConnected}
        currentState={state}
      />
    </AppLayout>
  );
}
```

### `hooks/useChat.ts` - Chat Integration

```typescript
import { useState, useEffect, useCallback, useRef } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Connect to SSE endpoint for streaming responses
    const es = new EventSource('/api/events/chat');

    es.onopen = () => setIsConnected(true);
    es.onerror = () => setIsConnected(false);

    es.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);

      setMessages(prev => {
        const lastMsg = prev[prev.length - 1];

        // Append to last assistant message if streaming
        if (lastMsg?.role === 'assistant' && !data.is_final) {
          return [...prev.slice(0, -1), {
            ...lastMsg,
            content: lastMsg.content + data.message
          }];
        }

        // New message
        return [...prev, {
          role: 'assistant',
          content: data.message,
          timestamp: Date.now()
        }];
      });
    });

    eventSourceRef.current = es;
    return () => es.close();
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    // Add user message immediately
    setMessages(prev => [...prev, {
      role: 'user',
      content,
      timestamp: Date.now()
    }]);

    // Send to backend (response streams via SSE)
    await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: content })
    });
  }, []);

  return { messages, sendMessage, isConnected };
}
```

---

## Data Flow

### AI Assistant Action Flow

```
User sends chat message →
  POST /api/chat →
    AIAssistant.handle_message() →
      Claude processes with context + tools →
        Tool called (e.g., add_source_file) →
          State updated →
            SSE emits assistant_action event →
              Frontend shows visual feedback →
                UI updates to reflect change →
                  Assistant response streams via SSE →
                    Frontend displays in chat
```

### Generation Flow

```
User clicks "Generate" (or AI calls tool) →
  POST /api/generate →
    generation_service starts job →
      SSE streams progress events →
        Frontend updates ProgressMonitor →
          Job completes →
            Frontend fetches generated doc →
              DocumentPreview renders with source attribution
```

---

## Integration with doc-evergreen

### Reuse Strategy

doc-studio **wraps** doc-evergreen's core modules rather than duplicating logic:

```python
# services/discovery_service.py
from doc_evergreen.core.discovery import discover_files

class DiscoveryService:
    async def run_discovery(self, workspace: Path, requirements: str):
        # Intercept LLM calls to stream reasoning
        async for event in discover_files(
            workspace=workspace,
            requirements=requirements,
            stream_callback=self._stream_callback
        ):
            yield event

    async def _stream_callback(self, reasoning: str):
        await self.events.emit({
            "type": "discovery",
            "reasoning": reasoning
        })
```

**Key Point**: Minimal changes to doc-evergreen core (add streaming callbacks). All business logic stays in doc-evergreen.

---

## Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation and models
- **Anthropic SDK** - Claude API client
- **Reuse**: doc-evergreen core modules

### Frontend
- **React 18** - Component-based UI
- **TypeScript** - Type safety
- **Vite** - Fast development server
- **Tailwind CSS** - Utility-first styling (optional)

### Real-Time
- **Server-Sent Events (SSE)** - One-way server-to-client streaming
- **WebSocket** - Alternative for bidirectional chat (if needed)

---

## Development Workflow

### Local Development

```bash
# Terminal 1: Backend
cd scenarios/doc_studio
uv sync
uv run uvicorn doc_studio.server:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Access at http://localhost:5173
```

### Production Build

```bash
# Build frontend
cd frontend && npm run build

# FastAPI serves static files
uv run uvicorn doc_studio.server:app

# Access at http://localhost:8000
```

---

## Design Principles

1. **Ruthless Simplicity**: Reuse doc-evergreen core, minimal abstractions
2. **Modular**: Self-contained scenario tool following Amplifier patterns
3. **Visual-First**: Make invisible processes visible (discovery, reasoning)
4. **AI-Amplified**: Chat interface as first-class control mechanism
5. **Progressive**: Build incrementally, enhance iteratively

---

## Example Interactions

### User: "Add all Python files from amplifier/synthesis to the template"

**AI Processing:**
1. Calls `search_files_by_pattern(pattern="amplifier/synthesis/**/*.py")`
2. Gets list of 12 files
3. Determines appropriate section ("Implementation")
4. Calls `add_source_file_to_section()` for each file
5. Emits action events to frontend
6. Responds: "I've added 12 Python files from amplifier/synthesis/ to the Implementation section."

**Frontend Updates:**
- File tree shows visual indicators on added files
- Template editor shows new files in section
- Chat shows assistant response

### User: "Generate documentation now"

**AI Processing:**
1. Calls `start_generation(template_name="current")`
2. Backend starts generation job
3. SSE streams progress events
4. Frontend shows real-time progress
5. Assistant responds: "Generation started. You can monitor progress above."

---

## Security Considerations

- **Local-only**: Designed for single-user local development
- **No authentication**: Not needed for local tools
- **CORS**: Restricted to localhost origins
- **API Key**: Uses ANTHROPIC_API_KEY from environment
- **File Access**: Limited to workspace directory

---

## Future Enhancements

- **Multi-template support**: Work on multiple docs simultaneously
- **Export/Import**: Share template configurations
- **Version control**: Track template changes
- **Collaboration**: Multi-user editing (WebSocket)
- **Plugin system**: Extend with custom tools

---

This architecture provides a solid foundation for building an AI-amplified documentation workspace that makes doc-evergreen's power accessible through an intuitive visual interface.
