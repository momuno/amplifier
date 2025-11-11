# doc-studio Implementation Plan

**Phased approach to building the AI-amplified documentation workspace**

---

## Overview

This document outlines the step-by-step implementation plan for doc-studio, broken into 5 phases. Each phase delivers working functionality that can be tested and validated before moving to the next.

---

## Phase 1: Foundation (Core Infrastructure)

**Goal**: Get basic backend and frontend running with minimal functionality

### Backend Tasks

- [ ] **1.1** Create project structure
  - Create `scenarios/doc_studio/` directory
  - Set up `doc_studio/` Python package
  - Create subdirectories: `api/`, `services/`, `models/`, `utils/`

- [ ] **1.2** Set up `pyproject.toml`
  ```toml
  [project]
  name = "doc-studio"
  version = "0.1.0"
  dependencies = [
      "fastapi",
      "uvicorn",
      "pydantic",
      "anthropic",
      "python-multipart",
  ]
  ```

- [ ] **1.3** Create basic FastAPI server (`server.py`)
  - Initialize FastAPI app
  - Configure CORS for local development
  - Add health check endpoint: `GET /health`
  - Test: `uvicorn doc_studio.server:app --reload`

- [ ] **1.4** Create Pydantic models (`models/state.py`)
  - `TemplateSection`
  - `Template`
  - `FileNode`
  - `GenerationJob`
  - `AppState`

- [ ] **1.5** Create basic REST routes (`api/routes.py`)
  - `GET /api/health` - Health check
  - `GET /api/state` - Get app state (mock data for now)
  - Test with curl/Postman

### Frontend Tasks

- [ ] **1.6** Create React + TypeScript project
  ```bash
  cd scenarios/doc_studio
  npm create vite@latest frontend -- --template react-ts
  cd frontend && npm install
  ```

- [ ] **1.7** Set up project structure
  - Create directories: `components/`, `hooks/`, `services/`, `types/`
  - Configure Vite proxy to backend (`vite.config.ts`)

- [ ] **1.8** Create basic layout components
  - `AppLayout.tsx` - Three-column layout (sidebar, main, chat)
  - `Sidebar.tsx` - Placeholder for file tree
  - `MainContent.tsx` - Placeholder for template editor
  - Test: `npm run dev`

- [ ] **1.9** Create API client (`services/api.ts`)
  - Axios or fetch wrapper
  - Type-safe API calls
  - Test health check endpoint

### Success Criteria
- ✅ Backend server runs on http://localhost:8000
- ✅ Frontend dev server runs on http://localhost:5173
- ✅ Frontend can call backend health check
- ✅ Basic layout renders

---

## Phase 2: Core Features (Template & File Management)

**Goal**: Template editor and file tree with drag-and-drop

### Backend Tasks

- [ ] **2.1** Implement template service (`services/template_service.py`)
  - Load templates from `.doc-evergreen/templates/`
  - Fall back to doc-evergreen built-in templates
  - CRUD operations on templates
  - Section-to-source file mapping

- [ ] **2.2** Implement file tree service (`utils/file_tree.py`)
  - Scan repository directory structure
  - Generate `FileNode` tree
  - Mark files that are included in template
  - Respect `.gitignore`

- [ ] **2.3** Add template endpoints (`api/routes.py`)
  - `GET /api/templates` - List templates
  - `GET /api/templates/{name}` - Get template
  - `PUT /api/templates/{name}` - Update template
  - `POST /api/templates/{name}/sections/{section_id}/sources` - Add source
  - `DELETE /api/templates/{name}/sections/{section_id}/sources/{path}` - Remove source

- [ ] **2.4** Add file tree endpoint
  - `GET /api/files/tree` - Get repository file tree

### Frontend Tasks

- [ ] **2.5** Create TypeScript types (`types/`)
  - `template.ts` - Template, TemplateSection
  - `fileTree.ts` - FileNode
  - Match backend Pydantic models

- [ ] **2.6** Build TemplateEditor component
  - `TemplateEditor.tsx` - Main editor
  - `SectionList.tsx` - List of template sections
  - `SourceFileMapping.tsx` - Show source files per section
  - Allow removing source files from sections

- [ ] **2.7** Build FileTree component
  - `FileTree.tsx` - Recursive tree
  - `TreeNode.tsx` - Single node (file/folder)
  - Visual indicators for included files (badge/highlight)
  - Collapsible folders

