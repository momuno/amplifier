# Workspace Dashboard V2 - Design Specification

## Executive Summary

The Workspace Dashboard is a **mental context management system** designed to help developers manage multiple parallel Claude Code sessions without cognitive overload. It provides a visual, spatially-organized canvas where users can track, organize, and quickly context-switch between numerous concurrent development tasks.

## Problem Statement

Managing multiple Claude Code sessions across different terminals and git worktrees creates overwhelming context-switching costs, especially after breaks. Users lose track of:
- What each session was working on
- Which sessions need attention
- What was produced/created
- Their own thoughts and next steps
- Relationships between related work

## Solution Vision

A desktop application providing a grid-based canvas dashboard where each Claude session appears as a card. Users can spatially organize their work, leave notes for themselves, quickly see session states, and fork sessions to explore parallel solutions—all while maintaining perfect isolation through git worktrees.

## Core Design Principles

### 1. Context Recovery First
Every interface element helps answer: "What was I doing here?" Visual states, personal notes, and clear naming enable instant context recovery.

### 2. Spatial Stability
Users control card placement on a grid. New sessions don't disturb existing layouts. Your mental map remains stable.

### 3. Exploration-Friendly
Easy forking for parallel exploration. Simple disposal of unsuccessful attempts. No penalty for experimentation.

### 4. Reality-Based
Shows actual files in worktrees, real git branches, true session states—not assumptions or abstractions.

### 5. Progressive Disclosure
- **Glance**: See all states at once
- **Inspect**: Click for details
- **Dive in**: View files, full context

## User Personas

### Primary: Solo Developer
- Managing 5-20 concurrent Claude sessions
- Working across multiple projects simultaneously
- Needs quick context recovery (especially Monday mornings)
- Values experimentation and parallel exploration
- Wants to reduce cognitive load of context switching

## System Architecture

### Data Model

```
Workspace
  └── Projects (abstract organizational units)
        ├── id: unique identifier
        ├── name: user-friendly project name
        ├── description: optional notes
        ├── created_date: timestamp
        ├── modified_date: timestamp
        └── Tasks (concrete work items)
              ├── id: unique identifier
              ├── project_id: parent project
              ├── name: user-friendly task name
              ├── state: PLANNING|WORKING|NEEDS_INPUT|REVIEW_READY|PAUSED|COMPLETED
              ├── notes: personal markdown notes
              ├── worktree_path: absolute path to git worktree
              ├── branch: git branch name
              ├── parent_task_id: if forked from another task
              ├── conversation_id: Claude conversation identifier
              ├── created_date: timestamp
              ├── modified_date: timestamp
              ├── last_activity: timestamp
              └── position: {x, y, width, height} on canvas grid
```

### Technical Architecture

#### Core Technologies (Current Implementation)
- **Frontend**: React 18 + Vite (fast dev server with HMR)
- **Grid System**: react-grid-layout (Azure Portal-style draggable grid)
- **Backend API**: FastAPI (Python, async endpoints)
- **Storage**: Local JSON files (designed for future database migration)
- **Icons**: react-icons (Feather icon set)
- **Styling**: Pure CSS with dark theme and glassmorphism
- **Development**: Hot module replacement, concurrent dev servers

#### Current Architecture (V2 Implementation)
- **Web-based dashboard** (accessible via browser at localhost:5173)
- **REST API backend** on port 8000 with CORS enabled
- **Stateless frontend** - all data loaded from API on mount
- **Real-time updates** via API calls (no websockets in MVP)
- **Grid persistence** - layouts saved to backend JSON storage

#### Current API Endpoints

**Session Management:**
- `GET /api/sessions` - Get all sessions
- `GET /api/sessions/{id}` - Get specific session
- `POST /api/sessions` - Create new session
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session
- `POST /api/sessions/{id}/fork` - Fork session

**Project Management:**
- `GET /api/projects` - Get all unique project names

**Layout Management:**
- `GET /api/layouts` - Get saved layouts
- `PUT /api/layouts` - Save layout configuration

#### Module Structure (Bricks & Studs Philosophy)

Each module is self-contained with clear contracts:

1. **session-manager**
   - Purpose: Manage Claude session lifecycle
   - Contract: Create, update, archive sessions
   - Dependencies: None

2. **worktree-controller**
   - Purpose: Git worktree operations
   - Contract: Create, list, delete worktrees
   - Dependencies: Git

3. **state-detector**
   - Purpose: Monitor and detect session states
   - Contract: Parse Claude output, return state enum
   - Dependencies: File system watcher

4. **file-browser**
   - Purpose: Navigate and preview worktree contents
   - Contract: List files, read content, detect changes
   - Dependencies: File system

5. **notes-store**
   - Purpose: Persist and retrieve personal notes
   - Contract: CRUD operations on notes
   - Dependencies: Storage layer

6. **canvas-renderer**
   - Purpose: Render grid-based dashboard
   - Contract: Display cards, handle interactions
   - Dependencies: UI framework

