// Core Worktree Controller Implementation

import simpleGit, { SimpleGit } from 'simple-git';
import * as path from 'path';
import * as fs from 'fs';
import {
  Worktree,
  WorktreeStatus,
  BranchInfo,
  CreateWorktreeOptions,
  DeleteWorktreeOptions,
  RepositoryNotFoundError,
  WorktreeExistsError,
  BranchExistsError,
  WorktreeNotFoundError,
  GitOperationError,
  StatusFile
} from './types';

export class WorktreeController {
  private git: SimpleGit;

  constructor(baseRepoPath?: string) {
    this.git = simpleGit(baseRepoPath);
  }

  /**
   * Create a new worktree
   */
  async createWorktree(options: CreateWorktreeOptions): Promise<string> {
    const { repoPath, branchName, baseBranch, targetPath, createBranch = true } = options;

    // Validate repository exists
    if (!await this.isGitRepository(repoPath)) {
      throw new RepositoryNotFoundError(repoPath);
    }

    // Set git instance to the repository path
    this.git = simpleGit(repoPath);

    // Generate target path if not provided
    const worktreePath = targetPath || path.join(path.dirname(repoPath), `${path.basename(repoPath)}-${branchName}`);

    // Check if worktree path already exists
    if (fs.existsSync(worktreePath)) {
      throw new WorktreeExistsError(worktreePath);
    }

    try {
      // Check if branch exists
      const branches = await this.git.branch();
      const branchExists = branches.all.includes(branchName) ||
                           branches.all.includes(`remotes/origin/${branchName}`);

      if (branchExists && createBranch) {
        throw new BranchExistsError(branchName);
      }

      // Build worktree add command
      const args = ['worktree', 'add'];

      if (createBranch && !branchExists) {
        args.push('-b', branchName);
      }

      args.push(worktreePath);

      if (!createBranch && branchExists) {
        args.push(branchName);
      } else if (baseBranch) {
        args.push(baseBranch);
      }

      // Execute worktree add command
      await this.git.raw(args);

      return worktreePath;
    } catch (error: any) {
      if (error instanceof BranchExistsError || error instanceof WorktreeExistsError) {
        throw error;
      }
      throw new GitOperationError('createWorktree', error.message || 'Unknown error');
    }
  }

  /**
   * List all worktrees for a repository
   */
  async listWorktrees(repoPath: string): Promise<Worktree[]> {
    if (!await this.isGitRepository(repoPath)) {
      throw new RepositoryNotFoundError(repoPath);
    }

    this.git = simpleGit(repoPath);

    try {
      const result = await this.git.raw(['worktree', 'list', '--porcelain']);
      return this.parseWorktreeList(result);
    } catch (error: any) {
      throw new GitOperationError('listWorktrees', error.message || 'Unknown error');
    }
  }

  /**
   * Delete a worktree
   */
  async deleteWorktree(worktreePath: string, options: DeleteWorktreeOptions = {}): Promise<void> {
    const { force = false } = options;

    // Find the main repository from worktree
    const mainRepo = await this.findMainRepository(worktreePath);
    if (!mainRepo) {
      throw new WorktreeNotFoundError(worktreePath);
    }

    this.git = simpleGit(mainRepo);

    try {
      const args = ['worktree', 'remove'];
      if (force) {
        args.push('--force');
      }
      args.push(worktreePath);

      await this.git.raw(args);
    } catch (error: any) {
      // Check if already removed
      if (error.message?.includes('is not a working tree')) {
        // Try to prune if it's already gone
        await this.git.raw(['worktree', 'prune']);
        return;
      }
      throw new GitOperationError('deleteWorktree', error.message || 'Unknown error');
    }
  }

  /**
   * Get branch information for a worktree
   */
  async getBranchInfo(worktreePath: string): Promise<BranchInfo> {
    if (!await this.isGitRepository(worktreePath)) {
      throw new WorktreeNotFoundError(worktreePath);
    }

    const worktreeGit = simpleGit(worktreePath);

    try {
      const branches = await worktreeGit.branch();
      const remotes = await worktreeGit.getRemotes(true);

      return {
        current: branches.current,
        branches: branches.all.filter(b => !b.startsWith('remotes/')),
        remotes: remotes.map(r => r.name),
        tracking: undefined // Tracking info can be obtained from status if needed
      };
    } catch (error: any) {
      throw new GitOperationError('getBranchInfo', error.message || 'Unknown error');
    }
  }

