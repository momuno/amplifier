# Workspace Dashboard V2 - Canvas UI

## Overview

A modern, canvas-based workspace dashboard built with React, TypeScript, and Electron. Features an Azure Portal-style grid system for managing session cards with drag-and-drop functionality.

## Features Implemented

### ✅ Grid-Based Canvas System
- **Snap-to-grid positioning** (50px grid units)
- **Drag and drop** session cards with visual feedback
- **Resizable cards** maintaining grid alignment
- **Multi-size support** (2x2, 3x2, 4x3, etc.)
- **Layout persistence** using Zustand with localStorage

### ✅ Session Card Components
- **Visual states** with color-coding:
  - 🟢 Active (green)
  - 🟡 Idle (yellow)
  - 🟠 Stale (orange)
  - ⚪ Archived (gray)
  - 🔵 Forked (blue)
- **Card information display**:
  - Title, project, state
  - Last activity time
  - Notes preview
  - Branch info (when available)
  - Tags support
- **Quick actions**: Fork, Archive, Open

### ✅ Canvas Controls
- **Zoom in/out** (50% - 200%)
- **Pan navigation** (Shift+drag or middle mouse)
- **Grid toggle** for visibility
- **Reset view** to default position
- **Fullscreen mode**
- **Add new sessions** with automatic placement

### ✅ Minimap Navigation
- **Real-time overview** of all sessions
- **Click to navigate** to specific areas
- **Viewport indicator** showing current view
- **Color-coded session states**

### ✅ State Management (Zustand)
- **Session store**: Manages session data and worktree info
- **Layout store**: Handles card positions and collision detection
- **Canvas store**: Controls zoom, pan, and grid settings
- **Persistent storage**: All settings saved to localStorage

### ✅ IPC Integration
- **Backend communication** ready
- **Event listeners** for session updates
- **Worktree status** monitoring
- **Real-time state changes**

## Usage

### Starting the Application

```bash
# Development mode (browser only)
npm run dev:vite

# Full Electron app (with backend)
npm run dev
```

Visit http://localhost:5173 to see the canvas interface.

### Canvas Interactions

- **Add Session**: Click the "+" button in the controls
- **Move Cards**: Click and drag to reposition
- **Resize Cards**: Drag the resize handle (bottom-right corner)
- **Pan Canvas**: Shift+drag or middle mouse button
- **Zoom**: Ctrl+scroll or use zoom buttons
- **Toggle Grid**: Click grid button in controls
- **Navigate with Minimap**: Click on minimap to jump to location

### Keyboard Shortcuts

- `Shift + Drag`: Pan the canvas
- `Ctrl + Scroll`: Zoom in/out
- `Click`: Select a session card
- `Drag`: Move session cards

## Architecture

### Component Structure

```
src/
├── components/
│   ├── canvas/
│   │   ├── Canvas.tsx          # Main canvas with grid layout
│   │   ├── CanvasControls.tsx  # Zoom, pan, grid controls
│   │   └── CanvasMinimap.tsx   # Overview navigation
│   └── session/
│       └── SessionCard.tsx     # Individual session cards
├── stores/
│   ├── sessionStore.ts         # Session data management
│   ├── layoutStore.ts          # Card positions & collision
│   └── canvasStore.ts          # Canvas settings (zoom, pan)
├── types/
│   └── index.ts                # TypeScript interfaces
└── utils/
    ├── cn.ts                   # Class name utility
    └── ipc.ts                  # IPC communication wrapper
```

### Key Technologies

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Zustand**: State management
- **react-grid-layout**: Grid system
- **Tailwind CSS**: Styling
- **Lucide React**: Icons

## Demo Data

The application creates demo sessions on first load to showcase functionality:
- Active session (green)
- Idle session (yellow)
- Stale session (orange)
- Archived session (gray)

## Next Steps

To fully integrate with the backend:

1. **Connect to Electron IPC**: Wire up the backend modules
2. **Real-time updates**: Implement WebSocket or SSE for live updates
3. **File browser integration**: Open worktrees in system file browser
4. **Git operations**: Fork, branch, commit from cards
5. **Advanced layouts**: Save/load layout presets
6. **Search & filter**: Find sessions quickly
7. **Collaboration**: Share canvas views with team

## Development Notes

- Canvas uses 50px grid units by default
- Cards auto-position to avoid overlaps
- Layout persists across sessions
- Supports both light and dark themes
- Optimized for performance with React.memo

The canvas UI provides an intuitive, visual way to manage multiple work sessions, making it easy to see status at a glance and navigate between different projects and tasks.