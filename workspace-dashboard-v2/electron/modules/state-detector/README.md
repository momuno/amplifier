# State Detector Module

A self-contained module for detecting and monitoring Claude Code session states in the Workspace Dashboard V2.

## Purpose

This module monitors session worktree directories and detects the current state of Claude Code sessions based on file patterns, activity timestamps, and content analysis.

## Contract

### Inputs

- **Session paths**: Array of directory paths to monitor
- **Configuration**: State detection thresholds and patterns
- **Manual state overrides**: User-initiated state changes

### Outputs

- **State events**: Emitted when session state changes
- **State queries**: Current state for any session on demand
- **Activity metrics**: Last activity time, file change counts

### Side Effects

- File system monitoring via chokidar
- IPC event emissions to renderer process
- State persistence to memory (no disk writes)

## States

The module detects these session states:

- `PLANNING`: Initial setup phase, minimal file activity
- `WORKING`: Active file changes detected recently
- `NEEDS_INPUT`: Claude waiting for user response (questions detected)
- `REVIEW_READY`: TODOs completed or completion indicated
- `PAUSED`: No activity for configured timeout (default 15 min)
- `COMPLETED`: User has marked session as complete

## Usage

```typescript
import { StateDetector } from './state-detector';

// Initialize detector
const detector = new StateDetector({
  pauseTimeout: 15 * 60 * 1000, // 15 minutes
  scanInterval: 5000, // 5 seconds
});

// Add session to monitor
await detector.addSession({
  id: 'session-123',
  path: '/path/to/session/worktree',
});

// Listen for state changes
detector.on('stateChange', (event) => {
  console.log(`Session ${event.sessionId} changed to ${event.newState}`);
});

// Get current state
const state = await detector.getState('session-123');

// Manual state override
await detector.setState('session-123', 'COMPLETED');

// Clean up
await detector.removeSession('session-123');
detector.destroy();
```

## Architecture

```
state-detector/
├── index.ts           # Public exports
├── core.ts           # Main StateDetector class
├── models.ts         # TypeScript interfaces and types
├── detector.ts       # State detection logic
├── watcher.ts        # File watching with chokidar
├── patterns.ts       # Pattern definitions for detection
├── ipc.ts           # IPC handlers for Electron
└── tests/
    ├── detector.test.ts
    ├── watcher.test.ts
    └── fixtures/
```

## Detection Logic

### Planning State
- `.claude/` directory exists
- Minimal file changes (< 5 files modified)
- No git commits yet
- Recent creation (< 5 minutes)

### Working State
- Active file modifications in last 5 minutes
- Multiple file changes detected
- Git activity present

### Needs Input State
- Question patterns in recent Claude output:
  - Lines ending with "?"
  - "Would you", "Should I", "Can you" phrases
  - "Please provide", "Please confirm"
- No user activity after question detected

### Review Ready State
- TODO list exists and all items marked complete
- Claude output contains completion indicators:
  - "completed", "finished", "done"
  - "ready for review"
- No pending questions

### Paused State
- No file changes for pauseTimeout duration
- No Claude conversation updates
- Session not manually marked

### Completed State
- User manually marks as complete via IPC
- Persists until session removed

## IPC Interface

```typescript
// Main -> Renderer events
'state-detector:state-changed': { sessionId, oldState, newState, timestamp }
'state-detector:activity-detected': { sessionId, type, details }

// Renderer -> Main handlers
'state-detector:get-state': (sessionId) => SessionState
'state-detector:set-state': (sessionId, state) => void
'state-detector:get-all-states': () => Map<string, SessionState>
```

## Dependencies

- `chokidar`: File system watching
- `electron`: IPC communication
- Node.js built-ins: `fs`, `path`, `events`

## Testing

```bash
npm test -- state-detector
```

Tests verify:
- State detection accuracy for each state
- File watching and event emission
- IPC handler functionality
- Edge cases and error handling
- Performance with multiple sessions

## Performance

- Efficient file watching with debounced events
- Minimal memory footprint per session
- Configurable scan intervals
- Graceful cleanup on session removal

## Error Handling

- Graceful handling of missing directories
- Recovery from file system errors
- Clear error messages in logs
- No crashes from malformed files