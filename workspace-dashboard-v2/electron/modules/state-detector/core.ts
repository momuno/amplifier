/**
 * State Detector Core
 * Main class for managing session state detection
 */

import { EventEmitter } from 'events';
import {
  SessionState,
  SessionConfig,
  StateDetectorConfig,
  SessionData,
  StateChangeEvent,
  ActivityEvent,
} from './models';
import { StateDetectionEngine } from './detector';
import { SessionWatcher } from './watcher';

export class StateDetector extends EventEmitter {
  private readonly sessions: Map<string, SessionData> = new Map();
  private readonly watchers: Map<string, SessionWatcher> = new Map();
  private readonly config: Required<StateDetectorConfig>;
  private readonly detectionEngine: StateDetectionEngine;
  private scanInterval: NodeJS.Timeout | null = null;

  constructor(config: StateDetectorConfig = {}) {
    super();
    this.config = {
      pauseTimeout: config.pauseTimeout ?? 15 * 60 * 1000, // 15 minutes
      scanInterval: config.scanInterval ?? 5000, // 5 seconds
      debounceDelay: config.debounceDelay ?? 500, // 500ms
    };
    this.detectionEngine = new StateDetectionEngine(this.config.pauseTimeout);
  }

  /**
   * Start the state detector
   */
  async start(): Promise<void> {
    // Start periodic state scanning
    if (!this.scanInterval) {
      this.scanInterval = setInterval(() => {
        this.scanAllSessions();
      }, this.config.scanInterval);
    }
  }

  /**
   * Stop the state detector
   */
  async stop(): Promise<void> {
    // Stop periodic scanning
    if (this.scanInterval) {
      clearInterval(this.scanInterval);
      this.scanInterval = null;
    }

    // Stop all watchers
    const stopPromises = Array.from(this.watchers.values()).map((watcher) => watcher.stop());
    await Promise.all(stopPromises);
    this.watchers.clear();
  }

  /**
   * Add a session to monitor
   */
  async addSession(config: SessionConfig): Promise<void> {
    if (this.sessions.has(config.id)) {
      throw new Error(`Session ${config.id} already exists`);
    }

    // Initialize session data
    const sessionData: SessionData = {
      config,
      state: SessionState.PLANNING,
      activity: {
        fileChangeCount: 0,
        hasQuestions: false,
      },
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.sessions.set(config.id, sessionData);

    // Create and start watcher
    const watcher = new SessionWatcher(
      config.id,
      config.path,
      sessionData.activity,
      this.detectionEngine,
      this.config.debounceDelay
    );

    // Listen to watcher events
    watcher.on('activity', (event: ActivityEvent) => {
      this.handleActivityEvent(event);
    });

    watcher.on('error', (error: Error) => {
      console.error(`Watcher error for session ${config.id}:`, error);
      this.emit('error', { sessionId: config.id, error });
    });

    try {
      await watcher.start();
      this.watchers.set(config.id, watcher);

      // Initial state detection
      this.detectStateChange(config.id);
    } catch (error) {
      // Clean up on failure
      this.sessions.delete(config.id);
      throw error;
    }
  }

  /**
   * Remove a session from monitoring
   */
  async removeSession(sessionId: string): Promise<void> {
    // Stop and remove watcher
    const watcher = this.watchers.get(sessionId);
    if (watcher) {
      await watcher.stop();
      this.watchers.delete(sessionId);
    }

    // Remove session data
    this.sessions.delete(sessionId);
  }

  /**
   * Get current state of a session
   */
  getState(sessionId: string): SessionState | null {
    const session = this.sessions.get(sessionId);
    return session ? session.state : null;
  }

  /**
   * Get all session states
   */
  getAllStates(): Map<string, SessionState> {
    const states = new Map<string, SessionState>();
    this.sessions.forEach((session, id) => {
      states.set(id, session.state);
    });
    return states;
  }

  /**
   * Manually set session state
   */
  setState(sessionId: string, state: SessionState): void {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    const oldState = session.state;
    session.state = state;
    session.manualOverride = true;
    session.updatedAt = new Date();

    // Emit state change event
    this.emitStateChange(sessionId, oldState, state, 'manual');
  }

  /**
   * Clear manual override for a session
   */
  clearManualOverride(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.manualOverride = false;
      this.detectStateChange(sessionId);
    }
  }

  /**
   * Get session data
   */
  getSessionData(sessionId: string): SessionData | null {
    return this.sessions.get(sessionId) || null;
  }

  /**
   * Get all sessions
   */
  getAllSessions(): SessionData[] {
    return Array.from(this.sessions.values());
  }

  /**
   * Handle activity events from watchers
   */
  private handleActivityEvent(event: ActivityEvent): void {
    // Update session timestamp
    const session = this.sessions.get(event.sessionId);
    if (session) {
      session.updatedAt = new Date();
    }

    // Emit activity event
    this.emit('activity', event);

    // Check for state change
    this.detectStateChange(event.sessionId);
  }

  /**
   * Scan all sessions for state changes
   */
  private scanAllSessions(): void {
    this.sessions.forEach((_, sessionId) => {
      this.detectStateChange(sessionId);
    });
  }

  /**
   * Detect and emit state changes for a session
   */
  private detectStateChange(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    const oldState = session.state;
    const newState = this.detectionEngine.detectState(session);

    if (newState !== oldState && !session.manualOverride) {
      session.state = newState;
      session.updatedAt = new Date();
      this.emitStateChange(sessionId, oldState, newState, 'detected');
    }
  }

  /**
   * Emit state change event
   */
  private emitStateChange(sessionId: string, oldState: SessionState, newState: SessionState, reason: string): void {
    const event: StateChangeEvent = {
      sessionId,
      oldState,
      newState,
      timestamp: new Date(),
      reason,
    };
    this.emit('stateChange', event);
  }

  /**
   * Clean up resources
   */
  async destroy(): Promise<void> {
    await this.stop();
    this.removeAllListeners();
    this.sessions.clear();
  }
}