/**
 * File Watching Implementation
 * Monitors session directories for changes using chokidar
 */

import * as chokidar from 'chokidar';
import * as path from 'path';
import * as fs from 'fs/promises';
import { EventEmitter } from 'events';
import { SessionActivity, ActivityEvent } from './models';
import { isClaudeFile, isTodoFile, parseTodoCompletion } from './patterns';
import { StateDetectionEngine } from './detector';

export interface WatcherEvents {
  activity: (event: ActivityEvent) => void;
  error: (error: Error) => void;
}

export class SessionWatcher extends EventEmitter {
  private watcher: chokidar.FSWatcher | null = null;
  private readonly sessionPath: string;
  private readonly sessionId: string;
  private readonly activity: SessionActivity;
  private readonly debounceTimers: Map<string, NodeJS.Timeout> = new Map();
  private readonly debounceDelay: number;
  private readonly detectionEngine: StateDetectionEngine;

  constructor(
    sessionId: string,
    sessionPath: string,
    activity: SessionActivity,
    detectionEngine: StateDetectionEngine,
    debounceDelay: number = 500
  ) {
    super();
    this.sessionId = sessionId;
    this.sessionPath = sessionPath;
    this.activity = activity;
    this.debounceDelay = debounceDelay;
    this.detectionEngine = detectionEngine;
  }

  /**
   * Start watching the session directory
   */
  async start(): Promise<void> {
    if (this.watcher) {
      return; // Already watching
    }

    // Verify directory exists
    try {
      await fs.access(this.sessionPath);
    } catch (error) {
      throw new Error(`Session path does not exist: ${this.sessionPath}`);
    }

    // Initialize watcher
    this.watcher = chokidar.watch(this.sessionPath, {
      ignored: [
        /(^|[/\\])\../, // Ignore dot files (except .claude)
        /node_modules/,
        /\.git(?!hub)/, // Ignore .git but not .github
        /__pycache__/,
        /\.pyc$/,
      ],
      persistent: true,
      ignoreInitial: true,
      depth: 5,
      awaitWriteFinish: {
        stabilityThreshold: 300,
        pollInterval: 100,
      },
    });

    // Set up event handlers
    this.watcher
      .on('add', (filePath) => this.handleFileChange(filePath, 'add'))
      .on('change', (filePath) => this.handleFileChange(filePath, 'change'))
      .on('unlink', (filePath) => this.handleFileChange(filePath, 'delete'))
      .on('error', (error) => this.emit('error', error));

    // Do initial scan for Claude and TODO files
    await this.initialScan();
  }

  /**
   * Stop watching
   */
  async stop(): Promise<void> {
    if (this.watcher) {
      await this.watcher.close();
      this.watcher = null;
    }

    // Clear any pending debounce timers
    this.debounceTimers.forEach((timer) => clearTimeout(timer));
    this.debounceTimers.clear();
  }

  /**
   * Initial scan for existing files
   */
  private async initialScan(): Promise<void> {
    try {
      // Check for .claude directory
      const claudePath = path.join(this.sessionPath, '.claude');
      try {
        await fs.access(claudePath);
        // Claude directory exists
        await this.scanClaudeDirectory(claudePath);
      } catch {
        // No .claude directory yet
      }

      // Scan for TODO files
      await this.scanForTodoFiles();

      // Check for git activity
      await this.checkGitActivity();
    } catch (error) {
      this.emit('error', error as Error);
    }
  }

