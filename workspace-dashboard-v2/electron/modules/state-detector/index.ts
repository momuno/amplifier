/**
 * State Detector Module
 * Public exports for session state detection
 */

export { StateDetector } from './core';
export { StateDetectionEngine } from './detector';
export { SessionWatcher } from './watcher';
export {
  registerStateDetectorHandlers,
  unregisterStateDetectorHandlers,
  sendStateChangeToRenderers,
  sendActivityToRenderers,
} from './ipc';

export type {
  SessionConfig,
  StateDetectorConfig,
  SessionData,
  SessionActivity,
  StateChangeEvent,
  ActivityEvent,
} from './models';

export { SessionState } from './models';

export {
  containsQuestions,
  containsCompletion,
  isTodoFile,
  isClaudeFile,
  parseTodoCompletion,
} from './patterns';