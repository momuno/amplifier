// Session Manager Type Definitions

export enum SessionState {
  PLANNING = 'planning',
  WORKING = 'working',
  NEEDS_INPUT = 'needs_input',
  REVIEW_READY = 'review_ready',
  PAUSED = 'paused',
  COMPLETED = 'completed'
}

export interface Session {
  id: string;
  projectId: string;
  parentSessionId?: string;
  name: string;
  state: SessionState;
  currentBranch?: string;
  worktreePath?: string;
  metadata?: Record<string, any>;
  isArchived: boolean;
  createdAt: Date;
  updatedAt: Date;
  archivedAt?: Date;
}

export interface SessionHistory {
  id: string;
  sessionId: string;
  fromState?: SessionState;
  toState: SessionState;
  note?: string;
  createdAt: Date;
}

export interface CreateSessionDto {
  projectId: string;
  name: string;
  metadata?: Record<string, any>;
  currentBranch?: string;
  worktreePath?: string;
}

export interface SessionUpdate {
  name?: string;
  state?: SessionState;
  currentBranch?: string;
  worktreePath?: string;
  metadata?: Record<string, any>;
}

export interface ListSessionOptions {
  projectId?: string;
  state?: SessionState;
  includeArchived?: boolean;
  limit?: number;
  offset?: number;
}

export interface SessionStats {
  total: number;
  byState: Record<SessionState, number>;
  activeCount: number;
  archivedCount: number;
}

// Database schema types
export interface DbSession {
  id: string;
  project_id: string;
  parent_session_id: string | null;
  name: string;
  state: string;
  current_branch: string | null;
  worktree_path: string | null;
  metadata: string | null;
  is_archived: number;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
}

export interface DbSessionHistory {
  id: string;
  session_id: string;
  from_state: string | null;
  to_state: string;
  note: string | null;
  created_at: string;
}

// Error types
export class SessionNotFoundError extends Error {
  constructor(id: string) {
    super(`Session ${id} not found`);
    this.name = 'SessionNotFoundError';
  }
}

export class InvalidStateTransitionError extends Error {
  constructor(from: SessionState, to: SessionState) {
    super(`Invalid state transition from ${from} to ${to}`);
    this.name = 'InvalidStateTransitionError';
  }
}