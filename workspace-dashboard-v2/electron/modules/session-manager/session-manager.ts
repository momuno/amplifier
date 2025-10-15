import { randomUUID } from 'crypto';
import type { StorageModule } from '../storage';
import Database from 'better-sqlite3';
import {
  Session,
  SessionState,
  SessionHistory,
  SessionUpdate,
  ListSessionOptions,
  SessionStats,
  DbSession,
  DbSessionHistory,
  SessionNotFoundError,
  InvalidStateTransitionError
} from './types';

export class SessionManager {
  private db: Database.Database;

  constructor(storage: StorageModule) {
    // Access the internal database from storage module
    // In production, we'd use a proper interface, but for simplicity we'll extend storage
    this.db = (storage as any).db;
    this.initializeTables();
  }

  private initializeTables(): void {
    // Create session tables if they don't exist
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        parent_session_id TEXT,
        name TEXT NOT NULL,
        state TEXT NOT NULL,
        current_branch TEXT,
        worktree_path TEXT,
        metadata TEXT,
        is_archived INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        archived_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS session_history (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        from_state TEXT,
        to_state TEXT NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
      );

      CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_id);
      CREATE INDEX IF NOT EXISTS idx_sessions_state ON sessions(state);
      CREATE INDEX IF NOT EXISTS idx_sessions_archived ON sessions(is_archived);
      CREATE INDEX IF NOT EXISTS idx_session_history_session ON session_history(session_id);
    `);
  }

  async createSession(projectId: string, name: string, metadata?: Record<string, any>): Promise<Session> {
    const id = randomUUID();
    const now = new Date().toISOString();
    const initialState = SessionState.PLANNING;

    const stmt = this.db.prepare(`
      INSERT INTO sessions (
        id, project_id, parent_session_id, name, state,
        current_branch, worktree_path, metadata, is_archived,
        created_at, updated_at, archived_at
      )
      VALUES (
        @id, @project_id, @parent_session_id, @name, @state,
        @current_branch, @worktree_path, @metadata, @is_archived,
        @created_at, @updated_at, @archived_at
      )
    `);

    stmt.run({
      id,
      project_id: projectId,
      parent_session_id: null,
      name,
      state: initialState,
      current_branch: null,
      worktree_path: null,
      metadata: metadata ? JSON.stringify(metadata) : null,
      is_archived: 0,
      created_at: now,
      updated_at: now,
      archived_at: null
    });

    // Create initial history entry
    await this.addHistoryEntry(id, undefined, initialState, 'Session created');

    const newSession = await this.getSession(id);
    if (!newSession) {
      throw new Error('Failed to create session');
    }
    return newSession;
  }

  async updateSessionState(id: string, state: SessionState, note?: string): Promise<Session> {
    const session = await this.getSession(id);
    if (!session) {
      throw new SessionNotFoundError(id);
    }

    // Validate state transition
    if (!this.isValidStateTransition(session.state, state)) {
      throw new InvalidStateTransitionError(session.state, state);
    }

    const stmt = this.db.prepare(`
      UPDATE sessions
      SET state = @state, updated_at = @updated_at
      WHERE id = @id
    `);

    stmt.run({
      id,
      state,
      updated_at: new Date().toISOString()
    });

    // Add history entry
    await this.addHistoryEntry(id, session.state, state, note);

    const updatedSession = await this.getSession(id);
    if (!updatedSession) {
      throw new Error('Failed to update session state');
    }
    return updatedSession;
  }

  async updateSession(id: string, updates: Partial<SessionUpdate>): Promise<Session> {
    const session = await this.getSession(id);
    if (!session) {
      throw new SessionNotFoundError(id);
    }

    const updateClauses: string[] = [];
    const params: any = { id, updated_at: new Date().toISOString() };

    if (updates.name !== undefined) {
      updateClauses.push('name = @name');
      params.name = updates.name;
    }

    if (updates.state !== undefined) {
      if (!this.isValidStateTransition(session.state, updates.state)) {
        throw new InvalidStateTransitionError(session.state, updates.state);
      }
      updateClauses.push('state = @state');
      params.state = updates.state;
    }

    if (updates.currentBranch !== undefined) {
      updateClauses.push('current_branch = @current_branch');
      params.current_branch = updates.currentBranch || null;
    }

    if (updates.worktreePath !== undefined) {
      updateClauses.push('worktree_path = @worktree_path');
      params.worktree_path = updates.worktreePath || null;
    }

    if (updates.metadata !== undefined) {
      updateClauses.push('metadata = @metadata');
      params.metadata = updates.metadata ? JSON.stringify(updates.metadata) : null;
    }

    if (updateClauses.length > 0) {
      updateClauses.push('updated_at = @updated_at');
      const stmt = this.db.prepare(
        `UPDATE sessions SET ${updateClauses.join(', ')} WHERE id = @id`
      );
      stmt.run(params);

      // Add history entry if state changed
      if (updates.state && updates.state !== session.state) {
        await this.addHistoryEntry(id, session.state, updates.state);
      }
    }

    const updatedSession = await this.getSession(id);
    if (!updatedSession) {
      throw new Error('Failed to update session');
    }
    return updatedSession;
  }

  async getSession(id: string): Promise<Session | null> {
    const stmt = this.db.prepare('SELECT * FROM sessions WHERE id = ?');
    const row = stmt.get(id) as DbSession | undefined;
    return row ? this.mapSession(row) : null;
  }

  async listSessions(options: ListSessionOptions = {}): Promise<Session[]> {
    let query = 'SELECT * FROM sessions WHERE 1=1';
    const params: any[] = [];

    if (options.projectId) {
      query += ' AND project_id = ?';
      params.push(options.projectId);
    }

    if (options.state) {
      query += ' AND state = ?';
      params.push(options.state);
    }

    if (!options.includeArchived) {
      query += ' AND is_archived = 0';
    }

    query += ' ORDER BY created_at DESC';

    if (options.limit) {
      query += ' LIMIT ?';
      params.push(options.limit);
    }

    if (options.offset) {
      query += ' OFFSET ?';
      params.push(options.offset);
    }

    const stmt = this.db.prepare(query);
    const rows = stmt.all(...params) as DbSession[];
    return rows.map(this.mapSession);
  }

  async archiveSession(id: string): Promise<boolean> {
    const session = await this.getSession(id);
    if (!session) {
      throw new SessionNotFoundError(id);
    }

    const now = new Date().toISOString();
    const stmt = this.db.prepare(`
      UPDATE sessions
      SET is_archived = 1, archived_at = @archived_at, updated_at = @updated_at
      WHERE id = @id
    `);

    const result = stmt.run({
      id,
      archived_at: now,
      updated_at: now
    });

    return result.changes > 0;
  }

  async forkSession(parentId: string, name: string): Promise<Session> {
    const parent = await this.getSession(parentId);
    if (!parent) {
      throw new SessionNotFoundError(parentId);
    }

    const id = randomUUID();
    const now = new Date().toISOString();

    const stmt = this.db.prepare(`
      INSERT INTO sessions (
        id, project_id, parent_session_id, name, state,
        current_branch, worktree_path, metadata, is_archived,
        created_at, updated_at, archived_at
      )
      VALUES (
        @id, @project_id, @parent_session_id, @name, @state,
        @current_branch, @worktree_path, @metadata, @is_archived,
        @created_at, @updated_at, @archived_at
      )
    `);

    // Fork inherits parent's metadata but starts in PLANNING state
    stmt.run({
      id,
      project_id: parent.projectId,
      parent_session_id: parentId,
      name,
      state: SessionState.PLANNING,
      current_branch: null, // New fork needs new branch
      worktree_path: null,  // New fork needs new worktree
      metadata: parent.metadata ? JSON.stringify(parent.metadata) : null,
      is_archived: 0,
      created_at: now,
      updated_at: now,
      archived_at: null
    });

    await this.addHistoryEntry(id, undefined, SessionState.PLANNING, `Forked from session ${parentId}`);

    const forkedSession = await this.getSession(id);
    if (!forkedSession) {
      throw new Error('Failed to fork session');
    }
    return forkedSession;
  }

  async getActiveSessionsForProject(projectId: string): Promise<Session[]> {
    return this.listSessions({
      projectId,
      includeArchived: false
    });
  }

  async getSessionHistory(id: string): Promise<SessionHistory[]> {
    const stmt = this.db.prepare(
      'SELECT * FROM session_history WHERE session_id = ? ORDER BY created_at ASC'
    );
    const rows = stmt.all(id) as DbSessionHistory[];
    return rows.map(this.mapSessionHistory);
  }

  async getSessionStats(projectId?: string): Promise<SessionStats> {
    let baseQuery = 'FROM sessions';
    const params: any[] = [];

    if (projectId) {
      baseQuery += ' WHERE project_id = ?';
      params.push(projectId);
    }

    // Get total count
    const totalStmt = this.db.prepare(`SELECT COUNT(*) as count ${baseQuery}`);
    const totalRow = totalStmt.get(...params) as { count: number };

    // Get state counts
    const stateQuery = projectId
      ? 'SELECT state, COUNT(*) as count FROM sessions WHERE project_id = ? GROUP BY state'
      : 'SELECT state, COUNT(*) as count FROM sessions GROUP BY state';
    const stateStmt = this.db.prepare(stateQuery);
    const stateRows = stateStmt.all(...params) as { state: string; count: number }[];

    // Get active count
    const activeQuery = projectId
      ? 'SELECT COUNT(*) as count FROM sessions WHERE project_id = ? AND is_archived = 0'
      : 'SELECT COUNT(*) as count FROM sessions WHERE is_archived = 0';
    const activeStmt = this.db.prepare(activeQuery);
    const activeRow = activeStmt.get(...params) as { count: number };

    // Build byState object
    const byState: Record<SessionState, number> = {
      [SessionState.PLANNING]: 0,
      [SessionState.WORKING]: 0,
      [SessionState.NEEDS_INPUT]: 0,
      [SessionState.REVIEW_READY]: 0,
      [SessionState.PAUSED]: 0,
      [SessionState.COMPLETED]: 0
    };

    stateRows.forEach(row => {
      byState[row.state as SessionState] = row.count;
    });

    return {
      total: totalRow.count,
      byState,
      activeCount: activeRow.count,
      archivedCount: totalRow.count - activeRow.count
    };
  }

  private async addHistoryEntry(
    sessionId: string,
    fromState: SessionState | undefined,
    toState: SessionState,
    note?: string
  ): Promise<void> {
    const id = randomUUID();
    const stmt = this.db.prepare(`
      INSERT INTO session_history (id, session_id, from_state, to_state, note, created_at)
      VALUES (@id, @session_id, @from_state, @to_state, @note, @created_at)
    `);

    stmt.run({
      id,
      session_id: sessionId,
      from_state: fromState || null,
      to_state: toState,
      note: note || null,
      created_at: new Date().toISOString()
    });
  }

  private isValidStateTransition(from: SessionState, to: SessionState): boolean {
    // Define valid state transitions
    const validTransitions: Record<SessionState, SessionState[]> = {
      [SessionState.PLANNING]: [
        SessionState.WORKING,
        SessionState.PAUSED,
        SessionState.COMPLETED
      ],
      [SessionState.WORKING]: [
        SessionState.NEEDS_INPUT,
        SessionState.REVIEW_READY,
        SessionState.PAUSED,
        SessionState.COMPLETED
      ],
      [SessionState.NEEDS_INPUT]: [
        SessionState.WORKING,
        SessionState.PAUSED,
        SessionState.COMPLETED
      ],
      [SessionState.REVIEW_READY]: [
        SessionState.WORKING,
        SessionState.COMPLETED,
        SessionState.PAUSED
      ],
      [SessionState.PAUSED]: [
        SessionState.PLANNING,
        SessionState.WORKING,
        SessionState.NEEDS_INPUT,
        SessionState.REVIEW_READY,
        SessionState.COMPLETED
      ],
      [SessionState.COMPLETED]: [] // Terminal state
    };

    return validTransitions[from]?.includes(to) ?? false;
  }

  private mapSession(row: DbSession): Session {
    return {
      id: row.id,
      projectId: row.project_id,
      parentSessionId: row.parent_session_id || undefined,
      name: row.name,
      state: row.state as SessionState,
      currentBranch: row.current_branch || undefined,
      worktreePath: row.worktree_path || undefined,
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
      isArchived: row.is_archived === 1,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
      archivedAt: row.archived_at ? new Date(row.archived_at) : undefined
    };
  }

  private mapSessionHistory(row: DbSessionHistory): SessionHistory {
    return {
      id: row.id,
      sessionId: row.session_id,
      fromState: row.from_state ? row.from_state as SessionState : undefined,
      toState: row.to_state as SessionState,
      note: row.note || undefined,
      createdAt: new Date(row.created_at)
    };
  }
}