7. **fork-manager**
   - Purpose: Branch sessions from existing ones
   - Contract: Copy conversation, create new worktree
   - Dependencies: worktree-controller, session-manager

## Core Features

### 1. Grid-Based Canvas Dashboard

#### Layout System
- **Snap-to-grid positioning** (like Azure Portal)
- **Fixed grid units** (e.g., 50x50 pixel units)
- **User-controlled placement** - manual positioning only
- **Persistent layouts** - saves position between sessions
- **Multi-monitor support** - expandable across displays

#### Card Sizes (Grid-Aligned)
- **Small**: 2x2 units (minimal status view)
- **Medium**: 3x2 or 2x3 units (standard view)
- **Large**: 4x3 or 3x4 units (detailed with notes)
- **Wide**: 6x2 units (horizontal timeline)
- **Tall**: 2x6 units (vertical task list)
- **Custom**: User-resizable maintaining grid alignment

#### Visual Organization
- **Color-coded zones** for projects or priorities
- **Swimlanes** for workflow stages
- **Visual connectors** showing fork relationships (optional)
- **Background regions** with labels

### 2. Session State Management

#### States (Action-Oriented)
- 🔴 **NEEDS INPUT** - Claude is blocked, requires response
- 🟡 **REVIEW READY** - Work complete, awaiting review
- 🟢 **WORKING** - Active progress, no action needed
- ⏸️ **PAUSED** - Idle but incomplete (TODOs remain)
- ✅ **COMPLETED** - Finished and reviewed
- 📋 **PLANNING** - Initial setup phase

#### State Detection Methods
- Monitor `.claude/` directory changes
- Parse Claude's last output for questions
- Check for TODO list modifications
- Detect git activity in worktree
- Timeout-based pause detection

### 3. Personal Notes System

#### Features
- **Markdown support** with preview
- **Per-session notes** field
- **Quick inline editing** without opening session
- **Template snippets** (next steps, blockers, ideas)
- **Search across all notes**
- **Note history/versioning** (future)

### 4. File Browser & Viewer

#### File Navigation
- **Tree view** of worktree contents
- **Recently modified indicators** (highlight changed files)
- **File type icons** and syntax detection
- **Expand/collapse** directories
- **Quick filter** by name or type

#### File Viewer (Progressive Enhancement)
- **Phase 1**: Modal popup with syntax highlighting (read-only)
- **Phase 2**: Inline editor with save capability
- **Phase 3**: Diff view, image preview, multiple tabs
- **Phase 4**: Full VS Code integration option

### 5. Session Forking

#### Workflow
1. Click "Fork Session" button on card
2. Enter new task name
3. System automatically:
   - Creates new git branch from current
   - Sets up new worktree
   - Copies Claude conversation context
   - Creates new session card
   - Links to parent visually (optional)

#### Fork Management
- **Visual indication** of parent-child relationships
- **Fork history** tracking
- **Bulk operations** on fork families
- **Prune abandoned forks** easily

### 6. Canvas Controls & Navigation

#### Interaction Methods
- **Drag & drop** cards with grid snapping
- **Keyboard navigation** (arrow keys between cards)
- **Pan/zoom** with mouse or trackpad
- **Mini-map** overlay for large canvases
- **Search-to-focus** (type to find and center)

#### Canvas Features
- **Multiple layout profiles** ("Daily", "Review", "Deep Work")
- **Named viewport anchors** (save positions)
- **Grid overlay toggle** (show/hide guides)
- **Density modes** (compact/comfortable/spacious)
- **Export/import** layouts

## User Workflows

### Monday Morning Workflow
1. Open dashboard → See all sessions at a glance
2. Red cards (NEEDS INPUT) immediately visible
3. Read personal notes to recover context
4. Check PAUSED sessions for what was in progress
5. Resume work with full context in < 2 minutes

### New Task Workflow
1. Right-click empty grid space → "New Session"
2. Enter project and task names
3. System creates worktree and branch
4. Card appears at chosen location
5. Click card to open terminal/start work

### Exploration Workflow
1. Working on authentication approach
2. Click "Fork Session" → Try OAuth approach
3. Click "Fork Session" again → Try Magic Link approach
4. Compare results across forks
5. Keep best solution, archive others

### Review Workflow
1. Yellow cards (REVIEW READY) indicate completed work
2. Click card → See file changes
3. Read session notes and outputs
4. Mark as COMPLETED or request changes
5. Optionally merge branch

## Future Enhancements

### Phase 2 (3-6 months)
- Advanced file editing capabilities
- Session templates and presets
- Batch operations (close/archive multiple)
- Keyboard shortcut customization
- Global search across all sessions
- Time-based activity views
- Basic metrics and analytics

### Phase 3 (6-12 months)
- Multi-machine sync via cloud storage
- Team collaboration features
- AI-powered session summaries
- Integration with project management tools (JIRA, Linear)
- Mobile companion app for monitoring
- Session replay and history
- Advanced automation and triggers

