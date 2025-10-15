/**
 * State Detector Models
 * Data structures and types for session state detection
 */

export enum SessionState {
  PLANNING = 'PLANNING',
  WORKING = 'WORKING',
  NEEDS_INPUT = 'NEEDS_INPUT',
  REVIEW_READY = 'REVIEW_READY',
  PAUSED = 'PAUSED',
  COMPLETED = 'COMPLETED',
}

export interface SessionConfig {
  id: string;
  path: string;
  name?: string;
}

export interface StateDetectorConfig {
  pauseTimeout?: number; // milliseconds, default 15 minutes
  scanInterval?: number; // milliseconds, default 5 seconds
  debounceDelay?: number; // milliseconds, default 500ms
}

export interface SessionActivity {
  lastFileChange?: Date;
  lastClaudeOutput?: Date;
  lastGitActivity?: Date;
  fileChangeCount: number;
  hasQuestions: boolean;
  todoCompletion?: {
    completed: number;
    total: number;
  };
}

export interface StateChangeEvent {
  sessionId: string;
  oldState: SessionState;
  newState: SessionState;
  timestamp: Date;
  reason?: string;
}

export interface ActivityEvent {
  sessionId: string;
  type: 'file_change' | 'claude_output' | 'git_activity' | 'todo_update';
  details: any;
  timestamp: Date;
}

export interface DetectionPatterns {
  questions: RegExp[];
  completion: RegExp[];
  todoFiles: RegExp[];
  claudeFiles: RegExp[];
}

export interface SessionData {
  config: SessionConfig;
  state: SessionState;
  activity: SessionActivity;
  manualOverride?: boolean;
  createdAt: Date;
  updatedAt: Date;
}