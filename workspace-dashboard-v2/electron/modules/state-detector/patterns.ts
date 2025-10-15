/**
 * Pattern Definitions for State Detection
 * Regular expressions and patterns for detecting session states
 */

import { DetectionPatterns } from './models';

export const DETECTION_PATTERNS: DetectionPatterns = {
  // Patterns indicating Claude is asking questions
  questions: [
    /\?$/m, // Lines ending with question mark
    /\b(would you|should i|can you|could you)\b/i,
    /\b(please provide|please confirm|please clarify)\b/i,
    /\b(do you want|do you need|do you prefer)\b/i,
    /\b(what would|what should|what do you)\b/i,
    /\b(is it okay|is this correct|does this look)\b/i,
  ],

  // Patterns indicating completion
  completion: [
    /\b(completed|finished|done|complete)\b/i,
    /\b(ready for review|all tests pass|successfully implemented)\b/i,
    /\b(task complete|tasks completed|all todos complete)\b/i,
    /\b(implementation complete|feature complete)\b/i,
  ],

  // File patterns for TODO lists
  todoFiles: [
    /\.todo$/,
    /TODO\.md$/i,
    /todos?\.(txt|md|json)$/i,
    /task[-_]?list\.(txt|md|json)$/i,
  ],

  // Claude-specific file patterns
  claudeFiles: [
    /^\.claude\//,
    /claude[-_]conversation/i,
    /claude[-_]output/i,
    /claude\.log$/i,
  ],
};

/**
 * Check if content contains question patterns
 */
export function containsQuestions(content: string): boolean {
  // Check last 500 characters for recency
  const recentContent = content.slice(-500);
  return DETECTION_PATTERNS.questions.some((pattern) => pattern.test(recentContent));
}

/**
 * Check if content indicates completion
 */
export function containsCompletion(content: string): boolean {
  // Check last 1000 characters for completion indicators
  const recentContent = content.slice(-1000);
  return DETECTION_PATTERNS.completion.some((pattern) => pattern.test(recentContent));
}

/**
 * Check if filename matches TODO pattern
 */
export function isTodoFile(filename: string): boolean {
  return DETECTION_PATTERNS.todoFiles.some((pattern) => pattern.test(filename));
}

/**
 * Check if path is Claude-related
 */
export function isClaudeFile(filepath: string): boolean {
  return DETECTION_PATTERNS.claudeFiles.some((pattern) => pattern.test(filepath));
}

/**
 * Parse TODO content for completion status
 */
export function parseTodoCompletion(content: string): { completed: number; total: number } {
  const lines = content.split('\n');
  let total = 0;
  let completed = 0;

  // Common TODO patterns with checkboxes or status
  const todoPatterns = {
    // Markdown checkboxes: - [ ] or - [x]
    markdown: /^[\s-]*\[([x ])\]/i,
    // Status keywords: TODO, DONE, COMPLETED
    status: /^[\s-]*(TODO|DONE|COMPLETED|PENDING|IN[_ ]PROGRESS)[:.\s]/i,
    // Numbered with status: 1. [DONE] or 1. TODO:
    numbered: /^\d+\.\s*\[(DONE|TODO|x| )\]/i,
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed) return;

    // Check markdown checkbox
    const mdMatch = trimmed.match(todoPatterns.markdown);
    if (mdMatch) {
      total++;
      if (mdMatch[1].toLowerCase() === 'x') {
        completed++;
      }
      return;
    }

    // Check status keywords
    const statusMatch = trimmed.match(todoPatterns.status);
    if (statusMatch) {
      total++;
      const status = statusMatch[1].toUpperCase();
      if (status === 'DONE' || status === 'COMPLETED') {
        completed++;
      }
      return;
    }

    // Check numbered with status
    const numMatch = trimmed.match(todoPatterns.numbered);
    if (numMatch) {
      total++;
      const status = numMatch[1].toUpperCase();
      if (status === 'DONE' || status === 'X') {
        completed++;
      }
      return;
    }

    // Simple bullet points might be TODOs too
    if (/^[-*+]\s+\w/.test(trimmed) && !trimmed.includes('[') && total === 0) {
      // Only count as TODO if we haven't found checkbox-style todos
      total++;
    }
  });

  return { completed, total };
}