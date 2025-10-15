// Session types
export type SessionState = 'active' | 'idle' | 'stale' | 'archived' | 'forked';

export interface SessionMetadata {
  id: string;
  title: string;
  project: string;
  state: SessionState;
  lastActivity: Date;
  notes: string;
  createdAt: Date;
  updatedAt: Date;
  parentId?: string; // For forked sessions
  tags?: string[];
}

// Canvas layout types
export interface CardPosition {
  x: number; // Grid units
  y: number; // Grid units
  w: number; // Width in grid units
  h: number; // Height in grid units
}

export interface SessionCardLayout {
  sessionId: string;
  position: CardPosition;
  isLocked?: boolean;
  zIndex?: number;
}

// Canvas settings
export interface CanvasSettings {
  gridSize: number; // Pixels per grid unit (default: 50)
  showGrid: boolean;
  zoom: number; // 0.5 to 2.0
  panX: number;
  panY: number;
  canvasWidth: number; // Grid units
  canvasHeight: number; // Grid units
}

// Worktree info from backend
export interface WorktreeInfo {
  path: string;
  branch: string;
  isDetached: boolean;
  isDirty: boolean;
  lastCommit?: {
    hash: string;
    message: string;
    date: Date;
  };
}

// IPC Events
export interface IPCEvents {
  'session:created': SessionMetadata;
  'session:updated': SessionMetadata;
  'session:deleted': string;
  'session:state-changed': { sessionId: string; state: SessionState };
  'worktree:status': { sessionId: string; info: WorktreeInfo };
}