### Phase 4 (12+ months)
- Full IDE integration (VS Code, JetBrains)
- Voice commands and control
- ML-based state prediction
- Automated session orchestration
- Template marketplace
- Enterprise features (SSO, audit logs)

## Technical Implementation Plan

### MVP Milestones (Current Status)

#### Milestone 1: Core Infrastructure ✅ COMPLETED
- [x] React + Vite web app scaffold
- [x] Basic grid canvas implementation (react-grid-layout)
- [x] Local storage layer (FastAPI + JSON)
- [ ] Git worktree integration (future)

#### Milestone 2: Session Management ✅ COMPLETED
- [x] Session CRUD operations via API
- [ ] State detection logic (future)
- [x] Project/task hierarchy
- [x] Personal notes system

#### Milestone 3: Canvas UI ✅ COMPLETED
- [x] Draggable cards with grid snap
- [x] Card resize functionality
- [x] Expandable canvas (48 cols x 4800px)
- [x] Layout persistence to backend

#### Milestone 4: Session Features ✅ COMPLETED
- [x] Session cards with state badges
- [x] Project sidebar with filtering
- [x] Session forking with numbering
- [x] New session modal
- [x] Project renaming
- [x] Dark theme UI with glassmorphism

#### Milestone 5: Next Steps (Planned)
- [ ] File browser component
- [ ] Worktree integration
- [ ] State detection from Claude output
- [ ] Search and filtering
- [ ] Git operations

## Success Metrics

### Quantitative
- Support 20+ concurrent sessions without performance degradation
- Context recovery time < 2 minutes
- Zero data loss from crashes
- 60fps canvas interaction
- < 100ms response time for all operations

### Qualitative
- Reduced cognitive load (user feedback)
- Improved task completion rate
- Higher satisfaction with parallel work
- Fewer abandoned sessions
- Better work organization

## Risk Mitigation

### Technical Risks
- **File system permissions**: Request appropriate permissions upfront
- **Git operations failing**: Graceful degradation, clear error messages
- **Performance with many sessions**: Virtual scrolling, lazy loading
- **Data corruption**: Regular backups, atomic operations

### User Experience Risks
- **Overwhelming initial complexity**: Progressive disclosure, guided setup
- **Loss of work**: Auto-save everything, recovery mode
- **Accidental deletions**: Confirmation dialogs, undo system
- **Learning curve**: Interactive tutorial, tooltips

## Storage Schema

### Primary Storage (JSON/SQLite)
```json
{
  "workspace": {
    "version": "1.0.0",
    "created": "2024-01-14T10:00:00Z",
    "modified": "2024-01-14T10:00:00Z"
  },
  "projects": {
    "proj_abc123": {
      "name": "AI Dashboard",
      "description": "Building a new dashboard system",
      "created": "2024-01-14T10:00:00Z",
      "task_ids": ["task_001", "task_002"]
    }
  },
  "tasks": {
    "task_001": {
      "name": "OAuth Integration",
      "project_id": "proj_abc123",
      "state": "WORKING",
      "notes": "Exploring OAuth2 flow with PKCE...",
      "worktree_path": "/Users/dev/projects/dashboard-oauth",
      "branch": "feature/oauth-integration",
      "parent_task_id": null,
      "conversation_id": "claude_conv_xyz",
      "position": {"x": 2, "y": 4, "width": 3, "height": 2},
      "created": "2024-01-14T10:00:00Z",
      "last_activity": "2024-01-14T10:30:00Z"
    }
  },
  "layouts": {
    "default": {
      "name": "Default Layout",
      "zoom": 1.0,
      "viewport": {"x": 0, "y": 0},
      "grid_size": 50
    }
  }
}
```

## Appendix

### State Transition Diagram
```
PLANNING → WORKING → REVIEW_READY → COMPLETED
    ↓         ↓            ↓
    ↓    NEEDS_INPUT       ↓
    ↓         ↓            ↓
    └──── PAUSED ←─────────┘
```

### Grid System Example
```
Grid Units (50x50px each):
┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
│ │ │ │ │ │ │ │ │ │ │ │ │ 12 units tall
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
│ │ │ │ │ │ │ │ │ │ │ │ │
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
20 units wide

Cards snap to grid intersections
Minimum size: 2x2 units (100x100px)
Maximum size: User-defined
```

### Keyboard Shortcuts (Proposed)
- `Ctrl/Cmd + N`: New session
- `Ctrl/Cmd + F`: Search sessions
- `Arrow Keys`: Navigate between cards
- `Enter`: Open selected session
- `Space`: Expand card preview
- `Ctrl/Cmd + D`: Duplicate (fork) session
- `Delete`: Archive session (with confirmation)
- `Ctrl/Cmd + 1-9`: Jump to layout preset

---

*This design specification represents the complete vision for the Workspace Dashboard V2, incorporating all requirements and feedback from the design consultation process.*