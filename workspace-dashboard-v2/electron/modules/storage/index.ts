import Database from 'better-sqlite3';
import { randomUUID } from 'crypto';
import type {
  Workspace,
  Project,
  Task,
  DbWorkspace,
  DbProject,
  DbTask,
  ProjectStatus,
  TaskStatus,
  Priority
} from '../../../shared/contracts/types';

export class StorageModule {
  private db: Database.Database;

  constructor(dbPath: string) {
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
  }

  async initialize(): Promise<void> {
    // Create tables
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS workspaces (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        color TEXT,
        icon TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        due_date TEXT,
        tags TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        assignee TEXT,
        due_date TEXT,
        completed_at TEXT,
        tags TEXT,
        checklist TEXT,
        metadata TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      );

      CREATE INDEX IF NOT EXISTS idx_projects_workspace ON projects(workspace_id);
      CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
      CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    `);
  }

  // Workspace operations
  async getWorkspaces(): Promise<Workspace[]> {
    const stmt = this.db.prepare('SELECT * FROM workspaces ORDER BY created_at DESC');
    const rows = stmt.all() as DbWorkspace[];
    return rows.map(this.mapWorkspace);
  }

  async createWorkspace(data: Omit<Workspace, 'id' | 'createdAt' | 'updatedAt'>): Promise<Workspace> {
    const id = randomUUID();
    const now = new Date().toISOString();

    const stmt = this.db.prepare(`
      INSERT INTO workspaces (id, name, description, color, icon, is_active, created_at, updated_at)
      VALUES (@id, @name, @description, @color, @icon, @is_active, @created_at, @updated_at)
    `);

    stmt.run({
      id,
      name: data.name,
      description: data.description || null,
      color: data.color || null,
      icon: data.icon || null,
      is_active: data.isActive ? 1 : 0,
      created_at: now,
      updated_at: now
    });

    return this.getWorkspace(id)!;
  }

  async updateWorkspace(id: string, data: Partial<Omit<Workspace, 'id' | 'createdAt' | 'updatedAt'>>): Promise<Workspace> {
    const current = this.getWorkspace(id);
    if (!current) {
      throw new Error(`Workspace ${id} not found`);
    }

    const updates: string[] = [];
    const params: any = { id, updated_at: new Date().toISOString() };

    if (data.name !== undefined) {
      updates.push('name = @name');
      params.name = data.name;
    }
    if (data.description !== undefined) {
      updates.push('description = @description');
      params.description = data.description || null;
    }
    if (data.color !== undefined) {
      updates.push('color = @color');
      params.color = data.color || null;
    }
    if (data.icon !== undefined) {
      updates.push('icon = @icon');
      params.icon = data.icon || null;
    }
    if (data.isActive !== undefined) {
      updates.push('is_active = @is_active');
      params.is_active = data.isActive ? 1 : 0;
    }

    if (updates.length > 0) {
      updates.push('updated_at = @updated_at');
      const stmt = this.db.prepare(`UPDATE workspaces SET ${updates.join(', ')} WHERE id = @id`);
      stmt.run(params);
    }

    return this.getWorkspace(id)!;
  }

  async deleteWorkspace(id: string): Promise<boolean> {
    const stmt = this.db.prepare('DELETE FROM workspaces WHERE id = ?');
    const result = stmt.run(id);
    return result.changes > 0;
  }

  // Project operations
  async getProjects(workspaceId: string): Promise<Project[]> {
    const stmt = this.db.prepare('SELECT * FROM projects WHERE workspace_id = ? ORDER BY created_at DESC');
    const rows = stmt.all(workspaceId) as DbProject[];
    return rows.map(this.mapProject);
  }

  async createProject(data: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>): Promise<Project> {
    const id = randomUUID();
    const now = new Date().toISOString();

    const stmt = this.db.prepare(`
      INSERT INTO projects (id, workspace_id, name, description, status, priority, due_date, tags, metadata, created_at, updated_at)
      VALUES (@id, @workspace_id, @name, @description, @status, @priority, @due_date, @tags, @metadata, @created_at, @updated_at)
    `);

    stmt.run({
      id,
      workspace_id: data.workspaceId,
      name: data.name,
      description: data.description || null,
      status: data.status,
      priority: data.priority,
      due_date: data.dueDate ? data.dueDate.toISOString() : null,
      tags: data.tags ? JSON.stringify(data.tags) : null,
      metadata: data.metadata ? JSON.stringify(data.metadata) : null,
      created_at: now,
      updated_at: now
    });

    return this.getProject(id)!;
  }

  async updateProject(id: string, data: Partial<Omit<Project, 'id' | 'createdAt' | 'updatedAt'>>): Promise<Project> {
    const current = this.getProject(id);
    if (!current) {
      throw new Error(`Project ${id} not found`);
    }

    const updates: string[] = [];
    const params: any = { id, updated_at: new Date().toISOString() };

    if (data.name !== undefined) {
      updates.push('name = @name');
      params.name = data.name;
    }
    if (data.description !== undefined) {
      updates.push('description = @description');
      params.description = data.description || null;
    }
    if (data.status !== undefined) {
      updates.push('status = @status');
      params.status = data.status;
    }
    if (data.priority !== undefined) {
      updates.push('priority = @priority');
      params.priority = data.priority;
    }
    if (data.dueDate !== undefined) {
      updates.push('due_date = @due_date');
      params.due_date = data.dueDate ? data.dueDate.toISOString() : null;
    }
    if (data.tags !== undefined) {
      updates.push('tags = @tags');
      params.tags = data.tags ? JSON.stringify(data.tags) : null;
    }
    if (data.metadata !== undefined) {
      updates.push('metadata = @metadata');
      params.metadata = data.metadata ? JSON.stringify(data.metadata) : null;
    }

    if (updates.length > 0) {
      updates.push('updated_at = @updated_at');
      const stmt = this.db.prepare(`UPDATE projects SET ${updates.join(', ')} WHERE id = @id`);
      stmt.run(params);
    }

    return this.getProject(id)!;
  }

  async deleteProject(id: string): Promise<boolean> {
    const stmt = this.db.prepare('DELETE FROM projects WHERE id = ?');
    const result = stmt.run(id);
    return result.changes > 0;
  }

  // Task operations
  async getTasks(projectId: string): Promise<Task[]> {
    const stmt = this.db.prepare('SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at DESC');
    const rows = stmt.all(projectId) as DbTask[];
    return rows.map(this.mapTask);
  }

  async createTask(data: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>): Promise<Task> {
    const id = randomUUID();
    const now = new Date().toISOString();

    const stmt = this.db.prepare(`
      INSERT INTO tasks (id, project_id, title, description, status, priority, assignee, due_date, completed_at, tags, checklist, metadata, created_at, updated_at)
      VALUES (@id, @project_id, @title, @description, @status, @priority, @assignee, @due_date, @completed_at, @tags, @checklist, @metadata, @created_at, @updated_at)
    `);

    stmt.run({
      id,
      project_id: data.projectId,
      title: data.title,
      description: data.description || null,
      status: data.status,
      priority: data.priority,
      assignee: data.assignee || null,
      due_date: data.dueDate ? data.dueDate.toISOString() : null,
      completed_at: data.completedAt ? data.completedAt.toISOString() : null,
      tags: data.tags ? JSON.stringify(data.tags) : null,
      checklist: data.checklist ? JSON.stringify(data.checklist) : null,
      metadata: data.metadata ? JSON.stringify(data.metadata) : null,
      created_at: now,
      updated_at: now
    });

    return this.getTask(id)!;
  }

  async updateTask(id: string, data: Partial<Omit<Task, 'id' | 'createdAt' | 'updatedAt'>>): Promise<Task> {
    const current = this.getTask(id);
    if (!current) {
      throw new Error(`Task ${id} not found`);
    }

    const updates: string[] = [];
    const params: any = { id, updated_at: new Date().toISOString() };

    if (data.title !== undefined) {
      updates.push('title = @title');
      params.title = data.title;
    }
    if (data.description !== undefined) {
      updates.push('description = @description');
      params.description = data.description || null;
    }
    if (data.status !== undefined) {
      updates.push('status = @status');
      params.status = data.status;
    }
    if (data.priority !== undefined) {
      updates.push('priority = @priority');
      params.priority = data.priority;
    }
    if (data.assignee !== undefined) {
      updates.push('assignee = @assignee');
      params.assignee = data.assignee || null;
    }
    if (data.dueDate !== undefined) {
      updates.push('due_date = @due_date');
      params.due_date = data.dueDate ? data.dueDate.toISOString() : null;
    }
    if (data.completedAt !== undefined) {
      updates.push('completed_at = @completed_at');
      params.completed_at = data.completedAt ? data.completedAt.toISOString() : null;
    }
    if (data.tags !== undefined) {
      updates.push('tags = @tags');
      params.tags = data.tags ? JSON.stringify(data.tags) : null;
    }
    if (data.checklist !== undefined) {
      updates.push('checklist = @checklist');
      params.checklist = data.checklist ? JSON.stringify(data.checklist) : null;
    }
    if (data.metadata !== undefined) {
      updates.push('metadata = @metadata');
      params.metadata = data.metadata ? JSON.stringify(data.metadata) : null;
    }

    if (updates.length > 0) {
      updates.push('updated_at = @updated_at');
      const stmt = this.db.prepare(`UPDATE tasks SET ${updates.join(', ')} WHERE id = @id`);
      stmt.run(params);
    }

    return this.getTask(id)!;
  }

  async deleteTask(id: string): Promise<boolean> {
    const stmt = this.db.prepare('DELETE FROM tasks WHERE id = ?');
    const result = stmt.run(id);
    return result.changes > 0;
  }

  close(): void {
    this.db.close();
  }

  // Private helper methods
  private getWorkspace(id: string): Workspace | null {
    const stmt = this.db.prepare('SELECT * FROM workspaces WHERE id = ?');
    const row = stmt.get(id) as DbWorkspace | undefined;
    return row ? this.mapWorkspace(row) : null;
  }

  private getProject(id: string): Project | null {
    const stmt = this.db.prepare('SELECT * FROM projects WHERE id = ?');
    const row = stmt.get(id) as DbProject | undefined;
    return row ? this.mapProject(row) : null;
  }

  private getTask(id: string): Task | null {
    const stmt = this.db.prepare('SELECT * FROM tasks WHERE id = ?');
    const row = stmt.get(id) as DbTask | undefined;
    return row ? this.mapTask(row) : null;
  }

  private mapWorkspace(row: DbWorkspace): Workspace {
    return {
      id: row.id,
      name: row.name,
      description: row.description || undefined,
      color: row.color || undefined,
      icon: row.icon || undefined,
      isActive: row.is_active === 1,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at)
    };
  }

  private mapProject(row: DbProject): Project {
    return {
      id: row.id,
      workspaceId: row.workspace_id,
      name: row.name,
      description: row.description || undefined,
      status: row.status as ProjectStatus,
      priority: row.priority as Priority,
      dueDate: row.due_date ? new Date(row.due_date) : undefined,
      tags: row.tags ? JSON.parse(row.tags) : undefined,
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at)
    };
  }

  private mapTask(row: DbTask): Task {
    return {
      id: row.id,
      projectId: row.project_id,
      title: row.title,
      description: row.description || undefined,
      status: row.status as TaskStatus,
      priority: row.priority as Priority,
      assignee: row.assignee || undefined,
      dueDate: row.due_date ? new Date(row.due_date) : undefined,
      completedAt: row.completed_at ? new Date(row.completed_at) : undefined,
      tags: row.tags ? JSON.parse(row.tags) : undefined,
      checklist: row.checklist ? JSON.parse(row.checklist) : undefined,
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at)
    };
  }
}

export { StorageModule as default };