// Worktree Controller Type Definitions

export interface Worktree {
  path: string;
  gitDir: string;
  branch?: string;
  isLocked: boolean;
  prunable?: string;
  head?: string;
}

export interface WorktreeStatus {
  path: string;
  branch: string;
  ahead: number;
  behind: number;
  current: boolean;
  detached: boolean;
  tracking?: string;
  files: StatusFile[];
  isClean: boolean;
}

export interface StatusFile {
  path: string;
  index: string;
  working_dir: string;
}

export interface BranchInfo {
  current: string;
  branches: string[];
  remotes: string[];
  tracking?: string;
}

export interface CreateWorktreeOptions {
  repoPath: string;
  branchName: string;
  baseBranch?: string;
  targetPath?: string;
  createBranch?: boolean;
}

export interface DeleteWorktreeOptions {
  force?: boolean;
}

// Error types
export class WorktreeError extends Error {
  constructor(message: string, public readonly code?: string) {
    super(message);
    this.name = 'WorktreeError';
  }
}

export class RepositoryNotFoundError extends WorktreeError {
  constructor(path: string) {
    super(`Repository not found at ${path}`, 'REPO_NOT_FOUND');
  }
}

export class WorktreeExistsError extends WorktreeError {
  constructor(path: string) {
    super(`Worktree already exists at ${path}`, 'WORKTREE_EXISTS');
  }
}

export class BranchExistsError extends WorktreeError {
  constructor(branch: string) {
    super(`Branch ${branch} already exists`, 'BRANCH_EXISTS');
  }
}

export class WorktreeNotFoundError extends WorktreeError {
  constructor(path: string) {
    super(`Worktree not found at ${path}`, 'WORKTREE_NOT_FOUND');
  }
}

export class GitOperationError extends WorktreeError {
  constructor(operation: string, details: string) {
    super(`Git operation failed: ${operation} - ${details}`, 'GIT_OPERATION_FAILED');
  }
}