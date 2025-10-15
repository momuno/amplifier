# Workspace Dashboard V2

A modern Electron + React + TypeScript application for managing workspaces, projects, and tasks with local SQLite persistence.

## Architecture

Built following the "bricks and studs" philosophy - modular, self-contained components with clear interfaces.

### Project Structure

```
workspace-dashboard-v2/
├── electron/               # Main process
│   ├── main.ts            # Electron entry point
│   ├── preload.ts         # Context bridge for IPC
│   └── modules/
│       └── storage/       # SQLite storage module (self-contained)
│           ├── README.md  # Module contract
│           ├── index.ts   # Implementation
│           └── storage.test.ts
├── src/                   # React frontend (renderer process)
│   ├── main.tsx
│   ├── App.tsx
│   ├── App.css
│   └── index.css
├── shared/               # Shared contracts
│   └── contracts/
│       └── types.ts     # TypeScript interfaces
└── package.json         # Dependencies and scripts
```

## Features

- **Workspace Management**: Create and manage multiple workspaces
- **Project Tracking**: Organize projects within workspaces
- **Task Management**: Track tasks with status, priority, and checklists
- **Local Persistence**: SQLite database for reliable local storage
- **Type Safety**: Full TypeScript support throughout
- **Dark Mode Support**: Automatic theme based on system preferences

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

### Development

Run the application in development mode with hot reload:

```bash
npm run dev
```

This will:
1. Start Vite dev server for React frontend
2. Launch Electron with the development build
3. Open DevTools automatically

### Building

Build for production:

```bash
npm run build
```

Create distributable packages:

```bash
npm run make
```

### Testing

Run all tests:

```bash
npm test
```

Run tests with UI:

```bash
npm run test:ui
```

Type checking:

```bash
npm run typecheck
```

Linting:

```bash
npm run lint
```

## Storage Module

The storage module is a self-contained SQLite implementation following the modular design philosophy:

- **Location**: `electron/modules/storage/`
- **Database Path**: `~/AppData/workspace.db` (or OS equivalent)
- **Tables**: workspaces, projects, tasks
- **Features**:
  - CRUD operations for all entities
  - Cascade deletion
  - JSON field support for metadata
  - Type-safe interfaces

### API

The storage module exposes methods through Electron IPC:

```typescript
// Frontend usage
const workspaces = await window.electronAPI.storage.getWorkspaces();
const workspace = await window.electronAPI.storage.createWorkspace({
  name: 'My Workspace',
  isActive: true
});
```

## Data Model

### Workspace
- `id`: UUID
- `name`: String
- `description`: Optional string
- `color`: Optional hex color
- `icon`: Optional icon identifier
- `isActive`: Boolean
- `createdAt`: Timestamp
- `updatedAt`: Timestamp

### Project
- `id`: UUID
- `workspaceId`: Foreign key
- `name`: String
- `description`: Optional string
- `status`: Enum (planned, in_progress, on_hold, completed, cancelled)
- `priority`: Enum (low, medium, high, urgent)
- `dueDate`: Optional date
- `tags`: String array
- `metadata`: JSON object

### Task
- `id`: UUID
- `projectId`: Foreign key
- `title`: String
- `description`: Optional string
- `status`: Enum (todo, in_progress, in_review, done, blocked)
- `priority`: Enum (low, medium, high, urgent)
- `assignee`: Optional string
- `dueDate`: Optional date
- `completedAt`: Optional timestamp
- `tags`: String array
- `checklist`: Array of checklist items
- `metadata`: JSON object

## Technology Stack

- **Electron 28**: Desktop application framework
- **React 18**: UI library
- **TypeScript 5**: Type safety
- **Vite 5**: Build tool and dev server
- **Better-SQLite3**: SQLite database driver
- **Vitest**: Testing framework

## License

MIT