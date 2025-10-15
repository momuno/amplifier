/**
 * State Detection Logic
 * Core logic for determining session state based on activity
 */

import { SessionState, SessionActivity, SessionData } from './models';
import { containsQuestions } from './patterns';

export class StateDetectionEngine {
  private readonly pauseTimeout: number;
  private readonly recentActivityThreshold: number = 5 * 60 * 1000; // 5 minutes

  constructor(pauseTimeout: number = 15 * 60 * 1000) {
    this.pauseTimeout = pauseTimeout;
  }

  /**
   * Determine session state based on activity data
   */
  detectState(session: SessionData, currentTime: Date = new Date()): SessionState {
    // Manual override takes precedence
    if (session.manualOverride) {
      return session.state;
    }

    const { activity, createdAt } = session;
    const timeSinceCreation = currentTime.getTime() - createdAt.getTime();
    const lastActivity = this.getLastActivityTime(activity);
    const timeSinceActivity = lastActivity
      ? currentTime.getTime() - lastActivity.getTime()
      : timeSinceCreation;

    // Check for COMPLETED state (based on TODO completion and completion indicators)
    if (this.isCompleted(activity)) {
      return SessionState.COMPLETED;
    }

    // Check for NEEDS_INPUT state (questions detected, waiting for user)
    if (this.needsInput(activity, timeSinceActivity)) {
      return SessionState.NEEDS_INPUT;
    }

    // Check for REVIEW_READY state (TODOs done or completion indicated)
    if (this.isReviewReady(activity)) {
      return SessionState.REVIEW_READY;
    }

    // Check for PAUSED state (no recent activity)
    if (this.isPaused(timeSinceActivity)) {
      return SessionState.PAUSED;
    }

    // Check for WORKING state (recent file changes)
    if (this.isWorking(activity, timeSinceActivity)) {
      return SessionState.WORKING;
    }

    // Default to PLANNING for new sessions or minimal activity
    if (this.isPlanning(activity, timeSinceCreation)) {
      return SessionState.PLANNING;
    }

    // Fallback to PAUSED if no other state matches
    return SessionState.PAUSED;
  }

  /**
   * Check if session is in PLANNING state
   */
  private isPlanning(activity: SessionActivity, timeSinceCreation: number): boolean {
    return (
      timeSinceCreation < 5 * 60 * 1000 && // Less than 5 minutes old
      activity.fileChangeCount < 5 && // Minimal file changes
      !activity.lastGitActivity // No git commits yet
    );
  }

  /**
   * Check if session is in WORKING state
   */
  private isWorking(activity: SessionActivity, timeSinceActivity: number): boolean {
    return (
      timeSinceActivity < this.recentActivityThreshold && // Recent activity
      (activity.fileChangeCount > 5 || // Multiple file changes
        activity.lastGitActivity !== undefined) && // Or git activity
      activity.hasQuestions === false // Not waiting for input
    );
  }

  /**
   * Check if session NEEDS_INPUT
   */
  private needsInput(activity: SessionActivity, timeSinceActivity: number): boolean {
    return (
      activity.hasQuestions === true &&
      timeSinceActivity < this.pauseTimeout && // Not paused yet
      (!activity.lastFileChange || // No user activity
        (activity.lastClaudeOutput !== undefined &&
          activity.lastFileChange !== undefined &&
          activity.lastClaudeOutput > activity.lastFileChange)) // Claude asked after last user activity
    );
  }

  /**
   * Check if session is REVIEW_READY
   */
  private isReviewReady(activity: SessionActivity): boolean {
    // TODOs completed
    if (
      activity.todoCompletion &&
      activity.todoCompletion.total > 0 &&
      activity.todoCompletion.completed === activity.todoCompletion.total
    ) {
      return true;
    }

    // Or has completion indicators but no pending questions
    return activity.hasQuestions === false && this.hasCompletionIndicators(activity);
  }

  /**
   * Check if session is PAUSED
   */
  private isPaused(timeSinceActivity: number): boolean {
    return timeSinceActivity >= this.pauseTimeout;
  }

  /**
   * Check if session is COMPLETED
   */
  private isCompleted(activity: SessionActivity): boolean {
    // Check if all TODOs are done AND there are completion indicators
    return (
      activity.todoCompletion !== undefined &&
      activity.todoCompletion.total > 0 &&
      activity.todoCompletion.completed === activity.todoCompletion.total &&
      this.hasCompletionIndicators(activity)
    );
  }

  /**
   * Check for completion indicators in activity
   */
  private hasCompletionIndicators(activity: SessionActivity): boolean {
    // This would be set by the watcher when it detects completion patterns
    // For now, we check TODO completion as a proxy
    return (
      activity.todoCompletion !== undefined &&
      activity.todoCompletion.total > 0 &&
      activity.todoCompletion.completed === activity.todoCompletion.total
    );
  }

  /**
   * Get the most recent activity timestamp
   */
  private getLastActivityTime(activity: SessionActivity): Date | null {
    const times = [activity.lastFileChange, activity.lastClaudeOutput, activity.lastGitActivity].filter(
      (t): t is Date => t !== undefined
    );

    if (times.length === 0) return null;

    return times.reduce((latest, current) => (current > latest ? current : latest));
  }

  /**
   * Update activity based on file content
   */
  updateActivityFromContent(
    activity: SessionActivity,
    content: string,
    isClaudeOutput: boolean = false
  ): void {
    if (isClaudeOutput) {
      activity.lastClaudeOutput = new Date();
      activity.hasQuestions = containsQuestions(content);
    }
  }

  /**
   * Update activity from TODO content
   */
  updateActivityFromTodo(activity: SessionActivity, todoCompletion: { completed: number; total: number }): void {
    activity.todoCompletion = todoCompletion;
  }
}