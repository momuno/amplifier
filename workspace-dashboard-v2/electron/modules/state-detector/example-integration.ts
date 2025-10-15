/**
 * Example integration of the State Detector module
 * This shows how to integrate the module into an Electron app
 */

import { app, BrowserWindow } from 'electron';
import { StateDetector, registerStateDetectorHandlers, SessionState } from './index';

// Initialize the state detector
const stateDetector = new StateDetector({
  pauseTimeout: 15 * 60 * 1000, // 15 minutes
  scanInterval: 5000, // 5 seconds
  debounceDelay: 500, // 500ms
});

export async function initializeStateDetector(mainWindow: BrowserWindow): Promise<StateDetector> {
  // Register IPC handlers for frontend communication
  registerStateDetectorHandlers(stateDetector);

  // Start the detector
  await stateDetector.start();

  // Listen for state changes and send to renderer
  stateDetector.on('stateChange', (event) => {
    console.log(`Session ${event.sessionId} changed from ${event.oldState} to ${event.newState}`);

    // Send to renderer process
    if (!mainWindow.isDestroyed()) {
      mainWindow.webContents.send('state-detector:state-changed', event);
    }
  });

  // Listen for activity events
  stateDetector.on('activity', (event) => {
    console.log(`Activity in session ${event.sessionId}: ${event.type}`);

    // Send to renderer process
    if (!mainWindow.isDestroyed()) {
      mainWindow.webContents.send('state-detector:activity-detected', event);
    }
  });

  // Handle errors
  stateDetector.on('error', (error) => {
    console.error('State detector error:', error);
  });

  return stateDetector;
}

// Example: Add a session to monitor
export async function addSessionExample(detector: StateDetector, sessionPath: string): Promise<void> {
  try {
    await detector.addSession({
      id: `session-${Date.now()}`,
      path: sessionPath,
      name: 'My Claude Session',
    });
    console.log('Session added successfully');
  } catch (error) {
    console.error('Failed to add session:', error);
  }
}

// Example: Manual state override
export function overrideStateExample(detector: StateDetector, sessionId: string): void {
  // Mark session as completed manually
  detector.setState(sessionId, SessionState.COMPLETED);
  console.log(`Session ${sessionId} marked as completed`);
}

// Example: Get all session states
export function getAllStatesExample(detector: StateDetector): void {
  const states = detector.getAllStates();

  states.forEach((state, sessionId) => {
    console.log(`Session ${sessionId}: ${state}`);
  });
}

// Cleanup on app quit
app.on('before-quit', async () => {
  await stateDetector.destroy();
});

/**
 * Frontend usage example (in renderer process):
 *
 * ```typescript
 * // Get current state of a session
 * const state = await window.electron.invoke('state-detector:get-state', sessionId);
 *
 * // Listen for state changes
 * window.electron.on('state-detector:state-changed', (event) => {
 *   console.log(`Session ${event.sessionId} is now ${event.newState}`);
 *   updateUI(event);
 * });
 *
 * // Manually mark as complete
 * await window.electron.invoke('state-detector:set-state', sessionId, 'COMPLETED');
 * ```
 */