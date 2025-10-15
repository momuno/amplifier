// Core domain types for Workspace Dashboard

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Project {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  priority: Priority;
  dueDate?: Date;
  tags?: string[];
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface Task {
  id: string;
  projectId: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: Priority;
  assignee?: string;
  dueDate?: Date;
  completedAt?: Date;
  tags?: string[];
  checklist?: ChecklistItem[];
  metadata?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
}

// Enums
export enum ProjectStatus {
  PLANNED = 'planned',
  IN_PROGRESS = 'in_progress',
  ON_HOLD = 'on_hold',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum TaskStatus {
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  IN_REVIEW = 'in_review',
  DONE = 'done',
  BLOCKED = 'blocked'
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Database schema types (for internal use in storage module)
export interface DbWorkspace {
  id: string;
  name: string;
  description: string | null;
  color: string | null;
  icon: string | null;
  is_active: number; // SQLite boolean
  created_at: string; // ISO timestamp
  updated_at: string; // ISO timestamp
}

export interface DbProject {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  status: string;
  priority: string;
  due_date: string | null;
  tags: string | null; // JSON string
  metadata: string | null; // JSON string
  created_at: string;
  updated_at: string;
}

export interface DbTask {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  assignee: string | null;
  due_date: string | null;
  completed_at: string | null;
  tags: string | null; // JSON string
  checklist: string | null; // JSON string
  metadata: string | null; // JSON string
  created_at: string;
  updated_at: string;
}