// IPC Handlers for Worktree Controller

import { ipcMain, IpcMainInvokeEvent } from 'electron';
import { WorktreeController } from './worktree-controller';
import {
  CreateWorktreeOptions,
  DeleteWorktreeOptions,
  WorktreeError
} from './types';

// Singleton instance
let controller: WorktreeController | null = null;

/**
 * Initialize IPC handlers for worktree operations
 */
export function initializeWorktreeHandlers(): void {
  // Create worktree
  ipcMain.handle('worktree:create', async (
    _event: IpcMainInvokeEvent,
    options: CreateWorktreeOptions
  ) => {
    try {
      controller = new WorktreeController();
      const worktreePath = await controller.createWorktree(options);
      return { success: true, data: worktreePath };
    } catch (error) {
      return handleError(error);
    }
  });

  // List worktrees
  ipcMain.handle('worktree:list', async (
    _event: IpcMainInvokeEvent,
    repoPath: string
  ) => {
    try {
      controller = new WorktreeController();
      const worktrees = await controller.listWorktrees(repoPath);
      return { success: true, data: worktrees };
    } catch (error) {
      return handleError(error);
    }
  });

  // Delete worktree
  ipcMain.handle('worktree:delete', async (
    _event: IpcMainInvokeEvent,
    worktreePath: string,
    options?: DeleteWorktreeOptions
  ) => {
    try {
      controller = new WorktreeController();
      await controller.deleteWorktree(worktreePath, options);
      return { success: true };
    } catch (error) {
      return handleError(error);
    }
  });

  // Get branch info
  ipcMain.handle('worktree:branch-info', async (
    _event: IpcMainInvokeEvent,
    worktreePath: string
  ) => {
    try {
      controller = new WorktreeController();
      const branchInfo = await controller.getBranchInfo(worktreePath);
      return { success: true, data: branchInfo };
    } catch (error) {
      return handleError(error);
    }
  });

  // Get worktree status
  ipcMain.handle('worktree:status', async (
    _event: IpcMainInvokeEvent,
    worktreePath: string
  ) => {
    try {
      controller = new WorktreeController();
      const status = await controller.getWorktreeStatus(worktreePath);
      return { success: true, data: status };
    } catch (error) {
      return handleError(error);
    }
  });

  // Fork worktree
  ipcMain.handle('worktree:fork', async (
    _event: IpcMainInvokeEvent,
    sourceWorktreePath: string,
    newBranchName: string,
    targetPath?: string
  ) => {
    try {
      controller = new WorktreeController();
      const newWorktreePath = await controller.forkWorktree(
        sourceWorktreePath,
        newBranchName,
        targetPath
      );
      return { success: true, data: newWorktreePath };
    } catch (error) {
      return handleError(error);
    }
  });

  // Prune worktrees
  ipcMain.handle('worktree:prune', async (
    _event: IpcMainInvokeEvent,
    repoPath: string
  ) => {
    try {
      controller = new WorktreeController();
      await controller.pruneWorktrees(repoPath);
      return { success: true };
    } catch (error) {
      return handleError(error);
    }
  });
}

/**
 * Clean up IPC handlers
 */
export function cleanupWorktreeHandlers(): void {
  const handlers = [
    'worktree:create',
    'worktree:list',
    'worktree:delete',
    'worktree:branch-info',
    'worktree:status',
    'worktree:fork',
    'worktree:prune'
  ];

  handlers.forEach(channel => {
    ipcMain.removeHandler(channel);
  });

  controller = null;
}

/**
 * Handle errors consistently
 */
function handleError(error: unknown): { success: false; error: { message: string; code?: string } } {
  if (error instanceof WorktreeError) {
    return {
      success: false,
      error: {
        message: error.message,
        code: error.code
      }
    };
  }

  const message = error instanceof Error ? error.message : 'An unknown error occurred';
  return {
    success: false,
    error: { message }
  };
}