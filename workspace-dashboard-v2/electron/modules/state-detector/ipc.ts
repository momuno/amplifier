/**
 * IPC Handlers for State Detector
 * Electron IPC communication for frontend integration
 */

import { ipcMain, IpcMainInvokeEvent } from 'electron';
import { StateDetector } from './core';
import { SessionConfig, SessionState } from './models';

/**
 * Register IPC handlers for state detector
 */
export function registerStateDetectorHandlers(detector: StateDetector): void {
  // Get state for a specific session
  ipcMain.handle('state-detector:get-state', async (_event: IpcMainInvokeEvent, sessionId: string) => {
    try {
      return detector.getState(sessionId);
    } catch (error) {
      console.error('Error getting session state:', error);
      throw error;
    }
  });

  // Get all session states
  ipcMain.handle('state-detector:get-all-states', async () => {
    try {
      const states = detector.getAllStates();
      return Object.fromEntries(states);
    } catch (error) {
      console.error('Error getting all states:', error);
      throw error;
    }
  });

  // Set session state manually
  ipcMain.handle('state-detector:set-state', async (_event: IpcMainInvokeEvent, sessionId: string, state: SessionState) => {
    try {
      detector.setState(sessionId, state);
      return true;
    } catch (error) {
      console.error('Error setting session state:', error);
      throw error;
    }
  });

  // Clear manual override
  ipcMain.handle('state-detector:clear-override', async (_event: IpcMainInvokeEvent, sessionId: string) => {
    try {
      detector.clearManualOverride(sessionId);
      return true;
    } catch (error) {
      console.error('Error clearing manual override:', error);
      throw error;
    }
  });

  // Add session to monitor
  ipcMain.handle('state-detector:add-session', async (_event: IpcMainInvokeEvent, config: SessionConfig) => {
    try {
      await detector.addSession(config);
      return true;
    } catch (error) {
      console.error('Error adding session:', error);
      throw error;
    }
  });

  // Remove session from monitoring
  ipcMain.handle('state-detector:remove-session', async (_event: IpcMainInvokeEvent, sessionId: string) => {
    try {
      await detector.removeSession(sessionId);
      return true;
    } catch (error) {
      console.error('Error removing session:', error);
      throw error;
    }
  });

  // Get session data
  ipcMain.handle('state-detector:get-session-data', async (_event: IpcMainInvokeEvent, sessionId: string) => {
    try {
      return detector.getSessionData(sessionId);
    } catch (error) {
      console.error('Error getting session data:', error);
      throw error;
    }
  });

  // Get all sessions
  ipcMain.handle('state-detector:get-all-sessions', async () => {
    try {
      return detector.getAllSessions();
    } catch (error) {
      console.error('Error getting all sessions:', error);
      throw error;
    }
  });
}

/**
 * Unregister IPC handlers
 */
export function unregisterStateDetectorHandlers(): void {
  const handlers = [
    'state-detector:get-state',
    'state-detector:get-all-states',
    'state-detector:set-state',
    'state-detector:clear-override',
    'state-detector:add-session',
    'state-detector:remove-session',
    'state-detector:get-session-data',
    'state-detector:get-all-sessions',
  ];

  handlers.forEach((channel) => {
    ipcMain.removeHandler(channel);
  });
}

/**
 * Send state change event to all renderer windows
 */
export function sendStateChangeToRenderers(webContents: Electron.WebContents[], event: any): void {
  webContents.forEach((contents) => {
    if (!contents.isDestroyed()) {
      contents.send('state-detector:state-changed', event);
    }
  });
}

/**
 * Send activity event to all renderer windows
 */
export function sendActivityToRenderers(webContents: Electron.WebContents[], event: any): void {
  webContents.forEach((contents) => {
    if (!contents.isDestroyed()) {
      contents.send('state-detector:activity-detected', event);
    }
  });
}