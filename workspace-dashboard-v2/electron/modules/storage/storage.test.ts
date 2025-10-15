import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { StorageModule } from './index';
import { ProjectStatus, TaskStatus, Priority } from '../../../shared/contracts/types';
import fs from 'fs';
import path from 'path';

describe('StorageModule', () => {
  let storage: StorageModule;
  const testDbPath = path.join(__dirname, 'test.db');

  beforeEach(async () => {
    // Clean up any existing test database
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }

    storage = new StorageModule(testDbPath);
    await storage.initialize();
  });

  afterEach(() => {
    storage.close();
    // Clean up test database
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
  });

  describe('Workspace operations', () => {
    it('should create a workspace', async () => {
      const workspace = await storage.createWorkspace({
        name: 'Test Workspace',
        description: 'A test workspace',
        isActive: true
      });

      expect(workspace).toBeDefined();
      expect(workspace.id).toBeDefined();
      expect(workspace.name).toBe('Test Workspace');
      expect(workspace.description).toBe('A test workspace');
      expect(workspace.isActive).toBe(true);
      expect(workspace.createdAt).toBeInstanceOf(Date);
      expect(workspace.updatedAt).toBeInstanceOf(Date);
    });

    it('should get all workspaces', async () => {
      await storage.createWorkspace({ name: 'Workspace 1', isActive: true });
      await storage.createWorkspace({ name: 'Workspace 2', isActive: false });

      const workspaces = await storage.getWorkspaces();

      expect(workspaces).toHaveLength(2);
      expect(workspaces[0].name).toBe('Workspace 2'); // Most recent first
      expect(workspaces[1].name).toBe('Workspace 1');
    });

    it('should update a workspace', async () => {
      const workspace = await storage.createWorkspace({
        name: 'Original Name',
        isActive: true
      });

      const updated = await storage.updateWorkspace(workspace.id, {
        name: 'Updated Name',
        description: 'Now with description'
      });

      expect(updated.name).toBe('Updated Name');
      expect(updated.description).toBe('Now with description');
      expect(updated.isActive).toBe(true); // Unchanged
      expect(updated.updatedAt.getTime()).toBeGreaterThan(workspace.updatedAt.getTime());
    });

    it('should delete a workspace', async () => {
      const workspace = await storage.createWorkspace({
        name: 'To Delete',
        isActive: true
      });

      const deleted = await storage.deleteWorkspace(workspace.id);
      expect(deleted).toBe(true);

      const workspaces = await storage.getWorkspaces();
      expect(workspaces).toHaveLength(0);
    });

    it('should throw error when updating non-existent workspace', async () => {
      await expect(
        storage.updateWorkspace('non-existent', { name: 'New Name' })
      ).rejects.toThrow('Workspace non-existent not found');
    });
  });

  describe('Project operations', () => {
    let workspaceId: string;

    beforeEach(async () => {
      const workspace = await storage.createWorkspace({
        name: 'Test Workspace',
        isActive: true
      });
      workspaceId = workspace.id;
    });

    it('should create a project', async () => {
      const project = await storage.createProject({
        workspaceId,
        name: 'Test Project',
        description: 'A test project',
        status: ProjectStatus.IN_PROGRESS,
        priority: Priority.HIGH,
        tags: ['test', 'sample']
      });

      expect(project).toBeDefined();
      expect(project.id).toBeDefined();
      expect(project.workspaceId).toBe(workspaceId);
      expect(project.name).toBe('Test Project');
      expect(project.status).toBe(ProjectStatus.IN_PROGRESS);
      expect(project.priority).toBe(Priority.HIGH);
      expect(project.tags).toEqual(['test', 'sample']);
    });

    it('should get projects for a workspace', async () => {
      await storage.createProject({
        workspaceId,
        name: 'Project 1',
        status: ProjectStatus.PLANNED,
        priority: Priority.MEDIUM
      });
      await storage.createProject({
        workspaceId,
        name: 'Project 2',
        status: ProjectStatus.IN_PROGRESS,
        priority: Priority.HIGH
      });

      const projects = await storage.getProjects(workspaceId);

      expect(projects).toHaveLength(2);
      expect(projects[0].name).toBe('Project 2'); // Most recent first
      expect(projects[1].name).toBe('Project 1');
    });

    it('should update a project', async () => {
      const project = await storage.createProject({
        workspaceId,
        name: 'Original Project',
        status: ProjectStatus.PLANNED,
        priority: Priority.LOW
      });

      const updated = await storage.updateProject(project.id, {
        name: 'Updated Project',
        status: ProjectStatus.IN_PROGRESS,
        priority: Priority.HIGH
      });

      expect(updated.name).toBe('Updated Project');
      expect(updated.status).toBe(ProjectStatus.IN_PROGRESS);
      expect(updated.priority).toBe(Priority.HIGH);
    });

    it('should delete a project', async () => {
      const project = await storage.createProject({
        workspaceId,
        name: 'To Delete',
        status: ProjectStatus.PLANNED,
        priority: Priority.LOW
      });

      const deleted = await storage.deleteProject(project.id);
      expect(deleted).toBe(true);

      const projects = await storage.getProjects(workspaceId);
      expect(projects).toHaveLength(0);
    });
  });

  describe('Task operations', () => {
    let projectId: string;

    beforeEach(async () => {
      const workspace = await storage.createWorkspace({
        name: 'Test Workspace',
        isActive: true
      });
      const project = await storage.createProject({
        workspaceId: workspace.id,
        name: 'Test Project',
        status: ProjectStatus.IN_PROGRESS,
        priority: Priority.MEDIUM
      });
      projectId = project.id;
    });

    it('should create a task', async () => {
      const task = await storage.createTask({
        projectId,
        title: 'Test Task',
        description: 'A test task',
        status: TaskStatus.TODO,
        priority: Priority.MEDIUM,
        assignee: 'user@example.com',
        tags: ['urgent', 'review']
      });

      expect(task).toBeDefined();
      expect(task.id).toBeDefined();
      expect(task.projectId).toBe(projectId);
      expect(task.title).toBe('Test Task');
      expect(task.status).toBe(TaskStatus.TODO);
      expect(task.assignee).toBe('user@example.com');
      expect(task.tags).toEqual(['urgent', 'review']);
    });

    it('should get tasks for a project', async () => {
      await storage.createTask({
        projectId,
        title: 'Task 1',
        status: TaskStatus.TODO,
        priority: Priority.LOW
      });
      await storage.createTask({
        projectId,
        title: 'Task 2',
        status: TaskStatus.IN_PROGRESS,
        priority: Priority.HIGH
      });

      const tasks = await storage.getTasks(projectId);

      expect(tasks).toHaveLength(2);
      expect(tasks[0].title).toBe('Task 2'); // Most recent first
      expect(tasks[1].title).toBe('Task 1');
    });

    it('should update a task', async () => {
      const task = await storage.createTask({
        projectId,
        title: 'Original Task',
        status: TaskStatus.TODO,
        priority: Priority.LOW
      });

      const updated = await storage.updateTask(task.id, {
        title: 'Updated Task',
        status: TaskStatus.DONE,
        completedAt: new Date()
      });

      expect(updated.title).toBe('Updated Task');
      expect(updated.status).toBe(TaskStatus.DONE);
      expect(updated.completedAt).toBeInstanceOf(Date);
    });

    it('should delete a task', async () => {
      const task = await storage.createTask({
        projectId,
        title: 'To Delete',
        status: TaskStatus.TODO,
        priority: Priority.LOW
      });

      const deleted = await storage.deleteTask(task.id);
      expect(deleted).toBe(true);

      const tasks = await storage.getTasks(projectId);
      expect(tasks).toHaveLength(0);
    });

    it('should handle task checklist', async () => {
      const checklist = [
        { id: '1', label: 'Step 1', completed: false },
        { id: '2', label: 'Step 2', completed: true }
      ];

      const task = await storage.createTask({
        projectId,
        title: 'Task with checklist',
        status: TaskStatus.TODO,
        priority: Priority.MEDIUM,
        checklist
      });

      expect(task.checklist).toEqual(checklist);

      const updated = await storage.updateTask(task.id, {
        checklist: [
          { id: '1', label: 'Step 1', completed: true },
          { id: '2', label: 'Step 2', completed: true },
          { id: '3', label: 'Step 3', completed: false }
        ]
      });

      expect(updated.checklist).toHaveLength(3);
      expect(updated.checklist![0].completed).toBe(true);
    });
  });

  describe('Cascade deletion', () => {
    it('should delete projects when workspace is deleted', async () => {
      const workspace = await storage.createWorkspace({
        name: 'Workspace to delete',
        isActive: true
      });

      await storage.createProject({
        workspaceId: workspace.id,
        name: 'Project 1',
        status: ProjectStatus.PLANNED,
        priority: Priority.LOW
      });

      await storage.deleteWorkspace(workspace.id);
      const projects = await storage.getProjects(workspace.id);
      expect(projects).toHaveLength(0);
    });

    it('should delete tasks when project is deleted', async () => {
      const workspace = await storage.createWorkspace({
        name: 'Test Workspace',
        isActive: true
      });

      const project = await storage.createProject({
        workspaceId: workspace.id,
        name: 'Project to delete',
        status: ProjectStatus.PLANNED,
        priority: Priority.LOW
      });

      await storage.createTask({
        projectId: project.id,
        title: 'Task 1',
        status: TaskStatus.TODO,
        priority: Priority.LOW
      });

      await storage.deleteProject(project.id);
      const tasks = await storage.getTasks(project.id);
      expect(tasks).toHaveLength(0);
    });
  });
});