import { SessionMetadata, WorktreeInfo } from '../types';

// IPC channels
export const IPC_CHANNELS = {
  // Session management
  SESSION_CREATE: 'session:create',
  SESSION_UPDATE: 'session:update',
  SESSION_DELETE: 'session:delete',
  SESSION_LIST: 'session:list',
  SESSION_GET: 'session:get',

  // Session events from backend
  SESSION_CREATED: 'session:created',
  SESSION_UPDATED: 'session:updated',
  SESSION_DELETED: 'session:deleted',
  SESSION_STATE_CHANGED: 'session:state-changed',

  // Worktree operations
  WORKTREE_CREATE: 'worktree:create',
  WORKTREE_DELETE: 'worktree:delete',
  WORKTREE_STATUS: 'worktree:status',
  WORKTREE_OPEN: 'worktree:open',

  // File operations
  FILE_BROWSER_OPEN: 'file:browser-open',

  // State detection events
  STATE_DETECTED: 'state:detected',
} as const;

// Type-safe IPC communication wrapper
class IPCClient {
  private electron: any;

  constructor() {
    // @ts-ignore - window.electron is injected by preload
    this.electron = window.electron;
  }

  // Session operations
  async createSession(data: Partial<SessionMetadata>): Promise<SessionMetadata> {
    return this.invoke(IPC_CHANNELS.SESSION_CREATE, data);
  }

  async updateSession(id: string, updates: Partial<SessionMetadata>): Promise<SessionMetadata> {
    return this.invoke(IPC_CHANNELS.SESSION_UPDATE, { id, updates });
  }

  async deleteSession(id: string): Promise<void> {
    return this.invoke(IPC_CHANNELS.SESSION_DELETE, id);
  }

  async listSessions(): Promise<SessionMetadata[]> {
    return this.invoke(IPC_CHANNELS.SESSION_LIST);
  }

  async getSession(id: string): Promise<SessionMetadata | null> {
    return this.invoke(IPC_CHANNELS.SESSION_GET, id);
  }

  // Worktree operations
  async createWorktree(sessionId: string, path: string, branch?: string): Promise<WorktreeInfo> {
    return this.invoke(IPC_CHANNELS.WORKTREE_CREATE, { sessionId, path, branch });
  }

  async deleteWorktree(sessionId: string): Promise<void> {
    return this.invoke(IPC_CHANNELS.WORKTREE_DELETE, sessionId);
  }

  async getWorktreeStatus(sessionId: string): Promise<WorktreeInfo> {
    return this.invoke(IPC_CHANNELS.WORKTREE_STATUS, sessionId);
  }

  async openWorktree(sessionId: string): Promise<void> {
    return this.invoke(IPC_CHANNELS.WORKTREE_OPEN, sessionId);
  }

  // File operations
  async openFileBrowser(path: string): Promise<void> {
    return this.invoke(IPC_CHANNELS.FILE_BROWSER_OPEN, path);
  }

  // Event listeners
  onSessionCreated(callback: (session: SessionMetadata) => void): () => void {
    return this.on(IPC_CHANNELS.SESSION_CREATED, callback);
  }

  onSessionUpdated(callback: (session: SessionMetadata) => void): () => void {
    return this.on(IPC_CHANNELS.SESSION_UPDATED, callback);
  }

  onSessionDeleted(callback: (id: string) => void): () => void {
    return this.on(IPC_CHANNELS.SESSION_DELETED, callback);
  }

  onSessionStateChanged(callback: (data: { sessionId: string; state: SessionMetadata['state'] }) => void): () => void {
    return this.on(IPC_CHANNELS.SESSION_STATE_CHANGED, callback);
  }

  onWorktreeStatus(callback: (data: { sessionId: string; info: WorktreeInfo }) => void): () => void {
    return this.on(IPC_CHANNELS.WORKTREE_STATUS, callback);
  }

  // Helper methods
  private async invoke(channel: string, ...args: any[]): Promise<any> {
    if (!this.electron) {
      console.warn('IPC not available, running in browser mode');
      return null;
    }
    return this.electron.ipcRenderer.invoke(channel, ...args);
  }

  private on(channel: string, callback: (...args: any[]) => void): () => void {
    if (!this.electron) {
      console.warn('IPC not available, running in browser mode');
      return () => {};
    }

    this.electron.ipcRenderer.on(channel, (_event: any, ...args: any[]) => {
      callback(...args);
    });

    // Return cleanup function
    return () => {
      this.electron.ipcRenderer.removeListener(channel, callback);
    };
  }
}

// Export singleton instance
export const ipc = new IPCClient();