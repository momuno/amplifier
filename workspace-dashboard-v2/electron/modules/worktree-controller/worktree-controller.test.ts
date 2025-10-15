// Worktree Controller Tests

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import * as fs from 'fs';
import simpleGit from 'simple-git';
import { WorktreeController } from './worktree-controller';
import {
  RepositoryNotFoundError,
  WorktreeExistsError,
  BranchExistsError,
  WorktreeNotFoundError
} from './types';

// Mock simple-git
vi.mock('simple-git');

describe('WorktreeController', () => {
  let controller: WorktreeController;
  let mockGit: any;

  beforeEach(() => {
    controller = new WorktreeController();

    // Setup mock git instance
    mockGit = {
      raw: vi.fn(),
      branch: vi.fn(),
      status: vi.fn(),
      revparse: vi.fn(),
      getRemotes: vi.fn()
    };

    (simpleGit as any).mockReturnValue(mockGit);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('createWorktree', () => {
    beforeEach(() => {
      vi.spyOn(fs, 'existsSync').mockImplementation((path) => {
        // Repository exists, but worktree path doesn't
        if (path === '/repo/path') return true;
        if (path === '/repo/path-feature') return false;
        return false;
      });

      mockGit.revparse.mockResolvedValue('--git-dir');
    });

    it('should create a new worktree with a new branch', async () => {
      mockGit.branch.mockResolvedValue({
        all: ['main', 'develop'],
        current: 'main',
        branches: {}
      });

      mockGit.raw.mockResolvedValue('');

      const result = await controller.createWorktree({
        repoPath: '/repo/path',
        branchName: 'feature',
        baseBranch: 'main'
      });

      expect(result).toBe('/repo/path-feature');
      expect(mockGit.raw).toHaveBeenCalledWith([
        'worktree', 'add', '-b', 'feature', '/repo/path-feature', 'main'
      ]);
    });

    it('should throw RepositoryNotFoundError for invalid repo path', async () => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(false);

      await expect(controller.createWorktree({
        repoPath: '/invalid/path',
        branchName: 'feature'
      })).rejects.toThrow(RepositoryNotFoundError);
    });

    it('should throw WorktreeExistsError if worktree path exists', async () => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(true);
      mockGit.revparse.mockResolvedValue('--git-dir');

      await expect(controller.createWorktree({
        repoPath: '/repo/path',
        branchName: 'feature'
      })).rejects.toThrow(WorktreeExistsError);
    });

    it('should throw BranchExistsError if branch already exists', async () => {
      mockGit.branch.mockResolvedValue({
        all: ['main', 'feature'],
        current: 'main',
        branches: {}
      });

      await expect(controller.createWorktree({
        repoPath: '/repo/path',
        branchName: 'feature',
        createBranch: true
      })).rejects.toThrow(BranchExistsError);
    });

    it('should use existing branch if createBranch is false', async () => {
      mockGit.branch.mockResolvedValue({
        all: ['main', 'feature'],
        current: 'main',
        branches: {}
      });

      mockGit.raw.mockResolvedValue('');

      const result = await controller.createWorktree({
        repoPath: '/repo/path',
        branchName: 'feature',
        createBranch: false
      });

      expect(result).toBe('/repo/path-feature');
      expect(mockGit.raw).toHaveBeenCalledWith([
        'worktree', 'add', '/repo/path-feature', 'feature'
      ]);
    });

    it('should use custom target path if provided', async () => {
      mockGit.branch.mockResolvedValue({
        all: ['main'],
        current: 'main',
        branches: {}
      });

      mockGit.raw.mockResolvedValue('');

      vi.spyOn(fs, 'existsSync').mockImplementation((path) => {
        if (path === '/repo/path') return true;
        if (path === '/custom/path') return false;
        return false;
      });

      const result = await controller.createWorktree({
        repoPath: '/repo/path',
        branchName: 'feature',
        targetPath: '/custom/path'
      });

      expect(result).toBe('/custom/path');
      expect(mockGit.raw).toHaveBeenCalledWith([
        'worktree', 'add', '-b', 'feature', '/custom/path'
      ]);
    });
  });

  describe('listWorktrees', () => {
    beforeEach(() => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(true);
      mockGit.revparse.mockResolvedValue('--git-dir');
    });

    it('should list all worktrees', async () => {
      const mockOutput = `worktree /repo/path
HEAD abc123
branch refs/heads/main

worktree /repo/path-feature
HEAD def456
branch refs/heads/feature
`;

      mockGit.raw.mockResolvedValue(mockOutput);

      const result = await controller.listWorktrees('/repo/path');

      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({
        path: '/repo/path',
        head: 'abc123',
        branch: 'refs/heads/main',
        isLocked: false
      });
      expect(result[1]).toEqual({
        path: '/repo/path-feature',
        head: 'def456',
        branch: 'refs/heads/feature',
        isLocked: false
      });
    });

    it('should handle locked worktrees', async () => {
      const mockOutput = `worktree /repo/path-locked
HEAD abc123
branch refs/heads/locked-branch
locked
`;

      mockGit.raw.mockResolvedValue(mockOutput);

      const result = await controller.listWorktrees('/repo/path');

      expect(result[0].isLocked).toBe(true);
    });

    it('should throw RepositoryNotFoundError for invalid repo', async () => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(false);

      await expect(controller.listWorktrees('/invalid/path'))
        .rejects.toThrow(RepositoryNotFoundError);
    });
  });

  describe('deleteWorktree', () => {
    beforeEach(() => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(true);
      mockGit.revparse.mockResolvedValue('/repo/path/.git');
    });

    it('should delete a worktree', async () => {
      mockGit.raw.mockResolvedValue('');

      await controller.deleteWorktree('/repo/path-feature');

      expect(mockGit.raw).toHaveBeenCalledWith([
        'worktree', 'remove', '/repo/path-feature'
      ]);
    });

    it('should force delete when force option is true', async () => {
      mockGit.raw.mockResolvedValue('');

      await controller.deleteWorktree('/repo/path-feature', { force: true });

      expect(mockGit.raw).toHaveBeenCalledWith([
        'worktree', 'remove', '--force', '/repo/path-feature'
      ]);
    });

    it('should prune if worktree is already gone', async () => {
      mockGit.raw.mockRejectedValueOnce(
        new Error('is not a working tree')
      ).mockResolvedValueOnce('');

      await controller.deleteWorktree('/repo/path-feature');

      expect(mockGit.raw).toHaveBeenCalledTimes(2);
      expect(mockGit.raw).toHaveBeenLastCalledWith(['worktree', 'prune']);
    });

    it('should throw WorktreeNotFoundError if main repo not found', async () => {
      mockGit.revparse.mockRejectedValue(new Error('not a git repository'));

      await expect(controller.deleteWorktree('/invalid/worktree'))
        .rejects.toThrow(WorktreeNotFoundError);
    });
  });

  describe('getBranchInfo', () => {
    beforeEach(() => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(true);
      mockGit.revparse.mockResolvedValue('--git-dir');
    });

    it('should return branch information', async () => {
      mockGit.branch.mockResolvedValue({
        all: ['main', 'feature', 'remotes/origin/main'],
        current: 'feature',
        branches: {
          feature: { current: true }
        }
      });

      mockGit.getRemotes.mockResolvedValue([
        { name: 'origin', refs: {} }
      ]);

      const result = await controller.getBranchInfo('/repo/path-feature');

      expect(result).toEqual({
        current: 'feature',
        branches: ['main', 'feature'],
        remotes: ['origin'],
        tracking: undefined
      });
    });

    it('should throw WorktreeNotFoundError for invalid path', async () => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(false);

      await expect(controller.getBranchInfo('/invalid/path'))
        .rejects.toThrow(WorktreeNotFoundError);
    });
  });

  describe('getWorktreeStatus', () => {
    beforeEach(() => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(true);
      mockGit.revparse.mockResolvedValue('--git-dir');
    });

    it('should return worktree status', async () => {
      mockGit.status.mockResolvedValue({
        current: 'feature',
        ahead: 2,
        behind: 1,
        detached: false,
        tracking: 'origin/feature',
        modified: ['file1.js'],
        created: ['file2.js'],
        deleted: ['file3.js'],
        renamed: [{ from: 'old.js', to: 'new.js' }],
        not_added: ['untracked.js'],
        isClean: () => false
      });

      const result = await controller.getWorktreeStatus('/repo/path-feature');

      expect(result.branch).toBe('feature');
      expect(result.ahead).toBe(2);
      expect(result.behind).toBe(1);
      expect(result.isClean).toBe(false);
      expect(result.files).toHaveLength(5);
    });

    it('should handle clean worktree', async () => {
      mockGit.status.mockResolvedValue({
        current: 'main',
        ahead: 0,
        behind: 0,
        detached: false,
        modified: [],
        created: [],
        deleted: [],
        renamed: [],
        not_added: [],
        isClean: () => true
      });

      const result = await controller.getWorktreeStatus('/repo/path');

      expect(result.isClean).toBe(true);
      expect(result.files).toHaveLength(0);
    });
  });

  describe('forkWorktree', () => {
    beforeEach(() => {
      vi.spyOn(fs, 'existsSync').mockImplementation((path) => {
        const pathStr = String(path);
        if (pathStr.includes('-new-feature')) return false;
        return true;
      });

      mockGit.revparse.mockResolvedValue('/repo/path/.git');
      mockGit.branch.mockResolvedValue({
        all: ['main', 'feature'],
        current: 'feature',
        branches: {}
      });
    });

    it('should fork a worktree with new branch', async () => {
      mockGit.raw.mockResolvedValue('');

      const result = await controller.forkWorktree(
        '/repo/path-feature',
        'new-feature'
      );

      expect(result).toBe('/repo/path-new-feature');
      expect(mockGit.raw).toHaveBeenCalledWith([
        'worktree', 'add', '-b', 'new-feature', '/repo/path-new-feature', 'feature'
      ]);
    });

    it('should use custom target path for fork', async () => {
      mockGit.raw.mockResolvedValue('');

      vi.spyOn(fs, 'existsSync').mockImplementation((path) => {
        if (path === '/custom/fork') return false;
        return true;
      });

      const result = await controller.forkWorktree(
        '/repo/path-feature',
        'new-feature',
        '/custom/fork'
      );

      expect(result).toBe('/custom/fork');
    });
  });

  describe('pruneWorktrees', () => {
    beforeEach(() => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(true);
      mockGit.revparse.mockResolvedValue('--git-dir');
    });

    it('should prune worktrees', async () => {
      mockGit.raw.mockResolvedValue('');

      await controller.pruneWorktrees('/repo/path');

      expect(mockGit.raw).toHaveBeenCalledWith(['worktree', 'prune']);
    });

    it('should throw RepositoryNotFoundError for invalid repo', async () => {
      vi.spyOn(fs, 'existsSync').mockReturnValue(false);

      await expect(controller.pruneWorktrees('/invalid/path'))
        .rejects.toThrow(RepositoryNotFoundError);
    });
  });
});