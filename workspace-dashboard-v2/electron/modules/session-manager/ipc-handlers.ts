import { ipcMain, IpcMainInvokeEvent } from 'electron';
import type { SessionManager } from './session-manager';
import type {
  SessionState,
  SessionUpdate,
  ListSessionOptions
} from './types';

/**
 * Register IPC handlers for session management
 * All handlers follow the pattern: session:action
 */
export function registerSessionIpcHandlers(sessionManager: SessionManager): void {
  // Create a new session
  ipcMain.handle('session:create', async (
    _event: IpcMainInvokeEvent,
    projectId: string,
    name: string,
    metadata?: Record<string, any>
  ) => {
    try {
      const session = await sessionManager.createSession(projectId, name, metadata);
      return { success: true, data: session };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create session'
      };
    }
  });

  // Update session state
  ipcMain.handle('session:updateState', async (
    _event: IpcMainInvokeEvent,
    id: string,
    state: SessionState,
    note?: string
  ) => {
    try {
      const session = await sessionManager.updateSessionState(id, state, note);
      return { success: true, data: session };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update session state'
      };
    }
  });

  // Update session details
  ipcMain.handle('session:update', async (
    _event: IpcMainInvokeEvent,
    id: string,
    updates: SessionUpdate
  ) => {
    try {
      const session = await sessionManager.updateSession(id, updates);
      return { success: true, data: session };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update session'
      };
    }
  });

  // Get a single session
  ipcMain.handle('session:get', async (
    _event: IpcMainInvokeEvent,
    id: string
  ) => {
    try {
      const session = await sessionManager.getSession(id);
      return { success: true, data: session };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session'
      };
    }
  });

  // List sessions with optional filters
  ipcMain.handle('session:list', async (
    _event: IpcMainInvokeEvent,
    options?: ListSessionOptions
  ) => {
    try {
      const sessions = await sessionManager.listSessions(options);
      return { success: true, data: sessions };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list sessions'
      };
    }
  });

  // Archive a session
  ipcMain.handle('session:archive', async (
    _event: IpcMainInvokeEvent,
    id: string
  ) => {
    try {
      const result = await sessionManager.archiveSession(id);
      return { success: result, data: result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to archive session'
      };
    }
  });

  // Fork a session
  ipcMain.handle('session:fork', async (
    _event: IpcMainInvokeEvent,
    parentId: string,
    name: string
  ) => {
    try {
      const session = await sessionManager.forkSession(parentId, name);
      return { success: true, data: session };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fork session'
      };
    }
  });

  // Get active sessions for a project
  ipcMain.handle('session:getActiveForProject', async (
    _event: IpcMainInvokeEvent,
    projectId: string
  ) => {
    try {
      const sessions = await sessionManager.getActiveSessionsForProject(projectId);
      return { success: true, data: sessions };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get active sessions'
      };
    }
  });

  // Get session history
  ipcMain.handle('session:getHistory', async (
    _event: IpcMainInvokeEvent,
    id: string
  ) => {
    try {
      const history = await sessionManager.getSessionHistory(id);
      return { success: true, data: history };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session history'
      };
    }
  });

  // Get session statistics
  ipcMain.handle('session:getStats', async (
    _event: IpcMainInvokeEvent,
    projectId?: string
  ) => {
    try {
      const stats = await sessionManager.getSessionStats(projectId);
      return { success: true, data: stats };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session stats'
      };
    }
  });
}