  /**
   * Handle file change events
   */
  private handleFileChange(filePath: string, changeType: 'add' | 'change' | 'delete'): void {
    const relativePath = path.relative(this.sessionPath, filePath);

    // Debounce file changes
    this.debounceFileChange(relativePath, async () => {
      try {
        // Update activity
        this.activity.lastFileChange = new Date();
        if (changeType !== 'delete') {
          this.activity.fileChangeCount++;
        }

        // Check if it's a Claude file
        if (isClaudeFile(relativePath)) {
          await this.processClaudeFile(filePath);
        }

        // Check if it's a TODO file
        if (isTodoFile(relativePath)) {
          await this.processTodoFile(filePath);
        }

        // Check for git activity
        if (relativePath.includes('.git/') && !relativePath.includes('.gitignore')) {
          this.activity.lastGitActivity = new Date();
          this.emitActivity('git_activity', { file: relativePath, changeType });
        }

        // Emit general file change activity
        this.emitActivity('file_change', {
          file: relativePath,
          changeType,
          timestamp: new Date(),
        });
      } catch (error) {
        this.emit('error', error as Error);
      }
    });
  }

  /**
   * Debounce file changes to avoid excessive events
   */
  private debounceFileChange(key: string, callback: () => void): void {
    // Clear existing timer
    const existingTimer = this.debounceTimers.get(key);
    if (existingTimer) {
      clearTimeout(existingTimer);
    }

    // Set new timer
    const timer = setTimeout(() => {
      this.debounceTimers.delete(key);
      callback();
    }, this.debounceDelay);

    this.debounceTimers.set(key, timer);
  }

  /**
   * Process Claude-related files
   */
  private async processClaudeFile(filePath: string): Promise<void> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      this.detectionEngine.updateActivityFromContent(this.activity, content, true);
      this.emitActivity('claude_output', {
        file: path.relative(this.sessionPath, filePath),
        hasQuestions: this.activity.hasQuestions,
      });
    } catch (error) {
      // File might have been deleted or is not readable
      console.error(`Error processing Claude file ${filePath}:`, error);
    }
  }

  /**
   * Process TODO files
   */
  private async processTodoFile(filePath: string): Promise<void> {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      const completion = parseTodoCompletion(content);
      this.detectionEngine.updateActivityFromTodo(this.activity, completion);
      this.emitActivity('todo_update', {
        file: path.relative(this.sessionPath, filePath),
        completion,
      });
    } catch (error) {
      // File might have been deleted or is not readable
      console.error(`Error processing TODO file ${filePath}:`, error);
    }
  }

  /**
   * Scan Claude directory for conversation files
   */
  private async scanClaudeDirectory(claudePath: string): Promise<void> {
    try {
      const files = await fs.readdir(claudePath);
      for (const file of files) {
        if (file.endsWith('.md') || file.endsWith('.txt')) {
          const filePath = path.join(claudePath, file);
          await this.processClaudeFile(filePath);
        }
      }
    } catch (error) {
      // Directory might not be accessible
      console.error('Error scanning Claude directory:', error);
    }
  }

  /**
   * Scan for TODO files in the session
   */
  private async scanForTodoFiles(): Promise<void> {
    const findTodos = async (dir: string, depth: number = 0): Promise<void> => {
      if (depth > 3) return; // Limit depth to avoid deep recursion

      try {
        const entries = await fs.readdir(dir, { withFileTypes: true });
        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);

          if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
            await findTodos(fullPath, depth + 1);
          } else if (entry.isFile() && isTodoFile(entry.name)) {
            await this.processTodoFile(fullPath);
          }
        }
      } catch (error) {
        // Directory might not be accessible
        console.error(`Error scanning directory ${dir}:`, error);
      }
    };

    await findTodos(this.sessionPath);
  }

  /**
   * Check for git activity
   */
  private async checkGitActivity(): Promise<void> {
    try {
      const gitPath = path.join(this.sessionPath, '.git');
      const stats = await fs.stat(gitPath);
      if (stats.isDirectory()) {
        // Check HEAD file for recent commits
        const headPath = path.join(gitPath, 'HEAD');
        const headStats = await fs.stat(headPath);
        this.activity.lastGitActivity = headStats.mtime;
      }
    } catch {
      // No git directory or not accessible
    }
  }

  /**
   * Emit activity event
   */
  private emitActivity(type: ActivityEvent['type'], details: any): void {
    const event: ActivityEvent = {
      sessionId: this.sessionId,
      type,
      details,
      timestamp: new Date(),
    };
    this.emit('activity', event);
  }
}