  /**
   * Get status of a worktree
   */
  async getWorktreeStatus(worktreePath: string): Promise<WorktreeStatus> {
    if (!await this.isGitRepository(worktreePath)) {
      throw new WorktreeNotFoundError(worktreePath);
    }

    const worktreeGit = simpleGit(worktreePath);

    try {
      const status = await worktreeGit.status();

      const files: StatusFile[] = [
        ...status.modified.map(f => ({ path: f, index: 'M', working_dir: 'M' })),
        ...status.created.map(f => ({ path: f, index: 'A', working_dir: ' ' })),
        ...status.deleted.map(f => ({ path: f, index: 'D', working_dir: ' ' })),
        ...status.renamed.map(f => ({ path: f.to, index: 'R', working_dir: ' ' })),
        ...status.not_added.map(f => ({ path: f, index: '?', working_dir: '?' }))
      ];

      return {
        path: worktreePath,
        branch: status.current || '',
        ahead: status.ahead,
        behind: status.behind,
        current: true,
        detached: status.detached,
        tracking: status.tracking || undefined,
        files,
        isClean: status.isClean()
      };
    } catch (error: any) {
      throw new GitOperationError('getWorktreeStatus', error.message || 'Unknown error');
    }
  }

  /**
   * Fork a worktree (create new branch from existing)
   */
  async forkWorktree(
    sourceWorktreePath: string,
    newBranchName: string,
    targetPath?: string
  ): Promise<string> {
    // Get the main repository path
    const mainRepo = await this.findMainRepository(sourceWorktreePath);
    if (!mainRepo) {
      throw new WorktreeNotFoundError(sourceWorktreePath);
    }

    // Get current branch from source worktree
    const branchInfo = await this.getBranchInfo(sourceWorktreePath);

    // Create new worktree with new branch based on current branch
    return this.createWorktree({
      repoPath: mainRepo,
      branchName: newBranchName,
      baseBranch: branchInfo.current,
      targetPath,
      createBranch: true
    });
  }

  /**
   * Prune worktrees (remove references to deleted worktrees)
   */
  async pruneWorktrees(repoPath: string): Promise<void> {
    if (!await this.isGitRepository(repoPath)) {
      throw new RepositoryNotFoundError(repoPath);
    }

    this.git = simpleGit(repoPath);

    try {
      await this.git.raw(['worktree', 'prune']);
    } catch (error: any) {
      throw new GitOperationError('pruneWorktrees', error.message || 'Unknown error');
    }
  }

  // Private helper methods

  private async isGitRepository(dirPath: string): Promise<boolean> {
    try {
      if (!fs.existsSync(dirPath)) {
        return false;
      }
      const git = simpleGit(dirPath);
      await git.revparse(['--git-dir']);
      return true;
    } catch {
      return false;
    }
  }

  private async findMainRepository(worktreePath: string): Promise<string | null> {
    try {
      const git = simpleGit(worktreePath);
      const gitDir = await git.revparse(['--git-common-dir']);

      // The common dir for a worktree points to the main repo's .git
      // We need to go up one level to get the main repo path
      if (gitDir.endsWith('.git')) {
        return path.dirname(gitDir.trim());
      }

      // If it's already the main repo
      return gitDir.trim();
    } catch {
      return null;
    }
  }

  private parseWorktreeList(output: string): Worktree[] {
    const worktrees: Worktree[] = [];
    const lines = output.split('\n').filter(line => line.trim());

    let current: Partial<Worktree> = {};

    for (const line of lines) {
      if (line.startsWith('worktree ')) {
        if (current.path) {
          worktrees.push(current as Worktree);
        }
        current = {
          path: line.substring(9),
          isLocked: false
        };
      } else if (line.startsWith('HEAD ')) {
        current.head = line.substring(5);
      } else if (line.startsWith('branch ')) {
        current.branch = line.substring(7);
      } else if (line.startsWith('gitdir ')) {
        current.gitDir = line.substring(7);
      } else if (line === 'locked') {
        current.isLocked = true;
      } else if (line.startsWith('prunable ')) {
        current.prunable = line.substring(9);
      }
    }

    if (current.path) {
      worktrees.push(current as Worktree);
    }

    return worktrees;
  }
}