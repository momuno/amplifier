# Session Manager Module

Self-contained module for managing Claude Code session lifecycle in Workspace Dashboard V2.

## Purpose

Manages the complete lifecycle of Claude Code sessions including creation, state tracking, updates, archiving, and forking. Tracks session states through their workflow from planning to completion.

## Contract

### Inputs
- Project ID (string) - Links sessions to projects
- Session name (string) - Human-readable session identifier
- Session state (SessionState enum) - Current workflow state
- Session metadata (Record<string, any>) - Flexible session data

### Outputs
- Session objects with full state and history
- Success/error responses for all operations
- List of sessions filtered by project or state

### Side Effects
- Persists session data to SQLite database via storage module
- Creates session history entries for state transitions
- Manages session archive lifecycle

## Public Interface

```typescript
class SessionManager {
  constructor(storage: StorageModule)

  // Core session operations
  async createSession(projectId: string, name: string, metadata?: Record<string, any>): Promise<Session>
  async updateSessionState(id: string, state: SessionState, note?: string): Promise<Session>
  async updateSession(id: string, updates: Partial<SessionUpdate>): Promise<Session>
  async getSession(id: string): Promise<Session | null>
  async listSessions(options?: ListSessionOptions): Promise<Session[]>
  async archiveSession(id: string): Promise<boolean>
  async forkSession(parentId: string, name: string): Promise<Session>

  // Query operations
  async getActiveSessionsForProject(projectId: string): Promise<Session[]>
  async getSessionHistory(id: string): Promise<SessionHistory[]>
  async getSessionStats(projectId?: string): Promise<SessionStats>
}

// Session states
enum SessionState {
  PLANNING = 'planning',        // Initial planning phase
  WORKING = 'working',          // Active development
  NEEDS_INPUT = 'needs_input',  // Blocked on user input
  REVIEW_READY = 'review_ready', // Ready for code review
  PAUSED = 'paused',            // Temporarily paused
  COMPLETED = 'completed'       // Successfully completed
}

// Core data types
interface Session {
  id: string
  projectId: string
  parentSessionId?: string  // For forked sessions
  name: string
  state: SessionState
  currentBranch?: string    // Git branch name
  worktreePath?: string     // Worktree directory
  metadata?: Record<string, any>
  isArchived: boolean
  createdAt: Date
  updatedAt: Date
  archivedAt?: Date
}

interface SessionHistory {
  id: string
  sessionId: string
  fromState?: SessionState
  toState: SessionState
  note?: string
  createdAt: Date
}

interface ListSessionOptions {
  projectId?: string
  state?: SessionState
  includeArchived?: boolean
  limit?: number
  offset?: number
}

interface SessionStats {
  total: number
  byState: Record<SessionState, number>
  activeCount: number
  archivedCount: number
}
```

## Dependencies
- storage module - For database persistence
- crypto - UUID generation
- shared/contracts - Type definitions

## Error Handling

| Error Type | Condition | Recovery Strategy |
|------------|-----------|-------------------|
| SessionNotFoundError | Session ID doesn't exist | Return null or throw with clear message |
| InvalidStateTransition | Invalid state change | Return current state with error message |
| StorageError | Database operation fails | Retry with exponential backoff |
| ValidationError | Invalid input data | Return detailed validation errors |

## Performance Characteristics
- Session creation: O(1) database insert
- State update: O(1) with history tracking
- List sessions: O(n) where n is result count
- Memory usage: Minimal, all data in SQLite

## Testing

```bash
# Run module tests
npm test -- session-manager

# Run specific test suite
npm test -- session-manager --grep "state transitions"
```

## Regeneration Specification

This module can be regenerated from this specification alone.
Key invariants that must be preserved:

- Session ID format (UUID v4)
- State transition rules and history
- Database schema compatibility
- IPC handler signatures
- Archive behavior (soft delete)