- [ ] **2.8** Implement drag-and-drop
  - `DragDropContext.tsx` - React DnD setup
  - `useDragDrop.ts` hook
  - Drag from file tree → Drop on template section
  - Call API to add source mapping

- [ ] **2.9** State management
  - `useAppState.ts` hook - Global app state
  - Load template on mount
  - Load file tree on mount
  - Update state when files added/removed

### Success Criteria
- ✅ Template editor displays loaded template
- ✅ File tree renders repository structure
- ✅ Drag file from tree to section adds it
- ✅ Visual indicator shows which files are included
- ✅ Remove button deletes source from section

---

## Phase 3: Real-Time Progress (SSE Streaming)

**Goal**: Live updates during generation process

### Backend Tasks

- [ ] **3.1** Implement SSE manager (`api/sse.py`)
  - `SSEManager` class for connection management
  - `add_connection()`, `remove_connection()`, `emit()`
  - Client disconnect handling

- [ ] **3.2** Create SSE endpoints
  - `GET /api/events/progress` - Generation progress stream
  - `GET /api/events/discovery` - Discovery reasoning stream
  - Test with curl: `curl -N http://localhost:8000/api/events/progress`

- [ ] **3.3** Create event models (`models/events.py`)
  - `ProgressEvent` - Generation progress
  - `DiscoveryEvent` - LLM reasoning
  - `ChatEvent` - AI responses
  - `AssistantActionEvent` - AI actions

- [ ] **3.4** Implement generation service (`services/generation_service.py`)
  - Wrap doc-evergreen's `DocumentGenerator`
  - Start generation job (async)
  - Emit progress events via SSE
  - Track job status
  - Store generated document

- [ ] **3.5** Implement discovery service (`services/discovery_service.py`)
  - Wrap doc-evergreen's `discover_files()`
  - Stream LLM reasoning via SSE
  - Emit discovery events

- [ ] **3.6** Add generation endpoints
  - `POST /api/generate` - Start generation
  - `GET /api/generate/{job_id}/status` - Check status
  - `GET /api/generated/{doc_id}` - Get generated doc

### Frontend Tasks

- [ ] **3.7** Create SSE hook (`hooks/useSSE.ts`)
  - Connect to SSE endpoints
  - Handle reconnection
  - Parse events
  - Return event stream

- [ ] **3.8** Build ProgressMonitor component
  - `ProgressMonitor.tsx` - Main progress UI
  - `StageProgress.tsx` - Progress bar per stage
  - `LLMReasoning.tsx` - Stream discovery reasoning
  - Show real-time updates from SSE

- [ ] **3.9** Integrate with generation flow
  - "Generate" button starts generation
  - ProgressMonitor appears and streams events
  - Show completion status
  - Load generated document when done

### Success Criteria
- ✅ Click "Generate" starts generation job
- ✅ Progress updates stream in real-time
- ✅ LLM reasoning displays during discovery
- ✅ Generated document loads when complete
- ✅ SSE reconnects if connection drops

---

## Phase 4: AI Chat Interface (Natural Language Control)

**Goal**: AI assistant that can control all app features

### Backend Tasks

- [ ] **4.1** Implement AI assistant service (`services/ai_assistant.py`)
  - Initialize Anthropic client
  - `handle_message()` - Process chat messages
  - `_build_context()` - Serialize app state for Claude
  - `_get_tool_definitions()` - Define available tools
  - `_execute_tool()` - Route tool calls to services

- [ ] **4.2** Define AI tools
  - `update_template_section` - Update template content
  - `add_source_file_to_section` - Add file to section
  - `remove_source_file_from_section` - Remove file
  - `start_generation` - Trigger generation
  - `search_files_by_pattern` - Find files by glob

- [ ] **4.3** Add chat endpoint
  - `POST /api/chat` - Send message to AI
  - Response streams via existing SSE (`/api/events/chat`)
  - Emit `assistant_action` events when AI uses tools

- [ ] **4.4** Create chat SSE endpoint
  - `GET /api/events/chat` - Stream AI responses
  - `GET /api/events/actions` - Stream AI actions

### Frontend Tasks

- [ ] **4.5** Create chat hook (`hooks/useChat.ts`)
  - Connect to chat SSE endpoint
  - `sendMessage()` function
  - Handle streaming responses
  - Track connection status

- [ ] **4.6** Build ChatPanel component
  - `ChatPanel.tsx` - Resizable chat panel
  - `MessageList.tsx` - Scrollable message list
  - `ChatInput.tsx` - Text input with send button
  - `AssistantActions.tsx` - Visual feedback for AI actions
  - Suggested command buttons

