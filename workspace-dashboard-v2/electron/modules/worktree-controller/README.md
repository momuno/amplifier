# Worktree Controller Module

A self-contained module for managing Git worktrees in the Workspace Dashboard V2 Electron application. This module provides a clean interface for creating, listing, deleting, and managing Git worktrees to enable isolated development environments for each Claude Code session.

## Purpose

The worktree-controller module enables:
- Creating isolated Git worktrees for parallel development
- Managing multiple work sessions without branch conflicts
- Forking existing worktrees to create new branches
- Cleaning up worktrees when sessions are archived
- Monitoring worktree status and branch information

## Module Contract

### Inputs
- Repository paths (absolute paths to Git repositories)
- Branch names for worktree creation
- Worktree paths for operations
- Configuration options for creation and deletion

### Outputs
- Worktree information (path, branch, status)
- Branch information (current, available branches, remotes)
- Status information (modified files, ahead/behind counts)
- Success/error responses with detailed error codes

### Side Effects
- Creates new directories for worktrees on filesystem
- Modifies Git repository metadata
- Creates or deletes Git branches
- Writes to Git configuration files

### Dependencies
- `simple-git`: ^3.28.0 - Git operations library
- Node.js built-in modules: `fs`, `path`
- Electron IPC for renderer communication

## Public Interface

### Core Class: WorktreeController

```typescript
class WorktreeController {
  // Create a new worktree with optional new branch
  async createWorktree(options: CreateWorktreeOptions): Promise<string>

  // List all worktrees for a repository
  async listWorktrees(repoPath: string): Promise<Worktree[]>

  // Delete a worktree (with optional force)
  async deleteWorktree(worktreePath: string, options?: DeleteWorktreeOptions): Promise<void>

  // Get branch information for a worktree
  async getBranchInfo(worktreePath: string): Promise<BranchInfo>

  // Get status of a worktree
  async getWorktreeStatus(worktreePath: string): Promise<WorktreeStatus>

  // Fork a worktree (create new branch from existing)
  async forkWorktree(sourceWorktreePath: string, newBranchName: string, targetPath?: string): Promise<string>

  // Prune deleted worktrees
  async pruneWorktrees(repoPath: string): Promise<void>
}
```

### IPC Handlers

```typescript
// Initialize IPC handlers for Electron
initializeWorktreeHandlers(): void

// Clean up IPC handlers
cleanupWorktreeHandlers(): void
```

### IPC Channels

- `worktree:create` - Create a new worktree
- `worktree:list` - List all worktrees
- `worktree:delete` - Delete a worktree
- `worktree:branch-info` - Get branch information
- `worktree:status` - Get worktree status
- `worktree:fork` - Fork a worktree
- `worktree:prune` - Prune deleted worktrees

## Usage

### Basic Usage

```typescript
import { WorktreeController } from './worktree-controller';

const controller = new WorktreeController();

// Create a new worktree with a new branch
const worktreePath = await controller.createWorktree({
  repoPath: '/path/to/main/repo',
  branchName: 'feature-branch',
  baseBranch: 'main',
  createBranch: true
});

// List all worktrees
const worktrees = await controller.listWorktrees('/path/to/main/repo');

// Get status of a worktree
const status = await controller.getWorktreeStatus(worktreePath);
console.log(`Branch: ${status.branch}, Clean: ${status.isClean}`);

// Delete worktree when done
await controller.deleteWorktree(worktreePath);
```

### Electron IPC Usage

In the main process:
```typescript
import { initializeWorktreeHandlers } from '@/modules/worktree-controller';

// Initialize handlers on app ready
app.whenReady().then(() => {
  initializeWorktreeHandlers();
});
```

In the renderer process:
```typescript
// Create a worktree
const result = await ipcRenderer.invoke('worktree:create', {
  repoPath: '/path/to/repo',
  branchName: 'new-feature',
  baseBranch: 'main'
});

if (result.success) {
  console.log('Worktree created at:', result.data);
} else {
  console.error('Error:', result.error.message);
}
```

### Forking Worktrees

```typescript
// Fork an existing worktree to create a new branch
const newWorktreePath = await controller.forkWorktree(
  '/path/to/existing/worktree',
  'new-branch-name',
  '/optional/custom/path'
);
```

## Error Handling

The module provides specific error types for different failure scenarios:

| Error Type | Condition | Recovery Strategy |
|------------|-----------|-------------------|
| `RepositoryNotFoundError` | Git repository doesn't exist at path | Verify repository path is correct |
| `WorktreeExistsError` | Worktree already exists at target path | Use different path or delete existing |
| `BranchExistsError` | Branch name already exists | Use different branch name or set createBranch=false |
| `WorktreeNotFoundError` | Worktree doesn't exist at specified path | Verify worktree path |
| `GitOperationError` | General Git operation failure | Check Git installation and permissions |

Example error handling:
```typescript
try {
  await controller.createWorktree(options);
} catch (error) {
  if (error instanceof BranchExistsError) {
    // Handle branch already exists
  } else if (error instanceof WorktreeExistsError) {
    // Handle worktree already exists
  } else {
    // Handle other errors
  }
}
```

## Performance Characteristics

- **Create worktree**: O(n) where n is repository size (Git operation)
- **List worktrees**: O(m) where m is number of worktrees
- **Delete worktree**: O(1) for removal, O(n) for cleanup
- **Status check**: O(f) where f is number of changed files
- **Memory usage**: Minimal, operations are streaming
- **Concurrent operations**: Safe for parallel read operations

## Configuration

No configuration required. The module automatically detects Git settings from the repository.

Optional environment variables:
- `GIT_EXEC_PATH`: Custom Git executable path
- `GIT_WORK_TREE`: Override work tree detection

## Testing

```bash
# Run module tests
npm test -- worktree-controller.test.ts

# Run with coverage
npm run test:coverage -- worktree-controller.test.ts
```

## Edge Cases Handled

1. **Repository not initialized**: Throws `RepositoryNotFoundError`
2. **Worktree already exists**: Throws `WorktreeExistsError`
3. **Branch conflicts**: Detects and reports existing branches
4. **Permission issues**: Wrapped in `GitOperationError` with details
5. **Detached HEAD state**: Properly reported in status
6. **Prunable worktrees**: Automatic cleanup with prune operation
7. **Locked worktrees**: Detected and reported, force option available
8. **Network drives**: Works with repositories on network paths
9. **Symbolic links**: Follows symlinks to actual repository

## Module Structure

```
worktree-controller/
├── index.ts              # Public exports
├── types.ts              # TypeScript type definitions
├── worktree-controller.ts # Core implementation
├── ipc-handlers.ts       # Electron IPC integration
├── worktree-controller.test.ts # Unit tests
└── README.md            # This file
```

## Regeneration Specification

This module can be regenerated from this specification. Key invariants:

- **Public interface**: All exported functions and their signatures
- **IPC channel names**: Must remain consistent for renderer compatibility
- **Error types**: Error classes and their error codes
- **Return data structures**: Shape of Worktree, BranchInfo, WorktreeStatus
- **Side effects**: Filesystem and Git repository modifications

To regenerate:
1. Implement WorktreeController class with specified methods
2. Use simple-git for Git operations
3. Implement IPC handlers wrapping controller methods
4. Ensure error types match specification
5. Maintain same export structure in index.ts

## License

MIT