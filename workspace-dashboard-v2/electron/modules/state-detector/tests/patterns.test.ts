/**
 * Tests for Pattern Detection
 */

import { describe, it, expect } from 'vitest';
import {
  containsQuestions,
  containsCompletion,
  isTodoFile,
  isClaudeFile,
  parseTodoCompletion,
} from '../patterns';

describe('Pattern Detection', () => {
  describe('containsQuestions', () => {
    it('should detect question marks', () => {
      expect(containsQuestions('Is this working?')).toBe(true);
      expect(containsQuestions('This is working.')).toBe(false);
    });

    it('should detect question phrases', () => {
      expect(containsQuestions('Would you like to continue')).toBe(true);
      expect(containsQuestions('Should I implement this feature')).toBe(true);
      expect(containsQuestions('Can you provide more details')).toBe(true);
      expect(containsQuestions('Please confirm your choice')).toBe(true);
    });

    it('should check recent content only', () => {
      const longText = 'a'.repeat(1000) + 'Should I continue?';
      expect(containsQuestions(longText)).toBe(true);

      const oldQuestion = 'Should I continue?' + 'b'.repeat(1000);
      expect(containsQuestions(oldQuestion)).toBe(false);
    });
  });

  describe('containsCompletion', () => {
    it('should detect completion keywords', () => {
      expect(containsCompletion('Task completed successfully')).toBe(true);
      expect(containsCompletion('All tests finished')).toBe(true);
      expect(containsCompletion('Implementation is done')).toBe(true);
      expect(containsCompletion('Ready for review now')).toBe(true);
    });

    it('should not detect partial matches', () => {
      expect(containsCompletion('Still working on it')).toBe(false);
      expect(containsCompletion('Not yet ready')).toBe(false);
    });
  });

  describe('isTodoFile', () => {
    it('should detect TODO file patterns', () => {
      expect(isTodoFile('tasks.todo')).toBe(true);
      expect(isTodoFile('TODO.md')).toBe(true);
      expect(isTodoFile('todos.txt')).toBe(true);
      expect(isTodoFile('task-list.md')).toBe(true);
      expect(isTodoFile('task_list.json')).toBe(true);
    });

    it('should not match non-TODO files', () => {
      expect(isTodoFile('readme.md')).toBe(false);
      expect(isTodoFile('index.js')).toBe(false);
      expect(isTodoFile('todo-component.tsx')).toBe(false);
    });
  });

  describe('isClaudeFile', () => {
    it('should detect Claude file patterns', () => {
      expect(isClaudeFile('.claude/conversation.md')).toBe(true);
      expect(isClaudeFile('claude-conversation.txt')).toBe(true);
      expect(isClaudeFile('claude_output.log')).toBe(true);
      expect(isClaudeFile('claude.log')).toBe(true);
    });

    it('should not match non-Claude files', () => {
      expect(isClaudeFile('README.md')).toBe(false);
      expect(isClaudeFile('.git/config')).toBe(false);
      expect(isClaudeFile('claude-component.tsx')).toBe(false);
    });
  });

  describe('parseTodoCompletion', () => {
    it('should parse markdown checkboxes', () => {
      const content = `
- [ ] First task
- [x] Second task
- [ ] Third task
- [X] Fourth task
`;
      const result = parseTodoCompletion(content);
      expect(result).toEqual({ completed: 2, total: 4 });
    });

    it('should parse status keywords', () => {
      const content = `
TODO: First task
DONE: Second task
COMPLETED: Third task
PENDING: Fourth task
IN_PROGRESS: Fifth task
`;
      const result = parseTodoCompletion(content);
      expect(result).toEqual({ completed: 2, total: 5 });
    });

    it('should parse numbered todos', () => {
      const content = `
1. [TODO] First task
2. [DONE] Second task
3. [x] Third task
4. [ ] Fourth task
`;
      const result = parseTodoCompletion(content);
      expect(result).toEqual({ completed: 2, total: 4 });
    });

    it('should handle empty content', () => {
      const result = parseTodoCompletion('');
      expect(result).toEqual({ completed: 0, total: 0 });
    });

    it('should handle mixed formats', () => {
      const content = `
# TODO List
- [x] Setup project
- [ ] Write tests
TODO: Add documentation
DONE: Configure linting
`;
      const result = parseTodoCompletion(content);
      expect(result).toEqual({ completed: 2, total: 4 });
    });
  });
});