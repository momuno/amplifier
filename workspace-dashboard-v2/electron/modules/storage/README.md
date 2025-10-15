# Storage Module

Self-contained SQLite storage module for Workspace Dashboard V2.

## Purpose

Provides persistent storage for workspaces, projects, and tasks using SQLite database.

## Contract

### Inputs
- Database file path (string)
- CRUD operation requests for workspaces, projects, and tasks

### Outputs
- Typed domain objects (Workspace, Project, Task)
- Success/error responses

### Side Effects
- Creates and manages SQLite database file
- Performs file I/O operations for persistence

## Public Interface

```typescript
class StorageModule {
  constructor(dbPath: string)
  async initialize(): Promise<void>

  // Workspace operations
  async getWorkspaces(): Promise<Workspace[]>
  async createWorkspace(data: CreateWorkspaceDto): Promise<Workspace>
  async updateWorkspace(id: string, data: UpdateWorkspaceDto): Promise<Workspace>
  async deleteWorkspace(id: string): Promise<boolean>

  // Project operations
  async getProjects(workspaceId: string): Promise<Project[]>
  async createProject(data: CreateProjectDto): Promise<Project>
  async updateProject(id: string, data: UpdateProjectDto): Promise<Project>
  async deleteProject(id: string): Promise<boolean>

  // Task operations
  async getTasks(projectId: string): Promise<Task[]>
  async createTask(data: CreateTaskDto): Promise<Task>
  async updateTask(id: string, data: UpdateTaskDto): Promise<Task>
  async deleteTask(id: string): Promise<boolean>

  close(): void
}
```

## Dependencies
- better-sqlite3: SQLite database driver
- crypto: UUID generation

## Testing
Run tests with: `npm test -- storage`