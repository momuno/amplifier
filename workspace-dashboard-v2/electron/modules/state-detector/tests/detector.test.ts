/**
 * Tests for State Detection Logic
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { StateDetectionEngine } from '../detector';
import { SessionState, SessionData, SessionActivity } from '../models';

describe('StateDetectionEngine', () => {
  let engine: StateDetectionEngine;
  let baseSession: SessionData;

  beforeEach(() => {
    engine = new StateDetectionEngine(15 * 60 * 1000); // 15 min timeout
    baseSession = {
      config: {
        id: 'test-session',
        path: '/test/path',
      },
      state: SessionState.PLANNING,
      activity: {
        fileChangeCount: 0,
        hasQuestions: false,
      },
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  });

  describe('detectState', () => {
    it('should detect PLANNING state for new sessions', () => {
      const state = engine.detectState(baseSession);
      expect(state).toBe(SessionState.PLANNING);
    });

    it('should detect WORKING state with recent file changes', () => {
      baseSession.activity.fileChangeCount = 10;
      baseSession.activity.lastFileChange = new Date();
      const state = engine.detectState(baseSession);
      expect(state).toBe(SessionState.WORKING);
    });

    it('should detect NEEDS_INPUT when questions are present', () => {
      baseSession.activity.hasQuestions = true;
      baseSession.activity.lastClaudeOutput = new Date();
      const state = engine.detectState(baseSession);
      expect(state).toBe(SessionState.NEEDS_INPUT);
    });

    it('should detect REVIEW_READY when todos are complete', () => {
      baseSession.activity.todoCompletion = {
        completed: 5,
        total: 5,
      };
      const state = engine.detectState(baseSession);
      expect(state).toBe(SessionState.REVIEW_READY);
    });

    it('should detect PAUSED state after timeout', () => {
      const oldDate = new Date(Date.now() - 20 * 60 * 1000); // 20 minutes ago
      baseSession.activity.lastFileChange = oldDate;
      baseSession.createdAt = oldDate;
      const state = engine.detectState(baseSession);
      expect(state).toBe(SessionState.PAUSED);
    });

    it('should detect COMPLETED when todos done with completion indicators', () => {
      baseSession.activity.todoCompletion = {
        completed: 3,
        total: 3,
      };
      const state = engine.detectState(baseSession);
      expect(state).toBe(SessionState.COMPLETED);
    });

    it('should respect manual override', () => {
      baseSession.manualOverride = true;
      baseSession.state = SessionState.COMPLETED;
      baseSession.activity.fileChangeCount = 10;
      baseSession.activity.lastFileChange = new Date();
      const state = engine.detectState(baseSession);
      expect(state).toBe(SessionState.COMPLETED);
    });
  });

  describe('updateActivityFromContent', () => {
    it('should detect questions in Claude output', () => {
      const activity: SessionActivity = {
        fileChangeCount: 0,
        hasQuestions: false,
      };
      const content = 'Should I proceed with this implementation?';
      engine.updateActivityFromContent(activity, content, true);
      expect(activity.hasQuestions).toBe(true);
      expect(activity.lastClaudeOutput).toBeDefined();
    });

    it('should not detect questions in non-Claude content', () => {
      const activity: SessionActivity = {
        fileChangeCount: 0,
        hasQuestions: false,
      };
      const content = 'This is a regular file with a question?';
      engine.updateActivityFromContent(activity, content, false);
      expect(activity.hasQuestions).toBe(false);
      expect(activity.lastClaudeOutput).toBeUndefined();
    });
  });

  describe('updateActivityFromTodo', () => {
    it('should update todo completion', () => {
      const activity: SessionActivity = {
        fileChangeCount: 0,
        hasQuestions: false,
      };
      engine.updateActivityFromTodo(activity, { completed: 2, total: 5 });
      expect(activity.todoCompletion).toEqual({ completed: 2, total: 5 });
    });
  });
});