- [ ] **4.7** Create chat types (`types/chat.ts`)
  - `ChatMessage` - User/assistant/system messages
  - `AssistantAction` - AI action events

- [ ] **4.8** Integrate with app state
  - AI actions update UI immediately
  - Visual feedback when AI adds/removes files
  - Highlight affected sections/files
  - Show toast notifications for AI actions

- [ ] **4.9** Add suggested commands
  - "Add all Python files from amplifier/"
  - "Generate documentation now"
  - "Show which files are included"
  - "Remove redundant sources"

### Success Criteria
- ✅ Chat panel displays and connects to AI
- ✅ Send message gets streaming response
- ✅ AI can add files to template via natural language
- ✅ AI can start generation via chat command
- ✅ Visual feedback shows what AI changed
- ✅ UI updates immediately when AI acts

---

## Phase 5: Document Preview & Polish

**Goal**: View generated docs with source attribution

### Backend Tasks

- [ ] **5.1** Enhance generated document model
  - Track source attribution per section
  - Map generated content to source files
  - Generate source links

- [ ] **5.2** Add source attribution endpoint
  - `GET /api/generated/{doc_id}/sources` - Get source mapping

### Frontend Tasks

- [ ] **5.3** Build DocumentPreview component
  - `DocumentPreview.tsx` - Preview pane
  - `MarkdownRenderer.tsx` - Render markdown with syntax highlighting
  - `SourceAttribution.tsx` - Show source files per section
  - Click source link → highlight in file tree

- [ ] **5.4** Add visual indicators to file tree
  - Badge showing number of times file is used
  - Different colors for used vs unused files
  - Tooltip showing which sections use this file

- [ ] **5.5** Polish UI
  - Add loading states
  - Error handling and user feedback
  - Keyboard shortcuts
  - Responsive design
  - Dark mode (optional)

- [ ] **5.6** Add template text editor
  - Syntax highlighting for markdown
  - Auto-save
  - Monaco Editor or CodeMirror integration

### Success Criteria
- ✅ Generated document displays in preview pane
- ✅ Source links navigate to file tree
- ✅ File tree shows usage badges
- ✅ UI is polished and responsive
- ✅ Template editor has syntax highlighting

---

## Testing Strategy

### Unit Tests
- Backend services (pytest)
- Frontend hooks (Vitest)
- Utility functions

### Integration Tests
- API endpoints (FastAPI TestClient)
- SSE streams
- AI tool execution

### E2E Tests (Manual for MVP)
- Load template
- Add files via drag-and-drop
- Add files via AI chat
- Generate documentation
- View preview with sources

---

## Development Guidelines

### Code Quality
- **Type safety**: Use TypeScript/Pydantic everywhere
- **Error handling**: Graceful degradation
- **Logging**: Debug-level logging for development
- **Comments**: Document non-obvious decisions

### Performance
- **Lazy loading**: Load large file trees incrementally
- **Debouncing**: Template auto-save
- **Caching**: Cache file tree, templates
- **Streaming**: Use SSE for large responses

### User Experience
- **Feedback**: Show loading states, progress bars
- **Errors**: User-friendly error messages
- **Responsiveness**: Smooth animations, instant UI updates
- **Accessibility**: Keyboard navigation, ARIA labels

---

## Deployment

### Development
```bash
# Start backend
cd scenarios/doc_studio
uv run uvicorn doc_studio.server:app --reload

# Start frontend
cd frontend
npm run dev
```

### Production (Single Command)
```bash
# Build and serve
make doc-studio-run
```

This will:
1. Build frontend (`npm run build`)
2. Start backend with static file serving
3. Open browser to http://localhost:8000

---

## Milestones

- **M1**: Phase 1 complete - Basic infrastructure running
- **M2**: Phase 2 complete - Template editor and file tree working
- **M3**: Phase 3 complete - Real-time generation progress
- **M4**: Phase 4 complete - AI chat controls app features
- **M5**: Phase 5 complete - Full product with polish

---

## Next Steps

After Phase 5, consider:
- **User testing**: Get feedback from real users
- **Documentation**: Write comprehensive README
- **Tutorial**: Create step-by-step guide
- **Video demo**: Record walkthrough
- **Blog post**: Share on Amplifier blog

---

This phased approach ensures continuous delivery of value while maintaining development velocity.
