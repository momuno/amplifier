// Worktree Controller Module - Public Interface

export { WorktreeController } from './worktree-controller';
export {
  initializeWorktreeHandlers,
  cleanupWorktreeHandlers
} from './ipc-handlers';

export type {
  Worktree,
  WorktreeStatus,
  StatusFile,
  BranchInfo,
  CreateWorktreeOptions,
  DeleteWorktreeOptions
} from './types';

export {
  WorktreeError,
  RepositoryNotFoundError,
  WorktreeExistsError,
  BranchExistsError,
  WorktreeNotFoundError,
  GitOperationError
} from './types';