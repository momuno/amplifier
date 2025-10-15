import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { SessionManager } from './session-manager';
import { StorageModule } from '../storage';
import {
  SessionState,
  SessionNotFoundError,
  InvalidStateTransitionError
} from './types';
import * as fs from 'fs';
import * as path from 'path';

describe('SessionManager', () => {
  let sessionManager: SessionManager;
  let storage: StorageModule;
  const testDbPath = path.join(__dirname, 'test-sessions.db');

  beforeEach(async () => {
    // Clean up any existing test database
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }

    // Initialize storage and session manager
    storage = new StorageModule(testDbPath);
    await storage.initialize();
    sessionManager = new SessionManager(storage);

    // Create a test workspace and project
    const workspace = await storage.createWorkspace({
      name: 'Test Workspace',
      isActive: true
    });

    await storage.createProject({
      workspaceId: workspace.id,
      name: 'Test Project',
      status: 'in_progress' as any,
      priority: 'medium' as any
    });
  });

  afterEach(() => {
    storage.close();
    // Clean up test database
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
    // Clean up WAL and SHM files
    ['wal', 'shm'].forEach(ext => {
      const filePath = `${testDbPath}-${ext}`;
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    });
  });

  describe('createSession', () => {
    it('should create a new session with initial PLANNING state', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session = await sessionManager.createSession(
        projectId,
        'New Feature Session',
        { description: 'Implementing user authentication' }
      );

      expect(session).toBeDefined();
      expect(session.id).toBeDefined();
      expect(session.projectId).toBe(projectId);
      expect(session.name).toBe('New Feature Session');
      expect(session.state).toBe(SessionState.PLANNING);
      expect(session.metadata).toEqual({ description: 'Implementing user authentication' });
      expect(session.isArchived).toBe(false);
      expect(session.createdAt).toBeInstanceOf(Date);
      expect(session.updatedAt).toBeInstanceOf(Date);
    });

    it('should create history entry on session creation', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session = await sessionManager.createSession(projectId, 'Test Session');
      const history = await sessionManager.getSessionHistory(session.id);

      expect(history).toHaveLength(1);
      expect(history[0].toState).toBe(SessionState.PLANNING);
      expect(history[0].fromState).toBeUndefined();
      expect(history[0].note).toBe('Session created');
    });
  });

  describe('updateSessionState', () => {
    it('should update session state with valid transition', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session = await sessionManager.createSession(projectId, 'Test Session');
      const updated = await sessionManager.updateSessionState(
        session.id,
        SessionState.WORKING,
        'Starting development'
      );

      expect(updated.state).toBe(SessionState.WORKING);
      expect(updated.updatedAt.getTime()).toBeGreaterThan(session.updatedAt.getTime());
    });

    it('should throw error for invalid state transition', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session = await sessionManager.createSession(projectId, 'Test Session');

      // Update to COMPLETED state first
      await sessionManager.updateSessionState(session.id, SessionState.COMPLETED);

      // Try to transition from COMPLETED to WORKING (invalid)
      await expect(
        sessionManager.updateSessionState(session.id, SessionState.WORKING)
      ).rejects.toThrow(InvalidStateTransitionError);
    });

    it('should throw error for non-existent session', async () => {
      await expect(
        sessionManager.updateSessionState('non-existent-id', SessionState.WORKING)
      ).rejects.toThrow(SessionNotFoundError);
    });

    it('should record state transitions in history', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session = await sessionManager.createSession(projectId, 'Test Session');
      await sessionManager.updateSessionState(session.id, SessionState.WORKING);
      await sessionManager.updateSessionState(session.id, SessionState.REVIEW_READY, 'Ready for review');

      const history = await sessionManager.getSessionHistory(session.id);
      expect(history).toHaveLength(3); // Initial + 2 updates
      expect(history[1].fromState).toBe(SessionState.PLANNING);
      expect(history[1].toState).toBe(SessionState.WORKING);
      expect(history[2].fromState).toBe(SessionState.WORKING);
      expect(history[2].toState).toBe(SessionState.REVIEW_READY);
      expect(history[2].note).toBe('Ready for review');
    });
  });

  describe('updateSession', () => {
    it('should update multiple session properties', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session = await sessionManager.createSession(projectId, 'Test Session');
      const updated = await sessionManager.updateSession(session.id, {
        name: 'Updated Session Name',
        currentBranch: 'feature/auth',
        worktreePath: '/path/to/worktree',
        metadata: { priority: 'high' }
      });

      expect(updated.name).toBe('Updated Session Name');
      expect(updated.currentBranch).toBe('feature/auth');
      expect(updated.worktreePath).toBe('/path/to/worktree');
      expect(updated.metadata).toEqual({ priority: 'high' });
    });
  });

  describe('listSessions', () => {
    it('should list all sessions', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      await sessionManager.createSession(projectId, 'Session 1');
      await sessionManager.createSession(projectId, 'Session 2');
      await sessionManager.createSession(projectId, 'Session 3');

      const sessions = await sessionManager.listSessions();
      expect(sessions).toHaveLength(3);
    });

    it('should filter sessions by project', async () => {
      const workspaceId = (await storage.getWorkspaces())[0].id;
      const project1 = await storage.createProject({
        workspaceId,
        name: 'Project 1',
        status: 'in_progress' as any,
        priority: 'medium' as any
      });
      const project2 = await storage.createProject({
        workspaceId,
        name: 'Project 2',
        status: 'in_progress' as any,
        priority: 'medium' as any
      });

      await sessionManager.createSession(project1.id, 'P1 Session 1');
      await sessionManager.createSession(project1.id, 'P1 Session 2');
      await sessionManager.createSession(project2.id, 'P2 Session 1');

      const project1Sessions = await sessionManager.listSessions({ projectId: project1.id });
      expect(project1Sessions).toHaveLength(2);

      const project2Sessions = await sessionManager.listSessions({ projectId: project2.id });
      expect(project2Sessions).toHaveLength(1);
    });

    it('should filter sessions by state', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session1 = await sessionManager.createSession(projectId, 'Session 1');
      const session2 = await sessionManager.createSession(projectId, 'Session 2');
      await sessionManager.createSession(projectId, 'Session 3');

      await sessionManager.updateSessionState(session1.id, SessionState.WORKING);
      await sessionManager.updateSessionState(session2.id, SessionState.WORKING);

      const workingSessions = await sessionManager.listSessions({ state: SessionState.WORKING });
      expect(workingSessions).toHaveLength(2);

      const planningSessions = await sessionManager.listSessions({ state: SessionState.PLANNING });
      expect(planningSessions).toHaveLength(1);
    });

    it('should exclude archived sessions by default', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session1 = await sessionManager.createSession(projectId, 'Active Session');
      const session2 = await sessionManager.createSession(projectId, 'Archived Session');

      await sessionManager.archiveSession(session2.id);

      const sessions = await sessionManager.listSessions();
      expect(sessions).toHaveLength(1);
      expect(sessions[0].id).toBe(session1.id);

      const allSessions = await sessionManager.listSessions({ includeArchived: true });
      expect(allSessions).toHaveLength(2);
    });
  });

  describe('archiveSession', () => {
    it('should archive a session', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const session = await sessionManager.createSession(projectId, 'Test Session');
      const result = await sessionManager.archiveSession(session.id);

      expect(result).toBe(true);

      const archived = await sessionManager.getSession(session.id);
      expect(archived?.isArchived).toBe(true);
      expect(archived?.archivedAt).toBeInstanceOf(Date);
    });

    it('should throw error when archiving non-existent session', async () => {
      await expect(
        sessionManager.archiveSession('non-existent-id')
      ).rejects.toThrow(SessionNotFoundError);
    });
  });

  describe('forkSession', () => {
    it('should create a forked session', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      const parent = await sessionManager.createSession(
        projectId,
        'Parent Session',
        { feature: 'authentication' }
      );

      await sessionManager.updateSessionState(parent.id, SessionState.WORKING);
      await sessionManager.updateSession(parent.id, {
        currentBranch: 'feature/auth',
        worktreePath: '/parent/worktree'
      });

      const fork = await sessionManager.forkSession(parent.id, 'Fork Session');

      expect(fork.parentSessionId).toBe(parent.id);
      expect(fork.projectId).toBe(parent.projectId);
      expect(fork.name).toBe('Fork Session');
      expect(fork.state).toBe(SessionState.PLANNING); // Reset to PLANNING
      expect(fork.currentBranch).toBeUndefined(); // New branch needed
      expect(fork.worktreePath).toBeUndefined(); // New worktree needed
      expect(fork.metadata).toEqual({ feature: 'authentication' }); // Inherited metadata
    });

    it('should throw error when forking non-existent session', async () => {
      await expect(
        sessionManager.forkSession('non-existent-id', 'Fork')
      ).rejects.toThrow(SessionNotFoundError);
    });
  });

  describe('getSessionStats', () => {
    it('should return correct statistics', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      // Create sessions in different states
      const s1 = await sessionManager.createSession(projectId, 'Session 1');
      const s2 = await sessionManager.createSession(projectId, 'Session 2');
      const s3 = await sessionManager.createSession(projectId, 'Session 3');
      const s4 = await sessionManager.createSession(projectId, 'Session 4');

      await sessionManager.updateSessionState(s1.id, SessionState.WORKING);
      await sessionManager.updateSessionState(s2.id, SessionState.WORKING);
      await sessionManager.updateSessionState(s3.id, SessionState.COMPLETED);
      await sessionManager.archiveSession(s4.id);

      const stats = await sessionManager.getSessionStats(projectId);

      expect(stats.total).toBe(4);
      expect(stats.activeCount).toBe(3);
      expect(stats.archivedCount).toBe(1);
      expect(stats.byState[SessionState.PLANNING]).toBe(1); // s4 (archived but still PLANNING)
      expect(stats.byState[SessionState.WORKING]).toBe(2); // s1, s2
      expect(stats.byState[SessionState.COMPLETED]).toBe(1); // s3
    });

    it('should return global stats when no projectId provided', async () => {
      const workspaceId = (await storage.getWorkspaces())[0].id;
      const project1 = await storage.createProject({
        workspaceId,
        name: 'Project 1',
        status: 'in_progress' as any,
        priority: 'medium' as any
      });
      const project2 = await storage.createProject({
        workspaceId,
        name: 'Project 2',
        status: 'in_progress' as any,
        priority: 'medium' as any
      });

      await sessionManager.createSession(project1.id, 'P1 Session');
      await sessionManager.createSession(project2.id, 'P2 Session');

      const globalStats = await sessionManager.getSessionStats();
      expect(globalStats.total).toBe(2);
    });
  });

  describe('State Transitions', () => {
    it('should validate all defined state transitions', async () => {
      const projects = await storage.getProjects((await storage.getWorkspaces())[0].id);
      const projectId = projects[0].id;

      // Test valid transitions from PLANNING
      let session = await sessionManager.createSession(projectId, 'Test');
      await expect(sessionManager.updateSessionState(session.id, SessionState.WORKING)).resolves.toBeDefined();

      session = await sessionManager.createSession(projectId, 'Test2');
      await expect(sessionManager.updateSessionState(session.id, SessionState.PAUSED)).resolves.toBeDefined();

      // Test valid transitions from WORKING
      session = await sessionManager.createSession(projectId, 'Test3');
      await sessionManager.updateSessionState(session.id, SessionState.WORKING);
      await expect(sessionManager.updateSessionState(session.id, SessionState.NEEDS_INPUT)).resolves.toBeDefined();

      // Test invalid transition from COMPLETED
      session = await sessionManager.createSession(projectId, 'Test4');
      await sessionManager.updateSessionState(session.id, SessionState.COMPLETED);
      await expect(sessionManager.updateSessionState(session.id, SessionState.WORKING)).rejects.toThrow(InvalidStateTransitionError);

      // Test PAUSED can transition to any state except itself
      session = await sessionManager.createSession(projectId, 'Test5');
      await sessionManager.updateSessionState(session.id, SessionState.PAUSED);
      await expect(sessionManager.updateSessionState(session.id, SessionState.REVIEW_READY)).resolves.toBeDefined();
    });
  });
});